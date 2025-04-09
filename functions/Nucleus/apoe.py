# 導入模組
import os
import sys
import json
import itertools
import pandas as pd
import argparse
from dataclasses import dataclass

# 導入 utils
from utils.InputParser import UserInfo
from utils.FileParser import FileParser
from utils.ConstVaribles import QCStatus, AssessmentStatus, NucleusVersion
from utils.DataObject import Range, RFUObj, Qsep100Peak, AnalysisOutput

# 獲取當前腳本所在的目錄. 將上一層目錄添加到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)
sys.path.append(current_dir)

# 引入 systemLogger
from systemLogger import Logger
logger = Logger()

# 定義 APOE peak Object
@dataclass
class APOEPeak(Qsep100Peak):
  peak_group: str
  peak_type: str

# 定義 APOE data Object
@dataclass
class APOEData:
  file_name: str
  sample_id: str
  peak_group: str
  well: str
  ic_peaks: APOEPeak
  tg_peaks: APOEPeak
  normalized_rfu: float
  qc_status: str
  errorMsg: str

# 定義 APOE Assessment 結果
@dataclass
class APOEAssessment:
  qc_status: str
  qc_message: str
  assessment: str
  rfu_status: list

# 定義 APOE 輸出結果
@dataclass
class APOEOutput(AnalysisOutput):
  control1: list = None
  control2: list = None
  samples: dict = None
  result: dict = None

# Peak size 理論數值範圍
EXPECTED_TARGET_RANGE_BP      = Range(MIN=160, MAX=195)
EXPECTED_INTERNAL_E2_RANGE_BP = Range(MIN=201, MAX=250)
EXPECTED_INTERNAL_E3_RANGE_BP = Range(MIN=251, MAX=300)
EXPECTED_INTERNAL_E4_RANGE_BP = Range(MIN=301, MAX=370)

# RFU CutOff
ACT_RFU_CUTOFF = 1
E2_RFU_CUTOFF = 0.7
E3_RFU_CUTOFF = 0.7
E4_RFU_CUTOFF = 0.8

