# import modules
import os
from dataclasses import dataclass
from utils.ConstVaribles import PATH_OF_DATA
from utils.DataObject import WELL

# 預期 input 格式
DEFAULT_EXPECTED_INPUT_ITEMS = [ 'instrument', 'reagent', 'organization', 'input_data' ]

# 定義分析名稱
@dataclass
class AnalysisName:
  APOE = 'APOE'
  MTHFR = 'MTHFR'
  NUDT15 = 'NUDT15'
  FXS = 'FXS'
  HTD = 'HTD'
  SMA = 'SMA'

# 定義使用者資訊
@dataclass
class UserInfo:
  instrument: str
  reagent: str
  organization: str

  def __str__(self):
    return f"instrument: {self.instrument}, reagent: {self.reagent}, organization: {self.organization}"

# 定義 APOE input 資料格式
@dataclass
class APOEInputData:
  control1: list
  control2: list
  samples: dict

# 定義 FXS input 資料格式
@dataclass
class FXSInputData:
  control_file_path: str
  samples_file_list: list

# 定義 HTD input 資料格式
@dataclass
class HTDInputData:
  control_file_path: str
  samples_file_list: list

# 定義 MTHFR input 資料格式
@dataclass
class MTHFRInputData:
  input_file_path: str
  FAM_file_path: str
  VIC_file_path: str
  control_well: WELL
  ntc_well: WELL

