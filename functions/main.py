# This works, use it as a template
# @https_fn.on_request(region="asia-east1", cors=options.CorsOptions(cors_origins="*", cors_methods=["get", "post"]))
# def on_request_example(req: https_fn.Request):
#     response_data = {"data": {"message": "Hello world!"}}
#     return https_fn.Response(json.dumps(response_data), content_type="application/json")

# 引入 Firebase 函數庫
from firebase_functions import https_fn, options, scheduler_fn

# 引入自製模組
from config_admin import bucket
from saveLogs import Logger

# 引入 check_file_format
from check_FileFormat import FileFormatChecker
from check_FileFormat import ProductType

# 引入 Nucleus
from Nucleus import Core

# 其他
import json

# 保存日誌
@https_fn.on_request(region="asia-east1", cors=options.CorsOptions(cors_origins="*", cors_methods=["get", "post"]))
def saveLogs(req: https_fn.Request):

    # 回傳 message
    response_data = {"data": {"status": "pending", "message": "Waiting to save logs..."}}

    try:

      # 實體化 Logger
      logger = Logger(bucket)

      # 取得 input data
      input_data = json.loads(req.data.decode("utf-8"))["data"]
      message = input_data["message"]
      logType = input_data["logType"]

      # 紀錄日誌
      if logType == "debug":
          logger.debug(message)
      elif logType == "error":
          logger.error(message)
      elif logType == "warn":
          logger.warn(message)
      elif logType == "info":
          logger.info(message)

      # 回傳 message
      response_data = {"data": {"status": "success", "message": "Save logs!"}}

    except Exception as e:
        response_data = {"data": {"status": "error", "message": str(e)}}

    # 回傳 response
    return https_fn.Response(json.dumps(response_data), content_type="application/json")

# 上傳日誌：呼叫觸發
@https_fn.on_request(region="asia-east1", cors=options.CorsOptions(cors_origins="*", cors_methods=["get", "post"]))
def uploadLogs(req: https_fn.Request):

    # 回傳 message
    response_data = {"data": {"status": "pending", "message": "Waiting to upload logs..."}}

    try:

      # 實體化 Logger
      logger = Logger(bucket)

      # 上傳日誌
      logger.upload_logs_to_storage()

      # 回傳 message
      response_data = {"data": {"status": "success", "message": "Successfully upload logs!"}}

    except Exception as e:
        response_data = {"data": {"status": "error", "message": str(e)}}

    # 回傳 response
    return https_fn.Response(json.dumps(response_data), content_type="application/json")

# 上傳日誌：定時觸發
@scheduler_fn.on_schedule(region="asia-east1", schedule="every day 00:00", timezone="Asia/Taipei")
def ScheduleUploadLogs(event: scheduler_fn.ScheduledEvent) -> None:
    try:

      # 實體化 Logger
      logger = Logger(bucket)

      logger.debug("Schedule upload logs on schedule!")

      # 上傳日誌
      logger.upload_logs_to_storage()

      # 回傳 message
      print("Successfully upload logs on schedule!")

    except Exception as e:
        print("Failed to upload logs on schedule: " + str(e))

# 檢查 input 檔案格式
@https_fn.on_request(region="asia-east1", cors=options.CorsOptions(cors_origins="*", cors_methods=["get", "post"]))
def check_file_format(req: https_fn.Request):

    # 回傳 message
    response_data = {"data": {"status": "pending", "message": "Waiting to check file format..."}}

    # 初始化 file_format
    file_format = ''

    try:
        # 實體化 FileFormatChecker
        checker = FileFormatChecker(bucket)

        # 取得 input data
        input_data = json.loads(req.data.decode("utf-8"))["data"]

        # 決定要檢查的檔案格式和檔案路徑
        file_path = input_data["file_path"]
        file_format = input_data["file_type"]

        # 輸出
        check_result = False
        message = "Not Checked"
        check_status = 'not_executed'

        # 檢查檔案格式
        if file_format == ProductType.qsep100:
            check_result = checker.check_qsep100_format(file_path)
            check_status = checker.check_status
            message = checker.error_message
        elif file_format == ProductType.z480:
            check_result = checker.check_z480_format(file_path)
            check_status = checker.check_status
            message = checker.error_message
        elif file_format == ProductType.qs3:
            check_result = checker.check_qs3_format(file_path)
            check_status = checker.check_status
            message = checker.error_message
        elif file_format == ProductType.tower:
            check_result = checker.check_tower_format(file_path)
            check_status = checker.check_status
            message = checker.error_message

        # 如果沒有 error message, 則設定 message 為 "Check file format success"
        if message == "":
            message = "Check file format success"

        # 回傳 response
        response_data = {"data": {"status": "success", "check_type": file_format, "check_result": check_result, "message": message, "check_status": check_status}}

    except Exception as e:
        response_data = {"data": {"status": "error", "check_type": file_format, "message": str(e)}}

    # 回傳 response
    return https_fn.Response(json.dumps(response_data), content_type="application/json")

# 執行 Nucleus 分析
@https_fn.on_request(region="asia-east1", cors=options.CorsOptions(cors_origins="*", cors_methods=["get", "post"]))
def RunAnalysis(req: https_fn.Request):

    # 回傳 message
    response_data = {"data": {"status": "pending","message": "Waiting to start analysis..."}}

    # 開始跑分析
    try:

        # 實體化 Nucleus
        core = Core()

        # 取得 input data
        input_data = json.loads(req.data.decode("utf-8"))["data"]

        # 決定要跑哪一個分析和 input data
        analysis_name = input_data["analysis_name"]
        analysis_input_data = input_data["analysis_input_data"]

        # 初始化 result
        result = None

        # 跑分析
        if analysis_name == "APOE":
            result = core.runApoe(analysis_input_data)
        elif analysis_name == "MTHFR":
            result = core.runMthfr(analysis_input_data)
        elif analysis_name == "NUDT15":
            result = core.runNudt15(analysis_input_data)
        elif analysis_name == "FXS":
            result = core.runFxs(analysis_input_data)
        elif analysis_name == "HTD":
            result = core.runHtd(analysis_input_data)
        elif analysis_name == "SMA":
            result = core.runSma(analysis_input_data)

        # 回傳 response
        response_data = {"data": {"status": "success", "message": "Analysis finished", "result": result}}

    except Exception as e:
        response_data = {"data": {"status": "error", "message": str(e)}}

    return https_fn.Response(json.dumps(response_data), content_type="application/json")

