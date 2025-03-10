# 引入套件
import os
import json
import argparse
import sys
from dataclasses import dataclass

# 導入自製模組
from utils.InputParser import UserInfo
from utils.FileParser import FileParser
from utils.DataObject import Range, CallPeak, Qsep100Peak, AnalysisOutput
from utils.ConstVaribles import QCStatus,AssessmentStatus,NucleusVersion

# 獲取當前腳本所在的目錄. 將上一層目錄添加到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)
sys.path.append(current_dir)

# 引入 saveLogs
from systemLogger import Logger
logger = Logger()

# 定義 SMAv4 peak obj
@dataclass
class SMAv4Peak(Qsep100Peak):
  peak_group: str   # internalControlPeak 或 targetPeak
  rfu_cutoff: float
  pass_cutoff: bool = False

  def __init__(self, peak_size, peak_rfu, smn, peak_group, rfu_cutoff):
    super().__init__(peak_size, peak_rfu)
    self.smn = smn
    self.peak_group = peak_group
    self.rfu_cutoff = rfu_cutoff
    self.pass_cutoff = False
    self.CutRFU()
  # 篩選 RFU
  def CutRFU(self):
    if self.peak_rfu >= self.rfu_cutoff:
      self.pass_cutoff = True

# 定義 SMAv4 Data Object
@dataclass
class SMAv4Data:
  smn: str
  group: str
  ic_peak: SMAv4Peak
  tg_peak: SMAv4Peak
  rfu_diff: float = -1
  data_qc: QCStatus = QCStatus.NOT_ANALYZED
  qc_message: str = ""

  def __init__(self, smn, group, ic_peak, tg_peak):
    self.smn = smn
    self.group = group
    self.ic_peak = ic_peak
    self.tg_peak = tg_peak
    self.set_data_qc()
    self.calculate_rfu_diff()

  # 計算 rfu_diff
  def calculate_rfu_diff(self):
    if self.ic_peak and self.tg_peak:
      self.rfu_diff = round(self.tg_peak.peak_rfu / self.ic_peak.peak_rfu, 3)

  # 設定 data_qc
  def set_data_qc(self):

    if not self.ic_peak:
      self.data_qc = QCStatus.FAILED
      self.qc_message += "沒有 Call 出 IC peak;"

    if not self.tg_peak:
      self.data_qc = QCStatus.FAILED
      self.qc_message += "沒有 Call 出 TG peak;"

    if self.ic_peak and self.tg_peak:
      if not self.ic_peak.pass_cutoff:
        self.data_qc = QCStatus.FAILED
        self.qc_message += "IC peak 沒有通過 RFU 篩選;"

      if not self.tg_peak.pass_cutoff:
        self.data_qc = QCStatus.FAILED
        self.qc_message += "TG peak 沒有通過 RFU 篩選;"

      if self.ic_peak.pass_cutoff and self.tg_peak.pass_cutoff:
        self.data_qc = QCStatus.PASSED
        self.qc_message = self.qc_message.rstrip(";")

# 定義 SMAv4 的 result Object
@dataclass
class SMAv4Result:
  sample_name: str
  smn1_copy_number: int
  smn2_copy_number: int
  typeStr: str = ''
  assessment_result: AssessmentStatus = AssessmentStatus.NOT_SET

  def __init__(self, sample_name, smn1_copy_number, smn2_copy_number):
    self.sample_name = sample_name
    self.smn1_copy_number = smn1_copy_number
    self.smn2_copy_number = smn2_copy_number
    self.typeStr = f"{self.smn1_copy_number}:{self.smn2_copy_number}"

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
    return f"SMAv4Result(sample_name={self.sample_name}, smn1_copy_number={self.smn1_copy_number}, smn2_copy_number={self.smn2_copy_number}, typeStr={self.typeStr}, assessment_result={self.assessment_result.value})"

  # 設定 assessment
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

# 定義 SMAv4 Output Object
@dataclass
class SMAv4Output(AnalysisOutput):
  STD_DATA: dict = None
  SAMPLE_DATA: dict = None
  COPY_NUMBER_RANGES: dict = None
  RESULT_LIST: dict = None
  PARAMETERS: dict = None

