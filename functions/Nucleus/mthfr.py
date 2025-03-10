# 導入模組
import os
import sys
import argparse
from dataclasses import dataclass
from enum import Enum

# 自定義模組
from utils.ConstVaribles import QCStatus, AssessmentStatus, NucleusVersion
from utils.DataObject import WELL, QPCRRecord, AnalysisOutput
from utils.InputParser import UserInfo
from utils.FileParser import readQPCRData

# 獲取當前腳本所在的目錄. 將上一層目錄添加到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)
sys.path.append(current_dir)

# 引入 saveLogs
from systemLogger import Logger
logger = Logger()

# CT_THRESHOLD
class CT_Threshold(Enum):
  TOWER = 38
  Z480 = 0
  QS3 = 35
  DELTA_CT_THRESHOLD_V3 = 4

# 定義 MTHFR DataObject
@dataclass
class MTHFRData():
  group: str # SC, NTC, Sample
  sample_name: str
  well_position: WELL
  c677_wt: QPCRRecord = None
  c677_mut: QPCRRecord = None
  c1298_wt: QPCRRecord = None
  c1298_mut: QPCRRecord = None

  def __str__(self):
    c677_wt_str = f"{self.c677_wt.ct_value}" if self.c677_wt else "None"
    c677_mut_str = f"{self.c677_mut.ct_value}" if self.c677_mut else "None"
    c1298_wt_str = f"{self.c1298_wt.ct_value}" if self.c1298_wt else "None"
    c1298_mut_str = f"{self.c1298_mut.ct_value}" if self.c1298_mut else "None"
    return f"MTHFRData(group: {self.group}, sample_name: {self.sample_name}, well_position: {str(self.well_position)}, c677_wtCT: {c677_wt_str}, c677_mutCT: {c677_mut_str}, c1298_wtCT: {c1298_wt_str}, c1298_mutCT: {c1298_mut_str})"

# 定義 MTHFR 結果
@dataclass
class MTHFRResult():
  sample_name: str
  reagent: str
  assessment: AssessmentStatus
  sample_qc_status: QCStatus
  sample_type: list[str]

  def __str__(self):
    return f"MTHFRResult(sample_name: {self.sample_name}, reagent: {self.reagent}, assessment: {self.assessment.value}, sample_qc_status: {self.sample_qc_status.value}, sample_type: {'/'.join(self.sample_type)})"

# 定義 MTHFR 輸出
@dataclass
class MTHFROutput(AnalysisOutput):
  controlData: MTHFRData = None
  ntcData: MTHFRData = None
  sampleDataList: list[MTHFRData] = None
  resultList: list[MTHFRResult] = None

