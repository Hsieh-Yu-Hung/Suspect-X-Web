<template>
  <q-page class="flex flex-center">
    <transition name="fade">
      <div v-if="display_page_content" style="display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: pointer;" @click="to_login">
        <!-- Logo -->
        <img
          alt="ACCUiNspection logo"
          src="/logo.png"
          height="40px"
        >
        <!-- Login button -->
        <div style="width: 100%; display: flex; flex-direction: row; align-items: center; justify-content: space-evenly; margin-top: 1.5em;">
          <q-icon class="login-hint" name="east" />
          <span class="login-hint">Click to Start</span>
          <q-icon class="login-hint" name="west" />
        </div>
      </div>
    </transition>
  </q-page>
</template>

<script setup>

/* Import modules */
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { getData, dataset_list } from '@/firebase';
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo.js';

/* refs */

// Quasar
const $q = useQuasar();

// Router
const router = useRouter();

// State to control visibility
const display_page_content = ref(true);

// 取得登入狀態
const { login_status } = updateGetUserInfo();

defineOptions({
  name: 'IndexPage'
});

/* functions */
const main = async () => {

  // 取得登入狀態
  const is_login = login_status.value.is_login;

  // 檢查使用者是否存在
  const user_email = login_status.value.user_info.email;
  const user_account_active = login_status.value.user_info.account_approved;
  const user_exist = await check_user_exist(user_email).then((result) => {
    return result;
  });

  if (is_login && user_exist) {
    $q.notify({
      message: '帳號已經登入',
      color: 'teal-7',
      icon: 'check',
      position: 'top',
      timeout: 500
    });
    // 跳轉至 page-analysis, 若未開通則到 not-active
    setTimeout(() => {
      if(user_account_active){
        router.push('/page-analysis');
      } else {
        router.push('/page-not-active');
      }
    }, 500);
  } else {
    // 顯示登入提示
    $q.notify({
      message: '嘗試登入中...',
      color: 'teal-7',
      icon: 'warning',
      position: 'top',
      timeout: 500
    });
    // 跳轉至 login page
    setTimeout(() => {
      to_login();
    }, 500);
  }
};

// Login function
const to_login = () => {
  // 關閉當前 page 顯示
  display_page_content.value = false;

  // 延遲 100ms 後跳轉到 login page
  setTimeout(() => {
    router.push('/login');
  }, 200);
}

// 檢查使用者是否存在
const check_user_exist = async (user_email) => {
  let user_exist = false;
  await getData(dataset_list.email_list, user_email)
  .then((result) => {
    if (result.status === 'success' && result.data) {
      user_exist = true;
    }
  })
  .catch((error) => {
    console.error(` Check user exist failed, Error: ${error}`);
  });
  return user_exist;
}

/* onMounted */
onMounted(() => {
  // 執行主函式
  main();
});

</script>

<style scoped>
.login-hint {
  font-size: 14px;
  color: silver;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.fade-enter-to, .fade-leave-from {
  opacity: 1;
}
</style>
