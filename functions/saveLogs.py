# 引入模組
from datetime import datetime
import logging
import os

# 載入環境變數
from config_env import load_env
load_env()

# Log 存放位置
DEFAULT_LOCAL_LOG_DIR = "logs"
DEFAULT_REMOTE_LOG_DIR = "logs/"

# 自訂 format 格式
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
current_date = datetime.now().strftime("%Y-%m-%d")
log_file = os.path.join(DEFAULT_LOCAL_LOG_DIR, f"{current_date}.log")

# 如果 logs 資料夾不存在, 則建立
if not os.path.exists(DEFAULT_LOCAL_LOG_DIR):
    os.makedirs(DEFAULT_LOCAL_LOG_DIR)

# 取得運行環境, 設定日誌級別
current_env = os.getenv("VUE_APP_FILE_ENV")
if current_env == "development":
    logging.basicConfig(level=logging.DEBUG, filename=log_file, format='%(asctime)s - %(levelname)s - %(message)s')
elif current_env == "production":
    logging.basicConfig(level=logging.INFO, filename=log_file, format='%(asctime)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(level=logging.DEBUG, filename=log_file, format='%(asctime)s - %(levelname)s - %(message)s')

# 上傳日誌檔案到 Storage Emulator logs/
def upload_logs(bucket, log_dir: str = DEFAULT_LOCAL_LOG_DIR):
    logs = os.listdir(log_dir)
    for log in logs:
      local = os.path.join(log_dir, log)
      remote = os.path.join(DEFAULT_REMOTE_LOG_DIR, log)
      blob = bucket.blob(remote)
      blob.upload_from_filename(local)

class Logger:
    def __init__(self, bucket):
        self.bucket = bucket

    def info(self, message):
        logging.info(message)

    def debug(self, message):
        logging.debug(message)

    def error(self, message):
        logging.error(message)

    def warn(self, message):
        logging.warn(message)

    def upload_logs_to_storage(self):
        upload_logs(self.bucket)