# MTHFR 主程式
def MTHFR(input_file_path, FAM_file_path, VIC_file_path, control_well, ntc_well, user_info):

  # Logger settings
  sender = user_info.organization
  logger.setSender(sender)

  # Logger : Start Message
  tmp_source = "mthfr.py line. 70"
  logger.analysis(f" ----> Start MTHFR Analysis <---- ", tmp_source)
  logger.analysis(f" User Info: {user_info}", tmp_source)

  # 取得 config
  config = {
    "reagent": user_info.reagent,
    "organization": user_info.organization,
    "instrument": user_info.instrument,
    "NucleusVersion": NucleusVersion.MTHFR.value
  }

  # 初始化 MTHFROutput
  mthfr_output = MTHFROutput(config=config)

  # 決定 CT_Threshold
  if user_info.instrument == "tower":
    ct_threshold = CT_Threshold.TOWER.value
  elif user_info.instrument == "z480":
    ct_threshold = CT_Threshold.Z480.value
  elif user_info.instrument == "qs3":
    ct_threshold = CT_Threshold.QS3.value
  else:
    raise ValueError(f"不支援的儀器: {user_info.instrument}")

  # 1. 讀取 Qpcr data 並轉換為 QPCRRecord 列表
  qpcr_record_list = readQPCRData(input_file_path, FAM_file_path, VIC_file_path, user_info.instrument, ct_threshold)

  # 紀錄 QPCRRecord 列表
  tmp_source = "mthfr.py line. 105"
  logger.analysis(f"[{user_info.instrument}] QPCR Raw data:", tmp_source)
  for r in qpcr_record_list:
    logger.analysis(f"{r}", tmp_source)

  # 初始化 controlWell 和 ntcWell
  controlWell = control_well
  ntcWell = ntc_well

  # 將 control_well 和 ntc_well 轉換為 WELL 物件
  if type(control_well) == str:
    controlWell = WELL(control_well)

  if type(ntc_well) == str:
    ntcWell = WELL(ntc_well)

  # 檢查 control_well 是否在 QPCRRecord 列表裡面
  if controlWell not in [r.well_position for r in qpcr_record_list]:
    tmp_source = "mthfr.py line. 123"
    logger.error(f"control_well {control_well} 不在 QPCRRecord 列表裡面", tmp_source)
    mthfr_output.qc_status = QCStatus.FAILED.value
    mthfr_output.errMsg = "control_well 不在 QPCRRecord 列表裡面"
    return mthfr_output.toJson()

  # 檢查 ntc_well 是否在 QPCRRecord 列表裡面
  if ntcWell not in [r.well_position for r in qpcr_record_list]:
    tmp_source = "mthfr.py line. 131"
    logger.error(f"ntc_well {ntc_well} 不在 QPCRRecord 列表裡面", tmp_source)
    mthfr_output.qc_status = QCStatus.FAILED.value
    mthfr_output.errMsg = "ntc_well 不在 QPCRRecord 列表裡面"
    return mthfr_output.toJson()

  # 2. 解析 MTHFRData 列表
  dataMatrix = parseMTHFRData(qpcr_record_list, controlWell, ntcWell)

  # 更新 mthfr_output
  mthfr_output.controlData = dataMatrix["control"]
  mthfr_output.ntcData = dataMatrix["ntc"]
  mthfr_output.sampleDataList = dataMatrix["sample"]

  # 對 MTHFRData 列表進行 QC
  qc_result = QC(dataMatrix, user_info.reagent)

  # 如果 QC 失敗, 則跳過 Sample Assessment
  if qc_result == QCStatus.FAILED:
    tmp_source = "mthfr.py line. 150"
    logger.warn(f"QC Failed, 跳過 Sample Assessment", tmp_source)
    mthfr_output.qc_status = QCStatus.FAILED.value
    mthfr_output.errMsg = "QC 失敗, 跳過 Sample Assessment"
    mthfr_output.resultList = []
    return mthfr_output.toJson()
  else:
    mthfr_output.qc_status = QCStatus.PASSED.value

  # 3. Sample Assessment
  sample_assessment_result = [SampleAssessment(data, user_info.reagent) for data in dataMatrix["sample"]]

  # 更新 mthfr_output
  mthfr_output.resultList = sample_assessment_result

  tmp_source = "mthfr.py line. 167"
  logger.analysis(f"* MTHFR Analysis Completed *", tmp_source)

  return mthfr_output.toJson()

