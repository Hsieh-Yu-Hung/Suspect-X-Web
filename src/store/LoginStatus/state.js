/* 設定 state */
export default function () {
  return {
    // 是否登入
    is_login: false,
    // 使用者 uid
    user_uid: null,
    // 使用者身份
    user_role: null,
    // 使用者 email
    user_email: null,
    // 使用者組織
    user_organization: null,
    // 帳號開通
    account_approved: false
  }
}