# APOE 主程式
def APOE(control1_list, control2_list, samples_list, user_info):

  # Logger settings
  sender = user_info.organization
  logger.setSender(sender)

  # Logger : Start Message
  tmp_source = "apoe.py line. 72"
  logger.analysis(f" ----> Start APOE Analysis <---- ", tmp_source)
  logger.analysis(f" User Info: {user_info}", tmp_source)

  # 取得 config
  config = {
    "reagent": user_info.reagent,
    "organization": user_info.organization,
    "instrument": user_info.instrument,
    "NucleusVersion": NucleusVersion.APOE.value
  }

  # 初始化 APOEOutput
  APOE_output = APOEOutput(config=config)

  # 1. 讀取檔案轉換成 DataFrame, 並加上 file_name, sample_id, well 欄位
  ctrl1_df_list, ctrl2_df_list, sample_df_list = readFileLists(control1_list, control2_list, samples_list)

  # 2. 讀取 Control peaks 和 Target peaks
  ctrl1_ic_peaks, ctrl2_ic_peaks, sample_ic_peaks = readPeaksAll("control", ctrl1_df_list, ctrl2_df_list, sample_df_list)
  ctrl1_tg_peaks, ctrl2_tg_peaks, sample_tg_peaks = readPeaksAll("target", ctrl1_df_list, ctrl2_df_list, sample_df_list)

  # 3. 製作 APOE Data Object
  ctrl1_apoeData_list = summaryAPOEData(ctrl1_df_list, ctrl1_ic_peaks, ctrl1_tg_peaks)
  ctrl2_apoeData_list = summaryAPOEData(ctrl2_df_list, ctrl2_ic_peaks, ctrl2_tg_peaks)
  sample_apoeData_list = {}
  for sample_name in sample_df_list:
    sample_apoeData_list[sample_name] = summaryAPOEData(sample_df_list[sample_name], sample_ic_peaks[sample_name], sample_tg_peaks[sample_name])

  # 更新 APOE_output: control1, control2, samples Data
  APOE_output.control1 = ctrl1_apoeData_list
  APOE_output.control2 = ctrl2_apoeData_list
  APOE_output.samples = sample_apoeData_list

  # 4. Standard Control QC assessment
  ctrl1_qc_status, ctrl1_rfuList = StdCtrlQCAssessment(ctrl1_apoeData_list, "control1")
  ctrl2_qc_status, ctrl2_rfuList = StdCtrlQCAssessment(ctrl2_apoeData_list, "control2")

  # 檢查 QC 狀態, 如果 Failed, 跳過 sample assessment
  if ctrl1_qc_status == QCStatus.FAILED or ctrl2_qc_status == QCStatus.FAILED:
    tmp_source = "apoe.py line. 120"
    logger.warn(f" * Standard Control QC Failed, skip sample assessment * ", tmp_source)
    logger.warn(f" Control1: {ctrl1_qc_status.value}, RFU status: {ctrl1_rfuList}", tmp_source)
    logger.warn(f" Control2: {ctrl2_qc_status.value}, RFU status: {ctrl2_rfuList}", tmp_source)
    APOE_output.qc_status = QCStatus.FAILED.value

    # 製作 inconclusive 的 result
    inconclusive_result = APOEAssessment(
      qc_status=QCStatus.FAILED.value,
      qc_message=f"Standard Control QC 未通過, 跳過 Sample Assessment.",
      assessment=AssessmentStatus.INCONCLUSIVE.value,
      rfu_status=[]
    )

    # 將 inconclusive 的 result 加入到 APOE_output.result
    APOE_output.result = {}
    for sample_name in sample_apoeData_list:
      APOE_output.result[sample_name] = inconclusive_result

    # 回傳 APOE_output
    return APOE_output.toJson()

  # 5. Sample Assessment
  sample_assessment_list = {}
  for sample_name in sample_apoeData_list:
    assessment_status, sample_qc_status, qc_message, rfuList = SampleAssessment(sample_apoeData_list[sample_name])
    sample_assessment_list[sample_name] = APOEAssessment(qc_status=sample_qc_status, qc_message=qc_message, assessment=assessment_status, rfu_status=rfuList)
  # 更新 APOE_output: result
  APOE_output.result = sample_assessment_list

  # 6. 打印結果
  tmp_source = "apoe.py line. 152"
  logger.analysis(f" * Assessment Results * ", tmp_source)
  logger.analysis(f" Control1 QC status: {ctrl1_qc_status.value}, RFU status: {ctrl1_rfuList}", tmp_source)
  logger.analysis(f" Control2 QC status: {ctrl2_qc_status.value}, RFU status: {ctrl2_rfuList}", tmp_source)
  for sample_name in sample_assessment_list:
    logger.analysis(f" \n\
      Sample: {sample_name}, \n\
      QC status: {sample_assessment_list[sample_name].qc_status.value}, \n\
      QC message: {sample_assessment_list[sample_name].qc_message}, \n\
      Assessment: {sample_assessment_list[sample_name].assessment.value}, \n\
      RFU status: {sample_assessment_list[sample_name].rfu_status}", tmp_source)

  # 7. 判斷有沒有任何一個 Failed QC assessment
  checkQCList = [ctrl1_qc_status, ctrl2_qc_status] + [q.qc_status for q in sample_assessment_list.values()]
  if any(qc_status == QCStatus.FAILED for qc_status in checkQCList):
    # 找出 failed 的 sample 並紀錄到 qc message
    failed_samples = [sample_name for sample_name in sample_assessment_list if sample_assessment_list[sample_name].qc_status == QCStatus.FAILED]
    failed_samples_message = [f"{sample_name}: {sample_assessment_list[sample_name].qc_message}" for sample_name in failed_samples]
    APOE_output.errMsg = f"; ".join(failed_samples_message)

    # 打印 failed 的 sample
    tmp_source = "apoe.py line. 164"
    logger.warn(f" * Some samples QC Failed :{', '.join(failed_samples)}* ", tmp_source)

  # 更新 APOE_output: qc_status
  tmp_source = "apoe.py line. 170"
  logger.analysis(f" * Analysis Completed * ", tmp_source)
  APOE_output.qc_status = QCStatus.PASSED.value

  # 轉換成 JSON 並回傳
  return APOE_output.toJson()