# InputParser
class InputParser:

  # 初始化
  def __init__(self, bucket, expectedInputItems=[]):

    # 初始化 bucket
    self.bucket = bucket

    # 預期 input 格式
    if expectedInputItems:
      self.expectedInputItems = expectedInputItems
    else:
      self.expectedInputItems = DEFAULT_EXPECTED_INPUT_ITEMS

    # 初始化資料
    self.instrument = None
    self.reagent = None
    self.organization = None
    self.input_data = None

  # 從 firebase Storage 取得檔案
  def download_file_from_storage(self, file_path):

    # 取得下載目標 blob
    blob = self.bucket.blob(file_path)

    # 本地存放檔案路徑
    local_file_path = os.path.join(PATH_OF_DATA, file_path)

    # 如果本地存放檔案路徑不存在，則建立目錄
    if not os.path.exists(os.path.dirname(local_file_path)):
        os.makedirs(os.path.dirname(local_file_path))

    # 下載檔案
    if not os.path.exists(local_file_path):
      blob.download_to_filename(local_file_path)

    # 回傳本地存放檔案路徑
    return local_file_path

  # 檢查 input 預期格式
  def checkInputFormat(self, inputObject):
    return list(inputObject.keys()) == self.expectedInputItems

  # 解析 input 預期格式
  def parseInputObject(self, inputObject, analysisName):

    # 先檢查 input 格式
    if not self.checkInputFormat(inputObject):
      print(
        f"""
          Error: Input format is not correct, expected: {self.expectedInputItems}
          Input: {list(inputObject.keys())}
        """)
      return

    # 解析 input 格式
    self.instrument = inputObject['instrument']
    self.reagent = inputObject['reagent']
    self.organization = inputObject['organization']
    self.input_data = inputObject['input_data']

    # 根據分析名稱解析 input 資料
    if analysisName == AnalysisName.APOE:
      apoe_input_data = self.parseAPOEInputData(self.input_data)
      return apoe_input_data
    elif analysisName == AnalysisName.MTHFR:
      mthfr_input_data = self.parseMTHFRInputData(self.input_data)
      return mthfr_input_data
    elif analysisName == AnalysisName.NUDT15:
      nudt15_input_data = self.parseNUDT15InputData(self.input_data)
      return nudt15_input_data
    elif analysisName == AnalysisName.FXS:
      fxs_input_data = self.parseFXSInputData(self.input_data)
      return fxs_input_data
    elif analysisName == AnalysisName.HTD:
      htd_input_data = self.parseHTDInputData(self.input_data)
      return htd_input_data
    elif analysisName == AnalysisName.SMA:
      sma_input_data = self.parseSMAInputData(self.input_data)
      return sma_input_data

  # 使用者資訊
  def getUserInfo(self):
    return UserInfo(
      instrument=self.instrument,
      reagent=self.reagent,
      organization=self.organization
    )

  # 解析 APOE input 資料
  def parseAPOEInputData(self, apoe_input_data):
    # Controls
    control1_list = apoe_input_data['control1PathList']
    control2_list = apoe_input_data['control2PathList']

    # 下載 control 檔案
    for control_list in [control1_list, control2_list]:
      for control in control_list:
        self.download_file_from_storage(control)

    # 加上 PATH_OF_DATA
    control1_list = [os.path.join(PATH_OF_DATA, control) for control in control1_list]
    control2_list = [os.path.join(PATH_OF_DATA, control) for control in control2_list]

    # 下載 samples 檔案
    for sample in apoe_input_data['samplePathList']:
      for filePath in sample['filePathList']:
        self.download_file_from_storage(filePath)

    # Samples
    sample_list = {}
    for sample in apoe_input_data['samplePathList']:
      sample_list[sample['sampleId']] = [os.path.join(PATH_OF_DATA, filePath) for filePath in sample['filePathList']]

    return APOEInputData(
      control1=control1_list,
      control2=control2_list,
      samples=sample_list
    )

  # 解析 MTHFR input 資料
  def parseMTHFRInputData(self, mthfr_input_data):

    # 取得 input 檔案
    input_file = mthfr_input_data['file_path']
    FAM_file = mthfr_input_data['FAM_file_path']
    VIC_file = mthfr_input_data['VIC_file_path']

    # 下載 input 檔案
    for file in [input_file, FAM_file, VIC_file]:
      if file:
        self.download_file_from_storage(file)

    # 加上 PATH_OF_DATA
    if input_file:
      input_file = os.path.join(PATH_OF_DATA, input_file)
    if FAM_file:
      FAM_file = os.path.join(PATH_OF_DATA, FAM_file)
    if VIC_file:
      VIC_file = os.path.join(PATH_OF_DATA, VIC_file)

    # 取得 well 位置
    control_well = WELL(mthfr_input_data['control_well'][0])
    ntc_well = WELL(mthfr_input_data['ntc_well'])

    # 回傳 input 檔案路徑
    return MTHFRInputData(
      input_file_path = input_file,
      FAM_file_path = FAM_file,
      VIC_file_path = VIC_file,
      control_well = control_well,
      ntc_well = ntc_well
    )

  # 解析 NUDT15 input 資料
  def parseNUDT15InputData(self, nudt15_input_data):
    return []

  # 解析 FXS input 資料
  def parseFXSInputData(self, fxs_input_data):
    # Control
    control_file_path = fxs_input_data['controlPath']

    # 下載 control 檔案
    self.download_file_from_storage(control_file_path)

    # 加上 PATH_OF_DATA
    control_file_path = os.path.join(PATH_OF_DATA, control_file_path)

    # Samples,
    samples_file_list = fxs_input_data['samplePathList']

    # 下載 samples 檔案
    for sample in samples_file_list:
      self.download_file_from_storage(sample)

    # 加上 PATH_OF_DATA
    samples_file_list = [os.path.join(PATH_OF_DATA, sample) for sample in samples_file_list]

    return FXSInputData(
      control_file_path = control_file_path,
      samples_file_list = samples_file_list
    )

  # 解析 HTD input 資料
  def parseHTDInputData(self, htd_input_data):
    # Control, 加上 PATH_OF_DATA
    control_file_path = htd_input_data['controlPath']

    # 下載 control 檔案
    self.download_file_from_storage(control_file_path)

    # 加上 PATH_OF_DATA
    control_file_path = os.path.join(PATH_OF_DATA, control_file_path)

    # Samples, 加上 PATH_OF_DATA
    samples_file_list = htd_input_data['samplePathList']

    # 下載 samples 檔案
    for sample in samples_file_list:
      self.download_file_from_storage(sample)

    # 加上 PATH_OF_DATA
    samples_file_list = [os.path.join(PATH_OF_DATA, sample) for sample in samples_file_list]

    return HTDInputData(
      control_file_path = control_file_path,
      samples_file_list = samples_file_list
    )

  # 解析 SMA input 資料
  def parseSMAInputData(self, sma_input_data):
    return []
