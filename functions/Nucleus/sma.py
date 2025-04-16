# 引入套件
import os
import sys
import argparse
from dataclasses import dataclass
from collections import Counter

# 自定義模組
from utils.InputParser import UserInfo
from utils.FileParser import readQPCRData
from utils.DataObject import WELL, QPCRRecord, Range, AnalysisOutput
from utils.ConstVaribles import QCStatus, AssessmentStatus, NucleusVersion

# 獲取當前腳本所在的目錄. 將上一層目錄添加到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)
sys.path.append(current_dir)

# 引入 saveLogs
from systemLogger import Logger
logger = Logger()

# 定義 SMA data object
@dataclass
class SMAData:
  group: str # SC1, SC2, NTC, Sample
  sample_name: str
  well_position: WELL
  smn1: QPCRRecord = None
  smn2: QPCRRecord = None
  rnp: QPCRRecord = None
  normalized_smn1: float = None
  normalized_smn2: float = None

  def __init__(self, group, sample_name, well_position, smn1 = None, smn2 = None, rnp = None):
    self.group = group
    self.sample_name = sample_name
    self.well_position = well_position
    self.smn1 = smn1
    self.smn2 = smn2
    self.rnp = rnp
    self.NormalizeSMNCT()

  def __str__(self):
    smn1CT = self.smn1.ct_value if self.smn1 else "None"
    smn2CT = self.smn2.ct_value if self.smn2 else "None"
    rnpCT = self.rnp.ct_value if self.rnp else "None"
    normalized_smn1 = self.normalized_smn1 if self.normalized_smn1 else "None"
    normalized_smn2 = self.normalized_smn2 if self.normalized_smn2 else "None"
    return f"SMAData(group={self.group}, sample_name={self.sample_name}, well_position={str(self.well_position)}, smn1={smn1CT}, smn2={smn2CT}, rnp={rnpCT}, normalized_smn1={normalized_smn1}, normalized_smn2={normalized_smn2})"

  # 計算 delta CT
  def NormalizeSMNCT(self):
    if self.smn1 and self.rnp and self.smn1.pass_cutoff and self.rnp.pass_cutoff:
      self.normalized_smn1 = round(self.rnp.ct_value - self.smn1.ct_value, 2)

    if self.smn2 and self.rnp and self.smn2.pass_cutoff and self.rnp.pass_cutoff:
      self.normalized_smn2 = round(self.rnp.ct_value - self.smn2.ct_value, 2)

# 定義 SMA result object
@dataclass
class SMAResult:
  sample_name: str
  well_position: WELL
  normalized_smn1: float
  normalized_smn2: float
  smn1_Type: int # 0N, 1N, 2N, 3N, 4N
  smn2_Type: int # 0N, 1N, 2N, 3N, 4N
  typeStr:str
  assessment_result: AssessmentStatus

  def __init__(self, sample_name, well_position, normalized_smn1, normalized_smn2, smn1_Type, smn2_Type):
    self.sample_name = sample_name
    self.well_position = well_position
    self.normalized_smn1 = normalized_smn1
    self.normalized_smn2 = normalized_smn2
    self.smn1_Type = smn1_Type
    self.smn2_Type = smn2_Type
    self.typeStr = f"{str(self.smn1_Type)}:{str(self.smn2_Type)}"

    # 初始化 normal_List, carrier_List, affected, affected_weho, affected_dubo, affected_kuwel, invalid_List
    self.normal_List = [
      "2:0", "2:1", "2:2", "2:3", "2:4",
      "3:0", "3:1", "3:2", "3:3", "3:4",
      "4:1", "4:2", "4:3", "4:4"
    ]

    # 定義 Carrier
    self.carrier_List = [
      "1:0", "1:1", "1:2", "1:3", "1:4"
    ]

    # 定義 Affected
    self.affected       = "0:1"
    self.affected_weho  = "0:2"
    self.affected_dubo  = "0:3"
    self.affected_kuwel = "0:4"

    # 定義 Invalid
    self.invalid_List = ["0:0"]

    self.assessment_result = self.getAssessmentResult()

  def __str__(self):
    return f"SMAResult(sample_name={self.sample_name}, well_position={str(self.well_position)}, normalized_smn1={self.normalized_smn1}, normalized_smn2={self.normalized_smn2}, smn1_Type={self.smn1_Type}, smn2_Type={self.smn2_Type}, assessment_result={self.assessment_result.value})"

  def getAssessmentResult(self):
    if self.typeStr in self.normal_List:
      return AssessmentStatus.NORMAL
    elif self.typeStr in self.carrier_List:
      return AssessmentStatus.CARRIER
    elif self.typeStr == self.affected:
      return AssessmentStatus.AFFECTED
    elif self.typeStr == self.affected_weho:
      return AssessmentStatus.AFFECTED_WEHO
    elif self.typeStr == self.affected_dubo:
      return AssessmentStatus.AFFECTED_DUBO
    elif self.typeStr == self.affected_kuwel:
      return AssessmentStatus.AFFECTED_KUWEL
    elif self.typeStr in self.invalid_List:
      return AssessmentStatus.INVALID
    else:
      return AssessmentStatus.INVALID

