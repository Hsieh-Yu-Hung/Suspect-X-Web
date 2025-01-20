/* Import modules */

// firebase SDK auth
import { signInWithGoogle, get_login_status } from '@/firebase';

// firebase SDK database
import { dataset_list, USER_INFO, EMAIL_INFO, login_method } from '@/firebase';
import { addLoginInfoDatabase, addEmailListDatabase, getData, getEmailList } from '@/firebase';

// logger
import logger from '@/utility/logger';

/* functions */

// Google 登入
export async function useGoogleLogin(store, router, $q) {

  // 登入狀態
  let status = 'pending';

  await signInWithGoogle()
  .then(async (result) => {
    if (result.status === 'success') {

      // 取得 email_list
      const email_list = await getEmailList();

      // 檢查 email 是否已存在於 email_list 中
      const emailExists = email_list.some(email => email.email === result.user_email);
      if (!emailExists) {
        // 將登入資訊加入到 database (Google 登入沒有輸入密碼)
        const id = result.user_uid;
        const LoginInfo = USER_INFO(result.user_email, login_method.google, id);
        addLoginInfoDatabase(LoginInfo, id);

        // 將 email 加入到 email_list
        const EmailInfo = EMAIL_INFO(result.user_email, login_method.google);
        addEmailListDatabase(EmailInfo);
      }

      // 將 user_info 加入到 store
      storeUserInfo(store, router, $q);

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
    // 如果登入成功，則跳轉
    if (status === 'success') {
      redirect_page(store, router, $q);
    }
  });
}

// 跳轉頁面
function redirect_page(store, router, $q) {

  // 取得 user_info
  const user_info = store.getters['login_status/getUserInfo'];
  const user_account_active = user_info.account_approved;

  // 如果帳號已開通, 則跳轉到 import, 否則跳轉到 not-active
  $q.loading.show({message: 'Redirecting...'});
  setTimeout(() => {
    if(user_account_active){
      router.push('/page-import');
    } else {
      router.push('/page-not-active');
    }
  }, 500);
  $q.loading.hide();
}

// 取得 user_info 並將 user_info 加入到 store
async function storeUserInfo(store, router, $q) {

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

        // 跳轉
        redirect_page(store, router, $q);

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

// 輸出
export function useAccountManagement() {
  return { useGoogleLogin, storeUserInfo, redirect_page };
}
