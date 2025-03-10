# [On call] This works, use it as a template
# import https_fn, options
# @https_fn.on_request(region="asia-east1", cors=options.CorsOptions(cors_origins="*", cors_methods=["get", "post"]), memory=1024)
# def on_request_example(req: https_fn.Request):
#     response_data = {"data": {"message": "Hello world!"}}
#     return https_fn.Response(json.dumps(response_data), content_type="application/json")
#
# [On schedule] This works, use it as a template
# import scheduler_fn, options
# @scheduler_fn.on_schedule(region="asia-east1", schedule="every day 00:00", timezone="Asia/Taipei", memory=512)
# def ScheduleUploadLogs(event: scheduler_fn.ScheduledEvent) -> None:
#     print("Do something on schedule!")


# 導入模組
import json
from firebase_functions import https_fn, options
from config_admin import bucket
from Nucleus import Core
import traceback

# 載入環境變數
from config_env import load_env
load_env()

# 執行 Nucleus 分析
@https_fn.on_request(region="asia-east1", cors=options.CorsOptions(cors_origins="*", cors_methods=["get", "post"]), memory=1024)
def RunAnalysis(req: https_fn.Request):

    # 回傳 message
    response_data = {"data": {"status": "pending","message": "Waiting to start analysis..."}}

    # 開始跑分析
    try:

        # 實體化 Nucleus
        core = Core(bucket)

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
        response_data = {"data": {"status": "error", "message": str(e) + " " + str(traceback.format_exc())}}

    return https_fn.Response(json.dumps(response_data), content_type="application/json")
