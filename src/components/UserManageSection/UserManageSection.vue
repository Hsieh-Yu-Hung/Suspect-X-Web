<template>

  <!-- 使用者資料管理 -->
  <q-card class="card">

    <!-- Header -->
    <q-card-section>
      <div class="section">
        <span class="text-h6">編輯使用者資料</span>
      </div>
    </q-card-section>

    <!-- 我是分隔線 -->
    <q-separator />

    <!-- Content -->
    <div class="flex flex-center" style="margin-top: 1.5em;" v-if="display_user.length <= 1">
      <span class="subtitle">...目前沒有使用者...</span>
    </div>
    <q-card-section v-else>
      <UserItem v-for="user in display_user"
      :key="user.id"
      :user_info="user"
      :organization_list="display_organization" />
    </q-card-section>
  </q-card>

</template>

<script setup>

// 導入模組
import { ref } from 'vue';

// 導入元件
import UserItem from './UserItem.vue';
import { USER_INFO } from '@/firebase';


// 組織列表
const display_organization = ref(["未選擇"]);




/* Debug Tmp */

// 使用者資料列表
const header = MAKE_HEADER();
const tmpUser = MAKE_USER_INFO("test@test.com", "test_organization", true, "user");
const display_user = ref([header,tmpUser,tmpUser,tmpUser]);

/* functions */

function MAKE_HEADER() {
  const user_info = USER_INFO("", "", "");
  user_info.id = "header_id";
  user_info.email = "人員帳號";
  user_info.login_method = "header_login_method";
  user_info.organization = "所屬組織";
  user_info.role = "帳號身份";
  user_info.account_active = "帳號開通";
  user_info.created_at = "申請日期";
  user_info.updated_at = "更新日期";
  return user_info;
}

function MAKE_USER_INFO(email, organization, account_active, role) {
  const id = "tmp_id";
  const login_method = "tmp_login_method";
  const user_info = USER_INFO(email, id, login_method);
  user_info.organization = organization;
  user_info.account_active = account_active;
  user_info.role = role;
  user_info.created_at = new Date().toLocaleDateString();
  user_info.updated_at = new Date().toLocaleDateString();
  return user_info;
}

</script>

<style scoped>
.card {
  width: 100%;
  overflow: auto;
  height: 100%;
}
.section {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.title {
  font-size: 1.2em;
  font-weight: bold;
}
.subtitle {
  font-size: 1em;
  font-weight: normal;
  font-style: italic;
}
</style>
