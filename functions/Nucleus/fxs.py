# 導入必要模組
import argparse
import os
import sys
from enum import Enum
from dataclasses import dataclass
from scipy.stats import linregress

# 導入自製模組
from utils.InputParser import UserInfo
from utils.FileParser import FileParser
from utils.DataObject import Range, Qsep100Peak, AnalysisOutput, CallPeak
from utils.ConstVaribles import QCStatus, AssessmentStatus, NucleusVersion

# 獲取當前腳本所在的目錄. 將上一層目錄添加到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)
sys.path.append(current_dir)

# 引入 saveLogs
from systemLogger import Logger
logger = Logger()

# 定義各種 Peak 篩選範圍
CTRL_PEAK_SELECTION_RANGE = Range(MIN=300, MAX=1000)
SAMPLE_PEAK_SELECTION_RANGE = Range(MIN=250, MAX=1000)

# 定義 XY peak 篩選範圍
X_PEAK_SIZE = 158
Y_PEAK_SIZE = 195
XY_PEAK_SIZE_DIV = 15
XY_PEAK_RFU_CUTOFF = 1.5
TARGET_PEAK_RFU_CUTOFF = 1
X_PEAK_RANGE = Range(MIN=X_PEAK_SIZE-XY_PEAK_SIZE_DIV, MAX=X_PEAK_SIZE+XY_PEAK_SIZE_DIV)
Y_PEAK_RANGE = Range(MIN=Y_PEAK_SIZE-XY_PEAK_SIZE_DIV, MAX=Y_PEAK_SIZE+XY_PEAK_SIZE_DIV)

# 性別字串
class Gender(Enum):
  MALE = 'male'
  FEMALE = 'female'
  NOT_SET = 'not-set'

# Standard Control
@dataclass
class StandardControl:
  STANDARD_NAME: str
  STANDARD_REPEATS: int
  STANDARD_LENGTH: int
  STANDARD_SIZE_DEVIATION: float = 0.1
  STD_PEAK_RANGE: Range = None

  def __init__(self, STANDARD_NAME, STANDARD_REPEATS, STANDARD_LENGTH):
    self.STANDARD_NAME = STANDARD_NAME
    self.STANDARD_REPEATS = STANDARD_REPEATS
    self.STANDARD_LENGTH = STANDARD_LENGTH
    self.STD_PEAK_RANGE = Range(
      MIN=round(self.STANDARD_LENGTH*(1- self.STANDARD_SIZE_DEVIATION)),
      MAX=round(self.STANDARD_LENGTH*(1+ self.STANDARD_SIZE_DEVIATION))
    )

# 定義 Standard Control 的 BP 範圍
STANARD_MTX = {
  'accuinFx1':{
    'std1' :StandardControl(STANDARD_NAME='SC1', STANDARD_REPEATS=30, STANDARD_LENGTH=311),
    'std2' :StandardControl(STANDARD_NAME='SC2', STANDARD_REPEATS=50, STANDARD_LENGTH=374),
    'std3' :StandardControl(STANDARD_NAME='SC3', STANDARD_REPEATS=80, STANDARD_LENGTH=462)
  },
  'accuinFx2':{
    'std1' :StandardControl(STANDARD_NAME='SC1', STANDARD_REPEATS=30, STANDARD_LENGTH=311),
    'std2' :StandardControl(STANDARD_NAME='SC2', STANDARD_REPEATS=50, STANDARD_LENGTH=374),
    'std3' :StandardControl(STANDARD_NAME='SC3', STANDARD_REPEATS=80, STANDARD_LENGTH=462),
    'std4' :StandardControl(STANDARD_NAME='SC4', STANDARD_REPEATS=200, STANDARD_LENGTH=823)
  }
}

