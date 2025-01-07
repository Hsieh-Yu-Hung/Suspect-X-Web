import app from "./firebaseApp";
import { getStorage, connectStorageEmulator } from "firebase/storage";

const storage = getStorage(app);

// 如果是開發環境，則連接 storage emulator
if (process.env.VUE_APP_FILE_ENV === "development") {
  connectStorageEmulator(storage, "localhost", 9199);
}

export default storage;
