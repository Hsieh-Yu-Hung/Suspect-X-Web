<template>

  <!-- 使用者資料管理 -->
  <q-card class="card">

    <!-- Header -->
    <q-card-section>
      <div class="section">
        <span class="text-h6">使用者資料管理</span>
        <div style="display: flex; flex-direction: row; gap: 10px;">
          <DropDownList name="filter_organization"
            ref="ref_filter_organization"
            label="篩選組織"
            icon="group"
            :list_data="display_organization"
            :selected_value="default_organization"
            style="width: 200px;"
            @update_selected_value="update_filter_selected_value"
          />
          <DropDownList name="filter_account_active"
            ref="ref_filter_account_active"
            label="篩選開通"
            icon="privacy_tip"
            :list_data="account_active_option_for_filtering"
            :selected_value="default_account_active"
            style="width: 150px;"
            @update_selected_value="update_filter_selected_value"
          />
          <DropDownList name="filter_account_role"
            ref="ref_filter_account_role"
            label="篩選身份"
            icon="key"
            :list_data="role_option_for_filtering"
            :selected_value="default_role"
            style="width: 150px;"
            @update_selected_value="update_filter_selected_value"
          />
          <!-- 重新載入使用者 -->
          <q-btn glossy color="primary" icon="refresh" @click="refresh_user_list" />
        </div>
      </div>
    </q-card-section>

    <!-- 我是分隔線 -->
    <q-separator />

    <!-- Content -->
    <div class="flex flex-center" style="margin-top: 1.5em;" v-if="display_user.length <= 1">
      <span class="subtitle">...目前沒有使用者...</span>
    </div>
    <q-card-section v-else>
      <div v-for="user in display_user" :key="user.id"
        :class="{'hide': !to_show_condition(user), 'show': to_show_condition(user)}"
      >
        <UserItem
          :user_info="user"
          :organization_list="display_organization"
          :account_role_option_list="account_role_option"
          @update_user_info="update_user_info"
          @delete_user="delete_user"/>
      </div>
    </q-card-section>
  </q-card>

</template>

<script setup>

// 導入模組
import { ref, onMounted } from 'vue';
import { useQuasar } from 'quasar';

// 導入元件
import UserItem from './UserItem.vue';
import { USER_INFO, dataset_list } from '@/firebase';
import { load_organization_for_dropdown } from '@/firebase';
import { load_users_from_firestore } from '@/firebase';
import { update_userData, getUsers_from_firestore, deleteData } from '@/firebase';
import loggerV2 from '@/composables/loggerV2';
import DropDownList from '@/components/DropDownList.vue';
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';

// 取得 login_status
const { login_status } = updateGetUserInfo();

// 取得 Quasar
const $q = useQuasar();

// 組織列表
const default_organization = "未選擇";
const display_organization = ref([default_organization]);

// 列表標題
const header = USER_INFO("人員帳號", "N/A", "header_id", "所屬組織", "帳號身份", "帳號開通", "權限")
header.created_at = "申請日期";
header.updated_at = "更新日期";

// 使用者資料列表
const display_user = ref([header]);

// 帳號身份選單
const account_role_option = ref([
  {role: 'not-set', label: '未選擇'},
  {role: 'user', label: '使用者'},
  {role: 'admin', label: '管理員'},
  {role: 'supervisor', label: '單位主管'},
]);

// 帳號身份選單 (篩選用)
const default_role = '未選擇';
const current_filter_account_role_selected = ref(account_role_option.value.find(item => item.label === default_role).role);
const role_option_for_filtering = account_role_option.value.map(item => item.label);

// 帳號開通選單 (篩選用)
const default_account_active = '未選擇';
const current_filter_account_active_selected = ref(default_account_active);
const account_active_option_for_filtering = [default_account_active,'開通','未開通'];

// 組織選單 (篩選用)
const default_organization_for_filtering = '未選擇';
const current_filter_organization_selected = ref(default_organization_for_filtering);

// Emits
const emit = defineEmits(['user_List_is_updated']);

/* functions */

// update filters
function update_filter_selected_value(data) {
  // 更新篩選：帳號開通
  if(data.name === 'filter_account_active') {
    if(data.new_value !== default_account_active) {
      current_filter_account_active_selected.value = data.new_value === "開通" ? true
      : data.new_value === "未開通" ? false : default_account_active;
    }
    else {
      current_filter_account_active_selected.value = default_account_active;
    }
  }

  // 更新篩選：帳號身份
  else if(data.name === 'filter_account_role') {
    if(data.new_value !== default_role) {
      current_filter_account_role_selected.value = account_role_option.value.find(item => item.label === data.new_value).role;
    }
    else {
      current_filter_account_role_selected.value = account_role_option.value.find(item => item.label === default_role).role;
    }
  }

  // 更新篩選：組織
  else if(data.name === 'filter_organization') {
    if(data.new_value !== default_organization) {
      current_filter_organization_selected.value = data.new_value;
    }
    else {
      current_filter_organization_selected.value = default_organization;
    }
  }

  // 重新載入使用者
  refresh_user_list();
}