# 處理 APOE 的檔名
def parseFileNameWell(filename):

  # 分割檔名, 取得各個部分
  well = ''
  parts = filename.split("_")

  # 如果檔名包含兩個以上的節, 取得 well 字串為倒數第二個節的後三個字元
  if len(parts) > 2:
    well = parts[-2][-3:]

  return well

# 讀取檔案並回傳 APOE Object
def readFileLists(control1_list, control2_list, samples_list):
  # 實體化 FileParser
  file_parser = FileParser()

  # 讀取 control1 的檔案
  control1_df_list = list(map(lambda x: file_parser.parseQsep100File(x), control1_list))

  # 讀取 control2 的檔案
  control2_df_list = list(map(lambda x: file_parser.parseQsep100File(x), control2_list))

  # 讀取 samples 的檔案
  samples_df_list = {}
  for samples in samples_list:
    samples_df_list[samples] = list(map(lambda x: file_parser.parseQsep100File(x), samples_list[samples]))

  # 幫每個 APOE Object 加上 well 欄位
  appendWellInfo(control1_df_list, control2_df_list, samples_df_list)

  # 回傳 APOE Object 列表
  return control1_df_list, control2_df_list, samples_df_list

# 幫每個 APOE Object 加上 well 欄位
def appendWellInfo(control1_list, control2_list, samples_list):
  # 幫 control1 的 APOE 加上 well 欄位
  for each in control1_list:
    each.well = parseFileNameWell(each.file_name)

  # 幫 control2 的 APOE 加上 well 欄位
  for each in control2_list:
    each.well = parseFileNameWell(each.file_name)

  # 幫 samples 的 APOE 加上 well 欄位
  for sample_name in samples_list:
    for each_sample in samples_list[sample_name]:
      each_sample.well = parseFileNameWell(each_sample.file_name)

