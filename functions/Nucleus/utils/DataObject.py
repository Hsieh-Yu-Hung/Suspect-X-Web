from dataclasses import dataclass, asdict
from .ConstVaribles import custom_serializer, QCStatus
import json
import pandas as pd

# 定義 Range (用於 peak 篩選)
@dataclass
class Range:
  MIN: int
  MAX: int

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
      return self.MIN <= int(bp) <= self.MAX and float(rfu) >= rfu_cutoff
    else:
      return self.MIN <= int(bp) <= self.MAX

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

  # 如果 rfu_value 小於 cutoff, 則將 peak_group 設為 "Cutoff"
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
