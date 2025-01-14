# This works, use it as a template
# @https_fn.on_request(region="asia-east1", cors=options.CorsOptions(cors_origins="*", cors_methods=["get", "post"]))
# def on_request_example(req: https_fn.Request):
#     response_data = {"data": {"message": "Hello world!"}}
#     return https_fn.Response(json.dumps(response_data), content_type="application/json")

# 引入 Firebase 函數庫
from firebase_functions import https_fn, options
from config_admin import bucket

# 引入 saveLogs
from saveLogs import Logger

# 其他
import json

# 保存日誌
@https_fn.on_request(region="asia-east1", cors=options.CorsOptions(cors_origins="*", cors_methods=["get", "post"]))
def saveLogs(req: https_fn.Request):

    # 回傳 message
    response_data = {"status": "pending", "data": {"message": "Waiting to save logs..."}}

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
      response_data = {"status": "success", "data": {"message": "Save logs!"}}

    except Exception as e:
        response_data = {"status": "error", "data": {"message": str(e)}}

    # 回傳 response
    return https_fn.Response(json.dumps(response_data), content_type="application/json")