# 預設 SMA v4 parameters
DEFAULT_PEAK_CONDITION = {
  "RANGE": {
    "SMA1_IC_SIZE_RANGE": {"min": 217, "max": 265}, # SMA1_IC +/- 10%
    "SMA1_TG_SIZE_RANGE": {"min": 111, "max": 135}, # SMA1_TG +/- 10%
    "SMA2_SEARCH_RANGE": {"min": 275, "max": 374}   # SMA2_IC +/- 10%
  },
  "RFU_THRESHOLD": {
    "SMN1_IC": 1,
    "SMN1_TG": 1,
    "SMN2": 1
  },
  "PEAK_NUMBER_CHECK": {
    "SMA1": 1,
    "SMA2": 2
  },
  "PEAK_SIZE":{
    "SMA1_IC": 241,
    "SMA1_TG": 123,
    "SMA2_IC": 340,
    "SMA2_TG": 306
  },
  "PEAK_RANGE_DIV":{
    "SMA1_IC": {
      "Negative_range": 10,
      "Positive_range": 10
    },
    "SMA1_TG": {
      "Negative_range": 10,
      "Positive_range": 10
    },
    "SMA2": {
      "Negative_range": 10,
      "Positive_range": 10
    }
  }
}

# SMAv4 分析腳本
def SMAv4(
    smn1_std1, smn1_std2, smn1_std3,
    smn2_std1, smn2_std2, smn2_std3,
    smn1_samples, smn2_samples,
    peak_condition, user_info
  ):

  # Logger settings
  sender = user_info.organization
  logger.setSender(sender)

  # Logger : Start Message
  tmp_source = "smav4.py line. 185"
  logger.analysis(f" ----> Start SMAv4 Analysis <---- ", tmp_source)
  logger.analysis(f" User Info: {user_info}", tmp_source)

  # 取得 config
  config = {
    "reagent": user_info.reagent,
    "organization": user_info.organization,
    "instrument": user_info.instrument,
    "NucleusVersion": NucleusVersion.SMAv4.value
  }

  # 初始化 SMAv4Output
  smav4_output = SMAv4Output(config=config)

  # 決定使用哪個 peak condition
  use_condition = peak_condition if peak_condition != {} else DEFAULT_PEAK_CONDITION

  # 如果 use_condition 為前端格式，則轉換為後端格式
  if use_condition.keys() != DEFAULT_PEAK_CONDITION.keys():
    use_condition = convert_peak_condition(use_condition)

  # 更新 smav4_output
  smav4_output.PARAMETERS = use_condition

  # 取得 peak 篩選範圍
  SMN1_IC_PEAK_RANGE = Range(
    MIN=use_condition["RANGE"]["SMA1_IC_SIZE_RANGE"]["min"],
    MAX=use_condition["RANGE"]["SMA1_IC_SIZE_RANGE"]["max"]
  )
  SMN1_TARGET_PEAK_RANGE = Range(
    MIN=use_condition["RANGE"]["SMA1_TG_SIZE_RANGE"]["min"],
    MAX=use_condition["RANGE"]["SMA1_TG_SIZE_RANGE"]["max"]
  )
  SMN2_SEARCH_RANGE = Range(
    MIN=use_condition["RANGE"]["SMA2_SEARCH_RANGE"]["min"],
    MAX=use_condition["RANGE"]["SMA2_SEARCH_RANGE"]["max"]
  )

  # 讀取 Qsep100 檔案
  std_control_objs, sample_objs = read_qsep100_file(smn1_std1, smn1_std2, smn1_std3, smn2_std1, smn2_std2, smn2_std3, smn1_samples, smn2_samples)

  # 整理 STD data 和 Sample data
  std_data_objs = summary_std_data(std_control_objs, use_condition, SMN1_IC_PEAK_RANGE, SMN1_TARGET_PEAK_RANGE, SMN2_SEARCH_RANGE)
  sample_data_objs = summary_sample_data(sample_objs, use_condition, SMN1_IC_PEAK_RANGE, SMN1_TARGET_PEAK_RANGE, SMN2_SEARCH_RANGE)

  # 更新 smav4_output
  smav4_output.STD_DATA = std_data_objs
  smav4_output.SAMPLE_DATA = sample_data_objs

  # 進行 QC
  QC_result, QC_message = QC(std_data_objs)
  tmp_source = "smav4.py line. 248"
  if QC_result == QCStatus.FAILED:
    logger.warn(f"QC Result: {QC_result}, QC Message: {QC_message}", tmp_source)
  else:
    logger.analysis(f"QC Result: {QC_result}, QC Message: {QC_message}", tmp_source)

  # 更新 smav4_output
  smav4_output.qc_status = QC_result
  smav4_output.errMsg = QC_message

  # 若可能繼續分析則不跳過

  # 計算 Copy Number Ranges
  copy_number_ranges = determine_range(std_data_objs)
  tmp_source = "smav4.py line. 259"
  logger.analysis(f"Copy Number Ranges: {copy_number_ranges}", tmp_source)

  # 更新 smav4_output
  smav4_output.COPY_NUMBER_RANGES = copy_number_ranges

  # 統整 Sample 的 Result
  assessment_results = {}
  sampleList = [sample for sample in sample_data_objs["smn1"]]
  for sample in sampleList:
    smn1_copy_number = getCopyNumber(sample_data_objs["smn1"][sample].rfu_diff, "smn1", copy_number_ranges)
    smn2_copy_number = getCopyNumber(sample_data_objs["smn2"][sample].rfu_diff, "smn2", copy_number_ranges)
    result = SMAv4Result(
      sample_name=sample,
      smn1_copy_number=smn1_copy_number,
      smn2_copy_number=smn2_copy_number
    )
    tmp_source = "smav4.py line. 269"
    logger.analysis(f"SMAv4 Result: {result}", tmp_source)
    assessment_results[sample] = result

  # 更新 smav4_output
  smav4_output.RESULT_LIST = assessment_results

  tmp_source = "smav4.py line. 285"
  logger.analysis(f"* SMAv4 Analysis Completed *", tmp_source)

  # 回傳 smav4_output
  return smav4_output.toJson()