# 定義 FXS Peak Object
@dataclass
class FXS_Peak(Qsep100Peak):
  peak_group: str
  rfu_cutoff: float
  peak_type: str = 'not-set'
  repeatNum: int = -1
  expected_repeatNum: float = -1
  average_repeatNum: float = -1
  pass_cutoff: bool = False
  assessment: AssessmentStatus = AssessmentStatus.NOT_SET

  def __init__(self, peak_group, peak_rfu, peak_size, peak_type = 'not-set', rfu_cutoff=0):
    self.peak_group = peak_group
    self.rfu_cutoff = rfu_cutoff
    self.peak_rfu = peak_rfu
    self.peak_size = peak_size
    self.peak_type = peak_type
    self.expected_repeatNum = round((self.peak_size - FLANKING_SIZE) /3, 1)
    self.CutRFU()

  # 篩選 RFU
  def CutRFU(self):
    if self.peak_rfu >= self.rfu_cutoff:
      self.pass_cutoff = True

  # 計算 Repeat 數並判斷 Assessment
  def CalculateRepeatNum(self, slope, intercept):
    # 計算 Repeat 數
    self.repeatNum = round(float(slope * self.peak_size + intercept), 1)
    self.average_repeatNum = int(round((self.repeatNum + self.expected_repeatNum) / 2, 0))

    # 由 Repeat 數判斷 FX peak 的 Assessment
    self.assessment = self.assessment_by_repeat_num()

  # 由 Repeat 數判斷 FX peak 的 Assessment
  def assessment_by_repeat_num(self):

    # Normal
    if self.average_repeatNum < RepeatCutoff.NORMAL_CUTOFF.value:
      return AssessmentStatus.NORMAL

    # Intermediate
    elif RepeatCutoff.NORMAL_CUTOFF.value <= self.average_repeatNum < RepeatCutoff.INTERMEDIATE_CUTOFF.value:
      return AssessmentStatus.INTERMEDIATE

    # Premutation
    elif RepeatCutoff.INTERMEDIATE_CUTOFF.value <= self.average_repeatNum < RepeatCutoff.MUTATION_CUTOFF.value:
      return AssessmentStatus.PREMUTATION

    # Full Penetrance
    elif self.average_repeatNum >= RepeatCutoff.MUTATION_CUTOFF.value:
      return AssessmentStatus.FULL_MUTATION

    # 如果 Repeat number 不在任何 AssessmentStatus 範圍內, 則回傳 Invalid
    else:
      return AssessmentStatus.INVALID

# 定義 Point Object
@dataclass
class Point:
  x: float
  y: float

# 定義 SC 的數值上限
MAX_LIMIT_SC_PEAK_SIZE = 1200
MAX_LIMIT_SC_REPEAT_NUM = 300
FX_PEAK_SIZE_EXPAND = 60

# PCR 的 Flanking Size
FLANKING_SIZE = 221

# 定義 repeat Cutoff
class RepeatCutoff(Enum):
  NORMAL_CUTOFF = 45
  INTERMEDIATE_CUTOFF = 55
  MUTATION_CUTOFF = 200

# 定義 FXS standard control 的 Assessment
@dataclass
class FXS_SC_Assessment:
  qc_status: str
  r_square: float
  slope: float
  intercept: float
  line: list[Point]
  formula: str
  errorMsg: str = ''

# 定義 FXS sample 的 Assessment
@dataclass
class FXS_Sample_Assessment:
  sample_id: str
  qc_status: str
  assessment: str
  interpretation: list[str]
  gender: str
  errorMsg: str = ''

# 定義 FXS 輸出結果
@dataclass
class FXSOutput(AnalysisOutput):
  control_data: dict = None
  sample_data: dict = None
  control_qc: dict = None
  result: dict = None

