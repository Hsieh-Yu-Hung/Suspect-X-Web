// 導入會用到的功能
import { getAuth, createUserWithEmailAndPassword, signOut, onAuthStateChanged } from "firebase/auth";
import { GoogleAuthProvider, signInWithPopup } from "firebase/auth";
import { signInWithEmailAndPassword } from "firebase/auth";
import logger from "@/utility/logger";
import app from "./firebaseApp";

// 取得 auth
const auth = getAuth(app);

// 導出 auth
export const Auth = auth;

// 取得 provider
const provider = new GoogleAuthProvider();

// 控制登入狀態
let is_login = false;
let user_info = null;

// 建立註冊函式
export const create_User_Account = async (email, password) => {
  return await createUserWithEmailAndPassword(auth, email, password);
};

// 登入函式
export const signInWithEmail = async (email, password) => {
  return await signInWithEmailAndPassword(auth, email, password);
};

// Google 登入函式
export const signInWithGoogle = async () => {
  let exec_status = {status: 'pending', message: 'Unknown'};
  try {
    const result = await signInWithPopup(auth, provider);
    const userEmail = result.user.email;
    const userUID = result.user.uid;
    exec_status = {status: 'success', message: `Google login success`, user_email: userEmail, user_uid: userUID};
    logger.info(`Google login success, Email: ${userEmail}, UID: ${userUID}`);
  } catch (error) {
    exec_status = {status: 'error', message: `Google login failed, error: ${error}`, error_code: error.code};
    if (error.code === 'auth/popup-closed-by-user' || error.code === 'auth/cancelled-popup-request') {
      exec_status = {status: 'error', message: `Close popup Warning, Error message: ${error.message}`, error_code: error.code};
      logger.warn(`Close popup Warning, Error message: ${error.message}`);
    } else {
      exec_status = {status: 'error', message: `Google login failed, error: ${error}`, error_code: error.code};
      logger.error(`Google login failed, error: ${error}`);
    }
  }
  return exec_status;
};

// 取得登入狀態
export const get_login_status = () => {
  return {is_login: is_login, user_info: user_info};
}

// 登出
export const logout = async () => {
  try {
    await signOut(auth);
    is_login = false;
    user_info = null;
    return {status: 'success', message: `Logout success`};
  } catch (error) {
    return {status: 'error', message: `Logout failed, error: ${error}`};
  }
}

// 監聽登入狀態
onAuthStateChanged(auth, (user) => {
  if (user) {
    is_login = true;
    user_info = user;
  } else {
    is_login = false;
    user_info = null;
  }
});