# 讀取 Control peaks (單個)
def readControlPeaks(data_df):

  # 檢查 data_df 是否為 DataFrame
  if not isinstance(data_df, pd.DataFrame):
    tmp_source = "apoe.py line. 229"
    error_message = "Internal control Error: Can not read Control peaks dataframe!"
    logger.error(error_message, tmp_source)
    return APOEPeak(peak_group="error", peak_type=error_message, peak_size=-1, peak_rfu=-1)

  # 排除非數值的 bp 的行
  filtered_df = data_df[data_df["bp"].str.isdigit()]

  # 取得 E2, E3, E4 的 peak
  is_E2_peak = list(filtered_df.apply(lambda row: EXPECTED_INTERNAL_E2_RANGE_BP.inRange(row["bp"], ACT_RFU_CUTOFF, row["RFU"]), axis=1))
  is_E3_peak = list(filtered_df.apply(lambda row: EXPECTED_INTERNAL_E3_RANGE_BP.inRange(row["bp"], ACT_RFU_CUTOFF, row["RFU"]), axis=1))
  is_E4_peak = list(filtered_df.apply(lambda row: EXPECTED_INTERNAL_E4_RANGE_BP.inRange(row["bp"], ACT_RFU_CUTOFF, row["RFU"]), axis=1))

  # 取得 E2, E3, E4 的 peak 數量
  number_of_E2_peak = sum(is_E2_peak)
  number_of_E3_peak = sum(is_E3_peak)
  number_of_E4_peak = sum(is_E4_peak)

  # 判斷狀況並回傳

  # 狀況 1: 只有一個 E2 control peak
  if number_of_E2_peak == 1 and number_of_E3_peak == 0 and number_of_E4_peak == 0:
    index = is_E2_peak.index(True)
    peakSize = int(filtered_df.iloc[index]["bp"])
    peakRfu = float(filtered_df.iloc[index]["RFU"])
    return APOEPeak(peak_group="E2", peak_type="control", peak_size=peakSize, peak_rfu=peakRfu)

  # 狀況 2: 只有一個 E3 peak
  elif number_of_E2_peak == 0 and number_of_E3_peak == 1 and number_of_E4_peak == 0:
    index = is_E3_peak.index(True)
    peakSize = int(filtered_df.iloc[index]["bp"])
    peakRfu = float(filtered_df.iloc[index]["RFU"])
    return APOEPeak(peak_group="E3", peak_type="control", peak_size=peakSize, peak_rfu=peakRfu)

  # 狀況 3: 只有一個 E4 peak
  elif number_of_E2_peak == 0 and number_of_E3_peak == 0 and number_of_E4_peak == 1:
    index = is_E4_peak.index(True)
    peakSize = int(filtered_df.iloc[index]["bp"])
    peakRfu = float(filtered_df.iloc[index]["RFU"])
    return APOEPeak(peak_group="E4", peak_type="control", peak_size=peakSize, peak_rfu=peakRfu)

  # 狀況 4: 都沒有 peak
  elif number_of_E2_peak == 0 and number_of_E3_peak == 0 and number_of_E4_peak == 0:
    tmp_source = "apoe.py line. 275"
    error_message = f"Internal control Error: E2, E3, E4 No peak was found!"
    logger.warn(error_message, tmp_source)
    return APOEPeak(peak_group="error", peak_type=error_message, peak_size=-1, peak_rfu=-1)

  # 狀況 5: 有兩個以上的 peak
  elif number_of_E2_peak > 1 or number_of_E3_peak > 1 or number_of_E4_peak > 1:
    tmp_source = "apoe.py line. 282"
    error_message = f"Internal control Error: Multiple peaks were found!"
    logger.warn(error_message, tmp_source)
    return APOEPeak(peak_group="error", peak_type=error_message, peak_size=-1, peak_rfu=-1)

  # 狀況 6: 其他狀況
  else:
    error_message = f"Internal control Error: Unknown error!"
    tmp_source = "apoe.py line. 289"
    logger.error(error_message, tmp_source)
    return APOEPeak(peak_group="error", peak_type=error_message, peak_size=-1, peak_rfu=-1)

# 讀取 Target peak (單個)
def readTargetPeaks(data_df):

  # 檢查 data_df 是否為 DataFrame
  if not isinstance(data_df, pd.DataFrame):
    error_message = "Target peak Error: Can not read Target peaks dataframe!"
    tmp_source = "apoe.py line. 299"
    logger.error(error_message, tmp_source)
    return APOEPeak(peak_group="error", peak_type=error_message, peak_size=-1, peak_rfu=-1)

  # 排除非數值的 bp 的行
  filtered_df = data_df[data_df["bp"].str.isdigit()]

  # 取得 Target peak
  is_Target_peak = list(filtered_df.apply(lambda row: EXPECTED_TARGET_RANGE_BP.inRange(row["bp"], ACT_RFU_CUTOFF), axis=1));

  # 如果 Target peak 存在, 則取得最大的 RFU 的 peak
  if len(is_Target_peak) > 0:
    true_indices = [index for index, value in enumerate(is_Target_peak) if value]
    select_df = filtered_df.iloc[true_indices]
    top_RFU = select_df.loc[select_df["RFU"].idxmax()]
    return APOEPeak(peak_group="Target", peak_type="target", peak_size=top_RFU["bp"], peak_rfu=top_RFU["RFU"])
  else:
    error_message = "No Target peak was found!"
    tmp_source = "apoe.py line. 317"
    logger.warn(error_message, tmp_source)
    return APOEPeak(peak_group="error", peak_type=error_message, peak_size=-1, peak_rfu=-1)

