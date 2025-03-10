from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from config_admin import db

# 定義 Log 等級
class LOG_LEVEL(Enum):
  DEBUG = "debug"
  INFO = "info"
  WARN = "warn"
  ERROR = "error"
  ANALYSIS = "analysis"

# 定義 Log 資料物件
@dataclass
class Log:
  level: LOG_LEVEL
  timestamp: str
  sender: str
  message: str
  source: str

  def toData(self):
    return {
      "level": self.level.value,
      "timestamp": self.timestamp,
      "user": self.sender,
      "message": self.message,
      "source": self.source
    }

  def __str__(self):
    return f"[{self.level.value}] {self.timestamp} {self.message}"

# System Logger
class Logger:

  # 初始化
  def __init__(self, mode="online"):
    self.sender = "system"
    self.mode = mode

  # 設定 sender
  def setSender(self, sender):
    self.sender = sender

  # 取得當下時間，精確至毫秒
  def getCurrentTime(self):
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

  # 記錄 info 日誌
  def info(self, message, source="No specified."):
    log = Log(LOG_LEVEL.INFO, self.getCurrentTime(), self.sender, message, source)
    if self.mode == "online":
      db.collection("logs").add(log.toData())
    else:
      print(log)

  # 記錄 analysis 日誌
  def analysis(self, message, source="No specified."):
    log = Log(LOG_LEVEL.ANALYSIS, self.getCurrentTime(), self.sender, message, source)
    if self.mode == "online":
      db.collection("logs").add(log.toData())
    else:
      print(log)

  # 記錄 debug 日誌
  def debug(self, message, source="No specified."):
    log = Log(LOG_LEVEL.DEBUG, self.getCurrentTime(), self.sender, message, source)
    if self.mode == "online":
      db.collection("logs").add(log.toData())
    else:
      print(log)

  # 記錄 warn 日誌
  def warn(self, message, source="No specified."):
    log = Log(LOG_LEVEL.WARN, self.getCurrentTime(), self.sender, message, source)
    if self.mode == "online":
      db.collection("logs").add(log.toData())
    else:
      print(log)

  # 記錄 error 日誌
  def error(self, message, source="No specified."):
    log = Log(LOG_LEVEL.ERROR, self.getCurrentTime(), self.sender, message, source)
    if self.mode == "online":
      db.collection("logs").add(log.toData())
    else:
      print(log)
