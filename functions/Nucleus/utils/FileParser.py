# import modules
import pandas as pd
import os
import sys
import warnings
from dataclasses import dataclass
from .DataObject import WELL, QPCRRecord

# 獲取當前腳本所在的目錄. 將上一層目錄添加到 sys.path, 以及上上層目錄添加到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
parent_dir_parent = os.path.abspath(os.path.join(parent_dir, os.pardir))
sys.path.append(parent_dir_parent)
sys.path.append(parent_dir)
sys.path.append(current_dir)

# 引入 systemLogger
from systemLogger import Logger
logger = Logger()

# 定義非法字符列表
ILLEGAL_CHARS = ['/', '\\', '?', '%', '*', ':', '|', '"', '<', '>', '.', ',']

# 移除非法字符
def removeIllegalChars(string):
  for char in ILLEGAL_CHARS:
    string = string.replace(char, '-')
  return string

# 定義 Excel Cell 位置
@dataclass
class Cell:
  x: int
  y: int

# 定義資料物件
@dataclass
class FileDataObject:
  data: pd.DataFrame
  sample_id: str
  file_name: str

  def __str__(self):
    return f"FileDataObject(sample_id: {self.sample_id}, file_name: {self.file_name}, data:pandas.DataFrame({self.data.shape[0]}x{self.data.shape[1]}))"

# 定義 Qsep100 Object
@dataclass
class Qsep100(FileDataObject):
  well: str = ''

  def __str__(self):
    return f"Qsep100(well: {self.well}, {super().__str__()})"

