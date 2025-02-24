import os
import json
import argparse
import sys
from enum import Enum
from dataclasses import dataclass

# 自定義模組
from utils.InputParser import UserInfo
from utils.FileParser import readQPCRData
from utils.DataObject import WELL, QPCRRecord, AnalysisOutput
from utils.ConstVaribles import QCStatus, AssessmentStatus, NucleusVersion

# 獲取當前腳本所在的目錄. 將上一層目錄添加到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)
sys.path.append(current_dir)

# 引入 saveLogs
from config_admin import bucket
from saveLogs import Logger
logger = Logger(bucket)

# CT_Threshold
class CT_Threshold(Enum):
  Z480 = 0
  QS3 = 35
  DELTA_CT_THRESHOLD = 4


# 定義 NUDT15 DataObject
@dataclass
class NUDT15Data():
  group: str # SC, NTC, Sample
  sample_name: str
  well_position: WELL
  wt: QPCRRecord = None
  mut: QPCRRecord = None

  def __str__(self):
    wt_str = f"{self.wt.ct_value}" if self.wt else "None"
    mut_str = f"{self.mut.ct_value}" if self.mut else "None"
    return f"NUDT15Data(group: {self.group}, sample_name: {self.sample_name}, well_position: {str(self.well_position)}, wtCT: {wt_str}, mutCT: {mut_str})"

# 定義 NUDT15 結果
@dataclass
class NUDT15Result():
  sample_name: str
  reagent: str
  assessment: AssessmentStatus
  sample_qc_status: QCStatus
  sample_type: list[str]

# 定義 NUDT15 輸出
@dataclass
class NUDT15Output(AnalysisOutput):
  controlData: NUDT15Data = None
  ntcData: NUDT15Data = None
  sampleDataList: list[NUDT15Data] = None
  resultList: list[NUDT15Result] = None

# NUDT15 主程式
def NUDT15(input_file_path, FAM_file_path, VIC_file_path, control_well, ntc_well, user_info):

  logger.info(f"\n")
  logger.info(f" ----> Start NUDT15 Analysis <---- ")
  logger.info(f" User Info: {user_info}")

  # 取得 config
  config = {
    "reagent": user_info.reagent,
    "organization": user_info.organization,
    "instrument": user_info.instrument,
    "NucleusVersion": NucleusVersion.NUDT15.value
  }

  # 初始化 NUDT15Output
  nudt15_output = NUDT15Output(config=config)

  # 決定 CT_Threshold
  if user_info.instrument == "z480":
    ct_threshold = CT_Threshold.Z480.value
  elif user_info.instrument == "qs3":
    ct_threshold = CT_Threshold.QS3.value
  else:
    raise ValueError(f"不支援的儀器: {user_info.instrument}")

  # 1. 讀取 Qpcr data 並轉換為 QPCRRecord 列表
  qpcr_record_list = readQPCRData(input_file_path, FAM_file_path, VIC_file_path, user_info.instrument, ct_threshold)

  # 紀錄 QPCRRecord 列表
  logger.info(f"[{user_info.instrument}] QPCR Raw data:")
  for r in qpcr_record_list:
    logger.info(f"{r}")

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
    logger.error(f"control_well {control_well} 不在 QPCRRecord 列表裡面")
    nudt15_output.qc_status = QCStatus.FAILED.value
    nudt15_output.errMsg = "control_well 不在 QPCRRecord 列表裡面"
    return nudt15_output.toJson()

  # 檢查 ntc_well 是否在 QPCRRecord 列表裡面
  if ntcWell not in [r.well_position for r in qpcr_record_list]:
    logger.error(f"ntc_well {ntc_well} 不在 QPCRRecord 列表裡面")
    nudt15_output.qc_status = QCStatus.FAILED.value
    nudt15_output.errMsg = "ntc_well 不在 QPCRRecord 列表裡面"
    return nudt15_output.toJson()

  # 解析 NUDT15Data 列表
  dataMatrix = parseNUDT15Data(qpcr_record_list, controlWell, ntcWell)

  # 更新 mthfr_output
  nudt15_output.controlData = dataMatrix["control"]
  nudt15_output.ntcData = dataMatrix["ntc"]
  nudt15_output.sampleDataList = dataMatrix["sample"]

  # QC
  qc_result = QC(dataMatrix)

  # 如果 QC 失敗, 則跳過 Sample Assessment
  if qc_result == QCStatus.FAILED:
    logger.warn(f"QC Failed, 跳過 Sample Assessment")
    nudt15_output.qc_status = QCStatus.FAILED.value
    nudt15_output.errMsg = "QC 失敗, 跳過 Sample Assessment"
    nudt15_output.resultList = []
    return nudt15_output.toJson()
  else:
    nudt15_output.qc_status = QCStatus.PASSED.value

  # 進行 Sample Assessment
  resultList = [SampleAssessment(sample, user_info.reagent) for sample in dataMatrix["sample"]]

  # 更新 nudt15_output
  nudt15_output.resultList = resultList

  logger.info(f"* NUDT15 Analysis Completed *")

  return nudt15_output.toJson()