# 定義 SMA output object
@dataclass
class SMAOutput(AnalysisOutput):
  SC1Data: SMAData = None
  SC2Data: SMAData = None
  NTCData: SMAData = None
  SMAparameters: dict = None
  sampleDataList: list[SMAData] = None
  resultList: list[SMAResult] = None

# SMA 分析腳本
def SMA(input_file_path, FAM_file_path, VIC_file_path, CY5_file_path, SC1_well, SC2_well, NTC_well, SMA_version, user_info, parameters = None):

  # 定義 SMA 的 CT 門檻
  TOWER_CT_Threshold_RANGE = Range(15, 30)
  CT_Threshold_SMA = 30

  # QS3 QC 的範圍
  SMN1_SC1_SC2_DIFF_Range = Range(0.87, 1.46)
  SMN2_SC1_SC2_DIFF_Range = Range(0.75, 1.44)

  # z480 校正數值
  Z480_SMN1_FACTOR = 0.47
  Z480_SMN2_FACTOR = 0.52

  if parameters:
    SMN1_SC1_SC2_DIFF_Range = Range(parameters["SMN1_SC1_SC2_DIFF_Range"]["MIN"], parameters["SMN1_SC1_SC2_DIFF_Range"]["MAX"])
    SMN2_SC1_SC2_DIFF_Range = Range(parameters["SMN2_SC1_SC2_DIFF_Range"]["MIN"], parameters["SMN2_SC1_SC2_DIFF_Range"]["MAX"])
    Z480_SMN1_FACTOR = parameters["Z480_SMN1_FACTOR"]
    Z480_SMN2_FACTOR = parameters["Z480_SMN2_FACTOR"]

  # Logger settings
  sender = user_info.organization
  logger.setSender(sender)

  # Logger : Start Message
  tmp_source = "sma.py line. 149"
  logger.analysis(f" ----> Start SMA Analysis <---- ", tmp_source)
  logger.analysis(f" User Info: {user_info}", tmp_source)

  # 取得 config
  config = {
    "reagent": user_info.reagent,
    "organization": user_info.organization,
    "instrument": user_info.instrument,
    "NucleusVersion": NucleusVersion.SMA.value,
    "SMA_version": SMA_version
  }

  # 初始化 SMAOutput
  sma_output = SMAOutput(config=config)

  # 初始化 CT_Limit_Range
  CT_Limit_Range = Range(0, CT_Threshold_SMA)

  # 如果 parameters 存在, 則使用 parameters 中的 CT_Threshold_Range
  if parameters:
    CT_Limit_Range = Range(parameters["CT_Threshold_Range"]["MIN"], parameters["CT_Threshold_Range"]["MAX"])

  # 1. 讀取 Qpcr data 並轉換為 QPCRRecord 列表
  qpcr_record_list = readQPCRData(input_file_path, FAM_file_path, VIC_file_path, user_info.instrument, CT_Limit_Range.MAX, CY5_file_path)

  # 將重複的樣本名稱加上後綴
  append_suffix_to_duplicates(qpcr_record_list)

  # 如果是 tower, 則在針對 pass cutoff 的 QPCRRecord 檢查 CT 是否小於等於 15, 或大於等於 30, 若超出此範圍 pass_cutoff 設為 False
  if user_info.instrument == "tower":
    if parameters:
      CT_Limit_Range = Range(parameters["CT_Threshold_Range"]["MIN"], parameters["CT_Threshold_Range"]["MAX"])
    else:
      CT_Limit_Range = TOWER_CT_Threshold_RANGE

    for r in qpcr_record_list:
      if r.pass_cutoff and not CT_Limit_Range.inRange(r.ct_value):
        r.pass_cutoff = False

  # 紀錄 QPCRRecord 列表
  tmp_source = "sma.py line. 185"
  logger.analysis(f"[{user_info.instrument}] QPCR Raw data:", tmp_source)
  for r in qpcr_record_list:
    logger.analysis(f"{r}", tmp_source)

  # 初始化 controlWell 和 ntcWell
  sc1_well = SC1_well
  sc2_well = SC2_well
  ntc_well = NTC_well

  # 將 control_well 和 ntc_well 轉換為 WELL 物件
  if type(sc1_well) == str:
    sc1_well = WELL(sc1_well)

  if type(sc2_well) == str:
    sc2_well = WELL(sc2_well)

  if type(ntc_well) == str:
    ntc_well = WELL(ntc_well)

  # 檢查 control_well 是否在 QPCRRecord 列表裡面
  for controlWell in [sc1_well, sc2_well]:
    if controlWell not in [r.well_position for r in qpcr_record_list]:
      errorMessage = f"control_well {controlWell} 不在 QPCRRecord 列表裡面"
      tmp_source = "sma.py line. 206"
      logger.error(errorMessage, tmp_source)
      sma_output.errMsg = errorMessage
      return sma_output.toJson()

  # 檢查 ntc_well 是否在 QPCRRecord 列表裡面
  if ntc_well not in [r.well_position for r in qpcr_record_list]:
    errorMessage = f"ntc_well {ntc_well} 不在 QPCRRecord 列表裡面"
    tmp_source = "sma.py line. 215"
    logger.error(errorMessage, tmp_source)
    sma_output.errMsg = errorMessage
    return sma_output.toJson()

  # 解析 SMAData
  dataMatrix = parseSMAData(qpcr_record_list, sc1_well, sc2_well, ntc_well, user_info.instrument)

  # 更新 SMAOutput
  sma_output.SC1Data = dataMatrix["sc1"]
  sma_output.SC2Data = dataMatrix["sc2"]
  sma_output.NTCData = dataMatrix["ntc"]
  sma_output.sampleDataList = dataMatrix["sample"]

  # QC
  qc_status, qc_message = QC(dataMatrix, user_info.instrument, SMN1_SC1_SC2_DIFF_Range, SMN2_SC1_SC2_DIFF_Range)

  # QC 通過, 進行 Sample Assessment
  if qc_status == QCStatus.PASSED:

    # 計算 1N 2N 3N 4N 的 CT 範圍
    Threshold_Range = calculate_CT_Threshold(dataMatrix["sc1"], dataMatrix["sc2"], parameters)
    sma_output.SMAparameters = {
      "Threshold_Range": Threshold_Range,
      "CT_Limit_Range": CT_Limit_Range,
      "z480_Factors": {
        "Z480_SMN1_FACTOR": Z480_SMN1_FACTOR,
        "Z480_SMN2_FACTOR": Z480_SMN2_FACTOR
      },
      "deltaCT_QC_Range": {
        "smn1": SMN1_SC1_SC2_DIFF_Range,
        "smn2": SMN2_SC1_SC2_DIFF_Range
      }
    }

    # 進行 Sample Assessment
    sample_assessment_results = [SampleAssessment(data, user_info.instrument, Threshold_Range, SMA_version, Z480_SMN1_FACTOR, Z480_SMN2_FACTOR) for data in dataMatrix["sample"]]

    # 輸出 Sample Assessment 結果
    tmp_source = "sma.py line. 250"
    logger.analysis(f"Sample Assessment Results:", tmp_source)
    for result in sample_assessment_results:
      logger.analysis(str(result), tmp_source)

    # 更新 SMAOutput
    sma_output.qc_status = qc_status
    sma_output.resultList = sample_assessment_results

  # QC 失敗, 跳過 Sample Assessment
  elif qc_status == QCStatus.FAILED:
    tmp_source = "sma.py line. 260"
    logger.error(qc_message, tmp_source)
    sma_output.qc_status = qc_status
    sma_output.errMsg = qc_message

    # 如果 QC 失敗也將每個 Sample 的空結果回傳
    failed_result = [SMAResult(data.sample_name, data.well_position, 0, 0, 0, 0) for data in dataMatrix["sample"]]
    sma_output.resultList = failed_result

  # 若 QC 未分析, 也跳過 Sample Assessment
  else:
    tmp_source = "sma.py line. 268"
    logger.error("Not Analyzed", tmp_source)
    sma_output.qc_status = qc_status
    sma_output.errMsg = qc_message

  tmp_source = "sma.py line. 275"
  logger.analysis(f"* SMA Analysis Completed *", tmp_source)

  return sma_output.toJson()