# FileParser
class FileParser:

  # 初始化
  def __init__(self):

    # Qsep100 預期欄位
    self.Qsep100ExpectedColumns = [
      'No', 'Time\n(sec.)', 'RFU', 'PeakArea', 'bp',
      'Concn.\n(ng/µl)', 'PeakStart\n(sec.)', 'PeakEnd\n(sec.)'
    ]

    # Qs3 預期欄位
    self.Qs3ExpectedColumns = [
      "Well Position", "Sample Name", "Target Name", "CT", "Reporter",
    ]

    # Tower 預期欄位
    self.TowerExpectedColumns = [
      "Well", "Sample name", "Sample type", "Dye", "Ct",
    ]

    # Z480 預期欄位和關鍵字
    self.FAM_RANGE_z480 = '465-510 (465-510)'
    self.FAM_RANGE_z480ii = 'FAM (465-510)'
    self.VIC_RANGE_z480 = '540-580 (540-580)'
    self.VIC_RANGE_z480ii = 'VIC / HEX / Yellow555 (533-580)'
    self.CY5_RANGE_z480 = '610-670 (610-670)'
    self.Z480ExpectedColumns = ["Pos", "Name", "Cp"]

  # 解析 Qsep100 檔案
  def parseQsep100File(self, file_path):

    # SampleID cell
    sample_id_cell = Cell(x=9, y=6)

    # Keyword of column header
    header_keywords = ["No", "bp"]

    # 讀取 Excel 檔案, 抑制 openpyxl's default warning
    with warnings.catch_warnings():
      warnings.simplefilter("ignore")
      df = pd.read_excel(file_path, engine='openpyxl')

    # 檔名, 不包含副檔名
    file_name = removeIllegalChars(os.path.splitext(os.path.basename(file_path))[0])

    # 得到 SampleID
    sample_id = df.iloc[sample_id_cell.x, sample_id_cell.y]

    # 如果 SampleID 為空, 則使用檔名作為 SampleID
    if pd.isna(sample_id):
      sample_id = file_name
    else:
      sample_id = removeIllegalChars(sample_id)

    # 找出 header_keywords 所在的列位置
    header_row = df[df.apply(lambda x: any(keyword in x.astype(str).values for keyword in header_keywords), axis=1)].index[0]

    # 重新設定 header
    df.columns = df.iloc[header_row]
    df = df.iloc[header_row + 1:-1].reset_index(drop=True)

    # 刪除 Column 名稱為 Nan的欄位, 以及刪除所有為 Nan 的行
    df = df.dropna(axis=1, how='all')
    df = df.dropna(axis=0, how='all')

    # 檢查欄位是否符合預期
    if not set(df.columns) == set(self.Qsep100ExpectedColumns):
      raise ValueError("Qsep100 欄位不符合預期")

    return Qsep100(data=df, sample_id=sample_id, file_name=file_name)

  # 解析 qs3 檔案
  def parseQs3File(self, file_path):

    # Sheet name
    sheet_name = "Results"

    # Keyword of column header
    header_keywords = self.Qs3ExpectedColumns

    # 讀取 Excel 檔案, 抑制 openpyxl's default warning
    with warnings.catch_warnings():
      warnings.simplefilter("ignore")
      if file_path.endswith(".xls"):
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine='xlrd')
      else:
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')

    # 檔名, 不包含副檔名
    file_name = removeIllegalChars(os.path.splitext(os.path.basename(file_path))[0])

    # 找出 header_keywords 所在的列位置
    header_row = df[df.apply(lambda x: any(keyword in x.astype(str).values for keyword in header_keywords), axis=1)].index[0]

    # 重新設定 header
    df.columns = df.iloc[header_row]
    df = df.iloc[header_row + 1:].reset_index(drop=True)

    # 刪除 Column 名稱為 Nan的欄位, 以及刪除所有為 Nan 的行
    df = df.dropna(axis=1, how='all')
    df = df.dropna(axis=0, how='all')

    # 檢查欄位是否符合預期
    if not set(header_keywords).issubset(df.columns):
      raise ValueError("Qs3 欄位不符合預期")

    # 精簡欄位, 只選擇 header_keywords
    df = df[header_keywords]

    return FileDataObject(data=df, sample_id=file_name, file_name=file_name)

  # 解析 tower 檔案
  def parseTowerFile(self, file_path):

    # 讀取檔案, 找到包含所有 header_keywords 的行數
    def findHeaderRow(file_path, header_keywords, encoding):
        with open(file_path, "r", encoding=encoding) as file:
          count = 0
          for line in file:
            if all(keyword in line for keyword in header_keywords):
              return count
            count += 1

    # Keyword of column header
    header_keywords = self.TowerExpectedColumns


    # 讀取檔案, 找到包含所有 header_keywords 的行數
    try:
      header_row = findHeaderRow(file_path, header_keywords, "utf-8")
    except UnicodeDecodeError as e:
      tmp_source = "FileParser.py line. 186"
      logger.warn(f"Tower 檔以 utf-8 編碼讀取失敗, 嘗試使用 latin1 編碼", tmp_source)
      header_row = findHeaderRow(file_path, header_keywords, "latin1")

    # 讀取 CSV 檔案
    try:
      df = pd.read_csv(file_path,sep=",",skiprows=header_row)
    except UnicodeDecodeError as e:
      tmp_source = "FileParser.py line. 194"
      logger.warn(f"Tower 檔以 utf-8 編碼讀取失敗, 嘗試使用 latin1 編碼", tmp_source)
      df = pd.read_csv(file_path,sep=",",skiprows=header_row, encoding="latin1")

    # 檔名, 不包含副檔名
    file_name = removeIllegalChars(os.path.splitext(os.path.basename(file_path))[0])

    # 刪除 Column 名稱為 Nan的欄位, 以及刪除所有為 Nan 的行
    df = df.dropna(axis=1, how='all')
    df = df.dropna(axis=0, how='all')

    # 檢查欄位是否符合預期
    if not set(header_keywords).issubset(df.columns):
      raise ValueError("Tower 欄位不符合預期")

    # 精簡欄位, 只選擇 header_keywords
    df = df[header_keywords]

    return FileDataObject(data=df, sample_id=file_name, file_name=file_name)

  # 解析 z480 檔案
  def parseZ480File(self, FAM_file_path, VIC_file_path, CY5_file_path=None):

    def parser(file_path, reporter):

      # 讀取第一行
      with open(file_path, "r") as file:
        first_line = file.readline().strip("\n").replace("  ", ": ")
        file.close()

      # 分割第一行
      first_line_splited = first_line.split(": ")
      experiment_name = first_line_splited[1]
      selected_filter = first_line_splited[3]

      # 設定檢查關鍵字
      if reporter == "FAM":
        checkingRange = [self.FAM_RANGE_z480, self.FAM_RANGE_z480ii]
      elif reporter == "VIC":
        checkingRange = [self.VIC_RANGE_z480, self.VIC_RANGE_z480ii]
      elif reporter == "CY5":
        checkingRange = [self.CY5_RANGE_z480]
      else:
        raise ValueError(f"Z480 File Reporter 不符合預期: {reporter}")

      # 檢查 selected_filter 是否符合預期
      if selected_filter not in checkingRange:
        raise ValueError(f"Z480 File Selected Filter 不符合預期: {selected_filter}")

      # 讀取 FAM 檔案
      df = pd.read_csv(file_path,sep="\t",skiprows=1)

      # 檢查 FAM 檔案欄位是否符合預期
      if not set(self.Z480ExpectedColumns).issubset(df.columns):
        raise ValueError("Z480 檔案欄位不符合預期")

      # 精簡欄位, 只選擇 Z480ExpectedColumns
      df = df[self.Z480ExpectedColumns]

      # 新增欄位 Reporter = "FAM"; RunID = experiment_name
      df["Reporter"] = reporter

      return df, experiment_name

    # 讀取 FAM 檔案
    FAM_df, fam_exp_name = parser(FAM_file_path, "FAM")

    # 讀取 VIC 檔案
    VIC_df, vic_exp_name = parser(VIC_file_path, "VIC")

    # 讀取 CY5 檔案
    if CY5_file_path:
      CY5_df, cy5_exp_name = parser(CY5_file_path, "CY5")

    # 檢查 FAM 和 VIC 的 experiment_name 是否相同
    if fam_exp_name != vic_exp_name:
      raise ValueError("FAM 和 VIC 的 experiment_name 不同")

    # 如果 CY5_file_path 存在, 則檢查 FAM 和 CY5 的 experiment_name 是否相同
    if CY5_file_path:
      if fam_exp_name != cy5_exp_name and vic_exp_name != cy5_exp_name:
        raise ValueError("VIC, FAM 和 CY5 的 experiment_name 不同")

    # 合併 FAM 和 VIC 檔案
    df = pd.concat([FAM_df, VIC_df])

    # 如果 CY5_file_path 存在, 則合併 FAM 和 CY5 檔案
    if CY5_file_path:
      df = pd.concat([df, CY5_df])

    # 檔名, 不包含副檔名
    file_name = ",".join([removeIllegalChars(os.path.splitext(os.path.basename(file_path))[0]) for file_path in [FAM_file_path, VIC_file_path]])
    if CY5_file_path:
      file_name += f",{removeIllegalChars(os.path.splitext(os.path.basename(CY5_file_path))[0])}"
    experiment_name = fam_exp_name

    return FileDataObject(data=df, sample_id=experiment_name, file_name=file_name)

