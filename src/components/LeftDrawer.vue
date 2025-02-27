<template>
  <div class="drawer-content">
    <q-btn glossy label="Debug" @click="debug" icon="bug_report" />
    <q-btn glossy label="USER" @click="print_user_info" icon="account_circle" />
  </div>
</template>

<script setup>
import { useStore } from 'vuex';

// Import modules
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';
import { getAnalysisResult } from '@/firebase/firebaseDatabase.js';

// 使用者身份
const { login_status } = updateGetUserInfo();

// Store
const store = useStore();

/* functions */

// Test check file format
async function debug() {
  // 取得 currentSettingProps
  const currentSettingProps = store.getters["analysis_setting/getSettingProps"];
  // 取得 currentDisplayAnalysis
  const currentDisplayAnalysis = {
    analysis_uuid: store.getters["analysis_setting/getCurrentDisplayAnalysisID"].analysis_uuid,
    analysis_name: store.getters["analysis_setting/getCurrentDisplayAnalysisID"].analysis_name,
  }
  const analysis_name_to_get = currentSettingProps.reagent === "accuinSma4" ? "SMAv4" : currentDisplayAnalysis.analysis_name;
  // 取得當前的分析結果
  const currentAnalysisResult = await getAnalysisResult(
    login_status.value.user_info.uid,
    analysis_name_to_get,
    currentDisplayAnalysis.analysis_uuid,
  );
  console.log("currentAnalysisResult: ", currentAnalysisResult);
}

// Get user info
function print_user_info() {
  console.log("is_login: ", login_status.value.is_login);
  console.log("user_info: ", login_status.value.user_info);
}

</script>

<style scoped>
.drawer-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 20px;
}
</style>