# 讀取 Qsep100 檔案
def read_qsep100_file(smn1_std1, smn1_std2, smn1_std3, smn2_std1, smn2_std2, smn2_std3, smn1_samples, smn2_samples):

  # 實體化 FileParser
  fileParser = FileParser()

  # 讀取 Qsep100 檔案
  std_control_objs = {
    "smn1":{
      "std1": fileParser.parseQsep100File(smn1_std1),
      "std2": fileParser.parseQsep100File(smn1_std2),
      "std3": fileParser.parseQsep100File(smn1_std3)
    },
    "smn2":{
      "std1": fileParser.parseQsep100File(smn2_std1),
      "std2": fileParser.parseQsep100File(smn2_std2),
      "std3": fileParser.parseQsep100File(smn2_std3)
    }
  }

  sample_objs = {
    "smn1": {},
    "smn2": {}
  }
  for sample in smn1_samples:
    sample_objs['smn1'][parse_file_name(sample)] = fileParser.parseQsep100File(sample)

  for sample in smn2_samples:
    sample_objs['smn2'][parse_file_name(sample)] = fileParser.parseQsep100File(sample)

  return std_control_objs, sample_objs

# 整理 SMN1 data
def summary_smn1_data(dataframe, group, ic_peak_range, tg_peak_range, ic_rfu_cutoff, tg_rfu_cutoff, top_n):

  # Call peaks
  ic_peak_list = CallPeak(dataframe, ic_peak_range, top_n=top_n)
  tg_peak_list = CallPeak(dataframe, tg_peak_range, top_n=top_n)

  # 如果 ic_peak_list 為空, 則回傳 None
  if len(ic_peak_list) == 0:
    tmp_source = "smav4.py line. 330"
    logger.warn(f"{group} 找不到 IC peak", tmp_source)
    ic_peak_obj = None
  else:
    # 實體化 SMAv4Peak
    ic_peak_obj = SMAv4Peak(
      peak_size=ic_peak_list[0].peak_size,
      peak_rfu=ic_peak_list[0].peak_rfu,
      smn="smn1",
      peak_group="internalControl",
      rfu_cutoff=ic_rfu_cutoff
    )

  # 如果 tg_peak_list 為空, 則回傳 None
  if len(tg_peak_list) == 0:
    tmp_source = "smav4.py line. 345"
    logger.warn(f"{group} 找不到 TG peak", tmp_source)
    target_peak_obj = None
  else:
    # 實體化 SMAv4Peak
    target_peak_obj = SMAv4Peak(
      peak_size=tg_peak_list[0].peak_size,
      peak_rfu=tg_peak_list[0].peak_rfu,
      smn="smn1",
      peak_group="target",
      rfu_cutoff=tg_rfu_cutoff
    )
  data = SMAv4Data(smn="smn1", group=group, ic_peak=ic_peak_obj, tg_peak=target_peak_obj)
  return data

