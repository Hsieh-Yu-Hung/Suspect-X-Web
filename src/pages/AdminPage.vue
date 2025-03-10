<template>
  <q-page v-if="displayAdmin" class="flex">

    <!-- TABS -->
    <div style="width: 100%; min-width: 600px;">
      <q-card>
        <q-tabs
          v-model="current_tab"
          dense
          class="text-grey"
          active-color="primary"
          indicator-color="primary"
          align="justify"
          narrow-indicator
        >
          <q-tab name="tab_users" label="使用者" />
          <q-tab name="tab_organizations" label="組織" />
          <q-tab name="tab_software" label="軟體" />
          <q-tab name="tab_logs" label="日誌" />
          <q-tab name="tab_other" label="其他" />
        </q-tabs>

        <q-separator />

        <!-- 頁籤內容 -->
        <q-tab-panels v-model="current_tab" animated style="height: 100vh;">

          <!-- 使用者頁籤 -->
          <q-tab-panel name="tab_users">

            <!-- 使用者資料管理 -->
            <div class="section-container">
              <UserManageSection ref="user_manage_section" />
            </div>

          </q-tab-panel>

          <!-- 組織頁籤 -->
          <q-tab-panel name="tab_organizations">

            <!-- 組織管理 -->
            <div class="section-container">
              <OrganizationSection ref="organization_section" />
            </div>

          </q-tab-panel>

          <!-- 軟體頁籤 -->
          <q-tab-panel name="tab_software">

            <!-- 軟體資料管理 -->
            <div class="section-container">
              <SoftwareSection ref="software_section" />
            </div>

          </q-tab-panel>

          <!-- 日誌頁籤 -->
          <q-tab-panel name="tab_logs">
            <div class="section-container">
              <LogSection ref="log_section" />
            </div>
          </q-tab-panel>

          <!-- 其他頁籤 -->
          <q-tab-panel name="tab_other">

            <!-- 其他控制項 -->
            <div class="section-container">
              <OtherSection ref="other_section" />
            </div>

          </q-tab-panel>

        </q-tab-panels>
      </q-card>
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
import loggerV2 from '@/composables/loggerV2';
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo.js';

// 導入元件
import OrganizationSection from '@/components/AdminPageViewComp/OrganizationSection/OrganizationSection.vue';
import SoftwareSection from '@/components/AdminPageViewComp/SoftwareSection/SoftwareSection.vue';
import UserManageSection from '@/components/AdminPageViewComp/UserManageSection/UserManageSection.vue';
import OtherSection from '@/components/AdminPageViewComp/OtherSettingSection/OtherSection.vue';
import LogSection from '@/components/AdminPageViewComp/LogSectionViews/LogSection.vue';

// refs
const organization_section = ref(null);
const software_section = ref(null);
const user_manage_section = ref(null);
const log_section = ref(null);
const other_section = ref(null);
const displayAdmin = ref(false);

// 目前選取的頁面
const current_tab = ref('tab_logs');
// router
const router = useRouter();

// 取得登入狀態
const { login_status } = updateGetUserInfo();

// 取得 Quasar
const $q = useQuasar();

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
    const message = `
      警告, 有人嘗試進入管理員頁面！
      Email: ${login_status.value.user_info.email};
      Role: ${login_status.value.user_info.role};
      Organization: ${login_status.value.user_info.organization};
      Account Approved: ${login_status.value.user_info.account_approved};
    `;
    const source = 'AdminPage.vue line.184';
    const user = login_status.value.user_info.email;
    loggerV2.warn(message, source, user);
  } else {
    displayAdmin.value = true;
  }
}

// 掛載時
onMounted(async () => {

  // 驗證管理員權限
  verify_admin_permission();

});

</script>

<style scoped>
.section-container {
  width: 100%;
  min-width: 700px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  gap: 10px;
}
</style>
