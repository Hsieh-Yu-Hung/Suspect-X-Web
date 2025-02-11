# 導入必要模組
import argparse
import os
import sys
from dataclasses import dataclass
from enum import Enum

# 導入自製模組
from utils.InputParser import UserInfo
from utils.FileParser import FileParser
from utils.DataObject import Range, Qsep100Peak, CallPeak, AnalysisOutput
from utils.ConstVaribles import AssessmentStatus, QCStatus, NucleusVersion

# 獲取當前腳本所在的目錄. 將上一層目錄添加到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)
sys.path.append(current_dir)

# 引入 saveLogs
from config_admin import bucket
from saveLogs import Logger
logger = Logger(bucket)

# 定義 Standard Peak 篩選範圍
STD_PEAK_DIVIATION = Range(MIN=0.9, MAX=1.1)
STD_PEAK_INIT_RANGE = Range(MIN=121, MAX=199)
STD_PEAK_RANGE = STD_PEAK_INIT_RANGE * STD_PEAK_DIVIATION
STD_SMALL_PEAK_RANGE = STD_PEAK_DIVIATION * STD_PEAK_INIT_RANGE.MIN
STD_LARGE_PEAK_RANGE = STD_PEAK_DIVIATION * STD_PEAK_INIT_RANGE.MAX

# 定義 Sample Peak 篩選範圍
HTD_RFU_CUTOFF = 1
SAMPLE_PEAK_DIVIATION = Range(MIN=0.9, MAX=1.1)
INTERNAL_CTRL_PEAK_SIZE = 453
INTERNAL_CTRL_PEAK_RANGE = SAMPLE_PEAK_DIVIATION * INTERNAL_CTRL_PEAK_SIZE
TARGET_PEAK_RANGE = Range(MIN=70, MAX=350)

# 定義 HTD 參數
HTD_RUF_RATIO_CUTOFF = 0.4
HTD_BP_THRESHOLD = 60
PCR_FLANKING_SIZE = 67

# 定義 Repeat 分類
class REPEAT_CUTOFF(Enum):
  NORMAL = 26
  INTERMEDIATE = 35
  PENETRANCE = 39
  FULL_PENETRANCE = 40

# 定義 Peak group
class PEAK_GROUP(Enum):
  STANDARD = "Standard"
  INTERNAL_CTRL = "Internal_Ctrl"
  TARGET = "Target"

# 定義 HTD Peak Object
@dataclass
class STD_HTDPeak(Qsep100Peak):
  peak_group: PEAK_GROUP
  inRange: bool = False

@dataclass
class SAMPLE_HTDPeak(Qsep100Peak):
  peak_group: PEAK_GROUP
  pass_rfu_cutoff: bool
  pass_rfu_ratio_cutoff: bool
  peak_rfu_ratio: float
  repeat_num: int = -1
  assessment: AssessmentStatus = AssessmentStatus.NOT_SET

  # 初始化 SAMPLE_HTDPeak
  def __init__(self, peak_group, peak_size, peak_rfu, peak_rfu_ratio = -1, pass_rfu_cutoff=False, pass_rfu_ratio_cutoff=False):
    super().__init__(peak_size, peak_rfu)
    self.peak_group = peak_group
    self.pass_rfu_cutoff = pass_rfu_cutoff
    self.pass_rfu_ratio_cutoff = pass_rfu_ratio_cutoff
    self.peak_rfu_ratio = peak_rfu_ratio

    if peak_group == PEAK_GROUP.TARGET.value:
      self.CalculateRepeatNum()
      self.assessment_by_repeat_num()

  # 計算 Repeat 數
  def CalculateRepeatNum(self):
    self.repeat_num = int(round((self.peak_size - PCR_FLANKING_SIZE) / 3, 0))

  # 由 Repeat 數判斷 Assessment
  def assessment_by_repeat_num(self):
    if 0 < self.repeat_num <= REPEAT_CUTOFF.NORMAL.value:
      self.assessment = AssessmentStatus.NORMAL
    elif REPEAT_CUTOFF.NORMAL.value < self.repeat_num <= REPEAT_CUTOFF.INTERMEDIATE.value:
      self.assessment = AssessmentStatus.INTERMEDIATE
    elif REPEAT_CUTOFF.INTERMEDIATE.value < self.repeat_num <= REPEAT_CUTOFF.PENETRANCE.value:
      self.assessment = AssessmentStatus.PENETRANCE
    elif self.repeat_num >= REPEAT_CUTOFF.FULL_PENETRANCE.value:
      self.assessment = AssessmentStatus.FULL_PENETRANCE
    else:
      self.assessment = AssessmentStatus.INVALID

