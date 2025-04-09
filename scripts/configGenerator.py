import os
import re
import json
import argparse
from dataclasses import dataclass
from enum import Enum

# 定義預設測試資料結構
DEFAULT_TEST_DATA_STRUCTURE = {
  "sample_list": []
}

# 定義預設資料庫路徑
DEFAULT_DB_PATH = "testing_data"

# 定義測試資料分類(資料庫路徑)
class TEST_DATA_TYPE(Enum):
  BETA_THAL = "thalassemia_test_data"

# 定義測試資料檔案
@dataclass
class FILE:
  file_name: str
  file_path: str

  def toDict(self):
    return {
        "file_name": self.file_name,
        "file_path": self.file_path
    }

# 定義測試資料樣本
@dataclass
class SAMPLE:
  index: int
  sample_name: str

# 定義 betaThal Sample
@dataclass
class BETA_THAL_SAMPLE(SAMPLE):
  sequencing_files: list[FILE]
  def toDict(self):
    return {
        "index": self.index,
        "sample_name": self.sample_name,
        "sequencing_files": [file.toDict() for file in self.sequencing_files]
    }

# 定義 config 生成器
class ConfigGenerator:

  # 套用預設設定
  def __init__(self):
    self.generated_config = DEFAULT_TEST_DATA_STRUCTURE
    self.default_database_path = DEFAULT_DB_PATH

  # 儲存 config 到 json 檔案
  def save_config(self, config_path: str):
    with open(config_path, "w") as f:
      json.dump(self.generated_config, f, indent=2)

  # 新增 betaThal Sample
  def add_beta_thal_sample(self, samples: list[list[str]], subClass: str = ''):
    for index, sample in enumerate(samples):
      sample_name = sample[0].split("-")[0]
      common_file_path = os.path.join(self.default_database_path, TEST_DATA_TYPE.BETA_THAL.value, subClass)
      sample_files = [FILE(file, os.path.join(common_file_path, file))for file in sample]
      if len(sample_files) < 2:
        print(f"Sample {sample_name}, Index = {index+1} 檔案不足 2 個, 請手動修正輸出 json 檔案!")
      newBetaThalSample = BETA_THAL_SAMPLE(index+1, sample_name, sample_files)
      self.generated_config["sample_list"].append(newBetaThalSample.toDict())

  # 新增其他種類 Sample
  # def ...

  # 新增 Sample
  def add_sample(self, sample_type: str, samples: list, subClass: str = ''):

    # 新增 betaThal Sample
    if sample_type == TEST_DATA_TYPE.BETA_THAL.value:
      self.add_beta_thal_sample(samples, subClass)

    # 新增其他種類 Sample
    # if sample_type == ...

    # 例外處理
    else:
      raise ValueError(f"不支援的測試資料分類：{sample_type}")

# 解析CLI參數
def arg_parser():

  # 接收CLI參數
  parser = argparse.ArgumentParser()
  parser.add_argument("-i", "--inputs", type=str, required=False, metavar="", help="輸入檔名, 多個檔名用「逗號」分隔, 組別用「分號」分隔, 將所有檔案加入 config")
  parser.add_argument("-d", "--directory", type=str, required=False, metavar="", help="輸入資料夾路徑, 確保同一組的檔案命名前綴相同, 前綴符號為「-」, 將資料夾內所有檔案加入 config")
  parser.add_argument("-p", "--pattern", type=str, required=False, metavar="", help="輸入檔案名稱的 pattern, 將符合 pattern 的檔案加入 config")
  parser.add_argument("-s", "--subClass", type=str, required=False, metavar="", default='', help="輸入測試資料子分類, 將子分類的 database 路徑加入 config")
  parser.add_argument("-t", "--type", type=str, required=True, metavar="", choices=TEST_DATA_TYPE, help=f"輸入測試資料分類, 目前選擇：{', '.join([type.value for type in TEST_DATA_TYPE])}")
  parser.add_argument("-o", "--output", type=str, required=True, metavar="", help="輸出 config 檔 (json)")
  args = parser.parse_args()

  # 檢查 type 是否存在
  if args.type not in TEST_DATA_TYPE:
    raise ValueError(f"請輸入正確的測試資料分類, 目前的選擇有：{', '.join([type.value for type in TEST_DATA_TYPE])}")

  # 若輸入檔名和資料夾路徑同時存在, 則拋出錯誤
  if args.inputs and args.directory:
    raise ValueError("請選擇一種模式, 輸入檔名用逗號隔開(-i name1,name2,...)或資料夾路徑(-d path)")

  # 若輸入檔名, 則將輸入檔名用逗號隔開
  elif args.inputs:
    processList = args.inputs.split(";")
    processList = [process.split(",") for process in processList]

  # 若輸入資料夾路徑, 則將資料夾內所有檔案加入 config
  elif args.directory:
    processList = os.listdir(args.directory)

    # 若輸入 pattern, 則將符合 pattern 的檔案加入 config
    if args.pattern:
      processList = [file for file in processList if (args.pattern in file)]

    # 分組
    uniqueList = list(set([process.split("-")[0] for process in processList]))
    collectList = []
    for name in uniqueList:
      collectList.append([file for file in processList if (re.match(f"^{name}-.*", file))])
      if len(collectList[-1]) == 0:
        raise ValueError(f"Sample {name}, 檔案檔名有誤, 請確定同一組檔案命名!前綴「-」以前的字串必須相同, 檔名必須包含「-」,只有一個檔案命名「-1」")
    processList = collectList

  # 例外處理
  else:
    raise ValueError("請至少提供一種輸入方式, 輸入檔名用逗號隔開(-i name1,name2,...)或資料夾路徑(-d path)或檔案名稱的 pattern(-p pattern)")

  return {
    "type": args.type,
    "subClass": args.subClass,
    "inputs": processList,
    "output": args.output
  }

if __name__ == "__main__":

  # 初始化 ConfigGenerator
  configGenerator = ConfigGenerator()

  # 取得 Samples
  args = arg_parser()

  # 新增 Sample
  configGenerator.add_sample(args["type"], args["inputs"], args["subClass"])

  # 儲存 config
  configGenerator.save_config(args["output"])