# 處理 MTHFRData 列表
def parseMTHFRData(qpcr_record_list, controlWell, ntcWell):

  # 實體化 MTHFRData
  controlMTHFRData = MTHFRData(
    group="SC",
    sample_name=next((x.sample_name for x in qpcr_record_list if x.well_position == controlWell), None),
    well_position=next((x.well_position for x in qpcr_record_list if x.well_position == controlWell), None),
    c677_wt=next((x for x in qpcr_record_list if x.well_position == controlWell and x.reporter == "VIC"), None),
    c677_mut=next((x for x in qpcr_record_list if x.well_position == controlWell and x.reporter == "FAM"), None),
    c1298_wt=next((x for x in qpcr_record_list if x.well_position == controlWell and x.reporter == "TAMRA"), None),
    c1298_mut=next((x for x in qpcr_record_list if x.well_position == controlWell and x.reporter == "ROX"), None),
  )
  ntcMTHFRData = MTHFRData(
    group="NTC",
    sample_name=next((x.sample_name for x in qpcr_record_list if x.well_position == ntcWell), None),
    well_position=next((x.well_position for x in qpcr_record_list if x.well_position == ntcWell), None),
    c677_wt=next((x for x in qpcr_record_list if x.well_position == ntcWell and x.reporter == "VIC"), None),
    c677_mut=next((x for x in qpcr_record_list if x.well_position == ntcWell and x.reporter == "FAM"), None),
    c1298_wt=next((x for x in qpcr_record_list if x.well_position == ntcWell and x.reporter == "TAMRA"), None),
    c1298_mut=next((x for x in qpcr_record_list if x.well_position == ntcWell and x.reporter == "ROX"), None),
  )

  # 取得 qpcr_record_list 中 sample names
  sample_names = list(set([x.sample_name for x in qpcr_record_list if x.well_position != controlWell and x.well_position != ntcWell]))
  sampleMTHFRDataList = [MTHFRData(
    group="Sample",
    sample_name=name,
    well_position=next((x.well_position for x in qpcr_record_list if x.sample_name == name), None),
    c677_wt=next((x for x in qpcr_record_list if x.sample_name == name and x.reporter == "VIC"), None),
    c677_mut=next((x for x in qpcr_record_list if x.sample_name == name and x.reporter == "FAM"), None),
    c1298_wt=next((x for x in qpcr_record_list if x.sample_name == name and x.reporter == "TAMRA"), None),
    c1298_mut=next((x for x in qpcr_record_list if x.sample_name == name and x.reporter == "ROX"), None),
  ) for name in sample_names]

  # 輸出 MTHFRData 列表
  tmp_source = "mthfr.py line. 172"
  logger.analysis(f"MTHFRData:", tmp_source)
  logger.analysis(str(controlMTHFRData), tmp_source)
  logger.analysis(str(ntcMTHFRData), tmp_source)
  for data in sampleMTHFRDataList:
    logger.analysis(str(data), tmp_source)

  # DataMatrix
  dataMatrix = {
    "control": controlMTHFRData,
    "ntc": ntcMTHFRData,
    "sample": sampleMTHFRDataList
  }

  return dataMatrix

