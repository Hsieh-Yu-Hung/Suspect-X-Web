import state from './state'
import * as getters from './getters'
import {
  set_current_display_product,
  set_current_display_record_id,
  set_current_selected_product,
} from './mutations'

export default {
  namespaced: true,
  getters,
  state,
  mutations: {
    set_current_display_product,
    set_current_display_record_id,
    set_current_selected_product,
  }
}
