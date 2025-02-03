# 導入個別分析腳本
from .apoe import APOE
from .mthfr import MTHFR

# Nucleus 控制核心
class Core:
    def __init__(self):
        self.msg = "Nucleus core"

    def runApoe(self, input_data):
        return APOE(input_data)

    def runMthfr(self, input_data):
        return MTHFR(input_data)