# 對 MTHFRData 列表進行 QC, 用 reagent 決定怎麼做 QC
def QC(dataMatrix, reagent):

  # 初始化 qc_status
  qc_status = QCStatus.NOT_ANALYZED

  if reagent == "accuinMTHFR1":

    # 取得 controlData 和 NTCData
    controlData = dataMatrix["control"]
    NTCData = dataMatrix["ntc"]

    # Control 的 c677_wt 和 c677_mut 都不能為 None
    if not controlData.c677_wt or not controlData.c677_mut:
      tmp_source = "mthfr.py line. 236"
      logger.error(f"controlData 的 c677_wt 或 c677_mut 為 None", tmp_source)
      qc_status = QCStatus.FAILED
      return qc_status

    # NTC 的 c677_wt 和 c677_mut 都不能為 None
    if not NTCData.c677_wt or not NTCData.c677_mut:
      tmp_source = "mthfr.py line. 243"
      logger.error(f"NTCData 的 c677_wt 或 c677_mut 為 None", tmp_source)
      qc_status = QCStatus.FAILED
      return qc_status

    # QC 條件1: Control 的 c677_wt 和 c677_mut 都通過 cutoff (CT < CT_Threshold)
    condition1 = controlData.c677_wt.pass_cutoff and controlData.c677_mut.pass_cutoff
    if not condition1:
      tmp_source = "mthfr.py line. 249"
      logger.warn(f"Control 的 c677_wt 或 c677_mut '沒有通過' cutoff", tmp_source)

    # QC 條件2: NTC 的 c677_wt 和 c677_mut 都"不"通過 cutoff (CT > CT_Threshold 或 沒有數值)
    condition2 = not NTCData.c677_wt.pass_cutoff and not NTCData.c677_mut.pass_cutoff
    if not condition2:
      tmp_source = "mthfr.py line. 254"
      logger.warn(f"NTCData 的 c677_wt 或 c677_mut '通過' cutoff", tmp_source)

    if condition1 and condition2:
      qc_status = QCStatus.PASSED
    else:
      tmp_source = "mthfr.py line. 263"
      logger.warn(f"QC Failed", tmp_source)
      qc_status = QCStatus.FAILED

  elif reagent == "accuinMTHFR2":

    # 取得 controlData 和 NTCData
    controlData = dataMatrix["control"]
    NTCData = dataMatrix["ntc"]

    # Control 的 c677_wt 和 c677_mut, c1298_wt 和 c1298_mut 都不能為 None
    if not controlData.c677_wt or not controlData.c677_mut or not controlData.c1298_wt or not controlData.c1298_mut:
      tmp_source = "mthfr.py line. 275"
      logger.error(f"controlData 的 c677_wt 或 c677_mut 或 c1298_wt 或 c1298_mut 為 None", tmp_source)
      qc_status = QCStatus.FAILED
      return qc_status

    # NTC 的 c677_wt 和 c677_mut 都不能為 None
    if not NTCData.c677_wt or not NTCData.c677_mut:
      tmp_source = "mthfr.py line. 282"
      logger.error(f"NTCData 的 c677_wt 或 c677_mut為 None", tmp_source)
      qc_status = QCStatus.FAILED
      return qc_status

    # QC 條件1: Control 的 c1298_wt 和 c1298_mut 都通過 cutoff (CT < CT_Threshold)
    condition1 = controlData.c1298_wt.pass_cutoff and controlData.c1298_mut.pass_cutoff
    if not condition1:
      tmp_source = "mthfr.py line. 288"
      logger.warn(f"Control 的 c1298_wt 或 c1298_mut '沒有通過' cutoff", tmp_source)

    # QC 條件2: Control 的 c677_wt 和 c677_mut 都通過 cutoff (CT < CT_Threshold)
    condition2 = controlData.c677_wt.pass_cutoff and controlData.c677_mut.pass_cutoff
    if not condition2:
      tmp_source = "mthfr.py line. 293"
      logger.warn(f"Control 的 c677_wt 或 c677_mut '沒有通過' cutoff", tmp_source)

    # QC 條件3: NTC 的 c677_wt 和 c677_mut 都"不"通過 cutoff (CT > CT_Threshold 或 沒有數值)
    condition3 = not NTCData.c677_wt.pass_cutoff and not NTCData.c677_mut.pass_cutoff
    if not condition3:
      tmp_source = "mthfr.py line. 298"
      logger.warn(f"NTCData 的 c677_wt 或 c677_mut '通過' cutoff", tmp_source)

    # QC 條件4: NTC 的 c1298_wt 和 c1298_mut 都"不"通過 cutoff (CT < CT_Threshold 或 沒有數值)
    condition4 = not NTCData.c1298_wt.pass_cutoff and not NTCData.c1298_mut.pass_cutoff
    if not condition4:
      tmp_source = "mthfr.py line. 303"
      logger.warn(f"NTCData 的 c1298_wt 或 c1298_mut '通過' cutoff", tmp_source)

    if condition1 and condition2 and condition3 and condition4:
      qc_status = QCStatus.PASSED
    else:
      qc_status = QCStatus.FAILED

  elif reagent == "accuinMTHFR3":

    # 取得 controlData 和 NTCData
    controlData = dataMatrix["control"]
    NTCData = dataMatrix["ntc"]

    # Control 的 c677_wt 和 c677_mut 都不能為 None
    if not controlData.c677_wt or not controlData.c677_mut:
      tmp_source = "mthfr.py line. 317"
      logger.error(f"controlData 的 c677_wt 或 c677_mut 為 None", tmp_source)
      qc_status = QCStatus.FAILED
      return qc_status

    # NTC 的 c677_wt 和 c677_mut 都不能為 None
    if not NTCData.c677_wt or not NTCData.c677_mut:
      tmp_source = "mthfr.py line. 324"
      logger.error(f"NTCData 的 c677_wt 或 c677_mut 為 None", tmp_source)
      qc_status = QCStatus.FAILED
      return qc_status

    # QC 條件1: Control 的 c677_wt 和 c677_mut 都通過 cutoff (CT > 0)
    condition1 = controlData.c677_wt.pass_cutoff and controlData.c677_mut.pass_cutoff
    if not condition1:
      tmp_source = "mthfr.py line. 331"
      logger.warn(f"Control 的 c677_wt 或 c677_mut '沒有通過' cutoff", tmp_source)

    # QC 條件2: NTC 的 c677_wt 和 c677_mut 都"不"通過 cutoff (CT > 0)
    condition2 = not NTCData.c677_wt.pass_cutoff and not NTCData.c677_mut.pass_cutoff
    if not condition2:
      tmp_source = "mthfr.py line. 337"
      logger.warn(f"NTCData 的 c677_wt 或 c677_mut '通過' cutoff", tmp_source)

    # QC 條件3: Control 的 c677_wt 和 c677_mut 的 CT 值差值必須小於 4
    condition3 = abs(controlData.c677_wt.ct_value - controlData.c677_mut.ct_value) < CT_Threshold.DELTA_CT_THRESHOLD_V3.value
    if not condition3:
      tmp_source = "mthfr.py line. 343"
      logger.warn(f"Control 的 c677_wt 和 c677_mut 的 CT 值差值必須小於 {CT_Threshold.DELTA_CT_THRESHOLD_V3.value}", tmp_source)

    # 如果所有條件都通過, 則 QC 狀態為 PASSED
    if condition1 and condition2 and condition3:
      qc_status = QCStatus.PASSED
    else:
      qc_status = QCStatus.FAILED

  else:
    raise ValueError(f"reagent {reagent} 不在支援的 reagent 列表裡面")

  return qc_status

