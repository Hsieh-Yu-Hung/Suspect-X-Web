# 導入個別分析腳本
from .apoe import APOE
from .mthfr import MTHFR
from .nudt15 import NUDT15
from .fxs import FXS
from .htd import HTD
from .sma import SMA
from utils.InputParser import InputParser

# 實體化 InputParser
inputParser = InputParser()

# Nucleus 控制核心
class Core:
    def __init__(self):
      pass

    # 執行 APOE 分析: 解析 APOE input 資料, 取得使用者資訊, 執行 APOE 分析並回傳結果
    def runApoe(self, input_data):
      apoe_parsed_data = inputParser.parseInputObject(input_data, 'APOE')
      user_info = inputParser.getUserInfo()
      apoe_result = APOE(
        control1_list = apoe_parsed_data.control1,
        control2_list = apoe_parsed_data.control2,
        samples_list = apoe_parsed_data.samples,
        user_info = user_info
      )
      return apoe_result

    def runMthfr(self, input_data):
      return MTHFR(input_data)

    def runNudt15(self, input_data):
      return NUDT15(input_data)

    def runFxs(self, input_data):
      return FXS(input_data)

    def runHtd(self, input_data):
      return HTD(input_data)

    def runSma(self, input_data):
      return SMA(input_data)