# # 處理 SMA 列表
def parseSMAData(qpcr_record_list, sc1_well, sc2_well, ntc_well, instrument):

  if instrument == "tower":
    SMN1_REPORTER = "FAM"
    SMN2_REPORTER = "VIC"
    RNP_REPORTER = ["ROX"]
  elif instrument == "qs3":
    SMN1_REPORTER = "FAM"
    SMN2_REPORTER = "VIC"
    RNP_REPORTER = ["ROX", "TAMRA"]
  elif instrument == "z480":
    SMN1_REPORTER = "FAM"
    SMN2_REPORTER = "VIC"
    RNP_REPORTER = ["CY5"]
  else:
    raise ValueError(f"不支援的儀器類型: {instrument}")

  # 實體化 SMAData
  sc1SMAData = SMAData(
    group="SC1",
    sample_name=next((x.sample_name for x in qpcr_record_list if x.well_position == sc1_well), None),
    well_position=next((x.well_position for x in qpcr_record_list if x.well_position == sc1_well), None),
    smn1=next((x for x in qpcr_record_list if x.well_position == sc1_well and x.reporter == SMN1_REPORTER), None),
    smn2=next((x for x in qpcr_record_list if x.well_position == sc1_well and x.reporter == SMN2_REPORTER), None),
    rnp=next((x for x in qpcr_record_list if x.well_position == sc1_well and x.reporter in RNP_REPORTER), None),
  )
  sc2SMAData = SMAData(
    group="SC2",
    sample_name=next((x.sample_name for x in qpcr_record_list if x.well_position == sc2_well), None),
    well_position=next((x.well_position for x in qpcr_record_list if x.well_position == sc2_well), None),
    smn1=next((x for x in qpcr_record_list if x.well_position == sc2_well and x.reporter == SMN1_REPORTER), None),
    smn2=next((x for x in qpcr_record_list if x.well_position == sc2_well and x.reporter == SMN2_REPORTER), None),
    rnp=next((x for x in qpcr_record_list if x.well_position == sc2_well and x.reporter in RNP_REPORTER), None),
  )
  ntcSMAData = SMAData(
    group="NTC",
    sample_name=next((x.sample_name for x in qpcr_record_list if x.well_position == ntc_well), None),
    well_position=next((x.well_position for x in qpcr_record_list if x.well_position == ntc_well), None),
    smn1=next((x for x in qpcr_record_list if x.well_position == ntc_well and x.reporter == SMN1_REPORTER), None),
    smn2=next((x for x in qpcr_record_list if x.well_position == ntc_well and x.reporter == SMN2_REPORTER), None),
    rnp=next((x for x in qpcr_record_list if x.well_position == ntc_well and x.reporter in RNP_REPORTER), None),
  )

  # 取得 qpcr_record_list 中 sample names
  sample_names = list(set([x.sample_name for x in qpcr_record_list if x.well_position != sc1_well and x.well_position != sc2_well and x.well_position != ntc_well]))
  sampleSMADataList = [SMAData(
    group="Sample",
    sample_name=name,
    well_position=next((x.well_position for x in qpcr_record_list if x.sample_name == name), None),
    smn1=next((x for x in qpcr_record_list if x.sample_name == name and x.reporter == SMN1_REPORTER), None),
    smn2=next((x for x in qpcr_record_list if x.sample_name == name and x.reporter == SMN2_REPORTER), None),
    rnp=next((x for x in qpcr_record_list if x.sample_name == name and x.reporter in RNP_REPORTER), None),
  ) for name in sample_names]

  # 輸出 MTHFRData 列表
  tmp_source = "sma.py line. 280"
  logger.analysis(f"SMAData:", tmp_source)
  logger.analysis(str(sc1SMAData), tmp_source)
  logger.analysis(str(sc2SMAData), tmp_source)
  logger.analysis(str(ntcSMAData), tmp_source)
  for data in sampleSMADataList:
    logger.analysis(str(data), tmp_source)

  dataMatrix = {
    "sc1": sc1SMAData,
    "sc2": sc2SMAData,
    "ntc": ntcSMAData,
    "sample": sampleSMADataList
  }

  return dataMatrix