# Sample Assessment
def SampleAssessment(SampleData, reagent):

  # 初始化 assessment
  assessment = AssessmentStatus.NOT_SET
  sample_qc_status = QCStatus.NOT_ANALYZED
  sample_type = []

  if reagent == "accuinMTHFR1":

    # 取得 SampleData 的 c677_wt 和 c677_mut
    c677_wt = SampleData.c677_wt
    c677_mut = SampleData.c677_mut

    # 若c677_wt 和 c677_mut都沒有 pass_cutoff, 則 assessment 為 INVALID
    if not c677_wt.pass_cutoff and not c677_mut.pass_cutoff:
      sample_qc_status = QCStatus.FAILED
      assessment = AssessmentStatus.INVALID
      return MTHFRResult(
        sample_name=SampleData.sample_name,
        reagent=reagent,
        assessment=assessment,
        sample_qc_status=sample_qc_status,
        sample_type=sample_type
      )

    # (c677_wt +) 和 (c677_mut +) 為 NORMAL_RISK
    if c677_wt.pass_cutoff and c677_mut.pass_cutoff:
      sample_qc_status = QCStatus.PASSED
      assessment = AssessmentStatus.NORMAL_RISK
      sample_type = ["C", "T"]

    # (c677_wt -) 和 (c677_mut +) 為 HIGH_RISK
    elif not c677_wt.pass_cutoff and c677_mut.pass_cutoff:
      sample_qc_status = QCStatus.PASSED
      assessment = AssessmentStatus.HIGH_RISK
      sample_type = ["T", "T"]

    # (c677_wt +) 和 (c677_mut -) 為 LOW_RISK
    elif c677_wt.pass_cutoff and not c677_mut.pass_cutoff:
      sample_qc_status = QCStatus.PASSED
      assessment = AssessmentStatus.LOW_RISK
      sample_type = ["C", "C"]

  elif reagent == "accuinMTHFR2":
    # 取得 SampleData 的 c677_wt 和 c677_mut, c1298_wt 和 c1298_mut
    c677_wt = SampleData.c677_wt
    c677_mut = SampleData.c677_mut
    c1298_wt = SampleData.c1298_wt
    c1298_mut = SampleData.c1298_mut

    # 若c677_wt 和 c677_mut 同時都沒有 pass_cutoff, 則 assessment 為 INVALID
    if not c677_wt.pass_cutoff and not c677_mut.pass_cutoff:
      sample_qc_status = QCStatus.FAILED
      assessment = AssessmentStatus.INVALID
      return MTHFRResult(
        sample_name=SampleData.sample_name,
        reagent=reagent,
        assessment=assessment,
        sample_qc_status=sample_qc_status,
        sample_type=sample_type
      )

    # 若c1298_wt 和 c1298_mut 同時都沒有 pass_cutoff, 則 assessment 為 INVALID
    if not c1298_wt.pass_cutoff and not c1298_mut.pass_cutoff:
      sample_qc_status = QCStatus.FAILED
      assessment = AssessmentStatus.INVALID
      return MTHFRResult(
        sample_name=SampleData.sample_name,
        reagent=reagent,
        assessment=assessment,
        sample_qc_status=sample_qc_status,
        sample_type=sample_type
      )

    # 判斷 c677 基因型
    c677_genotype = None

    # (c677_wt +) 和 (c677_mut +) 為 CT [Normal Risk]
    if c677_wt.pass_cutoff and c677_mut.pass_cutoff:
      c677_genotype = "CT"

    # (c677_wt -) 和 (c677_mut +) 為 TT [High Risk]
    elif not c677_wt.pass_cutoff and c677_mut.pass_cutoff:
      c677_genotype = "TT"

    # (c677_wt +) 和 (c677_mut -) 為 CC [Low Risk]
    elif c677_wt.pass_cutoff and not c677_mut.pass_cutoff:
      c677_genotype = "CC"

    # 判斷 c1298 基因型
    c1298_genotype = None

    # (c1298_wt +) 和 (c1298_mut +) 為 AC [Normal Risk]
    if c1298_wt.pass_cutoff and c1298_mut.pass_cutoff:
      c1298_genotype = "AC"

    # (c1298_wt -) 和 (c1298_mut +) 為 CC [High Risk]
    elif not c1298_wt.pass_cutoff and c1298_mut.pass_cutoff:
      c1298_genotype = "CC"

    # (c1298_wt +) 和 (c1298_mut -) 為 AA [Low Risk]
    elif c1298_wt.pass_cutoff and not c1298_mut.pass_cutoff:
      c1298_genotype = "AA"

    # 判斷風險

    # Low Risk: c677_genotype = CC, c1298_genotype = AA
    if c677_genotype == "CC" and c1298_genotype == "AA":
      assessment = AssessmentStatus.LOW_RISK

    # Normal Risk1: c677_genotype = CC, c1298_genotype = AC 或 CC
    elif c677_genotype == "CC" and (c1298_genotype == "AC" or c1298_genotype == "CC"):
      assessment = AssessmentStatus.NORMAL_RISK

    # Normal Risk2: c677_genotype = CT, c1298_genotype = AA
    elif c677_genotype == "CT" and c1298_genotype == "AA":
      assessment = AssessmentStatus.NORMAL_RISK

    # High Risk1: c677_genotype = CT, c1298_genotype = AC 或 CC
    elif c677_genotype == "CT" and (c1298_genotype == "AC" or c1298_genotype == "CC"):
      assessment = AssessmentStatus.HIGH_RISK

    # High Risk2: 只要 c677_genotype = TT 就一定是 HIGH_RISK
    elif c677_genotype == "TT":
      assessment = AssessmentStatus.HIGH_RISK

    # Pass QC and 設定 sample_type
    sample_qc_status = QCStatus.PASSED
    sample_type = [c677_genotype[0], c677_genotype[1], c1298_genotype[0], c1298_genotype[1]]

  elif reagent == "accuinMTHFR3":

    # 取得 SampleData 的 c677_wt 和 c677_mut
    c677_wt = SampleData.c677_wt
    c677_mut = SampleData.c677_mut

    # 若c677_wt 和 c677_mut都沒有 pass_cutoff, 則 assessment 為 INVALID
    if not c677_wt.pass_cutoff and not c677_mut.pass_cutoff:
      sample_qc_status = QCStatus.FAILED
      assessment = AssessmentStatus.INVALID
      return MTHFRResult(
        sample_name=SampleData.sample_name,
        reagent=reagent,
        assessment=assessment,
        sample_qc_status=sample_qc_status,
        sample_type=sample_type
      )

    # (c677_wt +) 和 (c677_mut +) 還要判斷 CT 相差是否大於 DELTA_CT_THRESHOLD_V3
    if c677_wt.pass_cutoff and c677_mut.pass_cutoff:
      sample_qc_status = QCStatus.PASSED

      # 判斷 CT 相差是否大於 DELTA_CT_THRESHOLD_V3
      if abs(c677_wt.ct_value - c677_mut.ct_value) > CT_Threshold.DELTA_CT_THRESHOLD_V3.value:

        # 如果 c677_wt < c677_mut, 則 assessment 為 LOW_RISK
        if c677_wt.ct_value < c677_mut.ct_value:
          assessment = AssessmentStatus.LOW_RISK
          sample_type = ["C", "C"]

        # 如果 c677_wt > c677_mut, 則 assessment 為 HIGH_RISK
        else:
          assessment = AssessmentStatus.HIGH_RISK
          sample_type = ["T", "T"]

      else:
        assessment = AssessmentStatus.NORMAL_RISK
        sample_type = ["C", "T"]

    # (c677_wt -) 和 (c677_mut +) 為 HIGH_RISK
    elif not c677_wt.pass_cutoff and c677_mut.pass_cutoff:
      sample_qc_status = QCStatus.PASSED
      assessment = AssessmentStatus.HIGH_RISK
      sample_type = ["T", "T"]

    # (c677_wt +) 和 (c677_mut -) 為 LOW_RISK
    elif c677_wt.pass_cutoff and not c677_mut.pass_cutoff:
      sample_qc_status = QCStatus.PASSED
      assessment = AssessmentStatus.LOW_RISK
      sample_type = ["C", "C"]

  else:
    raise ValueError(f"reagent {reagent} 不在支援的 reagent 列表裡面")

  return MTHFRResult(
    sample_name=SampleData.sample_name,
    reagent=reagent,
    assessment=assessment,
    sample_qc_status=sample_qc_status,
    sample_type=sample_type
  )