# 讀取 peaks (全部)
def readPeaksAll(readType, control1_list, control2_list, samples_list):
  if readType == "control":
    control1_control_peaks = list(map(lambda x: readControlPeaks(x.data), control1_list))
    control2_control_peaks = list(map(lambda x: readControlPeaks(x.data), control2_list))
    sample_control_peaks = {}
    for sample_name in samples_list:
      sample_control_peaks[sample_name] = list(map(lambda x: readControlPeaks(x.data), samples_list[sample_name]))
    return control1_control_peaks, control2_control_peaks, sample_control_peaks
  elif readType == "target":
    control1_target_peaks = list(map(lambda x: readTargetPeaks(x.data), control1_list))
    control2_target_peaks = list(map(lambda x: readTargetPeaks(x.data), control2_list))
    sample_target_peaks = {}
    for sample_name in samples_list:
      sample_target_peaks[sample_name] = list(map(lambda x: readTargetPeaks(x.data), samples_list[sample_name]))
    return control1_target_peaks, control2_target_peaks, sample_target_peaks

# 製作 APOE Object
def summaryAPOEData(qsep100Object, ic_peaks, tg_peaks):

  # 初始化 APOE Object 列表
  APOEObjectList = []

  # 製作 APOE Object
  for qsep100, ic_peaks, tg_peaks in zip(qsep100Object, ic_peaks, tg_peaks):

    # 初始化 qc_status 和 errorMsg
    qc_status = "meet-the-criteria"
    errorMsg = ""

    # 取得 errorPeaks
    errorPeaks = [p for p in [ic_peaks, tg_peaks] if p.peak_group == "error"]
    if len(errorPeaks) > 0:
      qc_status = QCStatus.FAILED
      errorMsg = ";".join([p.peak_type for p in errorPeaks])

    # 建立 APOE Object
    newAPOEdata = APOEData(
      file_name=qsep100.file_name,
      sample_id=qsep100.sample_id,
      peak_group=ic_peaks.peak_group,
      well=qsep100.well,
      ic_peaks=ic_peaks,
      tg_peaks=tg_peaks,
      qc_status=qc_status,
      errorMsg=errorMsg,
      normalized_rfu=round(float(tg_peaks.peak_rfu) / float(ic_peaks.peak_rfu), 2)
    )

    APOEObjectList.append(newAPOEdata)

  return APOEObjectList

# 判斷 RFU 數值有沒有通過 Cutoff
def RFUAssessment(e2_norm_rfu, e3_norm_rfu, e4_norm_rfu):

  # 檢查是否全部為 0
  if sum(list(map(lambda x: x > 0, [e2_norm_rfu, e3_norm_rfu, e4_norm_rfu]))) == 0:
    tmp_source = "apoe.py line. 380"
    logger.warn("[Type Assessment Failed] All type ratio are zero", tmp_source)
    return []

  else:
    # 如果 E2, E3, E4 不為 0 但 RFU 數值完全相同, 則回傳空列表
    if e2_norm_rfu == e3_norm_rfu and e3_norm_rfu == e4_norm_rfu:
      tmp_source = "apoe.py line. 385"
      logger.warn("[Type Assessment Failed] All type ratio are the same (non-zero)", tmp_source)
      return []

  # 建立 RFU 列表
  rfuList = [
    RFUObj(peak_group="E2", rfu_value=e2_norm_rfu, rfu_cutoff=E2_RFU_CUTOFF),
    RFUObj(peak_group="E3", rfu_value=e3_norm_rfu, rfu_cutoff=E3_RFU_CUTOFF),
    RFUObj(peak_group="E4", rfu_value=e4_norm_rfu, rfu_cutoff=E4_RFU_CUTOFF)
  ]

  # 依照 RFUObj.rfu_value 由大到小排序
  rfuList.sort(key=lambda x: x.rfu_value, reverse=True)

  # 把第二個 RFUObj 做 RFU Cutoff, 如果沒有通過 Cutoff, 則標記為 False
  rfuList[1].CutRFU()

  # 回傳 RFU 數值前兩高的 RFUObj
  return rfuList[:2]

