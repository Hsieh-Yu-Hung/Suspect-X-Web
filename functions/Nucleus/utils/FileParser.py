# import modules
import pandas as pd
import os
import warnings
from dataclasses import dataclass

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
    self.TowerFileSkipRows = 19
    self.TowerExpectedColumns = [
      "Well", "Sample name", "Sample type", "Dye", "Ct",
    ]

    # Z480 預期欄位和關鍵字
    self.FAM_RANGE_z480 = '465-510 (465-510)'
    self.FAM_RANGE_z480ii = 'FAM (465-510)'
    self.VIC_RANGE_z480 = '540-580 (540-580)'
    self.VIC_RANGE_z480ii = 'VIC / HEX / Yellow555 (533-580)'
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

    # Keyword of column header
    header_keywords = self.TowerExpectedColumns

    # 讀取 CSV 檔案
    df = pd.read_csv(file_path,sep=",",skiprows=self.TowerFileSkipRows)

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
  def parseZ480File(self, FAM_file_path, VIC_file_path):

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

    # 檢查 FAM 和 VIC 的 experiment_name 是否相同
    if fam_exp_name != vic_exp_name:
      raise ValueError("FAM 和 VIC 的 experiment_name 不同")

    # 合併 FAM 和 VIC 檔案
    df = pd.concat([FAM_df, VIC_df])

    # 檔名, 不包含副檔名
    file_name = ",".join([removeIllegalChars(os.path.splitext(os.path.basename(file_path))[0]) for file_path in [FAM_file_path, VIC_file_path]])
    experiment_name = fam_exp_name

    return FileDataObject(data=df, sample_id=experiment_name, file_name=file_name)
