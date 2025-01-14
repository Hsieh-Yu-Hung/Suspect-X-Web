// 使用 loglevel 作為前端日誌庫
import log from "loglevel";
import { saveLoggers } from "@/firebase";
import moment from "moment";

// 設置日誌等級（根據需求調整）
// trace: 最詳細的日誌，包含所有細節
// debug: 調試日誌，通常用於開發和調試
// info: 一般信息日誌，通常用於運行時的狀態和事件
// warn: 警告日誌，通常用於表示可能的問題或錯誤
// error: 錯誤日誌，通常用於表示嚴重的錯誤或異常

// 判斷運行環境 設置日誌等級
if (process.env.VUE_APP_FILE_ENV === "development") {
  log.setLevel("debug");
} else {
  log.setLevel("info");
}

// 格式化時間函數
const formatDate = moment().format("YYYY-MM-DD HH:mm:ss");

// 格式化日誌消息
const formatMessage = (message) => {
  return `${formatDate} ${message}`;
};

// 呼叫 saveLogs
async function call_saveLogs(logMsg, logType) {
  const input_data = {"message": logMsg, "logType": logType};
  const res = await saveLoggers(input_data).then((response) => {
    return response.data;
  });
  return res
}

// 封裝前端 Logger
const prefix = "[RUNNING MESSAGE] - ";
const frontendLogger = {
  info: async (message) => {
    log.info(formatMessage(`[Info] ${message}`));
    await call_saveLogs(`${prefix} ${message}`, "info"); // log 存入 firebase
  },
  warn: async (message) => {
    log.warn(formatMessage(`[Warn] ${message}`));
    await call_saveLogs(`${prefix} ${message}`, "warn"); // log 存入 firebase
  },
  error: async (message) => {
    log.error(formatMessage(`[Error] ${message}`));
    await call_saveLogs(`${prefix} ${message}`, "error"); // log 存入 firebase
  },
  debug: async (message) => {
    log.debug(formatMessage(`[Debug] ${message}`));
    await call_saveLogs(`${prefix} ${message}`, "debug"); // log 存入 firebase
  },
};

export default frontendLogger;
