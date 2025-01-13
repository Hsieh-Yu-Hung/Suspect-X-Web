// 登入時設定登入狀態
export function set_login_status (state, login_status) {
  state.is_login = login_status.is_login;
  state.user_uid = login_status.uid;
  state.user_role = login_status.role;
  state.user_email = login_status.email;
  state.user_organization = login_status.organization;
  state.account_approved = login_status.account_approved;
}

// 登出時設初始化
export function init_login_status (state) {
  state.is_login = false;
  state.user_uid = null;
  state.user_role = null;
  state.user_email = null;
  state.user_organization = null;
  state.account_approved = false;
}
