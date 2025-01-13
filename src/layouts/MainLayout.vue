<template>
  <q-layout view="hHh lpR lFr">

    <!-- Layout Header -->
    <q-header v-model="show_header" reveal elevated class="text-white" :class="header_color" height-hint="98">

      <!-- 標題列 -->
      <q-toolbar>

        <!-- 左邊選單按鈕 -->
        <q-btn flat round icon="menu" @click="toggleLeftDrawer" />

        <!-- 標題 -->
        <q-toolbar-title>
          <div style="width: fit-content; display: flex; flex-direction: row; align-items: center; cursor: pointer;" @click="to_index">
            <!-- logo -->
            <div class="logo" style="height: 35px; margin-inline: 10px;">
              <img src="/icon.png" style="height: 100%;">
            </div>
            <!-- 標題文字 -->
            <div style="height: 40px; margin-inline: 10px; display: flex; flex-direction: row; align-items: center;">
              <span style="font-size: 1.4em; font-weight: bold; color: black;">ACCUiNspection
                <span style="font-size: 0.4em; font-weight: bold; color: slategray; margin-inline: 5px;">{{ mode_display_name }}</span>
              </span>
            </div>
          </div>
        </q-toolbar-title>

        <!-- 右邊選單按鈕 -->
        <q-btn no-caps dense flat :icon="account_icon_display_name" :label="account_display_name" @click="toggleRightDrawer" color="black"/>
      </q-toolbar>

      <!-- 頁籤按鈕 -->
      <q-tabs align="right" class="text-blue-grey-8">
        <q-route-tab to="/page-import" label="Import" />
        <q-route-tab to="/page-analysis" label="Analysis" />
        <q-route-tab to="/page-export" label="Export" />
      </q-tabs>

    </q-header>

    <q-drawer v-model="leftDrawerOpen" side="left" overlay behavior="desktop" bordered>
      <LeftDrawer />
    </q-drawer>

    <q-drawer v-model="rightDrawerOpen" side="right" overlay behavior="mobile" bordered>
      <RightDrawer
        ref="rightDrawer"
        :account_name="account_display_name"
        :account_role="account_role"
        :account_organization="account_organization"
        :account_status="display_account_status"
      />
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>

  </q-layout>
</template>

<script setup>

/* Import modules */
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router';
import { useStore } from 'vuex';
import RightDrawer from '@/components/RightDrawer.vue';
import LeftDrawer from '@/components/LeftDrawer.vue';

// 取得 router, route, store
const router = useRouter();
const route = useRoute();
const store = useStore();

/* refs */

// rightDrawer
const rightDrawer = ref(null);

// Store 相關
const is_login = ref(false);
const user_info = ref(null);

// Drawers 開關
const leftDrawerOpen = ref(false)
const rightDrawerOpen = ref(false)

// 標題列顯示
const show_header = ref(true);
const header_color = ref('bg-indigo-2');

// 顯示帳號
const display_account_status = ref(false);
const account_display_name = ref('show account');
const account_organization = ref('NULL');
const account_role = ref('NULL');
const mode_display_name = ref('Web Service');
const account_icon_display_name = ref('group');

/* functions */

// 開關左邊選單
const toggleLeftDrawer = () => {
  leftDrawerOpen.value = !leftDrawerOpen.value
}

// 開關右邊選單
const toggleRightDrawer = () => {
  rightDrawerOpen.value = !rightDrawerOpen.value
}

// 開關標題列
const closeHeader = () => {
  show_header.value = false;
}

// 開啟標題列
const openHeader = () => {
  show_header.value = true;
}

// 跳轉到首頁
const to_index = () => {
  router.push('/');
}

// 開關標題列
const toggle_header = () => {
  if (route.path === '/login') {
    closeHeader();
  } else {
    openHeader();
  }
}

// 取得登入狀態
const updateLoginStatus = () => {
  is_login.value = store.getters['login_status/getLoginStatus'];
  user_info.value = store.getters['login_status/getUserInfo'];
}

// 更新UI
const updateUI = () => {

  // 若未登入, 則不更新UI
  if (!is_login.value) {return;}

  // 設定顯示帳號
  account_display_name.value = user_info.value.email;
  account_organization.value = user_info.value.organization;
  account_role.value = user_info.value.role;
  display_account_status.value = user_info.value.account_approved;

  // 設定顯示帳號 role
  if (user_info.value.role === 'admin') {
    // 設定標題列顏色和身份標籤
    account_display_name.value = account_display_name.value + '(Admin)';
    mode_display_name.value = 'Developper';
    header_color.value = 'bg-teal-2';
    account_icon_display_name.value = 'manage_accounts';
  } else {
    account_display_name.value = account_display_name.value.replace('(Admin)', '');
    mode_display_name.value = 'Web Service';
    header_color.value = 'bg-indigo-2';
    account_icon_display_name.value = 'group';
  }

  // 更新右邊選單
  rightDrawer.value.update_display_account_name();
}

/* onMounted */
onMounted(() => {

  // 取得登入狀態
  updateLoginStatus();

  // 決定是否要開啟標題列
  toggle_header();

  // 更新UI
  updateUI();
});

/* watch */
watch(route, () => {

  // 取得登入狀態
  updateLoginStatus();

  // 決定是否要開啟標題列
  toggle_header();

  // 更新UI
  updateUI();
});

</script>
