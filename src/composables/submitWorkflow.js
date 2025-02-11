// Import functions
import { useCheckFileFormat } from '@/composables/inputFormatChecker';
import logger from '@/utility/logger';

// 導入 firebase function
import { RunAnalysis } from '@/firebase/firebaseFunction';

// 由 AnalysisName 決定 check_type
function getCheckType(AnalysisName, currentSettingProps) {
  const Matrix = {
    'APOE': 'qsep100',
    'MTHFR': currentSettingProps.instrument,
    'NUDT15': currentSettingProps.instrument,
    'FXS': 'qsep100',
    'HTD': 'qsep100',
    'SMA': currentSettingProps.instrument
  }
  const check_type = AnalysisName in Matrix ? Matrix[AnalysisName] : null;
  return check_type;
}

// 檢查檔案格式
async function checkFileFormat(check_list, check_type) {

  // FLAG
  let PASS_CHECK_FILE_FORMAT = true;
  let message = "Check Success"

  // Check All file type
  const checkRes = await Promise.all(check_list.map(async (file) => {
    // 檢查檔案格式
    const checkRes = await useCheckFileFormat(file.path, check_type);
    // 回傳結果
    return checkRes;
  }));

  // 檢查 status 是否包含 'error' 如果有 error，則回傳 error message, 終止 function
  if (checkRes.some(res => res.status === 'error')) {
    // 印出 error message
    message = checkRes.filter(res => res.status === 'error').map(res => res.message).join(', \n');
    logger.error(message);
    PASS_CHECK_FILE_FORMAT = false;
    return {check_pass: PASS_CHECK_FILE_FORMAT, message : message, check_res: checkRes};
  }

  // 檢查 data.check_result 是否都是 true, 如果有 false，則回傳 error message, 終止 function
  if (checkRes.some(res => res.data.check_result === false)) {
    // 印出 error message
    message = checkRes.filter(res => res.data.check_result === false).map(res => res.message).join(', \n');
    logger.warn(message);
    PASS_CHECK_FILE_FORMAT = false;
  }

  return {check_pass: PASS_CHECK_FILE_FORMAT, message : message, check_res: checkRes};
}

// 製作 run parameter
function makeRunParameter(inputData, organization, instrument, reagent) {

  // 製作 run parameter
  const runParameter = {
    instrument: instrument,
    reagent: reagent,
    organization: organization,
    input_data: inputData
  }

  // 回傳 run parameter
  return runParameter;
}

// 送出表單
export async function submitWorkflow(FileCheckList, AnalysisName, InputData, userInfo, currentSettingProps) {

  //
  let execute_status = {status:"pending", message: "Waiting for start...", result:null}

  /* 1. Check file type */
  const checkType = getCheckType(AnalysisName, currentSettingProps);
  if (!checkType){
    execute_status = {status:"error", message: "未知的分析名稱", result:null}
    return execute_status;
  }

  // 檢查檔案格式
  const fileCheck = await checkFileFormat(FileCheckList, checkType);
  if (!fileCheck.check_pass) {
    let report_message = fileCheck.message;
    if (fileCheck.message.includes("No such object:")) {
      report_message = "檔案上傳失誤, 請重新上傳, 再試一次！";
    }
    execute_status = {status:"error", message: report_message, result:null}
    return execute_status;
  };

  /* 2. 製作 run Parameter */
  const currentInstrument = currentSettingProps.instrument;
  const currentReagent = currentSettingProps.reagent;
  const runParameter = makeRunParameter(InputData, userInfo.organization, currentInstrument, currentReagent);

  /* 3. 讓後台分析 */
  const analysis_name = AnalysisName;
  const analysis_input_data = runParameter;
  const analysis_result = await RunAnalysis({analysis_name, analysis_input_data}).then((response)=>{return response.data});

  // 回傳
  if (analysis_result.status === "success"){
    execute_status = {status:"success", message: analysis_result.message, result:analysis_result.result}
  } else {
    execute_status = {status:"error", message: analysis_result.message, result:null}
  }
  return execute_status;
}