# 執行 FXS 分析主程式
def FXS(control_file_path, samples_file_list, user_info):

  # Logger settings
  sender = user_info.organization
  logger.setSender(sender)

  # Logger : Start Message
  tmp_source = "fxs.py line. 185"
  logger.analysis(f" ----> Start FXS Analysis <---- ", tmp_source)
  logger.analysis(f" User Info: {user_info}", tmp_source)

  # 取得 config
  config = {
    "reagent": user_info.reagent,
    "organization": user_info.organization,
    "instrument": user_info.instrument,
    "NucleusVersion": NucleusVersion.FXS.value
  }

  # 初始化 FXSOutput
  fxs_output = FXSOutput(config=config, sample_data={})

  # 實體化 FileParser
  fileParser = FileParser()

  # 1. 解析 Qsep100 檔案
  control_obj = fileParser.parseQsep100File(control_file_path)
  samples_obj_list = [fileParser.parseQsep100File(sample) for sample in samples_file_list]

  # 2. 篩選控制檔案的 Peak
  controlPeaks = getControlPeak(control_obj.data, user_info.reagent)

  # 如果沒有找到 controlPeaks, 則回傳 QCStatus.FAILED
  if len(controlPeaks) == 0:
    tmp_source = "fxs.py line. 218"
    logger.warn(f" FXS Terminated: Control 檔案問題", tmp_source)
    fxs_output.qc_status = QCStatus.FAILED.value
    return fxs_output.toJson()

  # 輸出所有 SC 的資訊
  for each_peak in controlPeaks:
    tmp_source = "fxs.py line. 225"
    logger.analysis(f" Std Peak information: {each_peak}", tmp_source)

  # 檢查有沒有缺少 SC (peak_type=[SC1, SC2, SC3] 或 [SC1, SC2, SC3, SC4])
  SC_Checking = [each_std.STANDARD_NAME for each_std in STANARD_MTX[user_info.reagent].values()]
  if set([each_peak.peak_type for each_peak in controlPeaks]) != set(SC_Checking):
    tmp_source = "fxs.py line. 231"
    diff = list(set(SC_Checking) - set([each_peak.peak_type for each_peak in controlPeaks]))
    logger.warn(f" FXS Terminated: Control 檔案缺少一些 SC peaks: {diff}", tmp_source)
    fxs_output.qc_status = QCStatus.FAILED.value
    fxs_output.control_data = controlPeaks
    return fxs_output.toJson()
  else:
    tmp_source = "fxs.py line. 238"
    logger.analysis(f" All Standard Control peaks found.", tmp_source)

  # 對 ControlPeak 進行 Assessment
  SC_assessment = SC_peak_assessment(controlPeaks)
  tmp_source = "fxs.py line. 241"
  logger.analysis(f"Standard Control Assessment: \
   \n Standard Control Filename: {os.path.basename(control_file_path)} \
   \n qc-status: {SC_assessment.qc_status.value} \
   \n r-square: {SC_assessment.r_square} \
   \n slope: {SC_assessment.slope} \
   \n line: {SC_assessment.line} \
   \n formula: {SC_assessment.formula} \
   \n errorMsg: {SC_assessment.errorMsg}", tmp_source)

  # 3. 對每個 Sample 進行 Assessment
  sample_assessment_results = {}
  for each_sample in samples_obj_list:

    # 取得 SamplePeak
    samplePeaks = getSamplePeak(each_sample.data)

    # 計算 repeatNum
    for each_peak in samplePeaks['target_peaks']:
      each_peak.CalculateRepeatNum(SC_assessment.slope, SC_assessment.intercept)

    # 篩選 FX peak
    gender, selected_fx_peaks = filter_sample_peaks(samplePeaks, each_sample.sample_id)
    tmp_source = "fxs.py line. 266"
    logger.analysis(f"selected_fx_peaks: \n\t{"\n\t".join([str(each_peak) for each_peak in selected_fx_peaks])}", tmp_source)

    # 加入 sample_data
    fxs_output.sample_data[each_sample.sample_id] = {
      'sample_id': each_sample.sample_id,
      'gender': gender,
      'selected_fx_peaks': selected_fx_peaks
    }

    # Sample Assessment
    assessmentResult = sample_assessment(selected_fx_peaks, gender, each_sample.sample_id)
    sample_assessment_results[each_sample.sample_id] = assessmentResult

  # log result
  for each_sample_id, each_sample_result in sample_assessment_results.items():
    tmp_source = "fxs.py line. 282"
    logger.analysis(f"Sample Assessment Result: {each_sample_id} \n\t{each_sample_result}", tmp_source)

  # 更新 FXSOutput
  fxs_output.qc_status = SC_assessment.qc_status.value
  fxs_output.control_data = controlPeaks
  fxs_output.control_qc = SC_assessment
  fxs_output.result = sample_assessment_results

  tmp_source = "fxs.py line. 293"
  logger.analysis(f"* FXS Analysis Completed *", tmp_source)

  return fxs_output.toJson()

