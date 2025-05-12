<template>
  <ImportPCRTmpl :analysis_name="analysis_name" :testing_data="testing_data" ref="ref_import_ppcr_tmpl" />
</template>

<script setup>
// 導入模組
import { ref, onMounted } from 'vue';
import { useStore } from 'vuex';

// 導入 composable
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';
import { setAnalysisID } from '@/composables/checkAnalysisStatus';
import getTestingData from '@/composables/useGetTestingData';

// 元件
import ImportPCRTmpl from '@/components/ImportPCRQsepViews/ImportPCRTmpl.vue';

// consts
const analysis_name = 'HTD';
const ref_import_ppcr_tmpl = ref(null);
const testing_data = ref([]);

// store
const store = useStore();

// 使用者身份
const is_login = ref(false);
const user_info = ref(null);

// 當前的分析 ID
const currentAnalysisID = ref(null);

// 掛載時
onMounted(async () => {
  // 取得使用者身份
  const { login_status } = updateGetUserInfo();
  is_login.value = login_status.value.is_login;
  user_info.value = login_status.value.user_info;

  // 先嘗試取得當前的分析 ID, 如果沒有則建立新的分析 ID
  currentAnalysisID.value = store.getters['analysis_setting/getCurrentAnalysisID'];
  setAnalysisID(store, 'HTD');

  // 取得測試資料集
  testing_data.value = await getTestingData('HTD');
});
</script>
