# 引入套件
from dataclasses import asdict
from enum import Enum

# 分析資料存放路徑
PATH_OF_DATA = "data"

# 自定義序列化函數
def custom_serializer(obj):
  if isinstance(obj, (QCStatus, AssessmentStatus, NucleusVersion, Gender)):
      return obj.value
  elif hasattr(obj, '__dict__'):
      return asdict(obj)
  else:
      raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

# 性別字串
class Gender(Enum):
  MALE = 'male'
  FEMALE = 'female'
  NOT_SET = 'not-set'

# QC 狀態字串
class QCStatus(Enum):
  FAILED = 'fail-the-criteria'
  PASSED = 'meet-the-criteria'
  NOT_ANALYZED = 'not-analyzed'

# Assessment 狀態字串
class AssessmentStatus(Enum):
  NOT_SET = 'not-set'
  INVALID = 'invalid'
  INCONCLUSIVE = 'inconclusive'
  NORMAL = 'normal'
  INTERMEDIATE = 'intermediate'
  PREMUTATION = 'premutation'
  FULL_MUTATION = 'full-mutation'
  REDUCED_PENETRANCE = 'reduced-penetrance'
  PENETRANCE = 'penetrance'
  FULL_PENETRANCE = 'full-penetrance'
  LOW_RISK = 'low-risk'
  NORMAL_RISK = 'normal-risk'
  HIGH_RISK = 'high-risk'

# Nucleus 版本號碼
class NucleusVersion(Enum):
  APOE = 'v3.4.3'
  FXS = 'v3.4.3'
  HTD = 'v3.4.3'
