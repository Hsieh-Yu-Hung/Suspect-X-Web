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
from .smav4 import SMAv4
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
      nudt15_parsed_data = self.inputParser.parseInputObject(input_data, AnalysisName.NUDT15)
      user_info = self.inputParser.getUserInfo()
      nudt15_result = NUDT15(
        input_file_path = nudt15_parsed_data.input_file_path,
        FAM_file_path = nudt15_parsed_data.FAM_file_path,
        VIC_file_path = nudt15_parsed_data.VIC_file_path,
        control_well = nudt15_parsed_data.control_well,
        ntc_well = nudt15_parsed_data.ntc_well,
        user_info = user_info
      )
      return nudt15_result

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

      # SMA v4 分析
      if input_data['reagent'] == 'accuinSma4':
        sma_parsed_data = self.inputParser.parseInputObject(input_data, AnalysisName.SMAv4)
        user_info = self.inputParser.getUserInfo()
        sma_result = SMAv4(
          smn1_std1 = sma_parsed_data.smn1_std1,
          smn1_std2 = sma_parsed_data.smn1_std2,
          smn1_std3 = sma_parsed_data.smn1_std3,
          smn2_std1 = sma_parsed_data.smn2_std1,
          smn2_std2 = sma_parsed_data.smn2_std2,
          smn2_std3 = sma_parsed_data.smn2_std3,
          smn1_samples = sma_parsed_data.smn1_samples,
          smn2_samples = sma_parsed_data.smn2_samples,
          peak_condition = sma_parsed_data.peak_condition,
          user_info = user_info
        )

      # SMA v1-3 分析
      else:
        sma_parsed_data = self.inputParser.parseInputObject(input_data, AnalysisName.SMA)
        user_info = self.inputParser.getUserInfo()
        sma_versions = ['v1', 'v2', 'v3']
        sma_result = {}
        for sma_version in sma_versions:
          sma_result[sma_version] = SMA(
            input_file_path = sma_parsed_data.input_file_path,
            FAM_file_path = sma_parsed_data.FAM_file_path,
            VIC_file_path = sma_parsed_data.VIC_file_path,
            CY5_file_path = sma_parsed_data.CY5_file_path,
            SC1_well = sma_parsed_data.sc1_well,
            SC2_well = sma_parsed_data.sc2_well,
            NTC_well = sma_parsed_data.ntc_well,
            user_info = user_info,
            SMA_version = sma_version,
            parameters = sma_parsed_data.parameters
          )

      return sma_result
