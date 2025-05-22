/* Import */
import { store } from 'quasar/wrappers'
import createPersistedState from 'vuex-persistedstate';
import Vuex from 'vuex';

// 自定義 Modules
import login_status from './LoginStatus';
import analysis_history_data from './AnalysisHistory_data';
import analysis_setting from './AnalysisSetting';
import FXS_analysis_data from './FXS_analysis_data';
import HTD_analysis_data from './HTD_analysis_data';
import APOE_analysis_data from './APOE_analysis_data';
import MTHFR_analysis_data from './MTHFR_analysis_data';
import NUDT15_analysis_data from './NUDT15_analysis_data';
import SMA_analysis_data from './SMA_analysis_data';
import SMAv4_analysis_data from './SMAv4_analysis_data';
import export_page_setting from './ExportPageSetting';
import Beta_thal_analysis_data from './Beta_thal_analysis_data';

// 從 localStorage 中恢復登入狀態
const savedState = localStorage.getItem('store');
if (savedState) {
  store.replaceState(Object.assign(store.state, JSON.parse(savedState)));
}

export default store(function () {

  // 創建 Store
  const store = new Vuex.Store({

    // 使用 vuex-persistedstate 插件存儲登入狀態到 localStorage
    plugins: [createPersistedState()],

    // 加入自定義 Modules
    modules: {

      // 登入狀態
      login_status: login_status,

      // 分析設定
      analysis_setting: analysis_setting,

      // 分析歷史資料
      analysis_history_data: analysis_history_data,

      // 匯出頁面設定
      export_page_setting: export_page_setting,

      // FXS 分析結果
      FXS_analysis_data: FXS_analysis_data,

      // HTD 分析結果
      HTD_analysis_data: HTD_analysis_data,

      // APOE 分析結果
      APOE_analysis_data: APOE_analysis_data,

      // MTHFR 分析結果
      MTHFR_analysis_data: MTHFR_analysis_data,

      // NUDT15 分析結果
      NUDT15_analysis_data: NUDT15_analysis_data,

      // SMA 分析結果
      SMA_analysis_data: SMA_analysis_data,

      // SMAv4 分析結果
      SMAv4_analysis_data: SMAv4_analysis_data,

      // Beta Thal Analysis 結果
      Beta_thal_analysis_data: Beta_thal_analysis_data
    }
  })

  // 返回 Store
  return store;
})
