/**
 * 控制開發環境啟動行為
 */

// 導入會用到的功能

// SDK functions
import { connectFunctionsEmulator } from "firebase/functions";
import { connectStorageEmulator } from "firebase/storage";
import { createUserWithEmailAndPassword, connectAuthEmulator } from "firebase/auth";
import { connectFirestoreEmulator } from "firebase/firestore";

// SDK modules
import { Auth } from "./firebaseAuth";
import { Storage } from "./firebaseStorage";
import { Functions } from "./firebaseFunction";
import {
  Database, login_method, getData, addLoginInfoDatabase, addEmailListDatabase,
  USER_INFO, EMAIL_INFO, getSoftwareVersionDatabase, getOrganizationDatabase,
  addSoftwareVersionDatabase, addOrganizationDatabase, SOFTWARE_DATA, ORGAN_DATA
} from "./firebaseDatabase";

// logger
import logger from "@/utility/logger";

// 登入 admin
async function login_admin() {

  // 取得 admin 的 帳戶資料
  const env_admin_email = process.env.VUE_APP_ADMIN_ACCOUNT;
  const env_admin_password = process.env.VUE_APP_ADMIN_PASSWORD;

  // 取得 admin 的 email
  const admin_email = await getData("email_list", env_admin_email).then(Response => {
    return Response.data;
  });

  // 如果 admin 的 email 不存在，則建立管理員帳號
  if (!admin_email) {
    await createUserWithEmailAndPassword(Auth, env_admin_email, env_admin_password)
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
}

// 開發環境時，加入軟體資料
async function dev_add_software_version() {
  // 取得軟體資料
  const softwares = await getSoftwareVersionDatabase();
  if (softwares.length === 0) {
    // 測試加入軟體資料
    await addSoftwareVersionDatabase(SOFTWARE_DATA('soft1', '1.0.0', '測試軟體備注 1', null, false));
    await addSoftwareVersionDatabase(SOFTWARE_DATA('soft2', '1.0.2', '測試軟體備注 2', null, false));
    await addSoftwareVersionDatabase(SOFTWARE_DATA('soft3', '1.0.3', '測試軟體備注 3', null, false));
  }
}

// 開發環境時，加入組織資料
async function dev_add_organization() {
  // 取得組織資料
  const organizations = await getOrganizationDatabase();
  if (organizations.length === 0) {
    // 測試加入組織資料
    await addOrganizationDatabase(ORGAN_DATA('organ1', 'soft1', '0', '2077-02-30', null, false));
    await addOrganizationDatabase(ORGAN_DATA('organ2', 'soft2', '0', '2077-02-30', null, false));
    await addOrganizationDatabase(ORGAN_DATA('organ3', 'soft3', '0', '2077-02-30', null, false));
  }
}

// 主程式
export default async function onDevelopment() {

  // 連接 emulator
  connectAuthEmulator(Auth, "http://localhost:9099");     // 連接 auth emulator
  connectStorageEmulator(Storage, "localhost", 9199);     // 連接 storage emulator
  connectFunctionsEmulator(Functions, 'localhost', 5001); // 連接 functions emulator
  connectFirestoreEmulator(Database, 'localhost', 8085);  // 連接 firestore emulator

  // 登入 admin
  await login_admin();

  // 開發環境時，加入軟體資料
  await dev_add_software_version();

  // 開發環境時，加入組織資料
  await dev_add_organization();
}

