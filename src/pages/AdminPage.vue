<template>
  <q-page v-if="displayAdmin" class="flex flex-center">

    <!-- 其他 -->
    <div style="width: 100%;">
      <q-card>
        <q-card-section>
          <div style="display: flex; flex-direction: row; align-items: center; justify-content: space-between;">
            <span class="text-h6">其他控制項</span>
            <q-btn color="primary" label="上傳日誌" @click="callUploadLogs" />
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- 組織管理 -->
    <div class="section-container">
      <OrganizationSection ref="organization_section" @organization_List_is_updated="update_organization_List" />
    </div>

    <!-- 軟體資料管理 -->
    <div class="section-container">
      <SoftwareSection ref="software_section" @software_List_is_updated="update_software_List" />
    </div>

    <!-- 使用者資料管理 -->
    <div class="section-container" style="width: 95%; min-width: 1000px; height: 100%;">
      <UserManageSection ref="user_manage_section" @user_List_is_updated="update_user_List" />
    </div>

  </q-page>

  <q-page v-else class="flex flex-center">
    <div style="width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 20px;">
      <span class="text-h4 text-red">
        您沒有管理員權限! 請返回首頁!
      </span>
      <span class="text-h6 text-deep-orange">
        Warning! You are not an admin and try to access this page!
      </span>
    </div>
  </q-page>

</template>

<script setup>

// 導入模組
import { ref, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';
import { getEmailList } from '@/firebase/firebaseDatabase.js';
import logger from '@/utility/logger';
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo.js';
import { uploadLogs } from '@/firebase/firebaseFunction.js';

// 導入元件
import OrganizationSection from '@/components/OrganizationSection/OrganizationSection.vue';
import SoftwareSection from '@/components/SoftwareSection/SoftwareSection.vue';
import UserManageSection from '@/components/UserManageSection/UserManageSection.vue';

// refs
const organization_section = ref(null);
const software_section = ref(null);
const user_manage_section = ref(null);
const displayAdmin = ref(false);

// router
const router = useRouter();

// 取得登入狀態
const { login_status } = updateGetUserInfo();

// 取得 Quasar
const $q = useQuasar();

// 更新軟體列表
const update_software_List = () => {
  // 重新載入組織列表的軟體版本選單
  organization_section.value.update_software_version_list();
}

// 更新組織列表
const update_organization_List = () => {
  // 重新載入組織列表的軟體版本選單
  user_manage_section.value.update_organization_list();
}

// 更新使用者列表
const update_user_List = () => {
  // 重新載入使用者列表
  user_manage_section.value.update_user_list();
}

// 檢查是否為管理員權限
const check_admin_permission = async () => {

  // 顯示loaing
  $q.loading.show();

  // 取得 email_list
  const email_list = await getEmailList();
  const isUserExist = email_list.find(email => email.email === login_status.value.user_info.email);

  // 隱藏loaing
  $q.loading.hide();

  // 檢查是否為管理員權限
  if (
    login_status.value.user_info.account_approved && isUserExist &&
    login_status.value.user_info.role === 'admin'
  ) {
    // 通知
    $q.notify({
      message: '管理員權限檢查成功!',
      color: 'amber-8',
      icon: 'check',
      position: 'top',
      timeout: 1000
    });
    return true;
  } else {
    // 通知
    $q.notify({
      message: '你想做什麼!？',
      color: 'red',
      icon: 'warning',
      position: 'top',
      timeout: 3000
    });
    // 跳轉到首頁
    setTimeout(() => {
      $q.loading.show();
    }, 1000);
    setTimeout(() => {
      router.push('/');
      $q.loading.hide();
    }, 3000);
    return false;
  }
}

// 驗證管理員權限
const verify_admin_permission = async () => {
  // 如果非管理員權限，則跳轉到首頁
  const is_admin = await check_admin_permission();
  if (!is_admin) {
    displayAdmin.value = false;
    logger.error(`
      警告, 有人嘗試進入管理員頁面！
      Email: ${login_status.value.user_info.email}
      Role: ${login_status.value.user_info.role}
      Organization: ${login_status.value.user_info.organization}
      Account Approved: ${login_status.value.user_info.account_approved}
    `);
  } else {
    displayAdmin.value = true;
    logger.info(`
      人員成功進入管理員頁面！
      Email: ${login_status.value.user_info.email}
      Role: ${login_status.value.user_info.role}
      Organization: ${login_status.value.user_info.organization}
      Account Approved: ${login_status.value.user_info.account_approved}
    `);
  }
}

// 上傳日誌
const callUploadLogs = async () => {
  $q.loading.show();
  const response = await uploadLogs().then(res => {
    return res.data;
  });
  if (response.status === "success") {
    $q.notify({
      message: response.message,
      progress: true,
      color: 'green',
      icon: 'check',
      position: 'top',
      timeout: 1000
    });
  }
  else {
    $q.notify({
      message: response.message,
      color: 'red',
      icon: 'warning',
      position: 'top',
      timeout: 3000
    });
  }
  $q.loading.hide();
}

// 掛載時
onMounted(async () => {

  // 驗證管理員權限
  verify_admin_permission();

});

</script>

<style scoped>
.section-container {
  width: 45%;
  min-width: 700px;
  height: 600px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  gap: 10px;
  margin-block: auto;
  margin-inline: 10px;
  padding-block: 20px;
}
</style>
