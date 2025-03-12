import os
import openpyxl
from datetime import datetime
from systemLogger import Logger
logger = Logger()

PATH_OF_DATA = 'data'

# 從 firebase Storage 取得檔案
def download_file_from_storage(bucket, file_path):

  msg_source = "subjectInfo.py line.10"
  logger.debug(f"Attempting to download file from storage: {file_path}", msg_source)

  # 取得下載目標 blob
  blob = bucket.blob(file_path)

  # 本地存放檔案路徑
  local_file_path = os.path.join(PATH_OF_DATA, file_path)

  # 如果本地存放檔案路徑不存在，則建立目錄
  if not os.path.exists(os.path.dirname(local_file_path)):
    logger.debug(f"Creating directory: {os.path.dirname(local_file_path)}", msg_source)
    os.makedirs(os.path.dirname(local_file_path))

  # 下載檔案
  if not os.path.exists(local_file_path):
    blob.download_to_filename(local_file_path)

  logger.debug(f"File downloaded successfully: {local_file_path}", msg_source)

  # 回傳本地存放檔案路徑
  return local_file_path

def parse_subject_info(subject_file):
    gender_defined = {
        "Female": "female",
        "Male": "male",
        "男": "male",
        "女": "female",
    }

    type_defined = {
        "Blood": "blood",
        "Chorionic villi": "chorionicVilli",
        "Amniotic fluid": "amnioticFluid",
        "Cord blood": "cordBlood",
        "DBS": "dbs",
        "Buccal swab": "buccalSwab",
        "FFPE": "ffpe",
        "FFPE + Blood": "ffpeBlood",
        "RNA": "rna",
        "Others": "others",
    }

    try:
        workbook = openpyxl.load_workbook(subject_file)
        worksheet = workbook['Subject Info']
    except Exception as e:
        print(f"Error reading file: {e}")
        raise

    subject_info = {}
    for idx, row in enumerate(worksheet.iter_rows(min_row=2, values_only=True), start=1):
        sample_id, name, birth, gender, id_number, type_, collecting_date, received_date = row

        subject_info[idx] = {
            "sampleId": sample_id,
            "name": str(name) if name else "",
            "birth": datetime.strftime(birth, "%Y/%m/%d") if birth else "",
            "gender": gender_defined.get(gender, "") if gender else "",
            "idNumber": str(id_number) if id_number else "",
            "type": type_defined.get(type_, "") if type_ else "",
            "collectingDate": datetime.strftime(collecting_date, "%Y/%m/%d") if collecting_date else "",
            "receivedDate": datetime.strftime(received_date, "%Y/%m/%d") if received_date else "",
        }

    return subject_info