# 將重複的樣本名稱加上後綴
def append_suffix_to_duplicates(input_list):
    counter = Counter()

    # 紀錄當前 reporter, 如果遇到不同 reporter 則清空 counter
    current_reporter = input_list[0].reporter
    for item in input_list:
        next_reporter = item.reporter
        if next_reporter != current_reporter:
            current_reporter = next_reporter
            counter.clear()

        # 紀錄樣本名稱出現次數
        counter[item.sample_name] += 1

        # 如果樣本名稱出現次數大於 1, 則加上後綴
        if counter[item.sample_name] > 1:
            new_sample_name = f"{item.sample_name}-{counter[item.sample_name] - 1}"
        else:
            new_sample_name = item.sample_name

        # 更新 sample_name
        item.sample_name = new_sample_name

# QC
def QC(dataMatrix, instrument, SMN1_SC1_SC2_DIFF_Range, SMN2_SC1_SC2_DIFF_Range):

  # 初始化 qc_status
  qc_status = QCStatus.NOT_ANALYZED
  qc_message = ""

  # 取得 controlData 和 NTCData
  sc1Data = dataMatrix["sc1"]
  sc2Data = dataMatrix["sc2"]
  ntcData = dataMatrix["ntc"]

  # NTC, SC1, SC2 的 smn1 和 smn2, rnp 都不能為 None
  for data in [sc1Data, sc2Data, ntcData]:
    if not data.smn1 or not data.smn2 or not data.rnp:
      errMsg = f"{data.group} 的 smn1 或 smn2 或 rnp 為 None"
      tmp_source = "sma.py line. 389"
      logger.error(errMsg, tmp_source)
      qc_status = QCStatus.FAILED
      qc_message = errMsg
      return qc_status, qc_message

  # QC 條件1: NTC 的 smn1 和 smn2, rnp 都"不"通過 cutoff (CT > CT_Threshold 或 沒有數值)
  condition1 = not ntcData.smn1.pass_cutoff and not ntcData.smn2.pass_cutoff and not ntcData.rnp.pass_cutoff
  if not condition1:
    errMsg = f"Failed QC: NTC 的 smn1 或 smn2 或 rnp 沒有通過 cutoff"
    tmp_source = "sma.py line. 400"
    logger.warn(errMsg, tmp_source)
    qc_message = errMsg

  # QC 條件2: SC1 和 SC2 的 smn1 和 smn2 都通過 cutoff
  condition2 = sc1Data.smn1.pass_cutoff and sc1Data.smn2.pass_cutoff and sc2Data.smn1.pass_cutoff and sc2Data.smn2.pass_cutoff
  if not condition2:
    errMsg = f"Failed QC: SC1 或 SC2 的 smn1 或 smn2 沒有通過 cutoff"
    tmp_source = "sma.py line. 408"
    logger.warn(errMsg, tmp_source)
    qc_message = errMsg

  # QS3, 條件3 為 SC1, SC2 的 normalized_smn1 和 normalized_smn2 要在指定區間之內
  if instrument == "qs3":

    # 計算 SC1, SC2 的 smn1 difference
    smn1_sc1_sc2_difference = abs(sc1Data.normalized_smn1 - sc2Data.normalized_smn1)
    smn2_sc1_sc2_difference = abs(sc1Data.normalized_smn2 - sc2Data.normalized_smn2)

    # 計算 SC1, SC2 的 smn1 difference 是否在指定區間
    condition3 = SMN1_SC1_SC2_DIFF_Range.inRange(smn1_sc1_sc2_difference) and SMN2_SC1_SC2_DIFF_Range.inRange(smn2_sc1_sc2_difference)

    if not condition3:
      errMsg = f"Failed QC: SMN1 或 SMN2 的 SC1 和 SC2 的 delta CT 差值不在指定區間"
      tmp_source = "sma.py line. 424"
      logger.warn(errMsg, tmp_source)
      qc_message = errMsg

  # Tower, 條件3 為 SC1 的 normalized_smn1 和 normalized_smn2 都大於 0
  elif instrument == "tower":
    condition3 = sc1Data.normalized_smn1 > 0 and sc1Data.normalized_smn2 > 0
    if not condition3:
      errMsg = f"Failed QC: SC1 的 normalized_smn1 或 normalized_smn2 不大於 0"
      tmp_source = "sma.py line. 431"
      logger.warn(errMsg, tmp_source)
      qc_message = errMsg

  # Z480, 並沒有額外條件
  elif instrument == "z480":
    condition3 = True
    qc_message = "Passed"

  # 例外判斷：使用儀器類型錯誤
  else:
    raise ValueError(f"不支援的儀器類型: {instrument}")

  # 如果 QC 條件1 和 條件2 和 條件3 都通過, 則 qc_status 為 PASSED
  if condition1 and condition2 and condition3:
    qc_status = QCStatus.PASSED
    qc_message = "QC Passed"
  else:
    qc_status = QCStatus.FAILED

  return qc_status, qc_message

