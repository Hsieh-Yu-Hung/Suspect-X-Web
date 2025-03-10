import pandas as pd
from dataclasses import dataclass
import os
import warnings

# 產品種類
@dataclass
class ProductType:
  qsep100: str = 'qsep100'
  z480: str = 'z480'
  qs3: str = 'qs3'
  tower: str = 'tower'

# 檢查結果
@dataclass
class CheckStatus:
  not_checked: str = 'not_checked'
  fine: str = 'fine'
  problem: str = 'problem'

# Z480 Dye 種類
DYE_RANGES = [
  'FAM (465-510)',                    # FAM z480ii
  'VIC / HEX / Yellow555 (533-580)',  # VIC z480ii
  '465-510 (465-510)',                # FAM z480
  '540-580 (540-580)',                # VIC z480
  '610-670 (610-670)',                # CY5 z480
]

# 檢查 input 檔案格式
class FileFormatChecker:

    # 初始化
    def __init__(self):
      # 初始化 messages
      self.reset_messages()

    # 重置 messages
    def reset_messages(self):
      self.check_status = CheckStatus.not_checked
      self.error_message = ""

    # Check Excel and sheet name
    def checkExcel(self, file_path, target_sheet):
        try:
          # 讀取 Excel 檔案
          excel_file = pd.ExcelFile(file_path)

          # 檢查是否有目標頁籤
          if target_sheet not in excel_file.sheet_names:
              self.check_status = CheckStatus.problem
              self.error_message = f"\n 找不到頁籤：{target_sheet} \n 檔案：{os.path.basename(file_path)} \n"
              return False

          return True

        except Exception as e:
            self.check_status = CheckStatus.problem
            self.error_message = f"\n Excel 讀取失敗. \n 檔案：{os.path.basename(file_path)} \n 錯誤：{e}"
            return False

    # Check keyword
    def checkExcelKeyword(self, df, keyword):
        # 檢查關鍵字是否存在於 DataFrame 的任何值中
        return df.apply(lambda row: keyword in row.values, axis=1).any()

    # check qsep100 format
    def check_qsep100_format(self, file_path):

      # 目標頁籤
      target_sheet = "FolderReportMainPage"

      # 檢查 Excel 檔案
      excel_file_ok = self.checkExcel(file_path, target_sheet)

      # 如果 Excel 檔案格式錯誤，返回 False
      if not excel_file_ok:
          return False
      else:
          # 檢查內容, 抑制 openpyxl's default warning
          with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df = pd.read_excel(file_path, sheet_name=target_sheet)

          # Keyword to check
          keywords = ['No', 'bp', 'RFU']

          # 使用 Python 的 map 函數 檢查所有關鍵字
          check = map(lambda kw: self.checkExcelKeyword(df, kw), keywords)

          # 如果所有關鍵字都存在，返回 True
          if not all(check):
            self.check_status = CheckStatus.problem
            self.error_message = f"找不到其中一些關鍵字：{keywords} 檔案：{file_path}"
            return False
          else:
            self.check_status = CheckStatus.fine
            return True

    # check z480 format
    def check_z480_format(self, file_path):

      # 打開文字檔
      with open(file_path, 'r') as file:

        # 逐行讀取檔案內容
        lines = file.readlines()

      # 檢查是否有內容
      if not lines:
          self.check_status = CheckStatus.problem
          self.error_message = f"檔案內容為空：{file_path}"
          return False

      # 分離 DYE 資訊
      SPLITER = "Selected Filter: "

      # 預期欄位
      EXPECT_COLUMN = ['Include', 'Color', 'Pos', 'Name', 'Cp', 'Concentration', 'Standard', 'Status']

      # 檢查每一行
      for index, line in enumerate(lines):

        # 去除換行符號
        line = line.strip("\n")

        # 第一行
        if index == 0:
          # 檢查是否包含 DYE_RANGES 中的其中一個
          current_dye = line.split(SPLITER)[1].strip()
          if current_dye not in DYE_RANGES:
            self.check_status = CheckStatus.problem
            self.error_message = f"當前DYE：{current_dye} 不在預期之中：{DYE_RANGES} 檔案：{file_path}"
            return False

        # 第二行
        elif index == 1:
          # 與預期欄位取差集
          current_column = line.split("\t")
          diff_column = set(EXPECT_COLUMN) - set(current_column)
          if diff_column:
            self.check_status = CheckStatus.problem
            self.error_message = f"找不到其中一些欄位：{diff_column} 檔案：{file_path}"
            return False

        # 其他行
        else:
          # 比較當前和預期欄位數量
          current_column_count = len(line.split("\t"))
          expect_column_count = len(EXPECT_COLUMN)
          if current_column_count != expect_column_count:
            self.check_status = CheckStatus.problem
            self.error_message = f"第{index}行欄位數量：{current_column_count} 不在預期之中：{expect_column_count} 檔案：{file_path}"
            return False

        # 檢查完成,設定狀態
        self.check_status = CheckStatus.fine
        return True

    # check qs3 format
    def check_qs3_format(self, file_path):

      # 目標頁籤
      target_sheet = "Results"

      # 檢查 Excel 檔案
      excel_file_ok = self.checkExcel(file_path, target_sheet)

      # 如果 Excel 檔案格式錯誤，返回 False
      if not excel_file_ok:
        return False
      else:
        # 檢查內容, 抑制 openpyxl's default warning
        with warnings.catch_warnings():
          warnings.simplefilter("ignore")
          df = pd.read_excel(file_path, sheet_name=target_sheet)

        # Keyword to check
        keywords = ['Well Position', 'Sample Name', 'Reporter', 'Ct']

        # 使用 Python 的 map 函數 檢查所有關鍵字
        check = map(lambda kw: self.checkExcelKeyword(df, kw), keywords)

        # 如果所有關鍵字都存在，返回 True
        if not all(check):
          self.check_status = CheckStatus.problem
          self.error_message = f"找不到其中一些關鍵字：{keywords} 檔案：{file_path}"
          return False
        else:
          self.check_status = CheckStatus.fine
          return True

    # check tower format
    def check_tower_format(self, file_path):

      # 開啟文字檔
      ENCODING_1 = 'ISO-8859-1'
      ENCODING_2 = 'utf-8'

      # 嘗試以 ENCODING_1 讀取檔案
      try:
        with open(file_path, 'r', encoding=ENCODING_1) as file:
          lines = file.readlines()
      except Exception as e:
        # 如果讀取失敗，嘗試以 ENCODING_2 讀取檔案
        if isinstance(e, UnicodeDecodeError):
          with open(file_path, 'r', encoding=ENCODING_2) as file:
            lines = file.readlines()
        else:
          # 如果讀取失敗，回傳 False
          self.check_status = CheckStatus.not_checked
          self.error_message = f"讀取檔案失敗：{e}"
          return False

      # 檢查是否有內容
      if not lines:
        self.check_status = CheckStatus.problem
        self.error_message = f"檔案內容為空：{file_path}"
        return False

      # 分割符號
      SPLITER = ","

      # 預期欄位
      EXPECT_COLUMN = ['Well', 'Sample name', 'Dye', 'Ct']

      # Flag
      CHECK_PASS = False

      # 檢查每一行
      for line in lines:

        # 當前行
        current_line = line.split(SPLITER)

        # 尋找包含 EXPECT_COLUMN 的行
        if any(column in current_line for column in EXPECT_COLUMN):
          # 如果該行包含所有 EXPECT_COLUMN 回傳 True
          if all(column in current_line for column in EXPECT_COLUMN):
            self.reset_messages() # 重置messages
            self.check_status = CheckStatus.fine
            CHECK_PASS = True
            break
          else:
            missing_column = set(EXPECT_COLUMN) - set(current_line)
            self.reset_messages() # 重置messages
            self.check_status = CheckStatus.problem
            self.error_message = f"缺少欄位：{missing_column} 檔案：{file_path}"
            CHECK_PASS = False

      if not CHECK_PASS:
        if self.check_status == CheckStatus.not_checked:
          # 如果沒有找到, 回傳 False
          self.reset_messages() # 重置messages
          self.check_status = CheckStatus.problem
          self.error_message = f"找不到欄位所在的行：{EXPECT_COLUMN} 檔案：{file_path}"

      # 回傳檢查結果
      return CHECK_PASS
