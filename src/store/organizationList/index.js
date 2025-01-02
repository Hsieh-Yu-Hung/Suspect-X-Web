import state from './state'
import * as getters from './getters'
import {set_organization_list} from './mutations'
import {load_organization_list} from './actions'

export default {
  namespaced: true,
  getters,
  mutations:{set_organization_list},
  actions:{load_organization_list},
  state
}