# 計算 1N 2N 3N 4N 的 CT 範圍
def calculate_CT_Threshold(SC1_data, SC2_data, parameters):

  # SMN1 的 CT 範圍
  smn1_1n = SC1_data.normalized_smn1
  smn1_2n = SC2_data.normalized_smn1
  delta_smn1 = round(smn1_2n - smn1_1n, 2)
  smn1_3n = round(smn1_2n + delta_smn1, 2)
  smn1_4n = round(smn1_3n + delta_smn1, 2)

  # SMN2 的 CT 範圍
  smn2_1n = SC1_data.normalized_smn2
  smn2_2n = SC2_data.normalized_smn2
  delta_smn2 = round(smn2_2n - smn2_1n, 2)
  smn2_3n = round(smn2_2n + delta_smn2, 2)
  smn2_4n = round(smn2_3n + delta_smn2, 2)

  threshold_range = {
    "smn1": {
      "1n": smn1_1n,
      "2n": smn1_2n,
      "3n": smn1_3n,
      "4n": smn1_4n
    },
    "smn1_restricted": {
      "1n": float(smn1_1n + smn1_2n) / 2,
      "2n": float(smn1_2n + smn1_3n) / 2,
      "3n": float(smn1_3n + smn1_4n) / 2
    },
    "smn2": {
      "1n": smn2_1n,
      "2n": smn2_2n,
      "3n": smn2_3n,
      "4n": smn2_4n
    },
    "smn2_restricted": {
      "1n": float(smn2_1n + smn2_2n) / 2,
      "2n": float(smn2_2n + smn2_3n) / 2,
      "3n": float(smn2_3n + smn2_4n) / 2
    }
  }

  if parameters:
    threshold_range["smn1"]["1n"] = parameters["SMN_Select_Range"]["smn1"]["1n"]
    threshold_range["smn1"]["2n"] = parameters["SMN_Select_Range"]["smn1"]["2n"]
    threshold_range["smn1"]["3n"] = parameters["SMN_Select_Range"]["smn1"]["3n"]
    threshold_range["smn1_restricted"]["1n"] = float((parameters["SMN_Select_Range"]["smn1"]["1n"] + parameters["SMN_Select_Range"]["smn1"]["2n"]) / 2)
    threshold_range["smn1_restricted"]["2n"] = float((parameters["SMN_Select_Range"]["smn1"]["2n"] + parameters["SMN_Select_Range"]["smn1"]["3n"]) / 2)
    threshold_range["smn1_restricted"]["3n"] = float((parameters["SMN_Select_Range"]["smn1"]["3n"] + threshold_range["smn1"]["4n"]) / 2)
    threshold_range["smn2"]["1n"] = parameters["SMN_Select_Range"]["smn2"]["1n"]
    threshold_range["smn2"]["2n"] = parameters["SMN_Select_Range"]["smn2"]["2n"]
    threshold_range["smn2"]["3n"] = parameters["SMN_Select_Range"]["smn2"]["3n"]
    threshold_range["smn2_restricted"]["1n"] = float((parameters["SMN_Select_Range"]["smn2"]["1n"] + parameters["SMN_Select_Range"]["smn2"]["2n"]) / 2)
    threshold_range["smn2_restricted"]["2n"] = float((parameters["SMN_Select_Range"]["smn2"]["2n"] + parameters["SMN_Select_Range"]["smn2"]["3n"]) / 2)
    threshold_range["smn2_restricted"]["3n"] = float((parameters["SMN_Select_Range"]["smn2"]["3n"] + threshold_range["smn2"]["4n"]) / 2)

  return threshold_range

