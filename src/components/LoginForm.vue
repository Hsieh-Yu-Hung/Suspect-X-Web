<template>
  <div class="form flex-column-center q-pa-md">
    <q-form @submit="onSubmit" class="q-gutter-md">

      <div class="flex-column-center">

        <!--Logo-->
        <div style="width: 250px; height: 50px; margin: 1em; cursor: pointer;" @click="debug">
          <img src="/logo.png" alt="Logo" style="width: 100%; height: 100%;"/>
        </div>

        <!-- Login form -->
        <div class="flex-column-center" style="margin: 1em; background-color: white; border-radius: 1em; padding: 1em;">
          <!-- Title -->
          <div class="text-h6 flex-row-center">
            <q-avatar icon="lock_person" color="white" text-color="black" />
            <span class="text-h6" style="margin-inline: 0.5em;">Member Login</span>
            <q-avatar icon="login" color="white" text-color="black" />
          </div>

          <!--Input fields -->
          <div class="flex-column-center" style="min-width: 400px;">

            <!-- E-mail input -->
            <q-input v-model="email_input" label="E-mail" class="input-field" :error="email_error" :error-message="email_input_hint">
              <template v-slot:append>
                <q-icon name="email" />
              </template>
            </q-input>

            <!-- Password input -->
            <q-input v-model="password_input" label="Password" class="input-field" type="password" :error="password_error" :error-message="password_input_hint" >
              <template v-slot:append>
                <q-icon name="lock" />
              </template>
            </q-input>

            <!-- Login button -->
            <div class="flex-column-center input-field" style="width: 100%;">
              <q-btn class="login-button" color="teal-1" label="Enter" text-color="black" rounded @click="onSubmit"/>
              <q-btn icon="img:/google_logo.png" class="login-button" color="grey-2" rounded no-caps label="Sing in with Google" text-color="black" @click="applyGoogleLogin" />
              <q-btn icon="img:/icon.png" class="login-button" color="grey-2" rounded no-caps label="Register ACCUiN" text-color="black" @click="switch_to_register" />
            </div>
          </div>

        </div>

      </div>

    </q-form>
  </div>
</template>

<script setup>

/* Import modules */

// firebase SDK auth
import { signInWithEmail } from '@/firebase';

// firebase SDK database
import { login_method, getEmailList } from '@/firebase';

// Quasar Vue
import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';
import { ref, onMounted } from 'vue';

// logger
import logger from '@/utility/logger';

// composables
import { useAccountManagement } from '@/composables/accountManagement.js';
const { useGoogleLogin, storeUserInfo, redirect_page } = useAccountManagement();

/* Quasar */
const $q = useQuasar();
const router = useRouter();
const store = useStore();

/* refs */
const email_input = ref('');
const email_error = ref(false);
const email_input_hint = ref('');
const password_input = ref('');
const password_error = ref(false);
const password_input_hint = ref('');

/* emit */
const emit = defineEmits(['switch_to_register']);

/* functions */

// 送出登入
async function onSubmit() {
  // 登入狀態, 初始化
  let status = 'pending';
  email_error.value = false;
  password_error.value = false;
  email_input_hint.value = '';
  password_input_hint.value = '';

  // 顯示 loading
  $q.loading.show({message: '登入中...'});

  // 取得 email_list
  const email_list = await getEmailList();
  if (email_list.some(email => email.email === email_input.value && email.login_method === login_method.google)) {
    $q.notify({
      message: '此帳號已經註冊, 請使用Google登入',
      color: 'deep-orange',
      icon: 'warning',
      position: 'top',
      timeout: 500
    });
    setTimeout(() => {
      $q.loading.hide();
      applyGoogleLogin();
    }, 500);
    return;
  }

  // 登入
  await signInWithEmail(email_input.value, password_input.value)
  .then((result) => {
    // 將 user_info 加入到 store
    storeUserInfo(store, router, $q);

    // 登入成功
    status = 'success';
    logger.info(`Login success, Email: ${result.user.email}, UID: ${result.user.uid}`);
  })
  .catch((error) => {
    // 登入失敗
    status = 'error';
    if (error.code === 'auth/invalid-email') {
      email_error.value = true;
      email_input_hint.value = "請輸入有效格式的電子郵件";
      logger.warn(`Invalid email, Email: ${email_input.value}`);
    } else if (error.code === 'auth/user-not-found') {
      email_error.value = true;
      email_input_hint.value = "找不到此帳號, 請先註冊";
      logger.warn(`User not found, Email: ${email_input.value}`);
    } else if (error.code === 'auth/wrong-password') {
      password_error.value = true;
      password_input_hint.value = "密碼錯誤, 請重新輸入";
      logger.warn(`Wrong password, Email: ${email_input.value}`);
    } else {
      $q.notify({
        message: '[未知原因] 登入失敗, 請聯絡管理員',
        color: 'red',
        icon: 'error',
        position: 'top'
      });
      logger.error(`Login failed, Error Code: ${error.code}`);
    }
  }).finally(() => {
    // 隱藏 loading
    $q.loading.hide();

    // 如果登入成功，則跳轉到 index
    if (status === 'success') {
      // 通知
      $q.notify({
        message: '已經成功登入',
        color: 'green',
        icon: 'check',
        position: 'top'
      });

      // 跳轉
      redirect_page(store, router, $q);
    }
  });
}

// 應用 Google 登入
async function applyGoogleLogin() {
  await useGoogleLogin(store, router, $q);
}

// 切換表單 -- 註冊
function switch_to_register() {
  emit('switch_to_register');
}

/* onMounted */
onMounted(() => {
  // 取得登入狀態並將 user_info 加入到 store
  storeUserInfo(store, router, $q);
});

</script>

<style scoped>
.form {
  background-color: rgb(212, 232, 253);
  border-radius: 1em;
}
.flex-row-center{
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
}
.flex-column-center{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.input-field{
  width: 100%;
  margin-block: 0.5em;
  padding-bottom: 20px;
}
.login-button{
  width: 100%;
  margin-block: 0.5em;
}
</style>
