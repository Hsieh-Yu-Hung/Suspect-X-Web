import { v4 as uuidv4 } from 'uuid';
import { useStore } from 'vuex';
import { getAnalysisResult } from '@/firebase/firebaseDatabase.js';

// 更新 currentDisplayAnalysisID
export const getCurrentDisplayAnalysisID = () => {
  const store = useStore();
  return{
    analysis_uuid: store.getters["analysis_setting/getCurrentDisplayAnalysisID"].analysis_uuid,
    analysis_name: store.getters["analysis_setting/getCurrentDisplayAnalysisID"].analysis_name,
  }
}

// 取得當前的分析結果
export const getCurrentAnalysisResult = async (login_status, currentSettingProps) => {

  // store
  const store = useStore();

  // 取得 currentDisplayAnalysis
  const currentDisplayAnalysis = {
    analysis_uuid: store.getters["analysis_setting/getCurrentDisplayAnalysisID"].analysis_uuid,
    analysis_name: store.getters["analysis_setting/getCurrentDisplayAnalysisID"].analysis_name,
  }

  // 取得當前的分析結果
  const currentAnalysisResult = await getAnalysisResult(
    login_status.value.user_info.uid,
    currentDisplayAnalysis.analysis_name,
    currentDisplayAnalysis.analysis_uuid,
  );

  return currentAnalysisResult;
}

// 先嘗試取得當前的分析 ID, 如果沒有則建立新的分析 ID
export function setAnalysisID(store, analysis_name) {
  const currentAnalysisID = store.getters['analysis_setting/getCurrentAnalysisID'];
  if (currentAnalysisID.analysis_uuid == null) {
    const new_id = `analysis_${uuidv4()}`;
    store.commit('analysis_setting/updateCurrentAnalysisID', {
      analysis_name: analysis_name,
      analysis_uuid: new_id,
    });
  }
}
