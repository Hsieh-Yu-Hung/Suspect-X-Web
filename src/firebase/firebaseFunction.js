import app from "./firebaseApp";
import { getFunctions, httpsCallable, connectFunctionsEmulator } from "firebase/functions";

// 取得 functions
const functions = getFunctions(app, 'asia-east1');

// 連接 functions emulator
connectFunctionsEmulator(functions, 'localhost', 5001);

// 呼叫 saveLoggers
const saveLoggers = httpsCallable(functions, 'saveLogs');

// 導出 saveLoggers
export {
  saveLoggers,
};