// to_show condition
const to_show_condition = (user) => {
  const condition_account_active = (user.account_active === current_filter_account_active_selected.value || current_filter_account_active_selected.value === default_account_active);
  const condition_account_role = (
    user.role === current_filter_account_role_selected.value
  ) || (
    current_filter_account_role_selected.value === account_role_option.value.find(item => item.label === default_role).role
  ) || (
    user.role === '帳號身份'
  );
  const condition_organization = (
    user.organization === current_filter_organization_selected.value
  ) || (
    current_filter_organization_selected.value === default_organization_for_filtering
  ) || (
    user.organization === '所屬組織'
  );
  return condition_account_active && condition_account_role && condition_organization;
}

// 刷新頁面
async function refresh_user_list() {

  // 開啟loading
  $q.loading.show();

  // 取得使用者資料
  const allUser = await getUsers_from_firestore();

  // 清空 display_user
  display_user.value.forEach(item => {
    if(item.id !== header.id) {
      display_user.value.splice(display_user.value.indexOf(item), 1);
    }
  });

  // 更新 display_user
  allUser.forEach(user => {
    if(!display_user.value.find(item => item.id === user.id)) {
      display_user.value.push(user);
    }
  });

  // 排序 display_user
  display_user.value.sort((a, b) => {
    return a.email.localeCompare(b.email);
  });

  // 關閉loading
  $q.loading.hide();
}

// 更新使用者資料
async function update_user_info(data) {

  // 開啟loading
  $q.loading.show();

  // 取得使用者資料
  const targetUser = await getUsers_from_firestore(data.id);

  // 建立新使用者資料
  const newData = USER_INFO(
    targetUser.email,
    targetUser.login_method,
    targetUser.id,
    targetUser.organization,
    targetUser.role,
    targetUser.account_active
  );

  // 如果是帳號開通, 則更新帳號開通
  if(data.check_account_active){
    newData.account_active = data.account_active;
    const message = `帳號開通: id: ${data.id}, email: ${targetUser.email}, 帳號開通: ${data.account_active}`;
    const source = 'UserManageSection.vue line.233';
    const user = login_status.value.user_info.email;
    loggerV2.info(message, source, user);
  }

  // 如果是換組織, 則更新組織
  else if(data.organization){
    newData.organization = data.organization;
    const message = `換組織: id: ${data.id}, email: ${targetUser.email}, 舊組織: ${targetUser.organization}, 新組織: ${data.organization}`;
    const source = 'UserManageSection.vue line.242';
    const user = login_status.value.user_info.email;
    loggerV2.info(message, source, user);
  }

  // 如果是換帳號身份, 則更新帳號身份
  else if(data.role){
    newData.role = data.role;
    const message = `換帳號身份: id: ${data.id}, email: ${targetUser.email}, 舊帳號身份: ${targetUser.role}, 新帳號身份: ${data.role}`;
    const source = 'UserManageSection.vue line.249';
    const user = login_status.value.user_info.email;
    loggerV2.info(message, source, user);
  }

  // 更新使用者資料
  await update_userData(newData, data.id);

  // 重新載入使用者
  refresh_user_list();

  // 關閉loading
  setTimeout(() => {
    $q.loading.hide();
  }, 500);

  // 通知
  $q.notify({
    message: '帳號狀態已更新',
    color: 'teal-6',
    icon: 'check',
    position: 'top',
    timeout: 300
  });
}

// 載入組織列表 (下拉式選單用)
async function update_dropdown_organization() {
  await load_organization_for_dropdown(display_organization.value,default_organization);
}

// 更新組織列表
async function update_organization_list() {
  await update_dropdown_organization()
}

// 刪除使用者資料
async function delete_user(user_id_to_delete) {

  // 開啟loading
  $q.loading.show();

  // 更新 display_user
  const new_display_user = display_user.value.filter(
    item => item.id !== user_id_to_delete
  );
  display_user.value = new_display_user;

  // 更新 firestore
  await deleteData(dataset_list.user_info, user_id_to_delete)
  .then((Response) => {
    if(Response.status === 'success') {
      // 發送事件
      emit('user_List_is_updated');

      // 重新載入使用者
      refresh_user_list();
    }
    else {
      console.error(Response.message);
    }
  })
  .catch((error) => {
    console.error(error);
  }).finally(() => {
    // 關閉loading
    $q.loading.hide();
  });
}

// 更新使用者列表
async function update_user_list() {
  await load_users_from_firestore(display_user);
  // 排序 display_user
  display_user.value.sort((a, b) => {
    return a.email.localeCompare(b.email);
  });
}

/* onMounted */
onMounted(async () => {

  // 開啟loading
  $q.loading.show();

  // 載入組織列表 (下拉式選單用)
  await update_dropdown_organization();

  // 取得使用者資料
  await update_user_list();

  // 關閉loading
  $q.loading.hide();

});

// Expose
defineExpose({
  update_organization_list,
  update_user_list,
});

</script>

<style scoped>
.card {
  width: 100%;
  overflow: auto;
  height: 100%;
}
.section {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.title {
  font-size: 1.2em;
  font-weight: bold;
}
.subtitle {
  font-size: 1em;
  font-weight: normal;
  font-style: italic;
}
.hide{
  display: none;
}
.show{
  display: block;
}
</style>
