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
export async function submitWorkflow(AnalysisName, InputData, userInfo, currentSettingProps) {

  //
  let execute_status = {status:"pending", message: "Waiting for start...", result:null}

  /* 1. Check file type */
  const checkType = getCheckType(AnalysisName, currentSettingProps);
  if (!checkType){
    execute_status = {status:"error", message: "未知的分析名稱", result:null}
    return execute_status;
  }

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