# 決定 Standard Control 的 QC 狀態
def StdCtrlQCAssessment(APOEDataList, control_label):

  # 初始化 QC 狀態
  qc_status = QCStatus.FAILED

  # 檢查有沒有 peak_group='error', 如果有, 則回傳 QC_FAILED
  if any(data.peak_group == 'error' for data in APOEDataList):
    return qc_status, []

  # 取得各個 E2, E3, E4 的 normalized_rfu
  e2_apoe_rfu = [data for data in APOEDataList if data.peak_group == 'E2'][0].normalized_rfu
  e3_apoe_rfu = [data for data in APOEDataList if data.peak_group == 'E3'][0].normalized_rfu
  e4_apoe_rfu = [data for data in APOEDataList if data.peak_group == 'E4'][0].normalized_rfu

  # 判斷 RFU 數值有沒有通過 Cutoff
  RFUList = RFUAssessment(e2_apoe_rfu, e3_apoe_rfu, e4_apoe_rfu)

  # 如果 RFUList 為空, 則回傳 QC_FAILED
  if len(RFUList) == 0:
    return qc_status, RFUList

  # 取得 RFUList 的 peak_group
  peak_group_list = list(map(lambda x: x.peak_group, RFUList))

  # 如果是 control1, 則判斷 E2 和 E3 是否在 RFUList 中
  if control_label == "control1":
    if "E2" in peak_group_list and "E3" in peak_group_list:

      # 如果 E2 和 E3 都通過 Cutoff, 則 QC 狀態為 QC_PASSED
      failed_cutoff = [x for x in RFUList if not x.pass_cutoff]
      if len(failed_cutoff) == 0: qc_status = QCStatus.PASSED

  # 如果是 control2, 則判斷 E3 和 E4 是否在 RFUList 中
  elif control_label == "control2":
    if "E3" in peak_group_list and "E4" in peak_group_list:

      # 如果 E3 和 E4 都通過 Cutoff, 則 QC 狀態為 QC_PASSED
      failed_cutoff = [x for x in RFUList if not x.pass_cutoff]
      if len(failed_cutoff) == 0: qc_status = QCStatus.PASSED

  # 例外狀況
  else:
    qc_status = QCStatus.FAILED

  # 回傳 QC 狀態和 RFUList
  return qc_status, RFUList

