// 導入模組
import { ref, onMounted } from 'vue';
import { useStore } from 'vuex';

// 存取 store 的登入狀態
const login_status = ref({
  is_login: false,
  user_info: null
});

// 從 store 回傳 login_status (必須在 onMounted 呼叫)
export function updateGetUserInfo() {
  // 掛載時
  onMounted(() => {
    // 檢查登入狀態
    const store = useStore();
    login_status.value.is_login = store.getters['login_status/getLoginStatus'];
    login_status.value.user_info = store.getters['login_status/getUserInfo'];
  });
  return { login_status };
}

// 取得帳號狀態, 若未開通則跳轉到 not-active
export function useValidateAccountStatus($q, router, store) {

  // 取得登入狀態
  login_status.value.is_login = store.getters['login_status/getLoginStatus'];
  login_status.value.user_info = store.getters['login_status/getUserInfo'];

  // 檢查帳號狀態, 若未開通則跳轉到 not-active
  if(!login_status.value.is_login || !login_status.value.user_info.account_approved){
    $q.loading.show();
    $q.notify({
      message: '帳號未開通, 請先聯繫管理員',
      color: 'deep-orange',
      icon: 'warning',
      timeout: 1500,
      position: 'top'
    });
    setTimeout(() => {
      router.push('/page-not-active');
      $q.loading.hide();
    }, 1500);
  }
}
