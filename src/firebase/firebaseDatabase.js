// 導入會用到的功能
import { getFirestore } from "firebase/firestore";
import { collection, addDoc, setDoc, doc, getDocs, getDoc, deleteDoc } from "firebase/firestore";
import { v4 as uuidv4 } from 'uuid';
import loggerV2 from "@/composables/loggerV2";
import app from "./firebaseApp";
import moment from "moment";

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
  logs: 'logs',
  software_version_list: 'software_version_list',
  organization_list: 'organization_list',
  user_analysis: 'user_analysis',
};

// 定義 USER_INFO
export const USER_INFO = (email, login_method, id = null, organization = "not-set", role = "user", account_active = false) => {
  const created_at = new Date().toLocaleString();
  const updated_at = new Date().toLocaleString();
  return {
    id: id ? id : uuidv4(),
    email: email,
    organization: organization,
    role: role,
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

// 定義軟體資料
export const SOFTWARE_DATA = (new_name, new_version, new_note, id = null, editable = true) => {
  const software_id = id ? id : uuidv4();
  return {
    software_name: new_name,
    software_version: new_version,
    software_note: new_note,
    list_id: software_id,
    editable: editable
  }
}

// 定義組織資料
export const ORGAN_DATA = (name, software_select, member, date, id = null, editable = true) => {
  const organization_id = id ? id : uuidv4();
  return {
    organization_name: name,
    software_selection: software_select,
    member_count: member,
    join_date: date,
    organization_id: organization_id,
    editable: editable
  }
}

// 定義一個 log 資料結構
export const LOG_DATA = (id, log_level, log_message, log_time, log_source, log_user) => {
  return {
    id: id,
    level: log_level,
    message: log_message,
    time: log_time,
    source: log_source,
    user: log_user,
    display: true
  }
}

// 定義分析結果資料結構
export const ANALYSIS_RESULT = (analysis_name, analysis_id, config, control_ids, qc_status, qc_message, resultObj) => {
  const current_time = moment().format('YYYY-MM-DD HH:mm:ss');
  const analysisRes = {
    analysis_name: analysis_name,
    analysis_id: analysis_id,
    config: config,
    control_ids: control_ids,
    qc_status: qc_status,
    qc_message: qc_message,
    resultObj: resultObj,
    analysis_time: current_time
  }
  return analysisRes;
}

// 取得 firestore
const database = getFirestore(app);

// 導出 firestore
export const Database = database;

// 加入或更新現有資料
export const addData = async (dataset, data, uid = null) => {
  let exec_status = {status: 'pending', message: 'Unknown'};
  if (uid) {
    const docRef = doc(collection(database, dataset), uid);
    await setDoc(docRef, data)
    .then(() => {
      exec_status = {status: 'success', message: 'Edit document success, ID: ' + uid};
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

// 刪除指定資料
export const deleteData = async (dataset, uid) => {
  let exec_status = {'status': 'pending', 'message': 'Unknown'};
  const docRef = doc(collection(database, dataset), uid);
  await deleteDoc(docRef).then(() => {
    exec_status = {'status': 'success', 'message': 'Delete document success, ID: ' + uid};
  }).catch((error) => {
    exec_status = {'status': 'error', 'message': error};
  });
  return exec_status;
}

// 取得 email_list
export const getEmailList = async () => {
  let email_array = [];
  await getData(dataset_list.email_list)
  .then((result) => {
    if (result.status === 'success') {
      if (result.data) {
        result.data.forEach((email) => {
          email_array.push({email: email.email, login_method: email.login_method});
        });
      }
    } else {
      console.error(` Get email list failed, Error: ${result.message}`);
    }
  })
  .catch((error) => {
    console.error(` Get email list failed, Error: ${error}`);
  });
  return email_array;
}

// 將登入資訊加入到 database
export const addLoginInfoDatabase = async (LoginInfo, id) => {
  addData(dataset_list.user_info, LoginInfo, id).then((result) => {
    if (result.status === 'success') {
      const message = `成功加入登入資訊, Email: ${LoginInfo.email}`;
      const source = 'firebaseDatabase.js line.193';
      const user = 'admin';
      loggerV2.debug(message, source, user);
    } else if (result.status === 'error') {
      const message = `加入登入資訊失敗, Email: ${LoginInfo.email}, 原因: ${result.message}`;
      const source = 'firebaseDatabase.js line.200';
      const user = 'admin';
      loggerV2.error(message, source, user);
    }
  });
}

// 將 email 加入到 email_list
export const addEmailListDatabase = async (EmailInfo) => {
  addData(dataset_list.email_list, EmailInfo, EmailInfo.email).then((result) => {
    if (result.status === 'success') {
      const message = `成功加入 email 列表, Email: ${EmailInfo.email}, 登入方式: ${EmailInfo.login_method}`;
      const source = 'firebaseDatabase.js line.213';
      const user = 'admin';
      loggerV2.debug(message, source, user);
    } else if (result.status === 'error') {
      const message = `加入 email 列表失敗, Email: ${EmailInfo.email}, 原因: ${result.message}`;
      const source = 'firebaseDatabase.js line.220';
      const user = 'admin';
      loggerV2.error(message, source, user);
    }
  });
}

// 取得 firestore 軟體資料
export const getSoftwareVersionDatabase = async () => {
  let software_version_array = [];
  await getData(dataset_list.software_version_list)
  .then((result) => {
    if (result.status === 'success') {
      if (result.data) {
        result.data.forEach((software) => {
          software_version_array.push(software);
        });
      }
    } else {
      console.error(` Get software version failed, Error: ${result.message}`);
    }
  })
  .catch((error) => {
    console.error(` Get software version failed, Error: ${error}`);
  });
  return software_version_array;
}

// 將新軟體資料加入或更新到 firestore
export const addSoftwareVersionDatabase = async (SOFTWARE_DATA) => {
  addData(dataset_list.software_version_list, SOFTWARE_DATA, SOFTWARE_DATA.list_id).then((result) => {
    if (result.status === 'success') {
      const message = `成功更新軟體資料, 軟體 ID: ${SOFTWARE_DATA.list_id}`;
      const source = 'firebaseDatabase.js line.251';
      const user = 'admin';
      loggerV2.debug(message, source, user);
    } else if (result.status === 'error') {
      const message = `更新軟體資料失敗, 軟體 ID: ${SOFTWARE_DATA.list_id}, 原因: ${result.message}`;
      const source = 'firebaseDatabase.js line.258';
      const user = 'admin';
      loggerV2.error(message, source, user);
    }
  });
}

// 取得 firestore 組織資料
export const getOrganizationDatabase = async () => {
  let organization_array = [];
  await getData(dataset_list.organization_list)
  .then((result) => {
    if (result.status === 'success') {
      if (result.data) {
        result.data.forEach((organization) => {
          organization_array.push(organization);
        });
      }
    } else {
      console.error(` Get organization failed, Error: ${result.message}`);
    }
  })
  .catch((error) => {
    console.error(` Get organization failed, Error: ${error}`);
  });
  return organization_array;
}

// 從 firestore 載入組織資料 (Object)
export const load_organization_from_firestore = async (old_organization) => {
  // 取得組織列表
  const organizations = await getOrganizationDatabase();

  // 更新 display_organization
  organizations.forEach(organization => {
    if(!old_organization.find(item => item.organization_id === organization.organization_id)) {
      organization.editable = false;
      old_organization.push(organization);
    }
  });
}

// 從 firestore 載入軟體資料 (Object)
export const load_software_version_from_firestore = async (old_software_version) => {
  // 取得軟體版本列表
  const softwares = await getSoftwareVersionDatabase();

  // 更新 display_software_version
  softwares.forEach(software => {
    if(!old_software_version.find(item => item.list_id === software.list_id)) {
      software.editable = false;
      old_software_version.push(software);
    }
  });
}

// 從 firestore 載入使用者資料 (Object)
export const load_users_from_firestore = async (old_user_list) => {
  // 取得使用者資料
  const user_list = await getUsers_from_firestore();

  // 更新使用者資料列表
  user_list.forEach(user => {
    if (!old_user_list.value.find(item => item.id === user.id)) {
      old_user_list.value.push(user);
    }
  });
}

// 從 firestore 載入組織資料 (下拉式選單用)
export const load_organization_for_dropdown = async (old_organization_list, masked_organization_name=null) => {

  // 取得組織列表
  const new_organizations = await getOrganizationDatabase();

  // 移除組織列表中不存在的組織
  old_organization_list.forEach(organization => {
    if(!new_organizations.includes(organization)) {
      old_organization_list.splice(old_organization_list.indexOf(organization), 1);
    }
  });

  // 將組織列表加入到 old_organization
  if (masked_organization_name) {
    if (!old_organization_list.includes(masked_organization_name)) {
      old_organization_list.push(masked_organization_name);
    }
  }
  new_organizations.forEach(organization => {
    if (!old_organization_list.includes(organization.organization_name)) {
      old_organization_list.push(organization.organization_name);
    }
  });

  // 排序
  old_organization_list.sort((a, b) => {
    if (a === '全部') return -1;
    if (b === '全部') return 1;
    return a.localeCompare(b);
  });
}

// 從 firestore 載入軟體資料 (下拉式選單用)
export const load_software_version_for_dropdown = async (old_software_versions, masked_software_version_name=null) => {
  // 取得軟體版本列表
  const new_software_version = await getSoftwareVersionDatabase();

  // 移除軟體版本列表中不存在的軟體版本
  old_software_versions.forEach(version => {
    if(!new_software_version.includes(version)) {
      old_software_versions.splice(old_software_versions.indexOf(version), 1);
    }
  });

  // 載入新軟體版本列表
  if (masked_software_version_name) {
    if (!old_software_versions.includes(masked_software_version_name)) {
      old_software_versions.push(masked_software_version_name);
    }
  }
  new_software_version.forEach(version => {
    if(!old_software_versions.includes(version.software_name)) {
      old_software_versions.push(version.software_name);
    }
  });

  // 排序
  old_software_versions.sort((a, b) => {
    if (a === '全部') return -1;
    if (b === '全部') return 1;
    return a.localeCompare(b);
  });
}

// 將組織資料加入到 firestore
export const addOrganizationDatabase = async (ORGAN_DATA) => {
  addData(dataset_list.organization_list, ORGAN_DATA, ORGAN_DATA.organization_id).then((result) => {
    if (result.status === 'success') {
      const message = `成功更新組織資料, 組織 ID: ${ORGAN_DATA.organization_id}`;
      const source = 'firebaseDatabase.js line.395';
      const user = 'admin';
      loggerV2.debug(message, source, user);
    } else if (result.status === 'error') {
      const message = `更新組織資料失敗, 組織 ID: ${ORGAN_DATA.organization_id}, 原因: ${result.message}`;
      const source = 'firebaseDatabase.js line.402';
      const user = 'admin';
      loggerV2.error(message, source, user);
    }
  });
}

// 取得 firestore 使用者資料
export const getUsers_from_firestore = async (uid=null) => {
  // 如果沒有指定使用者 id，則取得所有使用者資料
  if (!uid) {
    let user_array = [];
    await getData(dataset_list.user_info)
    .then((result) => {
      if (result.status === 'success') {
        if (result.data) {
          result.data.forEach((user) => {
            user_array.push(user);
          });
        }
      } else {
        console.error(` Get users failed, Error: ${result.message}`);
      }
    })
    .catch((error) => {
      console.error(` Get users failed, Error: ${error}`);
    });
    return user_array;
  } else {
    // 如果指定使用者 id，則取得指定使用者資料
    let userData = null;
    await getData(dataset_list.user_info, uid)
    .then((result) => {
      if (result.status === 'success') {
        userData = result.data;
      } else {
        console.error(` Get user data failed, ID: ${uid}, Error: ${result.message}`);
      }
    }).catch((error) => {
      console.error(` Get user data failed, ID: ${uid}, Error: ${error}`);
    });
    return userData;
  }
}

// 更新使用者資料
export const update_userData = async (new_user_data, user_id) => {
  addData(dataset_list.user_info, new_user_data, user_id).then((result) => {
    if (result.status === 'success') {
      const message = `成功更新使用者資料, ID: ${user_id}`;
      const source = 'firebaseDatabase.js line.440';
      const user = 'admin';
      loggerV2.debug(message, source, user);
    } else if (result.status === 'error') {
      const message = `更新使用者資料失敗, ID: ${user_id}, 原因: ${result.message}`;
      const source = 'firebaseDatabase.js line.447';
      const user = 'admin';
      loggerV2.error(message, source, user);
    }
  }).catch((error) => {
    const message = `更新使用者資料失敗, ID: ${user_id}, 原因: ${error}`;
    const source = 'firebaseDatabase.js line.454';
    const user = 'admin';
    loggerV2.error(message, source, user);
  });
}

// 更新使用者分析資料
export const update_userAnalysisData = async (user_id, subDir, data, name) => {
  const dataset = dataset_list.user_analysis;
  const docRef = doc(collection(database, `${dataset}/${user_id}/${subDir}`), name);
  await setDoc(docRef, data)
  .then(() => {
    const message = `成功更新使用者分析資料, ID: ${user_id}/${subDir}`;
    const source = 'firebaseDatabase.js line.461';
    const user = 'admin';
    loggerV2.debug(message, source, user);
  })
  .catch((error) => {
    const message = `更新使用者分析資料失敗, ID: ${user_id}/${subDir}, 原因: ${error}`;
    const source = 'firebaseDatabase.js line.468';
    const user = 'admin';
    loggerV2.error(message, source, user);
  });
}

// 取得 database 中分析結果
export const getAnalysisResult = async (user_id, analysis_name, analysis_id) => {

  // 用 analysis_name 決定路徑名稱
  const get_db_path = (analysis_name) => {
    switch (analysis_name) {
      case 'APOE':
        return 'apoe_result';
      case 'FXS':
        return 'fxs_result';
      case 'SMA':
        return 'sma_result';
      case 'HTD':
        return 'htd_result';
      case 'MTHFR':
        return 'mthfr_result';
      case 'NUDT15':
        return 'nudt15_result';
      case 'SMAv4':
        return 'sma_v4_result';
      default:
        return analysis_name;
    }
  }

  const db_path = get_db_path(analysis_name);
  const doc_ref = doc(collection(database, `${dataset_list.user_analysis}/${user_id}/${db_path}`), analysis_id);
  const data = await getDoc(doc_ref).then((snapshot) => {
    return snapshot.data();
  }).catch((error) => {
    console.error(` Get analysis result failed, ID: ${analysis_id}, Error: ${error}`);
  });
  return data;
}

// 取得檔名並且移除附檔名
export const simplifyFilePath = (file_path) => {
  if (!file_path) return '';

  // 先取得檔案名稱（移除路徑）
  const fileName = file_path.split('/').pop();

  // 移除附檔名
  return fileName.replace(/\.[^.]+$/, '');
}
