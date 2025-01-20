import app from "./firebaseApp";
import { getFunctions, httpsCallable } from "firebase/functions";

// 取得 functions
const functions = getFunctions(app, 'asia-east1');

// 導出 functions
export const Functions = functions;

// 呼叫 saveLoggers
const saveLoggers = httpsCallable(functions, 'saveLogs');

// 導出 saveLoggers
export {
  saveLoggers,
};

