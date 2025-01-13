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
              <q-btn icon="img:/google_logo.png" class="submit-button" color="grey-2" rounded no-caps label="Register with Google" text-color="black" @click="onGoogleLogin"/>
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
import { create_User_Account, signInWithGoogle } from '@/firebase';
import { get_login_status } from '@/firebase';

// Firebase SDK: Database
import { dataset_list, USER_INFO, EMAIL_INFO, login_method } from '@/firebase';
import { addLoginInfoDatabase, addEmailListDatabase, getData } from '@/firebase';

// Logger
import logger from '@/utility/logger';

/* emit */
const emit = defineEmits(['switch_to_login']);

// Router
const router = useRouter();

// 通知
const $q = useQuasar();

// 取得 store
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

  // 註冊狀態
  let status = 'pending';

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
      position: 'top'
    });
    setTimeout(() => {
      $q.loading.hide();
      onGoogleLogin();
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
    const LoginInfo = USER_INFO(input_email.value, id, login_method.email_password);
    addLoginInfoDatabase(LoginInfo, id);

    // 將 email 加入到 email_list
    const EmailInfo = EMAIL_INFO(input_email.value, login_method.email_password);
    addEmailListDatabase(EmailInfo);

    // 取得登入狀態
    storeUserInfo();

    // 註冊成功
    $q.notify({
      message: '已經成功註冊帳號',
      color: 'green',
      icon: 'check',
      position: 'top',
      timeout: 500
    });

    // change status
    status = 'success';

  }).finally(() => {
    // 隱藏 loading
    $q.loading.hide();

    // 如果註冊成功，則跳轉到 tmpImportView
    if (status === 'success') {
      setTimeout(() => {
        router.push('/page-import');
      }, 1000);
    }
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

    // change status
    status = 'error';
  });
}

// Google 登入
async function onGoogleLogin() {

  // 註冊狀態
  let status = 'pending';

  await signInWithGoogle()
  .then((result) => {
    if (result.status === 'success') {
      // 將登入資訊加入到 database (Google 登入沒有輸入密碼)
      const id = result.user_uid;
      const LoginInfo = USER_INFO(result.user_email, id, login_method.google);
      addLoginInfoDatabase(LoginInfo, id);

      // 將 email 加入到 email_list
      const EmailInfo = EMAIL_INFO(result.user_email, login_method.google);
      addEmailListDatabase(EmailInfo);

      // 取得登入狀態
      storeUserInfo();

      // 註冊成功
      $q.notify({
        message: '已經成功使用 Google 帳戶登入',
        color: 'green',
        icon: 'check',
        position: 'top',
        timeout: 500
      });

      // change status
      status = 'success';
    }
  })
  .catch((error) => {
    logger.warn(`[Frontend] Google login failed, error: ${error}`);
    // change status
    status = 'error';
  }).finally(() => {
    // 如果註冊成功，則跳轉到 tmpImportView
    if (status === 'success') {
      setTimeout(() => {
        router.push('/page-import');
      }, 1000);
    }
  });
}

// 取得 email_list
async function getEmailList(){
  //
  let email_array = [];
  await getData(dataset_list.email_list)
  .then((result) => {
    if (result.status === 'success') {
      logger.debug(`[Frontend] Get email list success`);
      if (result.data) {
        result.data.forEach((email) => {
          email_array.push({email: email.email, login_method: email.login_method});
        });
      }
    } else {
      logger.error(`[Frontend] Get email list failed, Error: ${result.message}`);
    }
  })
  .catch((error) => {
    logger.error(`[Frontend] Get email list failed, Error: ${error}`);
  });
  return email_array;
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

// 取得 user_info 並將 user_info 加入到 store
async function storeUserInfo() {
  // 取得登入狀態
  const login_status = get_login_status();

  // 若未登入, 則不執行
  if (!login_status.is_login) {return;}

  // 取得 user_id
  const user_id = login_status.user_info.uid;

  // 取得 user_info 並將 user_info 加入到 store
  await getData(dataset_list.user_info, user_id)
  .then((result) => {
    if (result.status === 'success') {
      if (result.data) {

        // 取得 user_info
        const record_id = result.data.id;
        const record_role = result.data.role;
        const record_email = result.data.email;
        const record_organization = result.data.organization;
        const record_account_approved = result.data.account_active;

        // 將 user_info 加入到 store
        store.commit('login_status/set_login_status', {
          is_login: true,
          uid: record_id,
          role: record_role,
          email: record_email,
          organization: record_organization,
          account_approved: record_account_approved
        });

        // 通知
        $q.notify({
          message: '已經成功登入',
          color: 'green',
          icon: 'check',
          position: 'top',
          timeout: 500
        });

        // 跳轉到 tmpImportView
        setTimeout(() => {
          router.push('/page-import');
        }, 300);

      } else {
        logger.error(`[Frontend] Get user info failed, Error: No user info found!`);
      }
    } else {
      logger.error(`[Frontend] Get user info failed, Error: ${result.message}`);
    }
  })
  .catch((error) => {
      logger.error(`[Frontend] Get user info failed, Error: ${error}`);
    });
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