# 取得 controlPeak
def getControlPeak(controlDataFrame, reagent):

  # 根據試劑類型篩選 BP 數值篩選, accuinFx1 有 3 個 SC
  if reagent == "accuinFx1":
    select_SC_peak_num = 3

  # 根據試劑類型篩選 BP 數值篩選, accuinFx2 有 4 個 SC
  elif reagent == "accuinFx2":
    select_SC_peak_num = 4

  # 如果試劑類型錯誤, 則回傳錯誤
  else:
    tmp_source = "fxs.py line. 310"
    logger.warn(f"Error: 試劑類型錯誤, 目前只有 ['accuinFx1', 'accuinFx2'] 但是輸入：{reagent}", tmp_source)
    return []

  # CallPeak 取得所有 peaks
  All_peaks = CallPeak(controlDataFrame, CTRL_PEAK_SELECTION_RANGE)

  # 如果不到 select_SC_peak_num 個, 則回傳錯誤
  if len(All_peaks) < select_SC_peak_num:
    tmp_source = "fxs.py line. 318"
    logger.warn(f"Error: Control 檔案中沒有找到 {select_SC_peak_num} 個 peaks, 只有找到 {len(All_peaks)} 個 peaks", tmp_source)
    return []

  # 取得篩選後的 DataFrame, 依照 RFU 欄位排序, 取前四名
  selected_peaks = sorted(All_peaks, key=lambda x: float(x.peak_rfu), reverse=True)[:select_SC_peak_num]

  # 將篩選後的 DataFrame 轉換為 FXS_Peak Object 列表
  controlPeaks = [
    FXS_Peak(
      peak_group='control',
      peak_size=each_peak.peak_size,
      peak_rfu=each_peak.peak_rfu
    )
    for each_peak in selected_peaks
  ]

  # 設定 peak_type 和 repeatNum
  for each_peak in controlPeaks:
    for each_std in STANARD_MTX[reagent].values():
      stdRange = each_std.STD_PEAK_RANGE
      if stdRange.inRange(each_peak.peak_size):
        each_peak.peak_type = each_std.STANDARD_NAME
        each_peak.repeatNum = each_std.STANDARD_REPEATS
        break

  return controlPeaks

# 對 ControlPeak 進行 Assessment
def SC_peak_assessment(controlPeaks):

  # 使用 peak_size 和 repeatNum 進行線性回歸;計算 R^2
  peakSize = [each_peak.peak_size for each_peak in controlPeaks]
  peakRepeat = [each_peak.repeatNum for each_peak in controlPeaks]
  slope, intercept, r_value, p_value, std_err = linregress(peakSize, peakRepeat)

  # 簡化 slope 和 r_squared 的數值
  slope = round(slope, 4)
  intercept = round(intercept, 4)
  r_squared = round(r_value**2, 4)

  # 計算 line 列表
  lineFunc = lambda x: slope * x + intercept
  line = [Point(x=x, y=round(float(lineFunc(x)), 2)) for x in [-1, MAX_LIMIT_SC_PEAK_SIZE]]

  # 如果 r_squared 為 None, 則設定 QC 狀態為 FAILED, 並設定 errorMsg
  if not r_squared:
    qc_status = QCStatus.FAILED
    errorMsg = "R^2 計算失敗"

  else:

    # 計算 QC 狀態
    if r_squared >= 0.99:
      qc_status = QCStatus.PASSED
      errorMsg = ""
    else:
      qc_status = QCStatus.FAILED
      errorMsg = "R^2 小於 0.99"

  # 製作 formula
  formula = f"y = {slope}x + ({round(intercept, 2)})"

  # 製作 Assessment 物件
  assessment = FXS_SC_Assessment(
    qc_status=qc_status,
    r_square=r_squared,
    slope=slope,
    intercept=intercept,
    line=line,
    formula=formula,
    errorMsg=errorMsg
  )

  return assessment

# 取得 SamplePeak
def getSamplePeak(sampleDataFrame):

  X_peaks = CallPeak(sampleDataFrame, X_PEAK_RANGE)
  Y_peaks = CallPeak(sampleDataFrame, Y_PEAK_RANGE)

  x_peaks = [
    FXS_Peak(
      peak_group='sample',
      rfu_cutoff=XY_PEAK_RFU_CUTOFF,
      peak_type='X_peak',
      peak_size=each_peak.peak_size,
      peak_rfu=each_peak.peak_rfu
    )
    for each_peak in X_peaks
  ]
  y_peaks = [
    FXS_Peak(
      peak_group='sample',
      rfu_cutoff=XY_PEAK_RFU_CUTOFF,
      peak_type='Y_peak',
      peak_size=each_peak.peak_size,
      peak_rfu=each_peak.peak_rfu
    )
    for each_peak in Y_peaks
  ]

  # Call target Peaks
  target_peaks = CallPeak(sampleDataFrame, SAMPLE_PEAK_SELECTION_RANGE)

  # 取得 target Peaks
  target_peaks = [
    FXS_Peak(
      peak_group='sample',
      rfu_cutoff=TARGET_PEAK_RFU_CUTOFF,
      peak_type='target_peak',
      peak_size=each_peak.peak_size,
      peak_rfu=each_peak.peak_rfu
    )
    for each_peak in target_peaks
  ]

  # 輸出所有 Peaks
  CalledPeaks = {
    'x_peaks': x_peaks,
    'y_peaks': y_peaks,
    'target_peaks': target_peaks
  }

  return CalledPeaks

