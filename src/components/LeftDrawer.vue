<template>
  <div class="drawer-content">
    <q-btn glossy label="Debug" @click="debug" icon="bug_report" />
    <q-btn glossy label="USER" @click="print_user_info" icon="account_circle" />
  </div>
</template>

<script setup>
import { useStore } from 'vuex';
import { ref, computed, onMounted } from 'vue';
import { updateGetUserInfo, isDevMode } from '@/composables/accessStoreUserInfo';

// 使用者身份
const { login_status } = updateGetUserInfo();

// Store
const store = useStore();


/* functions */

// Test check file format
async function debug() {
  console.log("DEBUG");
  console.log("isDevMode: ", await isDevMode());
}

// Get user info
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
