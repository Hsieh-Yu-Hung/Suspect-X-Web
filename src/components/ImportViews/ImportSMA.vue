<template>
  <ImportSMAQsep v-if="getCurrentInstrument() == 'qsep100'" ref="ref_import_sma_qsep"/>
  <qPCRImportSection v-else ref="ref_qPCRImportSection"/>
</template>

<script setup>
// 導入模組
import { ref, onMounted } from 'vue';
import { useStore } from 'vuex';

// 導入 composable
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';
import { setAnalysisID } from '@/composables/checkAnalysisStatus';

// 元件
import qPCRImportSection from '@/components/SMAImportViewComp/ImportSMAqPCR.vue';
import ImportSMAQsep from '@/components/SMAImportViewComp/ImportSMAQsep.vue';

// store
const store = useStore();

// 使用者身份
const is_login = ref(false);
const user_info = ref(null);

// 控制 qPCRImportSection
const ref_qPCRImportSection = ref(null);
const ref_import_sma_qsep = ref(null);

// 當前的分析 ID
const currentAnalysisID = ref(null);

// 取得 instrument
const getCurrentInstrument = () => {
  return store.getters["analysis_setting/getSettingProps"].instrument;
}

// functions

// 執行資料集
async function runTestingDataset(dataset_name) {
  if (getCurrentInstrument() == 'qsep100') {
    ref_import_sma_qsep.value.runTestingDataset(dataset_name);
  } else {
    ref_qPCRImportSection.value.runTestingDataset(dataset_name);
  }
}

// Expose
defineExpose({
  runTestingDataset,
});

// 掛載時
onMounted(() => {
  // 取得使用者身份
  const { login_status } = updateGetUserInfo();
  is_login.value = login_status.value.is_login;
  user_info.value = login_status.value.user_info;

  // 先嘗試取得當前的分析 ID, 如果沒有則建立新的分析 ID
  currentAnalysisID.value = store.getters['analysis_setting/getCurrentAnalysisID'];
  setAnalysisID(store, 'SMA');
});

</script>