# 定義 HTD data object
@dataclass
class HTD_Data:
  sample_id: str
  internal_ctrl_peaks: SAMPLE_HTDPeak
  selected_target_peaks: list[SAMPLE_HTDPeak]
  assessmentList: list[AssessmentStatus] = None
  assessment: AssessmentStatus = AssessmentStatus.NOT_SET
  sample_qc_status: QCStatus = QCStatus.NOT_ANALYZED
  error_message: str = ""

  def DetermineAssessment(self):

    # 如果有 FULL_PENETRANCE, 則直接回傳 FULL_PENETRANCE
    if AssessmentStatus.FULL_PENETRANCE in self.assessmentList:
      self.assessment = AssessmentStatus.FULL_PENETRANCE

    # 如果有 PENETRANCE, 則回傳 PENETRANCE
    elif AssessmentStatus.PENETRANCE in self.assessmentList:
      self.assessment = AssessmentStatus.PENETRANCE

    # 如果有 INTERMEDIATE, 則回傳 INTERMEDIATE
    elif AssessmentStatus.INTERMEDIATE in self.assessmentList:
      self.assessment = AssessmentStatus.INTERMEDIATE

    # 如果沒有以上, 則回傳 NORMAL
    elif AssessmentStatus.NORMAL in self.assessmentList:
      self.assessment = AssessmentStatus.NORMAL

    # 如果沒有以上, 則回傳 INVALID
    else:
      self.assessment = AssessmentStatus.INVALID

# 定義 HTD 結果
@dataclass
class HTD_Output(AnalysisOutput):
  standard_control_data: list[STD_HTDPeak] = None
  result: dict = None

# 執行 HTD 主程式
def HTD(control_file_path, samples_file_list, user_info):

  logger.info(f"\n")
  logger.info(f" ----> Start HTD Analysis <---- ")
  logger.info(f" User Info: {user_info}")

  # 取得 config
  config = {
    "reagent": user_info.reagent,
    "organization": user_info.organization,
    "instrument": user_info.instrument,
    "NucleusVersion": NucleusVersion.HTD.value
  }

  # 初始化 HTD_Output
  htd_output = HTD_Output(config=config)

  # 實體化 FileParser
  fileParser = FileParser()

  # 1. 解析 Qsep100 檔案
  control_obj = fileParser.parseQsep100File(control_file_path)
  samples_obj_list = [fileParser.parseQsep100File(sample) for sample in samples_file_list]

  # 2. 取得 Standard Peak
  standard_peaks = getStandardPeak(control_obj.data)

  # 檢查 standard_peaks 是否為空
  if len(standard_peaks) == 0:
    logger.warn(f"Error: 終止 HTD 分析, 因為 Standard Peak 問題!")
    htd_output.qc_status = QCStatus.FAILED.value
    htd_output.errMsg = "Standard Peak 不足 2 個"
    return htd_output

  # log 印出 standard_peaks
  for peak in standard_peaks:
    logger.info(f"Standard Peak: {peak}")

  # 檢查 standard_peaks 是否都 inRange, 若有一個不在範圍內, 則回傳 "Inconclusive"
  std_in_range = all(peak.inRange for peak in standard_peaks)
  if not std_in_range:
    logger.warn(f"Error: 終止 HTD 分析, 因為 Standard Peak 不在指定範圍內!")
    htd_output.qc_status = QCStatus.FAILED.value
    htd_output.errMsg = "Standard Peak 不在指定範圍內"
    return htd_output

  # 更新 htd_output
  htd_output.qc_status = QCStatus.PASSED.value
  htd_output.standard_control_data = standard_peaks

  # 3. 取得和分析 Sample Peaks: internal_ctrl_peaks, target_peaks
  sampleData = analyzeSamplePeaks(samples_obj_list)

  # 4. 例外判斷：檢查 HTD peak 數量
  for sample_id, data in sampleData.items():
    # 若 internal_ctrl_peaks 不足 1 個, 則判定 "Inconclusive"
    if data.internal_ctrl_peaks is None:
      logger.warn(f"Warning: Sample {sample_id} 缺少 internal_ctrl_peaks, 判定為 'Inconclusive'!")
      data.assessment = AssessmentStatus.INCONCLUSIVE
      data.error_message = f"Sample {sample_id} 缺少 internal_ctrl_peaks"
      data.sample_qc_status = QCStatus.FAILED.value
      continue

    # 若 target_peaks 不足 1 個, 則判定 "Invalid"
    if not data.selected_target_peaks:
      logger.warn(f"Warning: Sample {sample_id} 缺少 target_peaks, 判定為 'Invalid'!")
      data.assessment = AssessmentStatus.INVALID
      data.error_message = f"Sample {sample_id} 缺少 target_peaks"
      data.sample_qc_status = QCStatus.FAILED.value
      continue

    # 若 target_peaks 大於 2 則判定 "Invalid"
    if len(data.selected_target_peaks) > 2:
      logger.warn(f"Warning: Sample {sample_id} 的 HTD peak 數量大於 2, 判定為 'Invalid'!")
      data.assessment = AssessmentStatus.INVALID
      data.error_message = f"Sample {sample_id} 的 HTD peak 數量大於 2"
      data.sample_qc_status = QCStatus.FAILED.value
      continue

    # 更新 sample_qc_status
    data.sample_qc_status = QCStatus.PASSED.value

    # 更新 assessment
    data.assessmentList = [peak.assessment for peak in data.selected_target_peaks]

    # 決定 assessment
    data.DetermineAssessment()

  # log 印出 sampleData
  for sample_id, data in sampleData.items():
    logger.info(f"Sample Name: {sample_id}")
    logger.info(f"Assessment List: {[assessment.value for assessment in data.assessmentList]}")
    logger.info(f"ErrMessage: {data.error_message}")
    logger.info(f"Internal Ctrl Peaks: {data.internal_ctrl_peaks}")
    logger.info(f"Selected Target Peaks: \n\t{'\n\t'.join([str(peak) for peak in data.selected_target_peaks])}")

  # 更新 htd_output
  htd_output.errMsg += ";" + ";".join([data.error_message for data in sampleData.values() if data.error_message != ""])
  htd_output.result = sampleData

  logger.info(f"* HTD Analysis Completed *")

  return htd_output.toJson()

