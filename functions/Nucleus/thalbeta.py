import os
import sys
import requests
import json
from dataclasses import dataclass
from utils.ConstVaribles import NucleusVersion
from utils.DataObject import AnalysisOutput

# 獲取當前腳本所在的目錄. 將上一層目錄添加到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)
sys.path.append(current_dir)

# 引入 saveLogs
from systemLogger import Logger
logger = Logger()

# 預設欄位(應對沒有結果的狀況)
DEFAULT_RESULT = {
  "columns": ['ref', 'alt', 'type', 'genotype', 'adjusted_position', 'ClinicalSignificance', 'Name', 'VARIANT_CLASS', 'Consequence', 'PhenotypeList'],
  "rows": []
}

# Tracy API URL
TRACY_API_URL = "https://run-tracy-1055355904275.asia-east1.run.app/analyze"

# 定義 ThalBeta 輸出
@dataclass
class ThalBetaOutput(AnalysisOutput):
  sample_name:str = None
  input_file:str = None
  parameters:dict = None
  result:dict = None
  plot_peak_data:dict = None
  plot_basecall_data:dict = None
  alignment_score:dict = None

# 執行 ThalBeta 分析
def ThalBeta(sample_name, input_file_path, left_trim, right_trim, peak_ratio, user_info):

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

    # Log progress
    logger.analysis(f"Call Tracy API ...", tmp_source)

    # Call Tracy API
    response = requests.post(
        TRACY_API_URL,
        json={
          "sample_name": sample_name,
          "input_file": input_file_path,
          "left_trim": left_trim,
          "right_trim": right_trim,
          "peak_ratio": peak_ratio
        },
        headers={
            "Content-Type": "application/json"
        }
    )

    # Log progress
    tmp_source = "thalbeta.py line. 56"
    logger.analysis(f"Tracy API response: {response.status_code}", tmp_source)

    # 取得分析結果
    result = response.json()
    thalbeta_output = ThalBetaOutput(
      input_file=result['inputs']['input_file'],
      parameters={
          'left_trim': result['inputs']['left_trim'],
          'right_trim': result['inputs']['right_trim'],
          'peak_ratio': result['inputs']['peak_ratio']
      },
      sample_name=result['inputs']['sample_name'],
      result=result['results'] if result['results'] != {} else DEFAULT_RESULT,
      config=config,
      qc_status=result['qc_status'],
      errMsg=json.dumps(result['message']),
      plot_peak_data=result['plot_peak_data'],
      plot_basecall_data=result['plot_basecall_data'],
      alignment_score=result['align_score']
    )

    # Receive response
    if response.status_code == 200:
        tmp_source = "thalbeta.py line. 75"
        logger.analysis(f"Beta Thalassemia Analysis Finished Successfully.", tmp_source)
    else:
        tmp_source = "thalbeta.py line. 96"
        logger.analysis(f"Beta Thalassemia Analysis Failed. Please check the container logs.", tmp_source)

    # 回傳分析結果
    return thalbeta_output.toJson()