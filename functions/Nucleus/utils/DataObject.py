from dataclasses import dataclass, asdict
from .ConstVaribles import custom_serializer, QCStatus
import json
import pandas as pd

# 定義 Range (用於 peak 篩選)
@dataclass
class Range:
  MIN: float
  MAX: float

  # 定義乘法運算符
  def __mul__(self, other):
    if isinstance(other, Range):
      return Range(int(round(self.MIN * other.MIN, 0)), int(round(self.MAX * other.MAX, 0)))
    elif isinstance(other, (float, int)):
      return Range(int(round(self.MIN * other, 0)), int(round(self.MAX * other, 0)))
    else:
      raise TypeError("乘法運算只支援雙方都是 Range 類型, 或雙方都是數值")

  # 判斷是否在範圍內, 且 RFU 大於 RFU CutOff
  def inRange(self, bp, rfu_cutoff=0, rfu=None):
    if rfu is not None:
      return self.MIN <= float(bp) <= self.MAX and float(rfu) >= rfu_cutoff
    else:
      return self.MIN <= float(bp) <= self.MAX

  # 回傳可迭代對象中數值在 MIN 和 MAX 之間的索引值
  def withinRange(self, iterable, indices=False):

    # 如果 indices 為 True, 則回傳可迭代對象中數值在 MIN 和 MAX 之間的索引值
    if indices:

      # 處理字典
      if isinstance(iterable, dict):
        return [key for key, value in iterable.items() if self.MIN <= value <= self.MAX]

      # 處理列表
      elif isinstance(iterable, list):
        return [index for index, value in enumerate(iterable) if self.MIN <= value <= self.MAX]

      # 處理其他類型
      else:
        raise ValueError(f"尚未支援此類型：{type(iterable)}")

    # 如果 indices 為 False, 則回傳可迭代對象中數值在 MIN 和 MAX 之間的值
    else:

      # 處理字典
      if isinstance(iterable, dict):
        selected_dict = {}
        for key, value in iterable.items():
          if self.MIN <= value <= self.MAX:
            selected_dict[key] = value
        return selected_dict

      # 處理列表
      elif isinstance(iterable, list):
        return [value for value in iterable if self.MIN <= value <= self.MAX]

      # 處理其他類型
      else:
        raise ValueError(f"尚未支援此類型：{type(iterable)}")

# 定義 RFU Object
@dataclass
class RFUObj:
  peak_group: str
  rfu_value: float
  rfu_cutoff: float
  pass_cutoff: bool = True

  # 如果 rfu_value 小於 cutoff, 則將 pass_cutoff 設為 False
  def CutRFU(self):
    if self.rfu_value < self.rfu_cutoff:
      self.pass_cutoff = False

# 定義 Qsep100 Peak Object
@dataclass
class Qsep100Peak:
  peak_size: int
  peak_rfu: float

# 定義 Analysis Output Object
@dataclass
class AnalysisOutput:
  errMsg: str = ""
  config: dict = None
  qc_status: str = QCStatus.NOT_ANALYZED.value

  def __init__(self, config, qc_status):
    self.config = config
    self.qc_status = qc_status

  def toJson(self):
    analysis_output_dict = asdict(self)
    analysis_output_json = json.dumps(analysis_output_dict, default=custom_serializer, indent=4, ensure_ascii=False)
    return analysis_output_json

# 定義 QPCR well position object
@dataclass
class WELL:
  X: str
  Y: int

  def __init__(self, well):
    if isinstance(well, dict):
      self.parseDictWell(well)
    elif isinstance(well, str):
      self.parseSTRWell(well)
    else:
      raise ValueError(f"well 必須是字串或字典, 目前為 {type(well)}")

    # 檢查 X 是否在 A-H 之間
    if self.X not in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
      raise ValueError(f"X 必須是 A-H 之間的字母, 目前為 {self.X}")

    # 檢查 Y 是否在 1-12 之間
    if self.Y not in range(1, 13):
      raise ValueError(f"Y 必須是 1-12 之間的數字, 目前為 {self.Y}")

  def __str__(self):
    return f"{self.X}{self.Y}"

  def __eq__(self, other):
    return self.X == other.X and self.Y == other.Y

  # 處理字串 Well 參數
  def parseSTRWell(self, well_str):
    self.X = well_str[0]
    self.Y = int(well_str[1:])

  # 處理字典 Well 參數
  def parseDictWell(self, well_dict):
    self.X = well_dict['X']
    self.Y = int(well_dict['Y'])

# 定義 QPCR data Record Object
@dataclass
class QPCRRecord:
  well_position: WELL
  sample_name: str
  ct_value: float
  reporter: str
  ct_cutoff: float
  pass_cutoff: bool = False

  def __init__(self, well_position, sample_name, ct_value, reporter, ct_cutoff):
    self.well_position = well_position
    self.sample_name = sample_name
    self.ct_value = ct_value
    self.reporter = reporter
    self.ct_cutoff = ct_cutoff

    # 處理 ct = Undetermined 或 'No Ct' 或 'NaN'
    if ct_value == "Undetermined" or ct_value == "No Ct" or pd.isna(ct_value):
      self.ct_value = -1
      self.pass_cutoff = False
    else:
      self.ct_value = round(float(ct_value), 2)

      # z480 儀器 cutoff 為大於 0
      if self.ct_cutoff == 0:
        # 處理 ct_value 大於 ct_cutoff
        if self.ct_value > self.ct_cutoff:
          self.pass_cutoff = True

      # 其他儀器 cutoff 為小於 CT_Threshold
      else:
        # 處理 ct_value 小於 ct_cutoff
        if self.ct_value <= self.ct_cutoff:
          self.pass_cutoff = True

  def __str__(self):
    return f"QPCRRecord(well_position: {str(self.well_position)}, sample_name: {self.sample_name}, ct_value: {self.ct_value}, reporter: {self.reporter}, ct_cutoff: {self.ct_cutoff}, pass_cutoff: {self.pass_cutoff})"

# 定義 CallPeak 方法
def CallPeak(df: pd.DataFrame, search_range: Range, top_n: int = -1) -> list[Qsep100Peak]:

  # 篩選 BP 數值, 並轉換為整數; RFU 數值轉換為浮點數
  df = df[df['bp'].apply(lambda x: str(x).replace(',', '').isdigit())]
  df.loc[:, 'bp'] = df['bp'].str.replace(',', '').astype(int)
  df.loc[:, 'RFU'] = df['RFU'].astype(float)

  # 取得 BP 數值列表
  bpList = df['bp'].tolist()

  # 篩選 BP 數值在 STD_PEAK_RANGE 範圍內的 BP 數值
  selected_bp_indices = search_range.withinRange(bpList, indices=True)

  # 取得篩選後的 DataFrame, 依照 RFU 欄位排序, 取前 N 名
  if top_n > 0:
    selected_df = df.iloc[selected_bp_indices].sort_values(by='RFU', ascending=False).head(top_n)
  else:
    selected_df = df.iloc[selected_bp_indices].sort_values(by='RFU', ascending=False)

  # 轉換為 Qsep100Peak 列表
  selected_peaks = [
    Qsep100Peak(
      peak_size=row['bp'],
      peak_rfu=row['RFU']
    )
    for index, row in selected_df.iterrows()
  ]

  return selected_peaks