# 整理 SMN2 data
def summary_smn2_data(dataframe, group, peak_size, selected_peak_range, rfu_cutoff, top_n):

  # Call peaks
  called_peaks = CallPeak(dataframe, selected_peak_range, top_n=top_n)

  if len(called_peaks) < top_n:
    tmp_source = "smav4.py line. 367"
    logger.warn(f"{group} 範圍內找不到 {top_n} 個 peak", tmp_source)
    data = SMAv4Data(smn="smn2", group=group, ic_peak=None, tg_peak=None) # 回傳 None
    return data

  # 使用 peak_size 排序 called_peaks
  called_peaks = sorted(called_peaks, key=lambda x: x.peak_size, reverse=True)

  # 檢查 peak_size 中 SMA2_IC 和 SMA2_TG 大小

  # SMA2_IC > SMA2_TG, 則 called_peaks[0] 為 SMA2_IC, called_peaks[1] 為 SMA2_TG
  if peak_size["SMA2_IC"] > peak_size["SMA2_TG"]:
    ic_peak = called_peaks[0]
    tg_peak = called_peaks[1]
  # SMA2_IC < SMA2_TG, 則 called_peaks[0] 為 SMA2_TG, called_peaks[1] 為 SMA2_IC
  else:
    tg_peak = called_peaks[0]
    ic_peak = called_peaks[1]

  # 實體化 SMAv4Peak
  ic_peak_obj = SMAv4Peak(
    peak_size=ic_peak.peak_size,
    peak_rfu=ic_peak.peak_rfu,
    smn="smn2",
    peak_group="internalControl",
    rfu_cutoff=rfu_cutoff
  )
  tg_peak_obj = SMAv4Peak(
    peak_size=tg_peak.peak_size,
    peak_rfu=tg_peak.peak_rfu,
    smn="smn2",
    peak_group="target",
    rfu_cutoff=rfu_cutoff
  )
  data = SMAv4Data(smn="smn2", group=group, ic_peak=ic_peak_obj, tg_peak=tg_peak_obj)
  return data

# 整理 STD data
def summary_std_data(std_control_objs, use_condition, smn1_ic_peak_range, smn1_target_peak_range, smn2_search_range):

  # 初始化 std_data_objs
  std_data_objs = {
    "smn1": {},
    "smn2": {}
  }

  smn1_ic_rfu_cutoff = use_condition["RFU_THRESHOLD"]["SMN1_IC"]
  smn1_tg_rfu_cutoff = use_condition["RFU_THRESHOLD"]["SMN1_TG"]
  smn1_selected_peak_top_n = use_condition["PEAK_NUMBER_CHECK"]["SMA1"]
  # 整理 SMN1 data
  for std in std_control_objs["smn1"]:
    std_data_objs["smn1"][std] = summary_smn1_data(std_control_objs["smn1"][std].data, std, smn1_ic_peak_range, smn1_target_peak_range, smn1_ic_rfu_cutoff, smn1_tg_rfu_cutoff, smn1_selected_peak_top_n)

  # 整理 SMN2 data
  peak_size = use_condition["PEAK_SIZE"]
  smn2_rfu_cutoff = use_condition["RFU_THRESHOLD"]["SMN2"]
  smn2_selected_peak_top_n = use_condition["PEAK_NUMBER_CHECK"]["SMA2"]
  for std in std_control_objs["smn2"]:
    std_data_objs["smn2"][std] = summary_smn2_data(std_control_objs["smn2"][std].data, std, peak_size, smn2_search_range, smn2_rfu_cutoff, smn2_selected_peak_top_n)

  # 紀錄 std_data_objs
  for smn in std_data_objs:
    for group in std_data_objs[smn]:
      tmp_source = "smav4.py line. 429"
      logger.analysis(f"{smn} {group} {std_data_objs[smn][group]}", tmp_source)

  return std_data_objs

