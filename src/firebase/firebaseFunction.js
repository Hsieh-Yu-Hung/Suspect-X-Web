import app from "./firebaseApp";
import { getFunctions, httpsCallable } from "firebase/functions";

// 取得 functions
const functions = getFunctions(app, 'asia-east1');

// 導出 functions
export const Functions = functions;

// 呼叫 RunAnalysis
const RunAnalysis = httpsCallable(functions, 'RunAnalysis');

// 呼叫 ParseSubjectInfo
const ParseSubjectInfo = httpsCallable(functions, 'ParseSubjectInfo');

// 導出 functions
export {
  RunAnalysis,
  ParseSubjectInfo,
};