# 取得 Standard Peak
def getStandardPeak(control_df):

  # CallPeak 取得 top2_sc_peaks
  top2_sc_peaks = CallPeak(control_df, STD_PEAK_RANGE, 2)

  # 如果 SC 不足 2 個, 則回傳空列表
  if len(top2_sc_peaks) < 2:
    logger.warn(f"Warning: Standard Peak 不足 2 個!")
    return []

  # 轉換成 STD_HTDPeak 列表
  top2_sc_peaks = [
    STD_HTDPeak(
      peak_group=PEAK_GROUP.STANDARD.value,
      peak_size=peak.peak_size,
      peak_rfu=peak.peak_rfu
    )
    for peak in top2_sc_peaks
  ]

  # 檢查 top2_sc_peaks 是否在 STD_PEAK_RANGE 範圍內, 標記 inRange
  for peak in top2_sc_peaks:
    peak.inRange = STD_SMALL_PEAK_RANGE.inRange(peak.peak_size) or STD_LARGE_PEAK_RANGE.inRange(peak.peak_size)

  # 取得 Standard Peak
  return top2_sc_peaks

# 取得 Sample Peak
def getSamplePeak(sample_df, peak_type):

  if peak_type == PEAK_GROUP.INTERNAL_CTRL:

    # CallPeak 取得 internal_ctrl_peaks, 最高 RFU 的 peak
    Called_peak = CallPeak(sample_df, INTERNAL_CTRL_PEAK_RANGE, 1)

    # 如果 internal_ctrl_peaks 不足 1 個, 則回 None
    if len(Called_peak) == 0:
      logger.warn(f"Warning: Sample internal_ctrl Peak 不足 1 個!")
      return None

    # CallPeak 取得 internal_ctrl_peaks 並轉換成 SAMPLE_HTDPeak 列表
    internal_ctrl_peaks = SAMPLE_HTDPeak(
      peak_group=PEAK_GROUP.INTERNAL_CTRL.value,
      peak_size=Called_peak[0].peak_size,
      peak_rfu=Called_peak[0].peak_rfu,
      peak_rfu_ratio=1,
      pass_rfu_cutoff=True,
      pass_rfu_ratio_cutoff=True
    )

    return internal_ctrl_peaks

  elif peak_type == PEAK_GROUP.TARGET:

    # CallPeak 取得 target_peaks
    target_peaks = CallPeak(sample_df, TARGET_PEAK_RANGE)

    # 如果 target_peaks 不足 1 個, 則回 None
    if len(target_peaks) == 0:
      logger.warn(f"Warning: Sample target Peak 沒有找到!")
      return None

    # CallPeak 取得 target_peaks 並轉換成 SAMPLE_HTDPeak 列表
    target_HTD_peaks = [
      SAMPLE_HTDPeak(
        peak_group=PEAK_GROUP.TARGET.value,
        peak_size=target_peak.peak_size,
        peak_rfu=target_peak.peak_rfu
      )
      for target_peak in target_peaks
    ]

    # 排序 target_HTD_peaks 依據 peak_rfu 由小到大
    target_HTD_peaks = sorted(target_HTD_peaks, key=lambda x: x.peak_rfu, reverse=True)

    # 取得 topRFU 的 target_peak
    topRFU_target_peak = target_HTD_peaks[0]
    topRFU_peak_size = topRFU_target_peak.peak_size
    topRFU_peak_rfu = topRFU_target_peak.peak_rfu

    # 計算 target_HTD_peaks 的 peak_rfu_ratio
    for peak in target_HTD_peaks:
      peak.pass_rfu_cutoff = peak.peak_rfu >= HTD_RFU_CUTOFF
      peak.peak_rfu_ratio = round(peak.peak_rfu / topRFU_peak_rfu, 2)
      peak.pass_rfu_ratio_cutoff = peak.peak_rfu_ratio >= HTD_RUF_RATIO_CUTOFF

    # selected_target_peak
    selected_target_peak = [
      peak for peak in target_HTD_peaks
      if (peak.peak_size <= topRFU_peak_size + HTD_BP_THRESHOLD and peak.pass_rfu_cutoff and peak.pass_rfu_ratio_cutoff)
      or (peak.peak_size > topRFU_peak_size + HTD_BP_THRESHOLD and peak.pass_rfu_cutoff)
    ]

    return selected_target_peak

  else:
    logger.warn(f"Warning: 不支援的 Peak Type: {peak_type}")
    return None