# 整理 Sample data
def summary_sample_data(sample_objs, use_condition, smn1_ic_peak_range, smn1_target_peak_range, smn2_search_range):

  # 初始化 sample_data_objs
  sample_data_objs = {
    "smn1": {},
    "smn2": {}
  }

  # 整理 SMN1 data
  smn1_ic_rfu_cutoff = use_condition["RFU_THRESHOLD"]["SMN1_IC"]
  smn1_tg_rfu_cutoff = use_condition["RFU_THRESHOLD"]["SMN1_TG"]
  smn1_selected_peak_top_n = use_condition["PEAK_NUMBER_CHECK"]["SMA1"]
  for sample in sample_objs["smn1"]:
    sample_data_objs["smn1"][sample] = summary_smn1_data(sample_objs["smn1"][sample].data, "sample", smn1_ic_peak_range, smn1_target_peak_range, smn1_ic_rfu_cutoff, smn1_tg_rfu_cutoff, smn1_selected_peak_top_n)

  # 整理 SMN2 data
  peak_size = use_condition["PEAK_SIZE"]
  smn2_rfu_cutoff = use_condition["RFU_THRESHOLD"]["SMN2"]
  smn2_selected_peak_top_n = use_condition["PEAK_NUMBER_CHECK"]["SMA2"]
  for sample in sample_objs["smn2"]:
    sample_data_objs["smn2"][sample] = summary_smn2_data(sample_objs["smn2"][sample].data, "sample", peak_size, smn2_search_range, smn2_rfu_cutoff, smn2_selected_peak_top_n)

  # 紀錄 sample_data_objs
  for smn in sample_data_objs:
    for group in sample_data_objs[smn]:
      tmp_source = "smav4.py line. 460"
      logger.analysis(f"{smn} {group} {sample_data_objs[smn][group]}", tmp_source)

  return sample_data_objs

# Std QC
def QC(std_data_objs):

  # 初始化 QC_result
  QC_result = QCStatus.NOT_ANALYZED
  QC_message = ""

  # QC1: std_data_objs 中, 每個 smn 的每個 group 的 data_qc 都必須是 QCStatus.PASSED
  for smn in std_data_objs:
    for group in std_data_objs[smn]:
      if std_data_objs[smn][group].data_qc != QCStatus.PASSED:
        QC_result = QCStatus.FAILED
        QC_message += f"{smn} {group} {std_data_objs[smn][group].qc_message};"

  # QC2: smn1 和 smn2 的 rfu_diff 必須逐漸遞增
  if not std_data_objs['smn1']['std1'].rfu_diff < std_data_objs['smn1']['std2'].rfu_diff < std_data_objs['smn1']['std3'].rfu_diff:
    QC_result = QCStatus.FAILED
    QC_message += "smn1 的 rfu_diff 沒有逐漸遞增;"

  if not std_data_objs['smn2']['std1'].rfu_diff < std_data_objs['smn2']['std2'].rfu_diff < std_data_objs['smn2']['std3'].rfu_diff:
    QC_result = QCStatus.FAILED
    QC_message += "smn2 的 rfu_diff 沒有逐漸遞增;"

  # 如果 QC_result 沒有改變, 則設為 QCStatus.PASSED
  if QC_result == QCStatus.NOT_ANALYZED:
    QC_result = QCStatus.PASSED

  return QC_result, QC_message