# 處理 CLI parameters
def parseParams():

  # 接收 CLI 參數
  parser = argparse.ArgumentParser()
  parser.add_argument("--inputfile", "-i", required=False, type=str, help="輸入檔案路徑 (Excel 或 CSV), 若儀器為 qs3 或 tower 必填")
  parser.add_argument("--FAMfile", "-f", required=False, type=str, help="FAM 檔案路徑 (Text), 若儀器為 z480 必填")
  parser.add_argument("--VICfile", "-v", required=False, type=str, help="VIC 檔案路徑 (Text), 若儀器為 z480 必填")
  parser.add_argument("--controlwell", "-c", required=True, type=str, help="控制 well 位置")
  parser.add_argument("--ntcwell", "-n", required=True, type=str, help="NTC well 位置")
  parser.add_argument("--reagent", required=True, type=str, choices=["accuinMTHFR1", "accuinMTHFR2", "accuinMTHFR3"], help="試劑類型, 目前有 ['accuinMTHFR1', 'accuinMTHFR2', 'accuinMTHFR3'] (必填)")
  parser.add_argument("--instrument", required=True, type=str, choices=["qs3", "tower", "z480"], help="儀器類型, 目前有 ['qs3', 'tower', 'z480'] (必填)")
  parser.add_argument("--organization", "-g", required=False, default="defaultOrg", type=str, help="組織所屬, MTHFR 不會用到可以不用設定")
  parser.add_argument("--output", "-o", required=False, type=str, help="輸出結果的 JSON 檔案路徑, 若不給定, 則輸出到 console")
  args = parser.parse_args()

  # 驗證 CLI 參數

  # 1. 驗證儀器類型, 若儀器為 qs3 或 tower 必填 inputfile 參數
  if args.instrument == "qs3" or args.instrument == "tower":

    # 驗證 inputfile 參數
    if not args.inputfile:
      raise ValueError("儀器為 qs3 或 tower 時, 請提供 inputfile 參數")

    # 檢查檔案是否存在
    if not os.path.exists(args.inputfile):
      raise ValueError(f"inputfile 檔案不存在: {args.inputfile}")

    # 初步檢查副檔名
    if not (args.inputfile.endswith(".xlsx") or args.inputfile.endswith(".xls")) and not args.inputfile.endswith(".csv"):
      raise ValueError("inputfile 副檔名錯誤, 請提供 .xlsx 或 .xls 或 .csv 檔案")

    # 如果是 qs3 或 tower, reagent 必須為 accuinMTHFR1 或 accuinMTHFR2
    if args.reagent != "accuinMTHFR1" and args.reagent != "accuinMTHFR2":
      raise ValueError("儀器為 qs3 或 tower 時, reagent 必須為 accuinMTHFR1 或 accuinMTHFR2")

  # 2. 驗證儀器類型, 若儀器為 z480 必填 FAMfile 和 VICfile 參數
  elif args.instrument == "z480":

    # 驗證 FAMfile 參數
    if not args.FAMfile or not args.VICfile:
      raise ValueError("儀器為 z480 時, 請提供 FAMfile 和 VICfile 參數")

    # 檢查 FAMfile 檔案是否存在
    if not os.path.exists(args.FAMfile):
      raise ValueError(f"FAMfile 檔案不存在: {args.FAMfile}")

    # 檢查 VICfile 檔案是否存在
    if not os.path.exists(args.VICfile):
      raise ValueError(f"VICfile 檔案不存在: {args.VICfile}")

    # 初步檢查副檔名
    if not args.FAMfile.endswith(".txt"):
      raise ValueError("FAMfile 副檔名錯誤, 請提供 .txt 檔案")
    if not args.VICfile.endswith(".txt"):
      raise ValueError("VICfile 副檔名錯誤, 請提供 .txt 檔案")

    # 如果是 z480, reagent 必須為 accuinMTHFR3
    if args.reagent != "accuinMTHFR3":
      raise ValueError("儀器為 z480 時, reagent 必須為 accuinMTHFR3")

  return args

# Run MTHFR CLI
if __name__ == "__main__":

  # 設定 Logger 模式
  logger = Logger(mode="offline")

  # 解析 CLI 參數
  args = parseParams()

  # 解析 CLI 參數
  input_file_path = args.inputfile
  FAM_file_path = args.FAMfile
  VIC_file_path = args.VICfile
  control_well = args.controlwell
  ntc_well = args.ntcwell
  user_info = UserInfo(
    instrument=args.instrument,
    reagent=args.reagent,
    organization=args.organization
  )

  # 輸出結果
  mthfr_output = MTHFR(
    input_file_path=input_file_path,
    FAM_file_path=FAM_file_path,
    VIC_file_path=VIC_file_path,
    control_well=control_well,
    ntc_well=ntc_well,
    user_info=user_info
  )

  # 如果有設定 output 參數, 則將結果寫入檔案
  if args.output:
    with open(args.output, "w") as f:
      f.write(mthfr_output)
  else:
    print(mthfr_output)
