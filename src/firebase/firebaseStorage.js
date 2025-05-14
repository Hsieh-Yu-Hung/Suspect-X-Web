// 導入會用到的功能
import app from "./firebaseApp";
import { getStorage, ref, uploadBytesResumable, getDownloadURL, listAll, deleteObject, getReference, getMetadata } from "firebase/storage";

// 取得 storage
const storage = getStorage(app);

// 分析 Data 存放區
const PATH_OF_DATA = 'analysis_data';
const PATH_OF_TEST_DATASET = 'testing_data';

// 上傳檔案到 Storage (接受 input 檔案, 放到使用者的 firebase storage 中)
export const uploadFileToStorage = async (file, upload_path, base=null, override=false) => {

  // 取得 base path
  const getBasePath = () => {
    switch (base) {
      case 'analysis':
        return PATH_OF_DATA;
      case 'test':
        return PATH_OF_TEST_DATASET;
      default:
        return PATH_OF_DATA;
    }
  }

  // 設定執行結果
  let execute_result = {status: 'pending', message: 'Waiting for upload', file: file.name, storage_path: ''};

  // 設定 storage_path
  const storage_path = `${getBasePath()}/${upload_path}`;
  execute_result.storage_path = storage_path; // 設定 storage_path回傳

  // 檢查檔案是否存在
  const file_exist = await checkFileExistInStorage(upload_path);
  if (file_exist) {
    if (!override) {
      execute_result.status = 'skipped';
      execute_result.message = `File already exists skip upload.`;
      return execute_result;
    }
    else {
      execute_result.status = 'Overwrite';
      execute_result.message = `File already exists, overwrite upload.`;
      // 若要覆寫則先刪除檔案
      await deleteFile(storage_path);
    }
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

// 取得路徑內資料夾列表
export const listAllFoldersInPath = async (path) => {
  const folderRef = ref(storage, `${PATH_OF_DATA}/${path}`);
  const result = await listAll(folderRef);
  return result.prefixes;
}

// 刪除資料夾內的檔案
export const deleteFile = async (file_path) => {
  // 設定執行結果
  let execute_result = {
    status: 'pending',
    message: 'Waiting for delete',
    file: file_path
  };

  try {
    // 取得檔案參考
    const fileRef = ref(storage, file_path);

    // 刪除檔案
    await deleteObject(fileRef);
    execute_result.status = 'success';
    execute_result.message = "Delete-file from storage success";

  } catch (error) {
    execute_result.status = 'error';
    execute_result.message = `Error: ${error}`;

    // 如果檔案不存在，回傳特別的訊息
    if (error.code === 'storage/object-not-found') {
      execute_result.message = 'File does not exist';
    }
  }

  return execute_result;
}

// 取得檔案 metadata
export const getFileMetadata = async (file_path) => {
  const fileRef = ref(storage, file_path);
  const metadata = await getMetadata(fileRef);
  return metadata;
}

// 取得下載連結
export const getFileDownloadURL = async (file_path) => {
  const fileRef = ref(storage, file_path);
  const url = await getDownloadURL(fileRef);
  return url;
}

// 導出 storage
export const Storage = storage;

// 導出 PATH_OF_DATA
export const getPATH_OF_DATA = () => {
  return PATH_OF_DATA;
}

// 刪除使用者分析檔案
export const deleteUserAnalysisFile = async (user_id, analysis_name, analysis_id) => {
  const folderPath = `${PATH_OF_DATA}/${user_id}/${analysis_name}/${analysis_id}`;
  const folderRef = ref(storage, folderPath);

  try {
    // 列出資料夾中的所有檔案
    const result = await listAll(folderRef);

    // 刪除所有檔案
    const deletePromises = result.items.map(item => deleteObject(item));
    await Promise.all(deletePromises);

    // 遞迴處理所有子資料夾
    const subFolderPromises = result.prefixes.map(async (prefix) => {
      const subResult = await listAll(prefix);
      const subDeletePromises = subResult.items.map(item => deleteObject(item));
      return Promise.all(subDeletePromises);
    });

    await Promise.all(subFolderPromises);
  } catch (error) {
    if (error.code !== 'storage/object-not-found') {
      throw error;
    }
  }
}
