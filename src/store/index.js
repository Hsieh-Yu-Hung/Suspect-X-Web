/* Import */
import { store } from 'quasar/wrappers'
import createPersistedState from 'vuex-persistedstate';
import Vuex from 'vuex';

// 自定義 Modules
import login_status from './LoginStatus';
import analysis_setting from './AnalysisSetting';
import FXS_analysis_data from './FXS_analysis_data';

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

      // FXS 分析結果
      FXS_analysis_data: FXS_analysis_data
    }
  })

  // 返回 Store
  return store;
})
