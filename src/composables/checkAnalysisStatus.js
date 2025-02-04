import { v4 as uuidv4 } from 'uuid';

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
