/* Import */
import { store } from 'quasar/wrappers'
import { createStore } from 'vuex'

// 自定義 Modules
import organization_list from './organizationList';

export default store(function () {

  // 創建 Store
  const store = createStore({

    // 加入自定義 Modules
    modules: {

      // 組織列表
      organization_list: organization_list
    }
  })

  // 返回 Store
  return store;
})
