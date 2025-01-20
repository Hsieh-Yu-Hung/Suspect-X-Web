<template>
  <div class="form flex-column-center q-pa-md">
    <q-form @submit="onSubmit" class="q-gutter-md">

      <div class="flex-column-center">

        <!--Logo-->
        <div style="width: 250px; height: 50px; margin: 1em;">
          <img src="/logo.png" alt="Logo" style="width: 100%; height: 100%;"/>
        </div>

        <!-- Register form -->
        <div class="flex-column-center" style="margin: 1em; background-color: white; border-radius: 1em; padding: 1em;">
          <!-- Title -->
          <div class="text-h6 flex-row-center">
            <q-avatar icon="assignment_add" color="white" text-color="black" />
            <span class="text-h6" style="margin-inline: 0.5em;">Registration</span>
            <q-avatar icon="token" color="white" text-color="black" />
          </div>

          <!--Input fields -->
          <div class="flex-column-center" style="min-width: 400px;">

            <!-- E-mail input -->
            <q-input class="input-field" v-model="input_email" label="E-mail" :error="input_email_error" :error-message="email_error_message">
              <template v-slot:append>
                <q-icon name="email" />
              </template>
            </q-input>

            <!-- Password input -->
            <q-input class="input-field" v-model="input_password" label="Password" :error="input_password_error" :error-message="password_error_message" type="password">
              <template v-slot:append>
                <q-icon name="lock" />
              </template>
            </q-input>

            <!-- Login button -->
            <div class="flex-column-center input-field" style="width: 100%;">
              <q-btn class="submit-button" color="deep-orange-1" label="Register" text-color="black" rounded @click="onSubmit"/>
              <q-btn icon="img:/google_logo.png" class="submit-button" color="grey-2" rounded no-caps label="Register with Google" text-color="black" @click="applyGoogleLogin"/>
              <q-btn no-caps icon="undo" class="submit-button" color="grey-2" label="Back to Login" text-color="black" rounded @click="switch_to_login" />
            </div>
          </div>

        </div>

      </div>

    </q-form>
  </div>
</template>

<script setup>

/* Import modules */

// Quasar and Vue
import { useQuasar } from 'quasar';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import { ref, watch } from 'vue';

// Firebase SDK: Auth
import { create_User_Account } from '@/firebase';

// Firebase SDK: Database
import { USER_INFO, EMAIL_INFO, login_method } from '@/firebase';
import { addLoginInfoDatabase, addEmailListDatabase, getEmailList } from '@/firebase';

// Logger
import logger from '@/utility/logger';

// composables
import { useAccountManagement } from '@/composables/accountManagement.js';
const { useGoogleLogin, storeUserInfo, redirect_page } = useAccountManagement();

/* emit */
const emit = defineEmits(['switch_to_login']);

// Quasar Vue
const $q = useQuasar();
const router = useRouter();
const store = useStore();

/* refs */

// 儲存輸入的值
const input_email = ref('');
const input_password = ref('');

// 檢查錯誤
const input_email_error = ref(false);
const email_error_message = ref('');
const input_password_error = ref(false);
const password_error_message = ref('');

/* functions */

// 送出註冊
async function onSubmit() {
  // 如果輸入有錯誤，則不送出
  if (!validate_input(input_email.value, 'email') ||
      !validate_input(input_password.value, 'password')) { return; }

  // 顯示 loading
  $q.loading.show({message: '帳號註冊中...'});

  // 取得 email_list
  const email_list = await getEmailList();
  if (email_list.some(email => email.email === input_email.value && email.login_method === login_method.google)) {
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

  // 送出註冊
  await create_User_Account(input_email.value, input_password.value)
  .then((result) => {
    // 紀錄到 logger
    logger.info(`New user registered: ${input_email.value}`);

    // 將登入資訊加入到 database
    const id = result.user.uid;
    const LoginInfo = USER_INFO(input_email.value, login_method.email_password, id);
    addLoginInfoDatabase(LoginInfo, id);

    // 將 email 加入到 email_list
    const EmailInfo = EMAIL_INFO(input_email.value, login_method.email_password);
    addEmailListDatabase(EmailInfo);

    // 取得登入狀態
    storeUserInfo(store, router, $q);

    // 註冊成功
    $q.notify({
      message: '已經成功註冊帳號',
      color: 'green',
      icon: 'check',
      position: 'top',
      timeout: 500
    });

  }).finally(() => {
    // 隱藏 loading
    $q.loading.hide();

    // 如果註冊成功，則跳轉
    redirect_page(store, router, $q);
  })
  .catch((error) => {
    // 補捉重複註冊
    if (catch_duplicate_register(error.message)) { return; }

    // 紀錄到 logger
    logger.error(`Register failed, Email: ${input_email.value}, Reason: ${error}`);

    // 註冊失敗
    $q.notify({
      message: '註冊失敗，請聯絡管理員',
      color: 'red',
      icon: 'error',
      position: 'top'
    });
  });
}

// 應用 Google 登入
async function applyGoogleLogin() {
  await useGoogleLogin(store, router, $q);
}

// 補捉重複註冊
function catch_duplicate_register(err_msg) {
  if (err_msg.includes('email-already-in-use')) {
    logger.error(`Duplicate register, Email: ${input_email.value}`);
    $q.notify({
      message: '此信箱已經註冊過',
      color: 'deep-orange-5',
      icon: 'warning',
      position: 'top'
    });
    return true;
  }
  return false;
}

// 切換表單 -- 登入
function switch_to_login() {
  emit('switch_to_login');
}

// 驗證輸入
function validate_input(value, type) {
  let valid = true;
  if (type === 'email') {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      input_email_error.value = true;
      email_error_message.value = 'Invalid email';
      valid = false;
    } else {
      input_email_error.value = false;
      email_error_message.value = '';
    }
  } else if (type === 'password') {
    if (value.length < 8) {
      input_password_error.value = true;
      password_error_message.value = 'Password must be at least 8 characters';
      valid = false;
    } else {
      input_password_error.value = false;
      password_error_message.value = '';
    }
  }
  return valid;
}

/* watch */

// Email input
watch(input_email, (new_value) => {
  validate_input(new_value, 'email');
});

// Password input
watch(input_password, (new_value) => {
  validate_input(new_value, 'password');
});

</script>

<style scoped>
.form {
  background-color: rgb(255, 230, 238);
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
  padding-bottom: 20px;
  margin-block: 0.5em;
}
.submit-button{
  width: 100%;
  margin-block: 0.5em;
}
</style>