# 處理 NUDT15Data 列表
def parseNUDT15Data(qpcr_record_list, controlWell, ntcWell):

  # 實體化 MTHFRData
  controlNUDT15Data = NUDT15Data(
    group="SC",
    sample_name=next((x.sample_name for x in qpcr_record_list if x.well_position == controlWell), None),
    well_position=next((x.well_position for x in qpcr_record_list if x.well_position == controlWell), None),
    wt=next((x for x in qpcr_record_list if x.well_position == controlWell and x.reporter == "VIC"), None),
    mut=next((x for x in qpcr_record_list if x.well_position == controlWell and x.reporter == "FAM"), None),
  )
  ntcNUDT15Data = NUDT15Data(
    group="NTC",
    sample_name=next((x.sample_name for x in qpcr_record_list if x.well_position == ntcWell), None),
    well_position=next((x.well_position for x in qpcr_record_list if x.well_position == ntcWell), None),
    wt=next((x for x in qpcr_record_list if x.well_position == ntcWell and x.reporter == "VIC"), None),
    mut=next((x for x in qpcr_record_list if x.well_position == ntcWell and x.reporter == "FAM"), None),
  )

  # 取得 qpcr_record_list 中 sample names
  sample_names = list(set([x.sample_name for x in qpcr_record_list if x.well_position != controlWell and x.well_position != ntcWell]))
  sampleNUDT15DataList = [NUDT15Data(
    group="Sample",
    sample_name=name,
    well_position=next((x.well_position for x in qpcr_record_list if x.sample_name == name), None),
    wt=next((x for x in qpcr_record_list if x.sample_name == name and x.reporter == "VIC"), None),
    mut=next((x for x in qpcr_record_list if x.sample_name == name and x.reporter == "FAM"), None),
  ) for name in sample_names]

  # 輸出 MTHFRData 列表
  logger.info(f"NUDT15Data:")
  logger.info(controlNUDT15Data)
  logger.info(ntcNUDT15Data)
  for data in sampleNUDT15DataList:
    logger.info(data)

  # DataMatrix
  dataMatrix = {
    "control": controlNUDT15Data,
    "ntc": ntcNUDT15Data,
    "sample": sampleNUDT15DataList
  }

  return dataMatrix

# QC
def QC(dataMatrix):

  # 初始化 qc_status
  qc_status = QCStatus.NOT_ANALYZED

  # 取得 controlData 和 NTCData
  controlData = dataMatrix["control"]
  NTCData = dataMatrix["ntc"]

  # Control 的 wt 和 mut 都不能為 None
  if not controlData.wt or not controlData.mut:
    logger.error(f"controlData 的 wt 或 mut 為 None")
    qc_status = QCStatus.FAILED
    return qc_status

  # NTC 的 wt 和 mut 都不能為 None
  if not NTCData.wt or not NTCData.mut:
    logger.error(f"NTCData 的 wt 或 mut 為 None")
    qc_status = QCStatus.FAILED
    return qc_status

  # QC 條件1: Control 的 wt 和 mut 都是 CT > 0
  condition1 = controlData.wt.ct_value > 0 and controlData.mut.ct_value > 0
  if not condition1:
    logger.warn(f"Failed QC: Control 的 wt 或 mut CT 值 < 0")

  # QC 條件2: NTC 的 wt 和 mut 都"不"通過 cutoff (CT > CT_Threshold 或 沒有數值)
  condition2 = not NTCData.wt.pass_cutoff and not NTCData.mut.pass_cutoff
  if not condition2:
    logger.warn(f"Failed QC: NTCData 的 wt 或 mut CT 值 pass cutoff")

  # QC 條件3: Control 的 wt 和 mut 的 CT 值相差不得超過 DELTA_CT_THRESHOLD
  condition3 = abs(controlData.wt.ct_value - controlData.mut.ct_value) <= CT_Threshold.DELTA_CT_THRESHOLD.value
  if not condition3:
    logger.warn(f"Failed QC: Control 的 wt 和 mut CT 值相差超過 {CT_Threshold.DELTA_CT_THRESHOLD.value}")

  if condition1 and condition2:
    qc_status = QCStatus.PASSED
  else:
    qc_status = QCStatus.FAILED

  return qc_status

