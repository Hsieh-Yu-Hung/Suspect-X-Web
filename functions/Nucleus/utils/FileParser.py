# import modules
import pandas as pd
import os
import warnings
from dataclasses import dataclass

# 定義 Excel Cell 位置
@dataclass
class Cell:
  x: int
  y: int

# 定義 Qsep100 Object
@dataclass
class Qsep100:
  data: pd.DataFrame
  sample_id: str
  file_name: str = ''
  well: str = ''

# FileParser
class FileParser:

  # 初始化
  def __init__(self):

    # Qsep100 預期欄位
    self.Qsep100ExpectedColumns = [
      'No', 'Time\n(sec.)', 'RFU', 'PeakArea', 'bp',
      'Concn.\n(ng/µl)', 'PeakStart\n(sec.)', 'PeakEnd\n(sec.)'
    ]

  # 解析 Qsep100 檔案
  def parseQsep100File(self, file_path):

    # SampleID cell
    sample_id_cell = Cell(x=9, y=6)

    # Keyword of column header
    header_keywords = "No"

    # 讀取 Excel 檔案, 抑制 openpyxl's default warning
    with warnings.catch_warnings():
      warnings.simplefilter("ignore")
      df = pd.read_excel(file_path, engine='openpyxl')

    # 得到 SampleID
    sample_id = df.iloc[sample_id_cell.x, sample_id_cell.y]

    # 檔名, 不包含副檔名
    file_name = os.path.splitext(os.path.basename(file_path))[0]

    # 找出 header_keywords 所在的列位置
    header_row = df[df.apply(lambda x: x.astype(str).str.contains(header_keywords, case=False).any(), axis=1)].index[0]

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
