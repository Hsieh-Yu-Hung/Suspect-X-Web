# 導入個別分析腳本
from .apoe import APOE

# Nucleus 控制核心
class Core:
    def __init__(self):
        self.msg = "Nucleus core"

    def runApoe(self, input_data):
        return APOE(input_data)