# 計算 Copy Number Ranges
def determine_range(std_data_objs):
  # SMA1 (2:2 和 1:1 的差值) & (3:3 和 2:2 的差值)
  sma1_diff_2_1 = std_data_objs['smn1']['std2'].rfu_diff - std_data_objs['smn1']['std1'].rfu_diff
  sma1_diff_3_2 = std_data_objs['smn1']['std3'].rfu_diff - std_data_objs['smn1']['std2'].rfu_diff

  # SMA2 (2:1 和 1:1 的差值) & (3:3 和 2:2 的差值)
  sma2_diff_2_1 = std_data_objs['smn2']['std2'].rfu_diff - std_data_objs['smn2']['std1'].rfu_diff
  sma2_diff_3_2 = std_data_objs['smn2']['std3'].rfu_diff - std_data_objs['smn2']['std2'].rfu_diff

  # 計算判斷間距
  SMA1_D1 = std_data_objs['smn1']['std1'].rfu_diff
  SMA1_RANGES = {
      '1': Range(MIN=SMA1_D1, MAX=SMA1_D1 + sma1_diff_2_1 / 2),
      '2': Range(MIN=SMA1_D1 + sma1_diff_2_1 / 2, MAX=SMA1_D1 + sma1_diff_2_1 / 2 + sma1_diff_3_2 / 2),
      '3': Range(MIN=SMA1_D1 + sma1_diff_2_1 / 2 + sma1_diff_3_2 / 2, MAX=float('inf')),
  }
  SMA2_D1 = std_data_objs['smn2']['std1'].rfu_diff
  SMA2_RANGES = {
      '1': Range(MIN=SMA2_D1, MAX=SMA2_D1 + sma2_diff_2_1 / 2),
      '2': Range(MIN=SMA2_D1 + sma2_diff_2_1 / 2, MAX=SMA2_D1 + sma2_diff_2_1 / 2 + sma2_diff_3_2 / 2),
      '3': Range(MIN=SMA2_D1 + sma2_diff_2_1 / 2 + sma2_diff_3_2 / 2, MAX=float('inf')),
  }
  SMA_RANGES = {
      'smn1': SMA1_RANGES,
      'smn2': SMA2_RANGES,
  }

  return SMA_RANGES

# 取得 Copy Number
def getCopyNumber(rfu_diff, smn, copy_number_ranges):
  if rfu_diff >= copy_number_ranges[smn]['3'].MIN :
    return 3
  elif rfu_diff >= copy_number_ranges[smn]['2'].MIN :
    return 2
  elif rfu_diff >= copy_number_ranges[smn]['1'].MIN :
    return 1
  else:
    return 0

# 轉換前端格式為後端格式
def convert_peak_condition(peak_condition):

  converted_peak_condition = {
    "RANGE": {
      "SMA1_IC_SIZE_RANGE": {
        "min": int(peak_condition['smn1']['internalControlPeak']['peak_select_range']['min']),
        "max": int(peak_condition['smn1']['internalControlPeak']['peak_select_range']['max'])
      },
      "SMA1_TG_SIZE_RANGE": {
        "min": int(peak_condition['smn1']['targetPeak']['peak_select_range']['min']),
        "max": int(peak_condition['smn1']['targetPeak']['peak_select_range']['max'])
      },
      "SMA2_SEARCH_RANGE": {
        "min": int(peak_condition['smn2']['peak_condition']['peak_select_range']['min']),
        "max": int(peak_condition['smn2']['peak_condition']['peak_select_range']['max'])
      }
    },
    "RFU_THRESHOLD": {
      "SMN1_IC": float(peak_condition['smn1']['internalControlPeak']['RFU_threshold']),
      "SMN1_TG": float(peak_condition['smn1']['targetPeak']['RFU_threshold']),
      "SMN2": float(peak_condition['smn2']['peak_condition']['RFU_threshold'])
    },
    "PEAK_NUMBER_CHECK": {
      "SMA1": int(peak_condition['smn1']['internalControlPeak']['Min_peak_count']),
      "SMA2": int(peak_condition['smn2']['peak_condition']['Min_peak_count'])
    },
    "PEAK_SIZE":{
      "SMA1_IC": int(peak_condition['smn1']['internalControlPeak']['Peak_size']),
      "SMA1_TG": int(peak_condition['smn1']['targetPeak']['Peak_size']),
      "SMA2_IC": int(peak_condition['smn2']['peak_condition']['internal_ctrl_size']),
      "SMA2_TG": int(peak_condition['smn2']['peak_condition']['target_size'])
    },
    "PEAK_RANGE_DIV":{
      "SMA1_IC": {
        "Negative_range": int(peak_condition['smn1']['internalControlPeak']['Negative_range']),
        "Positive_range": int(peak_condition['smn1']['internalControlPeak']['Positive_range'])
      },
      "SMA1_TG": {
        "Negative_range": int(peak_condition['smn1']['targetPeak']['Negative_range']),
        "Positive_range": int(peak_condition['smn1']['targetPeak']['Positive_range'])
      },
      "SMA2": {
        "Negative_range": int(peak_condition['smn2']['peak_condition']['Negative_range']),
        "Positive_range": int(peak_condition['smn2']['peak_condition']['Positive_range'])
      }
    }
  }

  return converted_peak_condition

