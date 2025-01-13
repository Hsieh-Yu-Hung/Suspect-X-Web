/* Import */
import { store } from 'quasar/wrappers'
import createPersistedState from 'vuex-persistedstate';
import Vuex from 'vuex';

// 自定義 Modules
import organization_list from './organizationList';
import login_status from './LoginStatus';

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

      // 組織列表
      organization_list: organization_list,

      // 登入狀態
      login_status: login_status
    }
  })

  // 返回 Store
  return store;
})
