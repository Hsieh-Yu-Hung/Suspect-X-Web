// Import firebase Storage SDK
import { uploadFileToStorage } from '@/firebase/firebaseStorage';

// logger
import logger from '@/utility/logger';

// 定義 category
const CATEGORY_LIST = {
  tmp: 'tmp',
  apoe_import: 'apoe_import',
  mthfr_import: 'mthfr_import',
}

export { CATEGORY_LIST };

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

    // 上傳檔案
    await uploadFileToStorage(file, upload_path).then((response) => {
      execute_result.status = response.status;
      execute_result.storage_path = response.storage_path;
      execute_result.message = response.message;
    });
  } else {
    execute_result.status = 'error';
    execute_result.message = `No file selected`;
  }

  // 取得檔案名稱
  const fileName = file ? file.name : '';

  // 印出 log
  logger.debug(`
    ${fileName} attempt to upload,
    status: ${execute_result.status},
    message: ${execute_result.message},
    storage_path: ${execute_result.storage_path}
    `);
  return execute_result;
}

