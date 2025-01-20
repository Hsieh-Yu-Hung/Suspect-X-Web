// 取得登入資訊
export function getLoginStatus (state) {
  return state.is_login;
}

// 取得使用者資訊
export function getUserInfo (state) {
  return {
    uid: state.user_uid,
    role: state.user_role,
    email: state.user_email,
    organization: state.user_organization,
    account_approved: state.account_approved
  };
}
