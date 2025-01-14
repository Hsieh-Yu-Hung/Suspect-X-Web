import app from "./firebaseApp";
import { getAuth, connectAuthEmulator, createUserWithEmailAndPassword, onAuthStateChanged, signOut } from "firebase/auth";
import { GoogleAuthProvider, signInWithPopup } from "firebase/auth";
import { signInWithEmailAndPassword } from "firebase/auth";
import logger from "@/utility/logger";
import { USER_INFO, EMAIL_INFO, addLoginInfoDatabase, addEmailListDatabase } from "./firebaseDatabase";
import { login_method, getData } from "./firebaseDatabase";

// 取得 auth
const auth = getAuth(app);
const provider = new GoogleAuthProvider();
let is_login = false;
let user_info = null;

// 如果是開發環境，則連接 auth emulator
if (process.env.VUE_APP_FILE_ENV === "development") {

  // 取得 admin 的 email
  const env_admin_email = process.env.VUE_APP_ADMIN_ACCOUNT;
  const env_admin_password = process.env.VUE_APP_ADMIN_PASSWORD;

  // 連接 auth emulator
  connectAuthEmulator(auth, "http://localhost:9099");

  // 取得 admin 的 email
  const admin_email = await getData("email_list", env_admin_email).then(Response => {
    return Response.data;
  });
  // 如果 admin_email 不存在，則建立管理員帳號
  if (!admin_email) {
    login_admin(env_admin_email, env_admin_password);
  }
}

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

// 登入 admin
async function login_admin(admin_email, admin_password) {
  await createUserWithEmailAndPassword(auth, admin_email, admin_password)
  .then((result) => {
    // 將登入資訊加入到 database
    const id = result.user.uid;
    const LoginInfo = USER_INFO(result.user.email, id, login_method.admin);

    // 設定管理員權限
    LoginInfo.account_active = true;
    LoginInfo.auth_level = 999; // 設定 auth_level 為 999
    LoginInfo.role = 'admin';
    addLoginInfoDatabase(LoginInfo, id);

    // 將 email 加入到 email_list
    const EmailInfo = EMAIL_INFO(result.user.email, login_method.admin);
    addEmailListDatabase(EmailInfo);
    logger.info(`Admin login success, Email: ${result.user.email}, UID: ${result.user.uid}`);
  })
  .catch((error) => {
    if (error.code === 'auth/email-already-in-use') {
      logger.warn(`Admin login failed, error: ${error}`);
    } else {
      logger.error(`Admin login failed, error: ${error}`);
    }
  });
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