# 進行 Sample Assessment
def SampleAssessment(data, instrument, Threshold_Range, SMA_version, Z480_SMN1_FACTOR, Z480_SMN2_FACTOR):

  # 判斷 SMN type
  def get_smn_type(normalized_smn, threshold_range):
    if normalized_smn is None:
      return 0
    elif normalized_smn <= threshold_range["1n"]:
      return 1
    elif normalized_smn <= threshold_range["2n"]:
      return 2
    elif normalized_smn <= threshold_range["3n"]:
      return 3
    elif normalized_smn > threshold_range["3n"]:
      return 4
    else:
      return None

  # 取得 normalized_smn1 和 normalized_smn2
  normalized_smn1 = data.normalized_smn1
  normalized_smn2 = data.normalized_smn2

  # 如果是 z480 則校正數值
  if instrument == "z480":
    if not normalized_smn1:
      normalized_smn1 = None
    else:
      normalized_smn1 = round(normalized_smn1 - Z480_SMN1_FACTOR, 3)

    if not normalized_smn2:
      normalized_smn2 = None
    else:
      normalized_smn2 = round(normalized_smn2 - Z480_SMN2_FACTOR, 3)

  # 取得 normalized_smn1 和 normalized_smn2 的 type
  if SMA_version == "v1":
    smn1_type = get_smn_type(normalized_smn1, Threshold_Range["smn1"])
    smn2_type = get_smn_type(normalized_smn2, Threshold_Range["smn2"])
  elif SMA_version == "v2":
    smn1_type = get_smn_type(normalized_smn1, Threshold_Range["smn1"])
    smn2_type = get_smn_type(normalized_smn2, Threshold_Range["smn2_restricted"])
  elif SMA_version == "v3":
    smn1_type = get_smn_type(normalized_smn1, Threshold_Range["smn1_restricted"])
    smn2_type = get_smn_type(normalized_smn2, Threshold_Range["smn2_restricted"])
  else:
    raise ValueError(f"不支援的 SMA 版本: {SMA_version}")

  # SMA result
  smar = SMAResult(
    sample_name=data.sample_name,
    well_position=data.well_position,
    normalized_smn1=normalized_smn1,
    normalized_smn2=normalized_smn2,
    smn1_Type=smn1_type,
    smn2_Type=smn2_type,
  )

  return smar

