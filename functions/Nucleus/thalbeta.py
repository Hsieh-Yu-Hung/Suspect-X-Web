import os
import sys
import requests
from dataclasses import dataclass
from utils.ConstVaribles import NucleusVersion, QCStatus
from utils.DataObject import AnalysisOutput

# 獲取當前腳本所在的目錄. 將上一層目錄添加到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)
sys.path.append(current_dir)

# 引入 saveLogs
from systemLogger import Logger
logger = Logger()

# Tracy API URL
TRACY_API_URL = "https://run-tracy-1055355904275.asia-east1.run.app/analyze"

# 定義 ThalBeta 輸出
@dataclass
class ThalBetaOutput(AnalysisOutput):
  input_file:str = None
  parameters:dict = None
  result:dict = None

# 執行 ThalBeta 分析
def ThalBeta(input_file_path, left_trim, right_trim, peak_ratio, user_info):

    # Logger settings
    sender = user_info.organization
    logger.setSender(sender)

    # Logger : Start Message
    tmp_source = "thalbeta.py line. 20"
    logger.analysis(f" ----> Start Beta Thalassemia Analysis <---- ", tmp_source)
    logger.analysis(f" User Info: {user_info}", tmp_source)

    # 取得 config
    config = {
      "reagent": user_info.reagent,
      "organization": user_info.organization,
      "instrument": user_info.instrument,
      "NucleusVersion": NucleusVersion.THAL_BETA.value
    }

    # Call Tracy API
    response = requests.post(
        TRACY_API_URL,
        json={
            "input_file": input_file_path,
            "left_trim": left_trim,
            "right_trim": right_trim,
            "peak_ratio": peak_ratio
        },
        headers={
            "Content-Type": "application/json"
        }
    )

    # Receive response
    if response.status_code == 200:
        # 取得分析結果
        result = response.json()
        thalbeta_output = ThalBetaOutput(
          input_file=result['inputs']['input_file'],
          parameters={
              'left_trim': result['inputs']['left_trim'],
              'right_trim': result['inputs']['right_trim'],
              'peak_ratio': result['inputs']['peak_ratio']
          },
          result=result['results'],
          config=config,
          qc_status=QCStatus.PASSED.value,
          errMsg=result['message']
        )
        return thalbeta_output.toJson()
    else:
        raise Exception(f"錯誤: {response.status_code}; {response.text}")