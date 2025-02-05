// 導入會用到的功能
import app from "./firebaseApp";
import { getStorage, ref, uploadBytesResumable, getDownloadURL, listAll } from "firebase/storage";

// 取得 storage
const storage = getStorage(app);

// 分析 Data 存放區
const PATH_OF_DATA = 'analysis_data';

// 上傳檔案到 Storage (接受 input 檔案, 放到使用者的 firebase storage 中)
export const uploadFileToStorage = async (file, upload_path) => {

  // 設定執行結果
  let execute_result = {status: 'pending', message: 'Waiting for upload', file: file.name, storage_path: ''};

  // 設定 storage_path
  const storage_path = `${PATH_OF_DATA}/${upload_path}`;
  execute_result.storage_path = storage_path; // 設定 storage_path回傳

  // 檢查檔案是否存在
  const file_exist = await checkFileExistInStorage(upload_path);
  if (file_exist) {
    execute_result.status = 'skipped';
    execute_result.message = `File already exists skip upload.`;
    return execute_result;
  }

  // 取得 storageRef
  const storageRef = ref(storage, storage_path);

  // 上傳檔案
  try {
    await uploadBytesResumable(storageRef, file).then(() => {
      execute_result.status = 'success';
      execute_result.message = 'Upload file to storage success';
    });
  } catch (error) {
    execute_result.status = 'error';
    execute_result.message = `Error: ${error}`;
    execute_result.storage_path = '';
  }
  return execute_result;
}

// 檢查 Storage 特定檔案是否存在
export const checkFileExistInStorage = async (target_path) => {
  try {
    const storageRef = ref(storage, `${PATH_OF_DATA}/${target_path}`);
    const exists = await getDownloadURL(storageRef);
    return exists;
  } catch (error) {
    if (error.code === 'storage/object-not-found') {
      return false;
    }

    throw error;
  }
}

// 檢查 Storage 特定資料夾是否存在,但資料夾不為空才會回傳 true
export const checkFolderExistInStorage = async (folder_path) => {
  const folderRef = ref(storage, `${PATH_OF_DATA}/${folder_path}`);
  try {
    const result = await listAll(folderRef);
    return result.items.length > 0 || result.prefixes.length > 0;
  } catch (error) {
    if (error.code === 'storage/object-not-found') {
      return false;
    }
    throw error;
  }
}

// 取得資料夾內的檔案列表
export const listAllFilesInFolder = async (folder_path) => {
  const folderRef = ref(storage, `${PATH_OF_DATA}/${folder_path}`);
  const result = await listAll(folderRef);
  return result.items;
}

// 導出 storage
export const Storage = storage;