# 處理 Sample Name
def parse_file_name(full_file_path):

  # 取得檔案名稱
  file_name = os.path.basename(full_file_path)
  file_name_without_extension = file_name.split(".")[0]

  # 取得 sample 名稱 = 檔案名稱的第 2 個底線後的文字
  sample_name = file_name_without_extension.split("_")[2]

  return sample_name

# 處理 CLI parameters
def parseParams():

  # 接收 CLI 參數
  parser = argparse.ArgumentParser()
  parser.add_argument("--configfile", "-c", required=True, type=str, help="由於 SMAv4 需要設定複雜, 使用設定檔, 指定路徑 (JSON格式)")
  parser.add_argument("--output", "-o", required=False, type=str, help="輸出結果的 JSON 檔案路徑, 若不給定, 則輸出到 console")
  args = parser.parse_args()

  # 檢查 configfile 是否存在
  if not os.path.exists(args.configfile):
    raise FileNotFoundError(f"設定檔不存在: {args.configfile}")

  return args

# 處理 Config 檔案
def parseConfig(configfile):

  # 讀取 Config 檔案
  with open(configfile, "r") as f:
    config = json.load(f)

  smn1_std1 = config["input_files"]["smn1_std1"]
  smn1_std2 = config["input_files"]["smn1_std2"]
  smn1_std3 = config["input_files"]["smn1_std3"]
  smn2_std1 = config["input_files"]["smn2_std1"]
  smn2_std2 = config["input_files"]["smn2_std2"]
  smn2_std3 = config["input_files"]["smn2_std3"]
  smn1_samples = config["input_files"]["smn1_samples"]
  smn2_samples = config["input_files"]["smn2_samples"]
  peak_condition = config["peak_condition"]

  # 檢查檔案是否存在
  for file in [smn1_std1, smn1_std2, smn1_std3, smn2_std1, smn2_std2, smn2_std3, *smn1_samples, *smn2_samples]:
    if not os.path.exists(file):
      raise FileNotFoundError(f"檔案不存在: {file}")

  # 檢查 smn1 和 smn2 的樣本數是否相同
  if len(smn1_samples) != len(smn2_samples):
    raise ValueError("smn1 和 smn2 的樣本數不相同")

  # 組成 inputFiles
  inputFiles = {
    "smn1_std1": smn1_std1,
    "smn1_std2": smn1_std2,
    "smn1_std3": smn1_std3,
    "smn2_std1": smn2_std1,
    "smn2_std2": smn2_std2,
    "smn2_std3": smn2_std3,
    "smn1_samples": smn1_samples,
    "smn2_samples": smn2_samples,
  }

  return inputFiles, peak_condition

# SMAv4 CLI
if __name__ == "__main__":

  # 設定 Logger 模式
  logger = Logger(mode="offline")

  # 處理 CLI parameters
  args = parseParams()

  # 處理 Config 檔案
  inputFiles, peak_condition = parseConfig(args.configfile)

  # 設定 UserInfo
  userInfo = UserInfo(
    reagent = "SMAv4",
    instrument = "Qsep100",
    organization = "defaultOrg"
  )

  # 執行 SMAv4
  sma_output = SMAv4(
    smn1_std1=inputFiles["smn1_std1"],
    smn1_std2=inputFiles["smn1_std2"],
    smn1_std3=inputFiles["smn1_std3"],
    smn2_std1=inputFiles["smn2_std1"],
    smn2_std2=inputFiles["smn2_std2"],
    smn2_std3=inputFiles["smn2_std3"],
    smn1_samples=inputFiles["smn1_samples"],
    smn2_samples=inputFiles["smn2_samples"],
    peak_condition=peak_condition,
    user_info=userInfo
  )

  # 如果有設定 output 參數, 則將結果寫入檔案
  if args.output:
    with open(args.output, "w") as f:
      f.write(sma_output)
  else:
    print(sma_output)
