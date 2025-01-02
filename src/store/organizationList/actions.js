/* Import */
import AppDataConfigs from '../../../AppDataConfigs.json';

/* Action */

// 讀取 AppDataConfigs.json 的組織列表並載入 UI
export function load_organization_list ({ commit }) {
  const organization_list = AppDataConfigs.organization_list;
  commit('set_organization_list', organization_list);
}