# 讀取 qPCR 檔案並轉換為 QPCRRecord 列表
def readQPCRData(input_file_path, FAM_file_path, VIC_file_path, instrument, CT_Threshold, CY5_file_path=None):

    # 實體化 FileParser
  file_parser = FileParser()

  # 初始化 qpcr_data
  qpcr_data = None
  qpcr_record_list = []

  # 以 instrument 決定要讀哪一種檔案
  if instrument == "qs3":

    # 解析 qs3 檔案
    qpcr_data = file_parser.parseQs3File(input_file_path)

    if not qpcr_data:
      tmp_source = "FileParser.py line. 309"
      logger.error(f"QPCR 資料解析失敗, 無法解析 qs3 檔案, 請檢查原始檔案", tmp_source)
      logger.error(f"input_file_path: {input_file_path}", tmp_source)
      raise ValueError("QPCR 資料解析失敗, 無法解析 qs3 檔案, 請檢查原始檔案")

    # 轉換 dataframe 為 QPCRRecord 列表
    for index, row in qpcr_data.data.iterrows():
      if pd.isna(row["Well Position"]): continue
      qpcr_record_list.append(QPCRRecord(
        well_position=WELL(row["Well Position"]),
        sample_name=row["Sample Name"],
        ct_value=row["CT"],
        ct_cutoff=CT_Threshold,
        reporter=row["Reporter"]
      ))

  elif instrument == "tower":

    # 解析 tower 檔案
    qpcr_data = file_parser.parseTowerFile(input_file_path)

    if not qpcr_data:
      tmp_source = "FileParser.py line. 330"
      logger.error(f"QPCR 資料解析失敗, 無法解析 tower 檔案, 請檢查原始檔案", tmp_source)
      logger.error(f"input_file_path: {input_file_path}", tmp_source)
      raise ValueError("QPCR 資料解析失敗, 無法解析 tower 檔案, 請檢查原始檔案")

    # 轉換 dataframe 為 QPCRRecord 列表
    for index, row in qpcr_data.data.iterrows():
      qpcr_record_list.append(QPCRRecord(
        well_position=WELL(row["Well"]),
        sample_name=row["Sample name"],
        ct_value=row["Ct"],
        ct_cutoff=CT_Threshold,
        reporter=row["Dye"]
      ))

  elif instrument == "z480":

    # 解析 z480 檔案
    qpcr_data = file_parser.parseZ480File(FAM_file_path, VIC_file_path, CY5_file_path)

    if not qpcr_data:
      tmp_source = "FileParser.py line. 351"
      logger.error(f"QPCR 資料解析失敗, 無法解析 z480 檔案, 請檢查原始檔案", tmp_source)
      logger.error(f"FAM_file_path: {FAM_file_path}", tmp_source)
      logger.error(f"VIC_file_path: {VIC_file_path}", tmp_source)
      logger.error(f"CY5_file_path: {CY5_file_path}", tmp_source)
      raise ValueError("QPCR 資料解析失敗, 無法解析 z480 檔案, 請檢查原始檔案")

    # 轉換 dataframe 為 QPCRRecord 列表
    for index, row in qpcr_data.data.iterrows():
      qpcr_record_list.append(QPCRRecord(
        well_position=WELL(row["Pos"]),
        sample_name=row["Name"],
        ct_value=row["Cp"],
        ct_cutoff=CT_Threshold,
        reporter=row["Reporter"]
      ))

  # 檢查 qpcr_data 是否為 None
  if len(qpcr_record_list) == 0:
    tmp_source = "FileParser.py line. 370"
    logger.error(f"QPCR 資料解析失敗沒有任何資料, 請檢查原始檔案", tmp_source)
    logger.error(f"input_file_path: {input_file_path}", tmp_source)
    logger.error(f"FAM_file_path: {FAM_file_path}", tmp_source)
    logger.error(f"VIC_file_path: {VIC_file_path}", tmp_source)
    logger.error(f"CY5_file_path: {CY5_file_path}", tmp_source)
    raise ValueError("QPCR 資料解析失敗, 請檢查原始檔案")

  return qpcr_record_list