# 決定 Sample 的 Assessment
def SampleAssessment(APOEDataList):

  # 初始化 Assessment, QC 狀態
  assessment_status = AssessmentStatus.INVALID
  qc_status = QCStatus.PASSED
  qc_message = ""

  # 檢查有沒有 peak_group='error', 如果有, 則回傳 QC_FAILED
  if any(data.peak_group == 'error' for data in APOEDataList):
    return assessment_status, qc_status, qc_message, []

  # 取得各個 E2, E3, E4 的 normalized_rfu
  e2_apoe_rfu = [data for data in APOEDataList if data.peak_group == 'E2'][0].normalized_rfu
  e3_apoe_rfu = [data for data in APOEDataList if data.peak_group == 'E3'][0].normalized_rfu
  e4_apoe_rfu = [data for data in APOEDataList if data.peak_group == 'E4'][0].normalized_rfu

  # 判斷 RFU 數值有沒有通過 Cutoff
  RFUList = RFUAssessment(e2_apoe_rfu, e3_apoe_rfu, e4_apoe_rfu)

  # 如果 RFUList 為空, 則回傳 INVALID
  if len(RFUList) == 0:
    qc_status = QCStatus.FAILED
    qc_message = "該 Sample 沒有任何 peak 通過 RFU Cutoff"
    return assessment_status, qc_status, qc_message, RFUList

  # 取得通過 Cutoff 的 peak_group, 如果該 peak_group 沒有通過 Cutoff, 則他會變成 None
  peak_group_list = [x.peak_group for x in RFUList if x.pass_cutoff]

  # 如果通過 Cutoff 的 peak_group 數量為 1, 則將唯一的那一個重複一次
  if len(peak_group_list) == 1:
    peak_group_list.append(peak_group_list[0])

  # Low Risk 的判斷: (E2, E2) 或 (E2, E3)
  if peak_group_list == ["E2", "E2"] or ("E2" in peak_group_list and "E3" in peak_group_list):
    assessment_status = AssessmentStatus.LOW_RISK

  # Normal Risk 的判斷: (E3, E3)
  elif peak_group_list == ["E3", "E3"]:
    assessment_status = AssessmentStatus.NORMAL_RISK

  # High Risk 的判斷: (E4, E4) 或 (E2, E4) 或 (E3, E4)
  elif peak_group_list == ["E4", "E4"] or \
    ("E2" in peak_group_list and "E4" in peak_group_list) or \
    ("E3" in peak_group_list and "E4" in peak_group_list):
    assessment_status = AssessmentStatus.HIGH_RISK

  return assessment_status, qc_status, qc_message, RFUList

# 處理 CLI 參數
def parseParams():

  # 接收 CLI 參數
  parser = argparse.ArgumentParser()
  parser.add_argument("--config", "-i", required=True, type=str, help="由於 APOE 輸入複雜, 請給定測試用設定檔(*.json)路徑")
  parser.add_argument("--output", "-o", required=False, type=str, help="輸出結果的 JSON 檔案路徑, 若不給定, 則輸出到 console")
  args = parser.parse_args()

  # 驗證 CLI 參數
  if not os.path.exists(args.config):
    print(f"設定檔不存在, 請確認路徑是否正確: {args.config}")
    return

  return args

# 處理 Config 檔案
def parseConfig(config):

  # 讀取 Config 檔案
  with open(config, "r") as f:
    config = json.load(f)

  # 分別取得各個參數
  control1_list = config["control1_list"]
  control2_list = config["control2_list"]
  samples_list = config["samples_list"]
  user_info = UserInfo(**config["user_info"])

  # 檢查各個檔案是否都存在
  flattened_samples_list = list(itertools.chain.from_iterable(samples_list.values()))
  check_list = control1_list + control2_list + flattened_samples_list
  file_exist = list(map(lambda x: os.path.exists(x), check_list))

  # 如果缺少檔案, 則回報缺少的檔案
  missing_file = [check_list[i] for i in range(len(check_list)) if not file_exist[i]]
  if len(missing_file) > 0:
    for file in missing_file:
      tmp_source = "apoe.py line. 541"
      logger.error(f"找不到檔案: {file}", tmp_source)
    return

  # 回傳各個參數, 符合 APOE() 的 input 格式
  return control1_list, control2_list, samples_list, user_info

# 運行 APOE CLI
if __name__ == "__main__":

  # 設定 Logger 模式
  logger = Logger(mode="offline")

  # 接收參數, 取得檔案路徑
  args = parseParams()

  # 如果參數解析失敗, 則回報並結束程式
  if not args:
    print("參數解析失敗, Exit")
    exit(1)

  # 解析設定檔案, 取得各個參數
  ctrl1, ctrl2, samples, user_info = parseConfig(args.config)

  # 運行 APOE 分析
  analysisResult = APOE(ctrl1, ctrl2, samples, user_info)

  # 輸出結果
  if args.output:
    with open(args.output, "w") as f:
      f.write(analysisResult)
  else:
    print(analysisResult)
