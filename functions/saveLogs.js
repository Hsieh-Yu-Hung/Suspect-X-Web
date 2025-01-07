/* import module */
import moment from "moment";
import {createLogger, transports, format} from "winston";
import env from "./config_env.js";
import configAdmin from "./config_admin.js";

// 取得 currentEnv
const currentEnv = env.VUE_APP_FILE_ENV;

/* 如果 currentEnv 是 development 則連接到 Storage Emulator */
if (currentEnv === "development") {
  // 設定 Storage Emulator 的主機和端口
  process.env.FIREBASE_STORAGE_EMULATOR_HOST = "localhost:9199";
}

// 取得 bucket
const bucket = configAdmin.admin.storage().bucket();

// 存檔路徑
const logPath = "logs/";

// 取的當前時間
const timestamp = moment().format("YYYY-MM-DD HH:mm:ss");
const currentDate = moment().format("YYYY-MM-DD");

// 自訂 format 格式
const customFormat = format.printf(({level, message}) => {
  return `${timestamp} [${level.toUpperCase()}]: ${message}`;
});

// 創建 Logger Debug
const debugLogger = createLogger({
  level: "debug",
  format: customFormat,
  transports: [
    new transports.Console(),
    new transports.File({
      filename: `${logPath}running_debug_${currentDate}.log.txt`,
      format: customFormat,
    }), // 暫存檔案
    new transports.File({
      filename: `${logPath}running_debug_${currentDate}.log.json`,
      format: format.combine(format.timestamp(), format.json()),
    }), // 暫存檔案
  ],
});

// 建立 Logger Info
const infoLogger = createLogger({
  level: "info",
  format: format.combine(format.timestamp(), customFormat),
  transports: [
    new transports.Console(),
    new transports.File({
      filename: `${logPath}running_info_${currentDate}.log.txt`,
      level: "info",
    }), // 暫存檔案
    new transports.File({
      filename: `${logPath}running_info_${currentDate}.log.json`,
      format: format.combine(format.timestamp(), format.json()),
    }), // 暫存檔案
  ],
});

// 寫入日誌
const currentLogger = process.env.VUE_APP_FILE_ENV === "production" ?
 infoLogger : debugLogger;

// 上傳日誌檔案到 Storage Emulator
const uploadLogToEmulator = async () => {
  // 設定 log 檔案名稱, 預設為 debugLogger
  let logFiles = `${logPath}running_debug_${currentDate}.log.txt`;
  let logFilesJson = `${logPath}running_debug_${currentDate}.log.json`;

  // 設定 log 檔案名稱, 如果是 production 則使用 infoLogger
  if (process.env.VUE_APP_FILE_ENV === "production") {
    logFiles = `${logPath}running_info_${currentDate}.log.txt`;
    logFilesJson = `${logPath}running_info_${currentDate}.log.json`;
  }

  try {
    // 上傳日誌檔案到 Storage Emulator logs/
    await bucket.upload(logFiles, {destination: `${logFiles}`});
    await bucket.upload(logFilesJson, {destination: `${logFilesJson}`});
    return {"status": "success", "message": "日誌已成功上傳到 Storage"};
  } catch (error) {
    return {"status": "error", "message": error.message};
  }
};

/* 紀錄 logs 到檔案 */

// 紀錄 info logs
const info = (logs) => {
  currentLogger.info(logs);
  const message = uploadLogToEmulator(); // 上傳日誌到 Storage Emulator
  return message;
};

// 紀錄 debug logs
const debug = (logs) => {
  currentLogger.debug(logs);
  const message = uploadLogToEmulator(); // 上傳日誌到 Storage Emulator
  return message;
};

// 紀錄 error logs
const error = (logs) => {
  currentLogger.error(logs);
  const message = uploadLogToEmulator(); // 上傳日誌到 Storage Emulator
  return message;
};

// 紀錄 warn logs
const warn = (logs) => {
  currentLogger.warn(logs);
  const message = uploadLogToEmulator(); // 上傳日誌到 Storage Emulator
  return message;
};

// 包裝 saveLogger
const saveLogger = {
  info,
  debug,
  error,
  warn,
};

// 導出 saveLogger
export {saveLogger};
