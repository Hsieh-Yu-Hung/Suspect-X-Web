import app from "./firebaseApp";
import { getFunctions, httpsCallable } from "firebase/functions";

// 取得 functions
const functions = getFunctions(app, 'asia-east1');

// 導出 functions
export const Functions = functions;

// 呼叫 saveLoggers
const saveLoggers = httpsCallable(functions, 'saveLogs');

// 呼叫 uploadLogs
const uploadLogs = httpsCallable(functions, 'uploadLogs');

// 呼叫 checkFileFormat
const checkFileFormat = httpsCallable(functions, 'check_file_format');

// 呼叫 RunAnalysis
const RunAnalysis = httpsCallable(functions, 'RunAnalysis');

// 導出 saveLoggers
export {
  saveLoggers,
  checkFileFormat,
  RunAnalysis,
  uploadLogs,
};

