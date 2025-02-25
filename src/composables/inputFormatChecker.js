// 導入 firebase function
import { checkFileFormat } from '@/firebase';

// logger
import loggerV2 from '@/composables/loggerV2';

// 呼叫 checkFileFormat
export async function useCheckFileFormat(file_path, file_type) {

  // 回傳結果
  let response = {status: 'pending', message: 'Waiting for upload', data: null};

  // 如果沒有選擇檔案, 則回傳 error
  if (!file_path) {
    response.status = 'error';
    response.message = 'No file selected';
    return response;
  }

  // 檢查檔案格式
  const input_data = {"file_path": file_path, "file_type": file_type};
  const res = await checkFileFormat(input_data).then((response) => {return response.data;});
  if (res.status === 'success' && res.check_result !== undefined) {
    response.status = 'success';
    response.message = res.message;
    response.data = {check_result: res.check_result, check_status: res.check_status, file_path: file_path, check_type: res.check_type};

    // 紀錄到 logger
    const message = `
      ${file_path} check file format,
      check_type: ${res.check_type},
      status: ${response.status},
      message: ${response.message},
      check_result: ${response.data.check_result},
      check_status: ${response.data.check_status}
    `;
    const source = 'inputFormatChecker.js line.23';
    const user = 'system';
    loggerV2.debug(message, source, user);
  } else if (res.status === 'error') {
    response.status = 'error';
    response.message = res.message;

    // 紀錄到 logger
    const message = `
      ${file_path} check file format,
      check_type: ${res.check_type},
      status: ${response.status},
      message: ${response.message}
    `;
    const source = 'inputFormatChecker.js line.40';
    const user = 'system';
    loggerV2.error(message, source, user);
  }
  return response;
}