# 對 SamplePeak 進行 Assessment
def filter_sample_peaks(samplePeaks, sample_id):

  # 紀錄 Peaks 到 log
  tmp_source = "fxs.py line. 447"
  logger.analysis(f"Fx peak selection of {sample_id} \
    \n X-Peaks: [\n\t{"\n\t".join([str(each_peak) for each_peak in samplePeaks['x_peaks']])}\n] \
    \n Y-Peaks: [\n\t{"\n\t".join([str(each_peak) for each_peak in samplePeaks['y_peaks']])}\n] \
    \n Target-Peaks: [\n\t{"\n\t".join([str(each_peak) for each_peak in samplePeaks['target_peaks']])}\n]", tmp_source)

  # 初始化性別, 選擇的 FX peak 列表
  gender = Gender.NOT_SET.value
  selected_fx_peaks = []

  # 篩選 pass_cutoff 為 True 的 Peak
  pass_x_peaks = [each_peak for each_peak in samplePeaks['x_peaks'] if each_peak.pass_cutoff]
  pass_y_peaks = [each_peak for each_peak in samplePeaks['y_peaks'] if each_peak.pass_cutoff]
  pass_target_peaks = [each_peak for each_peak in samplePeaks['target_peaks'] if each_peak.pass_cutoff]

  # 如過沒有 X peak, 則回傳 Invalid
  if len(pass_x_peaks) == 0:
    tmp_source = "fxs.py line. 466"
    logger.warn(f"Error: Sample {sample_id} 沒有 X peak", tmp_source)
    return gender, selected_fx_peaks

  # 用有沒有 Y 決定性別
  if len(pass_y_peaks) > 0:
    gender = Gender.MALE.value
  else:
    gender = Gender.FEMALE.value

  # 如果沒有 TargetPeak, 則回傳 Invalide
  if len(pass_target_peaks) == 0:
    tmp_source = "fxs.py line. 478"
    logger.warn(f"Error: Sample {sample_id} 沒有 TargetPeak", tmp_source)
    return gender, selected_fx_peaks

  # 取得最高 RFU 的 Peak
  highest_rfu_peak = max(pass_target_peaks, key=lambda x: x.peak_rfu)

  # 女性
  if gender == Gender.FEMALE.value:

    # 前面步驟已經篩選過 250 < peak_size < 1000 和 RFU > 1, 這裡不再重複篩選
    # FX peak 選擇範圍： 250 ~ 最高 RFU 的 Peak 的 BP 數值 + FX_PEAK_SIZE_EXPAND
    selection_range = Range(MIN=SAMPLE_PEAK_SELECTION_RANGE.MIN, MAX=highest_rfu_peak.peak_size + FX_PEAK_SIZE_EXPAND)

    # 歷遍 pass_target_peaks
    for passed_peaks in pass_target_peaks:

      # 如果在範圍內, 則計算 peak_rfu / 最高 RFU 的 peak_rfu 比值是否 > 0.2
      if selection_range.inRange(passed_peaks.peak_size):
        rfu_ratio = passed_peaks.peak_rfu / highest_rfu_peak.peak_rfu
        if rfu_ratio > 0.2:
          selected_fx_peaks.append(passed_peaks)

      # 如果不在範圍內, 則加入 FX peak 列表 (不考慮比值, 前面步驟已經篩選過 250 < peak_size < 1000)
      else:
        selected_fx_peaks.append(passed_peaks)

  # 男性
  elif gender == Gender.MALE.value:

    # 男性直接選擇最高 RFU 的 Peak 即可
    selected_fx_peaks.append(highest_rfu_peak)

  # 未設定
  else:
    tmp_source = "fxs.py line. 513"
    logger.error(f"Error: Sample {sample_id} SamplePeak_Assessment(samplePeaks, sample_id) 執行錯誤", tmp_source)
    raise ValueError(f"Error: At fxs.py SamplePeak_Assessment(samplePeaks, sample_id) 執行錯誤")

  return gender, selected_fx_peaks