# Sample Assessment
def SampleAssessment(SampleData, reagent):

  # 初始化 assessment
  assessment = AssessmentStatus.NOT_SET
  sample_qc_status = QCStatus.NOT_ANALYZED
  sample_type = []

  # 取得 SampleData 的 wt 和 mut
  wt = SampleData.wt
  mut = SampleData.mut

  # 若wt 和 mut都沒有 pass_cutoff, 則 assessment 為 INVALID
  if not wt.pass_cutoff and not mut.pass_cutoff:
    sample_qc_status = QCStatus.FAILED
    assessment = AssessmentStatus.INVALID
    return NUDT15Result(
      sample_name=SampleData.sample_name,
      reagent=reagent,
      assessment=assessment,
      sample_qc_status=sample_qc_status,
      sample_type=sample_type
    )

  # Low Risk: (wt +) 和 (mut -)
  if wt.pass_cutoff and not mut.pass_cutoff:
    assessment = AssessmentStatus.LOW_RISK
    sample_qc_status = QCStatus.PASSED
    sample_type = ["C", "C"]

  # High Risk1: (wt -) 和 (mut +)
  elif not wt.pass_cutoff and mut.pass_cutoff:
    assessment = AssessmentStatus.HIGH_RISK
    sample_qc_status = QCStatus.PASSED
    sample_type = ["T", "T"]

  # (wt +) 和 (mut +), CT 相差超過 DELTA_CT_THRESHOLD
  elif wt.pass_cutoff and mut.pass_cutoff :

    # High Risk2: CT 相差小於 DELTA_CT_THRESHOLD
    if abs(wt.ct_value - mut.ct_value) <= CT_Threshold.DELTA_CT_THRESHOLD.value:
      assessment = AssessmentStatus.HIGH_RISK
      sample_qc_status = QCStatus.PASSED
      sample_type = ["C", "T"]

    #
    else:

      # 如果 wt 的 CT 值大於 mut 的 CT 值, 則 assessment 為 HIGH_RISK
      if wt.ct_value > mut.ct_value:
        assessment = AssessmentStatus.HIGH_RISK
        sample_qc_status = QCStatus.PASSED
        sample_type = ["T", "T"]

      # 如果 wt 的 CT 值小於 mut 的 CT 值, 則 assessment 為 Low Risk
      else:
        assessment = AssessmentStatus.LOW_RISK
        sample_qc_status = QCStatus.PASSED
        sample_type = ["C", "C"]

  return NUDT15Result(
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
  parser.add_argument("--inputfile", "-i", required=False, type=str, help="輸入檔案路徑 (Excel 或 CSV), 若儀器為 qs3 必填")
  parser.add_argument("--FAMfile", "-f", required=False, type=str, help="FAM 檔案路徑 (Text), 若儀器為 z480 必填")
  parser.add_argument("--VICfile", "-v", required=False, type=str, help="VIC 檔案路徑 (Text), 若儀器為 z480 必填")
  parser.add_argument("--controlwell", "-c", required=True, type=str, help="控制 well 位置")
  parser.add_argument("--ntcwell", "-n", required=True, type=str, help="NTC well 位置")
  parser.add_argument("--reagent", required=True, type=str, choices=["accuinNUDT151", "accuinNUDT152"], help="試劑類型, 目前有 ['accuinNUDT151', 'accuinNUDT152'] (必填)")
  parser.add_argument("--instrument", required=True, type=str, choices=["qs3", "z480"], help="儀器類型, 目前有 ['qs3', 'z480'] (必填)")
  parser.add_argument("--organization", "-g", required=False, default="defaultOrg", type=str, help="組織所屬, NUDT15 不會用到可以不用設定")
  parser.add_argument("--output", "-o", required=False, type=str, help="輸出結果的 JSON 檔案路徑, 若不給定, 則輸出到 console")
  args = parser.parse_args()

  # 驗證 CLI 參數

  # 1. 驗證儀器類型, 若儀器為 qs3 必填 inputfile 參數
  if args.instrument == "qs3":

    # 驗證 inputfile 參數
    if not args.inputfile:
      raise ValueError("儀器為 qs3 時, 請提供 inputfile 參數")

    # 檢查檔案是否存在
    if not os.path.exists(args.inputfile):
      raise ValueError(f"inputfile 檔案不存在: {args.inputfile}")

    # 初步檢查副檔名
    if not (args.inputfile.endswith(".xlsx") or args.inputfile.endswith(".xls")):
      raise ValueError("inputfile 副檔名錯誤, 請提供 .xlsx 或 .xls 檔案")

    # 如果是 qs3, reagent 必須為 accuinNUDT151
    if args.instrument == "qs3" and args.reagent != "accuinNUDT151":
      raise ValueError("儀器為 qs3 時, reagent 必須為 accuinNUDT151")

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

    # 如果是 z480, reagent 必須為 accuinNUDT152
    if args.instrument == "z480" and args.reagent != "accuinNUDT152":
      raise ValueError("儀器為 z480 時, reagent 必須為 accuinNUDT152")

  return args

# Run NUDT15 CLI
if __name__ == "__main__":

    # 處理 CLI parameters
    args = parseParams()

    #
    input_file_path = args.inputfile
    FAM_file_path = args.FAMfile
    VIC_file_path = args.VICfile
    control_well = args.controlwell
    ntc_well = args.ntcwell
    reagent = args.reagent
    instrument = args.instrument
    user_info = UserInfo(
      instrument=args.instrument,
      reagent=args.reagent,
      organization=args.organization
    )

    # 執行 NUDT15
    nudt15_output = NUDT15(
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
        f.write(nudt15_output)
    else:
      print(nudt15_output)