# 處理 CLI parameters
def parseParams():

  # 接收 CLI 參數
  parser = argparse.ArgumentParser()
  parser.add_argument("--inputfile", "-i", required=False, type=str, help="輸入檔案路徑 (Excel), 若儀器為 qs3 或 tower 必填")
  parser.add_argument("--FAMfile", "-f", required=False, type=str, help="FAM 檔案路徑 (Text), 若儀器為 z480 必填")
  parser.add_argument("--VICfile", "-v", required=False, type=str, help="VIC 檔案路徑 (Text), 若儀器為 z480 必填")
  parser.add_argument("--CY5file", "-y", required=False, type=str, help="CY5 檔案路徑 (Text), 若儀器為 z480 必填")
  parser.add_argument("--controlwell1", "-c1", required=True, type=str, help="Standard 1 控制組 well 位置")
  parser.add_argument("--controlwell2", "-c2", required=True, type=str, help="Standard 2 控制組 well 位置")
  parser.add_argument("--ntcwell", "-n", required=True, type=str, help="NTC well 位置")
  parser.add_argument("--smaversion", "-s", required=True, type=str, choices=["v1", "v2", "v3"], help="SMA 版本, 目前有 ['v1', 'v2', 'v3']")
  parser.add_argument("--reagent", required=True, type=str, choices=["accuinSMA1", "accuinSMA2", "accuinSMA3"], help="試劑類型, 目前有 ['accuinSMA1', 'accuinSMA2', 'accuinSMA3'] (必填)")
  parser.add_argument("--instrument", required=True, type=str, choices=["qs3", "tower", "z480"], help="儀器類型, 目前有 ['qs3', 'tower', 'z480'] (必填)")
  parser.add_argument("--organization", "-g", required=False, default="defaultOrg", type=str, help="組織所屬, SMA 不會用到可以不用設定")
  parser.add_argument("--output", "-o", required=False, type=str, help="輸出結果的 JSON 檔案路徑, 若不給定, 則輸出到 console")
  args = parser.parse_args()

  # 驗證 CLI 參數

  # 1. 驗證儀器類型, 若儀器為 qs3 或 tower 必填 inputfile 參數
  if args.instrument == "qs3" or args.instrument == "tower":

    # 驗證 inputfile 參數
    if not args.inputfile:
      raise ValueError("儀器為 qs3 或 tower 時, 必填 inputfile 參數")

    # 檢查檔案是否存在
    if not os.path.exists(args.inputfile):
      raise ValueError(f"inputfile 檔案不存在: {args.inputfile}")

    # 初步檢查副檔名
    if not (args.inputfile.endswith(".xlsx") or args.inputfile.endswith(".xls") or args.inputfile.endswith(".csv")):
      raise ValueError("inputfile 副檔名錯誤, 請提供 .xlsx 或 .xls 或 .csv 檔案")

    # 如果是 qs3, reagent 必須為 accuinSMA1 或 accuinSMA2
    if args.instrument == "qs3" and args.reagent != "accuinSMA1" and args.reagent != "accuinSMA2":
      raise ValueError("儀器為 qs3 時, reagent 必須為 accuinSMA1 或 accuinSMA2")

    # 如果是 tower, reagent 必須為 accuinSMA1
    if args.instrument == "tower" and args.reagent != "accuinSMA1":
      raise ValueError("儀器為 tower 時, reagent 必須為 accuinSMA1")

  # 2. 驗證儀器類型, 若儀器為 z480 必填 FAMfile 和 VICfile 和 CY5file 參數
  elif args.instrument == "z480":

    # 驗證 FAMfile 和 VICfile 和 CY5file 參數
    if not args.FAMfile or not args.VICfile or not args.CY5file:
      raise ValueError("儀器為 z480 時, 必填 FAMfile 和 VICfile 和 CY5file 參數")

    # 檢查檔案是否存在
    if not os.path.exists(args.FAMfile):
      raise ValueError(f"FAMfile 檔案不存在: {args.FAMfile}")
    if not os.path.exists(args.VICfile):
      raise ValueError(f"VICfile 檔案不存在: {args.VICfile}")
    if not os.path.exists(args.CY5file):
      raise ValueError(f"CY5file 檔案不存在: {args.CY5file}")

    # 初步檢查副檔名
    if not args.FAMfile.endswith(".txt"):
      raise ValueError("FAMfile 副檔名錯誤, 請提供 .txt 檔案")
    if not args.VICfile.endswith(".txt"):
      raise ValueError("VICfile 副檔名錯誤, 請提供 .txt 檔案")
    if not args.CY5file.endswith(".txt"):
      raise ValueError("CY5file 副檔名錯誤, 請提供 .txt 檔案")

    # 如果是 z480, reagent 必須為 accuinSMA3
    if args.instrument == "z480" and args.reagent != "accuinSMA3":
      raise ValueError("儀器為 z480 時, reagent 必須為 accuinSMA3")

  return args

# SMA CLI
if __name__ == "__main__":

  # 設定 Logger 模式
  logger = Logger(mode="offline")

  # 處理 CLI parameters
  args = parseParams()

  # 解析 CLI 參數
  input_file_path = args.inputfile
  FAM_file_path = args.FAMfile
  VIC_file_path = args.VICfile
  CY5_file_path = args.CY5file
  SC1_well = args.controlwell1
  SC2_well = args.controlwell2
  NTC_well = args.ntcwell
  user_info = UserInfo(
    instrument=args.instrument,
    reagent=args.reagent,
    organization=args.organization
  )

  # 輸出結果
  sma_output = SMA(
    input_file_path=input_file_path,
    FAM_file_path=FAM_file_path,
    VIC_file_path=VIC_file_path,
    CY5_file_path=CY5_file_path,
    SC1_well=SC1_well,
    SC2_well=SC2_well,
    NTC_well=NTC_well,
    SMA_version=args.smaversion,
    user_info=user_info
  )

  # 如果有設定 output 參數, 則將結果寫入檔案
  if args.output:
    with open(args.output, "w") as f:
      f.write(sma_output)
  else:
    print(sma_output)
