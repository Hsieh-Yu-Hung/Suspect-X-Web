import state from './state'
import * as getters from './getters'
import { set_login_status, init_login_status } from './mutations'

export default {
  namespaced: true,
  getters,
  state,
  mutations: {
    set_login_status,
    init_login_status
  }
}
