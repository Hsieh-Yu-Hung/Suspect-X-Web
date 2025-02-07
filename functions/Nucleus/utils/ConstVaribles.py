# 引入套件
from dataclasses import asdict
from enum import Enum

# 分析資料存放路徑
PATH_OF_DATA = "data"

# 自定義序列化函數
def custom_serializer(obj):
  if isinstance(obj, (QCStatus, AssessmentStatus)):
      return obj.value
  elif hasattr(obj, '__dict__'):
      return asdict(obj)
  else:
      raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

# QC 狀態字串
class QCStatus(Enum):
  FAILED = 'fail-the-criteria'
  PASSED = 'meet-the-criteria'
  NOT_ANALYZED = 'not-analyzed'
# Assessment 狀態字串
class AssessmentStatus(Enum):
  INVALID = 'invalid'
  LOW_RISK = 'low-risk'
  NORMAL_RISK = 'normal-risk'
  HIGH_RISK = 'high-risk'

# Nucleus 版本號碼
class NucleusVersion(Enum):
  APOE = 'v3.4.3'
