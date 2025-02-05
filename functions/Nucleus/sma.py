# 引入套件
import pandas as pd
import os

# 檔案存放資料夾路徑
PATH_OF_DATA = "data"

# SMA 分析腳本
def SMA(input_data):
  # 取得儀器
  instrument = input_data['instrument']

  # 取得試劑
  reagent = input_data['reagent']

  # 取得組織
  organization = input_data['organization']

  # 輸入檔案
  smn1_std1_file = os.path.join(PATH_OF_DATA, str(input_data['input_data']['file_path']['smn1_std1']))
  df = pd.read_excel(smn1_std1_file,skiprows=18)
  print("SMA", df)

  return "RUN SMA"