# Sample Assessment
def sample_assessment(selected_fx_peaks, gender, sample_id):

  # 初始化結果們
  assessment_result = FXS_Sample_Assessment(
    sample_id=sample_id,
    qc_status=QCStatus.PASSED.value,
    assessment=AssessmentStatus.INVALID.value,
    interpretation=[],
    gender=gender
  )

  # 取得選擇的 FX peak 數量
  peak_number = len(selected_fx_peaks)

  # 如果選擇的 FX peak 數量為 1
  if peak_number == 1:
    assessment_result.assessment = selected_fx_peaks[0].assessment.value
    assessment_result.interpretation = [selected_fx_peaks[0].assessment.value]

  # 如果選擇的 FX peak 數量為 2
  elif peak_number == 2:

    # 如果兩個 FX peak 的 assessment 不同, 則將兩個 assessment 合併
    if selected_fx_peaks[0].assessment.value != selected_fx_peaks[1].assessment.value:
      assessment_result.assessment = f"{selected_fx_peaks[0].assessment.value}/{selected_fx_peaks[1].assessment.value}"
      assessment_result.interpretation = [selected_fx_peaks[0].assessment.value, selected_fx_peaks[1].assessment.value]

    # 如果兩個 FX peak 的 assessment 相同, 則將 assessment 設定為相同
    else:
      assessment_result.assessment = selected_fx_peaks[0].assessment.value
      assessment_result.interpretation = [selected_fx_peaks[0].assessment.value]

  # 如果選擇的 FX peak 數量不為 1 或 2
  else:
    errorMessage = f"Sample ID: {sample_id} 選擇的 FX peak 數量為 {peak_number} 個, 應該只能為 1 或 2 個 peaks"
    tmp_source = "fxs.py line. 554"
    logger.warn(errorMessage, tmp_source)
    logger.warn(f"Skipping Sample Assessment...", tmp_source)
    assessment_result.errorMsg = errorMessage
    return assessment_result

  return assessment_result

# 處理 CLI 參數
def parseParams():

  # 接收 CLI 參數
  parser = argparse.ArgumentParser()
  parser.add_argument("--control", "-c", required=True, type=str, help="控制檔案路徑")
  parser.add_argument("--samples", "-s", required=True, type=str, help="樣本檔案路徑, 多個檔案使用逗號分隔")
  parser.add_argument("--reagent", "-r", required=True, type=str, choices=["accuinFx1", "accuinFx2"], help="試劑類型, 目前有 ['accuinFx1', 'accuinFx2']")
  parser.add_argument("--instrument", "-i", required=False, default="qsep100", type=str, choices=["qsep100"], help="儀器類型, 目前只有 qsep100 可以不用設定")
  parser.add_argument("--organization", "-g", required=False, default="defaultOrg", type=str, help="組織所屬, FXS 不會用到可以不用設定")
  parser.add_argument("--output", "-o", required=False, type=str, help="輸出結果的 JSON 檔案路徑, 若不給定, 則輸出到 console")
  args = parser.parse_args()

  # 驗證 CLI 參數
  if not os.path.exists(args.control):
    print(f"控制檔案不存在, 請確認路徑是否正確: {args.control}")
    return

  if not args.reagent in ["accuinFx1", "accuinFx2"]:
    print(f"試劑類型錯誤, 目前可選有 ['accuinFx1', 'accuinFx2']")
    return

  # 使用逗號分隔樣本檔案路徑
  args.samples = args.samples.split(",")

  # 驗證樣本檔案是否存在
  for sample in args.samples:
    if not os.path.exists(sample):
      print(f"樣本檔案不存在, 請確認路徑是否正確: {sample}")
      return

  return args

# 運行 FXS CLI
if __name__ == "__main__":

  # 設定 Logger 模式
  logger = Logger(mode="offline")

  # 接收參數, 取得檔案路徑
  args = parseParams()

  # 如果參數解析失敗, 則回報並結束程式
  if not args:
    print("參數解析失敗, Exit")
    exit(1)

  # 設定 FXS 輸入參數
  control = args.control
  samples = args.samples
  userInfo = UserInfo(
    reagent = args.reagent,
    instrument = args.instrument,
    organization = args.organization
  )

  # 運行 FXS 主程式
  analysisResult = FXS(control, samples, userInfo)

  # 輸出結果
  if args.output:
    with open(args.output, "w") as f:
      f.write(analysisResult)
  else:
    print(analysisResult)
