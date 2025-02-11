<template>
  <div class="drawer-content">
    <q-btn glossy label="USER" @click="print_user_info" icon="mdi-login" />
    <q-btn glossy label="Debug" @click="debug" icon="bug_report" />
  </div>
</template>

<script setup>

// Import modules
import { ref } from 'vue';
import { useStore } from 'vuex';

// 導入 composable
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';

// 取得 login_status
const { login_status } = updateGetUserInfo();

// 取得 store
const store = useStore();

/* functions */

// Test check file format
async function debug() {
  console.log("currentAnalysisID: ", store.getters['analysis_setting/getCurrentAnalysisID']);
}

// 印出 user_info
function print_user_info() {
  console.log("is_login: ", login_status.value.is_login);
  console.log("user_info: ", login_status.value.user_info);
}

</script>

<style scoped>
.drawer-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 20px;
}
</style>
