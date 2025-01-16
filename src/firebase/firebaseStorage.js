// 導入會用到的功能
import app from "./firebaseApp";
import { getStorage } from "firebase/storage";

// 取得 storage
const storage = getStorage(app);

// 導出 storage
export const Storage = storage;
