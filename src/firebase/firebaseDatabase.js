// 引入 firebase
import app from "./firebaseApp";
import { getFirestore, connectFirestoreEmulator } from "firebase/firestore";
import { collection, addDoc, setDoc, doc, Timestamp, getDocs, getDoc } from "firebase/firestore";
import logger from "@/utility/logger";

// 定義登入方法
export const login_method = {
  email_password: 'Email_Password',
  google: 'Google',
  admin: 'Admin',
};

// 登記 datasets
export const dataset_list = {
  user_info: 'user_info',
  email_list: 'email_list',
};

// 定義 USER_INFO
export const USER_INFO = (email, id, login_method) => {
  const organization = "not-set";
  const role = "user";
  const auth_level = 0;
  const account_active = false;
  const created_at = Timestamp.now();
  const updated_at = Timestamp.now();
  return {
    id: id,
    email: email,
    organization: organization,
    role: role,
    auth_level: auth_level,
    account_active: account_active,
    created_at: created_at,
    updated_at: updated_at,
    login_method: login_method,
  };
};

// 定義 EMAIL_INFO
export const EMAIL_INFO = (email, login_method) => {
  return {
    email: email,
    login_method: login_method,
  };
};

// 取得 firestore
const database = getFirestore(app);

// 如果是開發環境，則連接 firestore emulator
if (process.env.VUE_APP_FILE_ENV === "development") {
  connectFirestoreEmulator(database, 'localhost', 8085);
}

// 加入資料
export const addData = async (dataset, data, uid = null) => {
  let exec_status = {status: 'pending', message: 'Unknown'};
  if (uid) {
    const docRef = doc(collection(database, dataset), uid);
    await setDoc(docRef, data)
    .then(() => {
      exec_status = {status: 'success', message: 'Add document success, ID: ' + uid};
    })
    .catch((error) => {
      exec_status = {status: 'error', message: error};
    });
  } else {
    // 新加入資料
    await addDoc(collection(database, dataset), data).then((docRef) => {
      exec_status = {status: 'success', message: 'Add document success, ID: ' + docRef.id};
    }).catch((error) => {
      exec_status = {status: 'error', message: error};
    });
  }
  return exec_status;
}

// 取得指定資料
export const getData = async (dataset, uid = null) => {
  let exec_status = {'status': 'pending', 'message': 'Unknown'};
  if (uid) {
    const docRef = doc(collection(database, dataset), uid);
    await getDoc(docRef).then((snapshot) => {
      exec_status = {'status': 'success', 'message': 'Get document success, ID: ' + uid, 'data': snapshot.data()};
    }).catch((error) => {
      exec_status = {'status': 'error', 'message': error};
    });
  } else {
    // 取得所有資料
    await getDocs(collection(database, dataset))
    .then((querySnapshot) => {
      const allData = [];
      querySnapshot.forEach((doc) => {
        allData.push({ id: doc.id, ...doc.data() });
      });
      exec_status = {'status': 'success', 'message': 'Get all documents success', 'data': allData};
    })
    .catch((error) => {
      exec_status = {'status': 'error', 'message': error};
    });
  }
  return exec_status;
}

// 將登入資訊加入到 database
export const addLoginInfoDatabase = async (LoginInfo, id) => {
  addData(dataset_list.user_info, LoginInfo, id).then((result) => {
    if (result.status === 'success') {
      logger.debug(`Add login info success, Email: ${LoginInfo.email}`);
    } else if (result.status === 'error') {
      logger.error(`Add login info failed, Email: ${LoginInfo.email}, Reason: ${result.message}`);
    }
  });
}

// 將 email 加入到 email_list
export const addEmailListDatabase = async (EmailInfo) => {
  addData(dataset_list.email_list, EmailInfo, EmailInfo.email).then((result) => {
    if (result.status === 'success') {
      logger.debug(`Add email list success, Email: ${EmailInfo.email}, Login Method: ${EmailInfo.login_method}`);
    }
  });
}
