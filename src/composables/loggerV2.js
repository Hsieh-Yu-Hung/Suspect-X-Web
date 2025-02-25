// 使用 loglevel 作為前端日誌庫
import log from "loglevel";
import moment from "moment";

//
import { dataset_list, addData } from "@/firebase/firebaseDatabase";

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

// 格式化日誌消息
const front_formatMessage = (message, source) => {
  const formatDate = moment().format("YYYY-MM-DD HH:mm:ss");
  return `[${formatDate}] \n訊息: ${message} \n來源: ${source}`;
};

// 在前端印出
function print_at_console(level, message, source) {
  const log_message = front_formatMessage(message, source);
  if (level === 'info') {
    log.info(log_message);
  } else if (level === 'debug') {
    log.debug(log_message);
  } else if (level === 'warn') {
    log.warn(log_message);
  } else if (level === 'error') {
    log.error(log_message);
  }
}

// 紀錄到 firestore
async function record_to_firestore(level, message, source, user) {
  const formatDate = moment().format("YYYY-MM-DD HH:mm:ss");
  const data = {
    user: user,
    level: level,
    message: message,
    source: source,
    timestamp: formatDate,
  }
  const result = await addData(dataset_list.logs, data);
  if (result.status === 'error') {
    console.error('紀錄到 firestore 失敗', result.message);
  }
}

// 封裝前端 Logger
const frontendLogger = {
  info: async (message, source, user='admin') => {
    print_at_console('info', message, source);
    await record_to_firestore('info', message, source, user);
  },
  warn: async (message, source, user='admin') => {
    print_at_console('warn', message, source);
    await record_to_firestore('warn', message, source, user);
  },
  error: async (message, source, user='admin') => {
    print_at_console('error', message, source);
    await record_to_firestore('error', message, source, user);
  },
  debug: async (message, source, user='admin') => {
    print_at_console('debug', message, source);
    await record_to_firestore('debug', message, source, user);
  },
};

export default frontendLogger;
