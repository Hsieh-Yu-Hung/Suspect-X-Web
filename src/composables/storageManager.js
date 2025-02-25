// Import firebase Storage SDK
import { uploadFileToStorage } from '@/firebase/firebaseStorage';

// logger
import loggerV2 from '@/composables/loggerV2';

// 定義 category
const CATEGORY_LIST = {
  tmp: 'tmp',
  apoe_import: 'apoe_import',
  mthfr_import: 'mthfr_import',
  nudt15_import: 'nudt15_import',
  fx_import: 'fx_import',
  htd_import: 'htd_import',
  sma_import: 'sma_import',
}

export { CATEGORY_LIST };

// 定義一個輔助函數來處理上傳的重試邏輯
async function uploadWithRetry(file, upload_path, retries = 3, timeout = 5000) {
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      const response = await Promise.race([
        uploadFileToStorage(file, upload_path),
        new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout')), timeout))
      ]);
      return response;
    } catch (error) {
      if (attempt === retries) throw error;
      const message = `Upload attempt ${attempt} failed. Retrying...`;
      const source = 'storageManager.js line.29';
      const user = 'system';
      loggerV2.debug(message, source, user);
    }
  }
}

// 上傳檔案到 storage
export async function upload_files_to_storage(file, user_id=null, category=CATEGORY_LIST.tmp, analysis_uuid=null, sub_dir=null) {

  // 紀錄狀態
  let execute_result = {status: 'pending', message: 'Waiting for upload', file: '', storage_path: '', analysis_uuid: analysis_uuid};

  // 上傳檔案到 storage
  if (file) {

    // 如果沒有指定 user, 把檔案放到 tmp
    const tmp_path = 'tmp';

    // 如果沒有指定 user, 把檔案放到 tmp
    const userLayer = user_id ? user_id : tmp_path;
    const categoryLayer = category;
    const subDirLayer = sub_dir ? sub_dir : null;

    // 決定上傳路徑
    const upload_path = subDirLayer != null && analysis_uuid != null
      ? `${userLayer}/${categoryLayer}/${analysis_uuid}/${subDirLayer}/${file.name}`
      : analysis_uuid != null
        ? `${userLayer}/${categoryLayer}/${analysis_uuid}/${file.name}`
        : `${userLayer}/${categoryLayer}/${file.name}`;

    try {
      const response = await uploadWithRetry(file, upload_path);
      execute_result.status = response.status;
      execute_result.storage_path = response.storage_path;
      execute_result.message = response.message;
      execute_result.file = file.name;
    } catch (error) {
      execute_result.status = 'error';
      execute_result.message = error.message;
    }
  } else {
    execute_result.status = 'error';
    execute_result.message = `No file selected`;
  }

  // 取得檔案名稱
  const fileName = file ? file.name : '';

  // 印出 log
  const message = `
    ${fileName} attempt to upload,
    status: ${execute_result.status},
    message: ${execute_result.message},
    storage_path: ${execute_result.storage_path}
  `;
  const source = 'storageManager.js line.82';
  const user = 'system';
  loggerV2.debug(message, source, user);
  return execute_result;
}