# 分析 Sample Peaks
def analyzeSamplePeaks(samples_obj_list):

  # 初始化 sampleData
  sampleData = {}

  # 分析每個樣本
  for sample_obj in samples_obj_list:

    # 初始化 HTD_Data
    htd_data = HTD_Data(
      sample_id=sample_obj.sample_id,
      internal_ctrl_peaks=None,
      selected_target_peaks=[]
    )

    # 取得 internal_ctrl_peaks
    internal_ctrl_peaks = getSamplePeak(sample_obj.data, peak_type=PEAK_GROUP.INTERNAL_CTRL)
    htd_data.internal_ctrl_peaks = internal_ctrl_peaks

    # 取得 target_peaks
    target_peaks = getSamplePeak(sample_obj.data, peak_type=PEAK_GROUP.TARGET)

    # 如果 target_peaks 為 None, 則跳過
    if target_peaks is None:
      error_message = f"Sample {sample_obj.sample_id} target_peaks 沒有找到"
      logger.warn(f"Warning: {error_message}")
      htd_data.error_message = error_message
    else:
      # 更新 target_peaks
      htd_data.selected_target_peaks = target_peaks

    # 更新 sampleData
    sampleData[sample_obj.sample_id] = htd_data

  return sampleData

# 處理 CLI 參數
def parseParams():

  # 接收 CLI 參數
  parser = argparse.ArgumentParser()
  parser.add_argument("--control", "-c", required=True, type=str, help="控制檔案路徑")
  parser.add_argument("--samples", "-s", required=True, type=str, help="樣本檔案路徑, 多個檔案使用逗號分隔")
  parser.add_argument("--reagent", "-r", required=False, default="accuinHD1", type=str, help="試劑類型, 目前只有 accuinHD1 可以不用設定")
  parser.add_argument("--instrument", "-i", required=False, default="qsep100", type=str, help="儀器類型, 目前只有 qsep100 可以不用設定")
  parser.add_argument("--organization", "-g", required=False, default="defaultOrg", type=str, help="組織所屬, FXS 不會用到可以不用設定")
  parser.add_argument("--output", "-o", required=False, type=str, help="輸出結果的 JSON 檔案路徑, 若不給定, 則輸出到 console")
  args = parser.parse_args()

  # 驗證 CLI 參數
  if not os.path.exists(args.control):
    print(f"控制檔案不存在, 請確認路徑是否正確: {args.control}")
    return

  # 使用逗號分隔樣本檔案路徑
  args.samples = args.samples.split(",")

  # 驗證樣本檔案是否存在
  for sample in args.samples:
    if not os.path.exists(sample):
      print(f"樣本檔案不存在, 請確認路徑是否正確: {sample}")
      return

  return args

# 執行 CLI
if __name__ == "__main__":

  # 接收參數, 取得檔案路徑
  args = parseParams()

  # 如果參數解析失敗, 則回報並結束程式
  if not args:
    print("參數解析失敗, Exit")
    exit(1)

  # 設定 HTD 輸入參數
  control = args.control
  samples = args.samples
  userInfo = UserInfo(
    reagent = args.reagent,
    instrument = args.instrument,
    organization = args.organization
  )

  # 運行 HTD 主程式
  analysisResult = HTD(control, samples, userInfo)

  # 輸出結果
  if args.output:
    with open(args.output, "w") as f:
      f.write(analysisResult)
  else:
    print(analysisResult)
