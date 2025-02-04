# 導入個別分析腳本
from .apoe import APOE
from .mthfr import MTHFR
from .nudt15 import NUDT15
from .fxs import FXS
from .htd import HTD

# Nucleus 控制核心
class Core:
    def __init__(self):
        self.msg = "Nucleus core"

    def runApoe(self, input_data):
        return APOE(input_data)

    def runMthfr(self, input_data):
        return MTHFR(input_data)

    def runNudt15(self, input_data):
        return NUDT15(input_data)

    def runFxs(self, input_data):
        return FXS(input_data)

    def runHtd(self, input_data):
        return HTD(input_data)
