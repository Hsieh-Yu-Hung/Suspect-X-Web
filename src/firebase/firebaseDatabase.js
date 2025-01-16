// 導入會用到的功能
import { getFirestore } from "firebase/firestore";
import { collection, addDoc, setDoc, doc, Timestamp, getDocs, getDoc, deleteDoc } from "firebase/firestore";
import { v4 as uuidv4 } from 'uuid';
import logger from "@/utility/logger";
import app from "./firebaseApp";


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
  software_version_list: 'software_version_list',
  organization_list: 'organization_list',
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
      logger.debug(`[Frontend] Get email list success`);
      if (result.data) {
        result.data.forEach((email) => {
          email_array.push({email: email.email, login_method: email.login_method});
        });
      }
    } else {
      logger.error(`[Frontend] Get email list failed, Error: ${result.message}`);
    }
  })
  .catch((error) => {
    logger.error(`[Frontend] Get email list failed, Error: ${error}`);
  });
  return email_array;
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

// 取得 firestore 軟體資料
export const getSoftwareVersionDatabase = async () => {
  let software_version_array = [];
  await getData(dataset_list.software_version_list)
  .then((result) => {
    if (result.status === 'success') {
      logger.debug(`Get software version success`);
      if (result.data) {
        result.data.forEach((software) => {
          software_version_array.push(software);
        });
      }
    } else {
      logger.error(`Get software version failed, Error: ${result.message}`);
    }
  })
  .catch((error) => {
    logger.error(`Get software version failed, Error: ${error}`);
  });
  return software_version_array;
}

// 將新軟體資料加入或更新到 firestore
export const addSoftwareVersionDatabase = async (SOFTWARE_DATA) => {
  addData(dataset_list.software_version_list, SOFTWARE_DATA, SOFTWARE_DATA.list_id).then((result) => {
    if (result.status === 'success') {
      logger.debug(`Update software version success, Software ID: ${SOFTWARE_DATA.list_id}`);
    }
  });
}

// 取得 firestore 組織資料
export const getOrganizationDatabase = async () => {
  let organization_array = [];
  await getData(dataset_list.organization_list)
  .then((result) => {
    if (result.status === 'success') {
      logger.debug(`Get organization success`);
      if (result.data) {
        result.data.forEach((organization) => {
          organization_array.push(organization);
        });
      }
    } else {
      logger.error(`Get organization failed, Error: ${result.message}`);
    }
  })
  .catch((error) => {
    logger.error(`Get organization failed, Error: ${error}`);
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

// 從 firestore 載入組織資料 (下拉式選單用)
export const load_organization_for_dropdown = async (old_organization_list) => {
  // 取得組織列表
  const organizations = await getOrganizationDatabase();

  // 移除組織列表中不存在的組織
  organizations.forEach(organization => {
    if(!old_organization_list.includes(organization.organization_name)) {
      old_organization_list.splice(old_organization_list.indexOf(organization.organization_name), 1);
    }
  });

  // 將組織列表加入到 old_organization
  organizations.forEach(organization => {
    old_organization_list.push(organization.organization_name);
  });
}

// 從 firestore 載入軟體資料 (下拉式選單用)
export const load_software_version_for_dropdown = async (old_software_versions) => {
  // 取得軟體版本列表
  const new_software_version = await getSoftwareVersionDatabase();

  // 移除軟體版本列表中不存在的軟體版本
  old_software_versions.forEach(version => {
    if(!new_software_version.find(item => item.software_name === version)) {
      old_software_versions.splice(old_software_versions.indexOf(version), 1);
    }
  });

  // 載入新軟體版本列表
  new_software_version.forEach(version => {
    if(!old_software_versions.includes(version.software_name)) {
      old_software_versions.push(version.software_name);
    }
  });
}

// 將組織資料加入到 firestore
export const addOrganizationDatabase = async (ORGAN_DATA) => {
  addData(dataset_list.organization_list, ORGAN_DATA, ORGAN_DATA.organization_id).then((result) => {
    if (result.status === 'success') {
      logger.debug(`Update organization success, Organization ID: ${ORGAN_DATA.organization_id}`);
    }
  });
}
