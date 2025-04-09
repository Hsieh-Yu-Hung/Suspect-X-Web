/**
 * 控制開發環境啟動行為
 */

// 導入會用到的功能

// SDK functions
import { connectFunctionsEmulator } from "firebase/functions";
import { connectStorageEmulator } from "firebase/storage";
import { createUserWithEmailAndPassword, connectAuthEmulator } from "firebase/auth";
import { connectFirestoreEmulator } from "firebase/firestore";
import loggerV2 from "@/composables/loggerV2";

// SDK modules
import { Auth } from "./firebaseAuth";
import { Storage } from "./firebaseStorage";
import { Functions } from "./firebaseFunction";
import {
  Database, login_method, getData, addLoginInfoDatabase, addEmailListDatabase,
  USER_INFO, EMAIL_INFO, getSoftwareVersionDatabase, getOrganizationDatabase,
  addSoftwareVersionDatabase, addOrganizationDatabase, SOFTWARE_DATA, ORGAN_DATA,
  addTestingSample, getPermissionDatabase, addPermissionDatabase, PERMISSION,
  getRoleDatabase, addRoleDatabase, ROLE, ACTION
} from "./firebaseDatabase";

// 設定
import config from "../../config.js";

// 設定模擬用預設權限
const default_permission = [
  ACTION('enter_admin_page', '管理員頁面', true),
  ACTION('dev_mode', '開發者模式', true),
];

// 登入 admin
async function create_fake_user(email, password, admin=false) {

  // 取得 admin 的 email
  const is_email_exist = await getData("email_list", email).then(Response => {
    return Response.data;
  });

  // 如果 admin 的 email 不存在，則建立管理員帳號
  if (!is_email_exist) {
    await createUserWithEmailAndPassword(Auth, email, password)
    .then((result) => {
      // 將登入資訊加入到 database
      const id = result.user.uid;
      const LoginInfo = USER_INFO(result.user.email, login_method.admin, id);

      // 設定管理員權限
      if (admin) {
        LoginInfo.account_active = true;
        LoginInfo.role = 'admin';
        LoginInfo.organization = 'AdminOrg';
        LoginInfo.actions = default_permission;
      }
      else {
        LoginInfo.account_active = false;
        LoginInfo.role = 'user';
        LoginInfo.organization = 'not-set';
        LoginInfo.actions = [];
      }
      addLoginInfoDatabase(LoginInfo, id);

      // 將 email 加入到 email_list
      const EmailInfo = EMAIL_INFO(result.user.email, login_method.admin);
      addEmailListDatabase(EmailInfo);

      // 紀錄到 logger
      const message = `Admin login success, Email: ${result.user.email}, UID: ${result.user.uid}`;
      const source = 'onDevelopment.js line.34';
      const user = 'admin';
      loggerV2.info(message, source, user);
    })
    .catch((error) => {
      if (error.code === 'auth/email-already-in-use') {
        console.warn(` Admin is already exist, Skip ...`);
      } else {
        console.error(` Admin login failed, Error: ${error}`);
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
    await addSoftwareVersionDatabase(SOFTWARE_DATA('AdminSoftware', 'N/A', '管理員用', 'Admin', false));
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
    await addOrganizationDatabase(ORGAN_DATA('AdminOrg', 'AdminSoftware', 'N/A', 'Admin', false, default_permission));
    await addOrganizationDatabase(ORGAN_DATA('organ1', 'soft1', '2077-02-30'));
    await addOrganizationDatabase(ORGAN_DATA('organ2', 'soft2', '2077-02-30'));
    await addOrganizationDatabase(ORGAN_DATA('organ3', 'soft3', '2077-02-30'));
  }
}

// 開發環境時，加入權限資料
async function dev_add_permission() {
  // 取得權限資料
  const permissions = await getPermissionDatabase();
  if (permissions.length === 0) {
    // 測試加入權限資料
    await addPermissionDatabase(PERMISSION(default_permission[0].action_name, default_permission[0].action_label, '能讓你進入管理員頁面的權限'));
    await addPermissionDatabase(PERMISSION(default_permission[1].action_name, default_permission[1].action_label, '能讓你啟動開發者模式的權限'));
  }
}

// 開發環境時，加入角色資料
async function dev_add_role() {
  // 取得角色資料
  const roles = await getRoleDatabase();
  if (roles.length === 0) {
    // 測試加入角色資料
    await addRoleDatabase(ROLE('admin', '管理員', '測試管理員, 可以進入管理員頁面, 可以管理後台', default_permission));
    await addRoleDatabase(ROLE('user', '使用者', '測試使用者, 可以使用分析功能, 無特殊功能', []));
  }
}

// 開發環境時，加入 Beta Thal 測試樣本
async function dev_add_beta_thal_testing_samples() {

  // 取得測試樣本設定
  const beta_thal_testing_sample = config.testing_samples.beta_thal;
  const hbb_mutant_testing_sample = config.testing_samples.hbb_mutant;
  const hbb_wild_type_testing_sample = config.testing_samples.hbb_wild_type;
  const sanger_low_signal_testing_sample = config.testing_samples.sanger_low_signal;
  const non_hbb_sanger_testing_sample = config.testing_samples.non_hbb_sanger;
  const non_hbb_highbg_testing_sample = config.testing_samples.non_hbb_highbg;

  // 加入到 firestore
  await addTestingSample(beta_thal_testing_sample, 'test_betaThal');
  await addTestingSample(hbb_mutant_testing_sample, 'test_hbb_mutant');
  await addTestingSample(hbb_wild_type_testing_sample, 'test_hbb_wild_type');
  await addTestingSample(sanger_low_signal_testing_sample, 'test_sanger_low_signal');
  await addTestingSample(non_hbb_sanger_testing_sample, 'test_non_hbb_sanger');
  await addTestingSample(non_hbb_highbg_testing_sample, 'test_non_hbb_highbg');
}

// 主程式
export default async function onDevelopment() {

  // 連接 emulator
  connectAuthEmulator(Auth, "http://localhost:9099");     // 連接 auth emulator
  connectStorageEmulator(Storage, "localhost", 9199);     // 連接 storage emulator
  connectFunctionsEmulator(Functions, 'localhost', 5001); // 連接 functions emulator
  connectFirestoreEmulator(Database, 'localhost', 8085);  // 連接 firestore emulator

  // 登入 fake users
  await create_fake_user('subject1@test.com', 'f12345678', false);
  await create_fake_user('subject2@test.com', 'f12345678', false);
  await create_fake_user('subject3@test.com', 'f12345678', false);

  // 登入 admin
  const admin_email = process.env.VUE_APP_ADMIN_ACCOUNT;
  const admin_password = process.env.VUE_APP_ADMIN_PASSWORD;
  await create_fake_user(admin_email, admin_password, true);

  // 開發環境時，加入軟體資料
  await dev_add_software_version();

  // 開發環境時，加入組織資料
  await dev_add_organization();

  // 開發環境時，加入權限資料
  await dev_add_permission();

  // 開發環境時，加入角色資料
  await dev_add_role();

  // 開發環境時，加入 Beta Thal 測試樣本
  await dev_add_beta_thal_testing_samples();
}

