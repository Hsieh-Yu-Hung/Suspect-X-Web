# 處理環境變數
import os
from dotenv import load_dotenv

# 取得環境變數檔,載入環境變數
def load_env():
    ENV_PATH = str(os.getenv("ENV_PATH"))
    ENV_FILE = os.path.join("..", ENV_PATH)
    load_dotenv(ENV_FILE)
