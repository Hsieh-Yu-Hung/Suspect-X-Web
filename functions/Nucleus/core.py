# 導入模組
import os
import sys

# 獲取當前腳本所在的目錄. 將上一層目錄添加到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)
sys.path.append(current_dir)

# 導入個別分析腳本
from .apoe import APOE
from .mthfr import MTHFR
from .nudt15 import NUDT15
from .fxs import FXS
from .htd import HTD
from .sma import SMA
from utils.InputParser import InputParser, AnalysisName

# Nucleus 控制核心
class Core:
    def __init__(self, bucket):
      self.bucket = bucket
      self.inputParser = InputParser(bucket)

    # 執行分析: 解析 input 資料, 取得使用者資訊, 分析並回傳結果

    # APOE 分析
    def runApoe(self, input_data):
      apoe_parsed_data = self.inputParser.parseInputObject(input_data, AnalysisName.APOE)
      user_info = self.inputParser.getUserInfo()
      apoe_result = APOE(
        control1_list = apoe_parsed_data.control1,
        control2_list = apoe_parsed_data.control2,
        samples_list = apoe_parsed_data.samples,
        user_info = user_info
      )
      return apoe_result

    # MTHFR 分析
    def runMthfr(self, input_data):
      mthfr_parsed_data = self.inputParser.parseInputObject(input_data, AnalysisName.MTHFR)
      user_info = self.inputParser.getUserInfo()
      mthfr_result = MTHFR(
        input_file_path = mthfr_parsed_data.input_file_path,
        FAM_file_path = mthfr_parsed_data.FAM_file_path,
        VIC_file_path = mthfr_parsed_data.VIC_file_path,
        control_well = mthfr_parsed_data.control_well,
        ntc_well = mthfr_parsed_data.ntc_well,
        user_info = user_info
      )
      return mthfr_result

    # NUDT15 分析
    def runNudt15(self, input_data):
      return NUDT15(input_data)

    # FXS 分析
    def runFxs(self, input_data):
      fxs_data = self.inputParser.parseInputObject(input_data, AnalysisName.FXS)
      user_info = self.inputParser.getUserInfo()
      fxs_result = FXS(
        control_file_path = fxs_data.control_file_path,
        samples_file_list = fxs_data.samples_file_list,
        user_info = user_info
      )
      return fxs_result

    # HTD 分析
    def runHtd(self, input_data):
      htd_data = self.inputParser.parseInputObject(input_data, AnalysisName.HTD)
      user_info = self.inputParser.getUserInfo()
      htd_result = HTD(
        control_file_path = htd_data.control_file_path,
        samples_file_list = htd_data.samples_file_list,
        user_info = user_info
      )
      return htd_result

    # SMA 分析
    def runSma(self, input_data):
      return SMA(input_data)

