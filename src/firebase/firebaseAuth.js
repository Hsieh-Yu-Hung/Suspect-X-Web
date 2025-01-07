import app from "./firebaseApp";
import { getAuth, connectAuthEmulator, createUserWithEmailAndPassword } from "firebase/auth";
import { GoogleAuthProvider, signInWithPopup } from "firebase/auth";
import logger from "@/utility/logger";

// 取得 auth
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

// 如果是開發環境，則連接 auth emulator
if (process.env.VUE_APP_FILE_ENV === "development") {
  connectAuthEmulator(auth, "http://localhost:9099");
}

// 建立註冊函式
export const create_User_Account = (email, password) => {
  return createUserWithEmailAndPassword(auth, email, password);
};

// 登入函式
export const signInWithGoogle = async () => {
  try {
    const result = await signInWithPopup(auth, provider);
    const userEmail = result.user.email;
    const userUID = result.user.uid;
    logger.info(`Google login success, Email: ${userEmail}, UID: ${userUID}`);
  } catch (error) {
    logger.error(`Google login failed, error: ${error}`);
  }
};
