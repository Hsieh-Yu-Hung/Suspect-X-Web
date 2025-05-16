<template>
  <q-page>

    <!-- 設定面板 -->
    <div class="row justify-between q-mt-lg q-mx-xl">
      <div class="col">
        <AnalysisSettings></AnalysisSettings>
      </div>
    </div>

    <!-- 輸入面板 -->
    <div class="row justify-between q-mt-lg q-mx-xl">

      <!-- =========================== Imports =========================== -->

      <!-- APOE -->
      <div class="col " v-if="currentProduct() == 'apoe-import'">
        <ImportApoe class="q-ma-none" ref="ref_import_apoe" />
      </div>

      <!-- MTHFR -->
      <div class="col " v-else-if="currentProduct() == 'mthfr-import'">
        <ImportMthfr class="q-ma-none" ref="ref_import_mthfr" />
      </div>

      <!-- NUDT15 -->
      <div class="col " v-else-if="currentProduct() == 'nudt15'">
        <ImportNudt15 class="q-ma-none" ref="ref_import_nudt15" />
      </div>

      <!-- FXS -->
      <div class="col " v-else-if="currentProduct() == 'fx'">
        <ImportFXS class="q-ma-none" ref="ref_import_fxs" />
      </div>

      <!-- HTD -->
      <div class="col " v-else-if="currentProduct() == 'hd'">
        <ImportHTD class="q-ma-none" ref="ref_import_htd" />
      </div>

      <!-- SMA -->
      <div class="col " v-else-if="currentProduct() == 'sma'">
        <ImportSMA class="q-ma-none" ref="ref_import_sma" />
      </div>

      <!-- THAL ALPHA -->
      <div class="col " v-else-if="currentProduct() == 'thal-import-alpha'">
        <ImportThalAlpha class="q-ma-none" />
      </div>

      <!-- THAL BETA -->
      <div class="col " v-else-if="currentProduct() == 'thal-import-beta'">
        <ImportThalBeta class="q-ma-none" ref="ref_import_thal_beta" />
      </div>

      <!-- =========================== Inputs =========================== -->

      <!-- Thal -->
      <div class="col " v-else-if="currentProduct() == 'thal'">
        <InputThal />
      </div>

      <!-- Alcohol -->
      <div class="col " v-else-if="currentProduct() == 'alcohol'">
        <InputAlcohol />
      </div>

      <!-- APOE -->
      <div class="col " v-else-if="currentProduct() == 'apoe'">
        <InputApoe />
      </div>

      <!-- CVD -->
      <div class="col " v-else-if="currentProduct() == 'cvd'">
        <InputCvd />
      </div>

      <!-- B27 -->
      <div class="col " v-else-if="currentProduct() == 'b27'">
        <InputB27 />
      </div>

      <!-- CYP1A2 -->
      <div class="col " v-else-if="currentProduct() == 'cyp1a2'">
        <InputCyp1a2 />
      </div>

      <!-- CD -->
      <div class="col " v-else-if="currentProduct() == 'cd'">
        <InputCd />
      </div>

      <!-- F2F5 -->
      <div class="col " v-else-if="currentProduct() == 'f2f5'">
        <InputF2f5 />
      </div>

      <!-- PD -->
      <div class="col " v-else-if="currentProduct() == 'pd'">
        <InputPd />
      </div>

      <!-- HFE -->
      <div class="col " v-else-if="currentProduct() == 'hfe'">
        <InputHfe />
      </div>

      <!-- LCT -->
      <div class="col " v-else-if="currentProduct() == 'lct'">
        <InputLct />
      </div>

      <!-- NOTCH3 -->
      <div class="col " v-else-if="currentProduct() == 'notch3'">
        <InputNotch3 />
      </div>

      <!-- MTHFR1 -->
      <div class="col " v-else-if="currentProduct() == 'mthfr-input'">
        <InputMthfr1 v-if="currentReagent() == 'accuinMTHFR1'" />
        <InputMthfr2 v-else-if="currentReagent() == 'accuinMTHFR2'" />
      </div>

    </div>

    <!-- 測試面板開關 -->
    <div class="row justify-between q-mt-lg q-mx-xl">
      <!-- DevMode 開關-->
      <div v-if="is_dev_mode">
        <q-toggle
          v-model="switch_dev_mode"
          :label="switch_dev_mode"
          true-value="DevMode: ON"
          false-value="DevMode: OFF"
          size="lg"
          color="pink-7"
        />
      </div>
    </div>

    <!-- 測試面版 -->
    <div class="row justify-between q-mt-lg q-mx-xl" v-if="is_dev_mode && switch_dev_mode === 'DevMode: ON' && importProductArray.includes(currentProduct())">
      <TestingTable :current_product="currentProduct()" :current_reagent="currentReagent()" ref="testingTable" @runDataset="runDataset" />
    </div>

  </q-page>
</template>

<script setup>
/* Import modules */
import { onMounted, watch, ref } from 'vue';
import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';
import { v4 as uuidv4 } from 'uuid';

// 導入模組 composable
import { useValidateAccountStatus } from '@/composables/accessStoreUserInfo.js';
import { isDevMode } from '@/composables/accessStoreUserInfo.js';

// 導入其他元件
import AnalysisSettings from '@/components/AnalysisSettings.vue';
import TestingTable from '@/components/TestingTable.vue';

// Import views
import ImportApoe from '@/components/ImportViews/ImportApoe.vue';
import ImportMthfr from '@/components/ImportViews/ImportMthfr.vue';
import ImportNudt15 from '@/components/ImportViews/ImportNudt15.vue';
import ImportFXS from '@/components/ImportViews/ImportFXS.vue';
import ImportHTD from '@/components/ImportViews/ImportHTD.vue';
import ImportSMA from '@/components/ImportViews/ImportSMA.vue';
import ImportThalAlpha from '@/components/ImportViews/ImportThalAlpha.vue';
import ImportThalBeta from '@/components/ImportViews/ImportThalBeta.vue';

// Input views
import InputThal from '@/components/InputViews/InputThal.vue';
import InputAlcohol from '@/components/InputViews/InputAlcohol.vue';
import InputApoe from '@/components/InputViews/InputApoe.vue';
import InputCvd from '@/components/InputViews/InputCvd.vue';
import InputB27 from '@/components/InputViews/InputB27.vue';
import InputCyp1a2 from '@/components/InputViews/InputCyp1a2.vue';
import InputCd from '@/components/InputViews/InputCd.vue';
import InputF2f5 from '@/components/InputViews/InputF2f5.vue';
import InputPd from '@/components/InputViews/InputPd.vue';
import InputHfe from '@/components/InputViews/InputHfe.vue';
import InputLct from '@/components/InputViews/InputLct.vue';
import InputNotch3 from '@/components/InputViews/InputNotch3.vue';
import InputMthfr1 from '@/components/InputViews/InputMthfr1.vue';
import InputMthfr2 from '@/components/InputViews/InputMthfr2.vue';

// 取得 Quasar 和 Router 和 store
const $q = useQuasar();
const router = useRouter();
const store = useStore();

// Import Products
const importProductArray = ['apoe-import', 'mthfr-import', 'nudt15', 'fx', 'hd', 'sma', 'thal-import-alpha', 'thal-import-beta'];

// DevMode 開關
const is_dev_mode = ref(false);
const switch_dev_mode = ref("DevMode: ON");

// 取得元件
const ref_import_fxs = ref(null);
const ref_import_htd = ref(null);
const ref_import_thal_beta = ref(null);
const ref_import_sma = ref(null);
const ref_import_apoe = ref(null);
const ref_import_mthfr = ref(null);
const ref_import_nudt15 = ref(null);

// 取得 testingTable
const testingTable = ref(null);

// 取得 settingProps, 當前產品
const currentProduct = () => {
  return store.getters["analysis_setting/getSettingProps"].product;
};

// 取得 settingProps, 當前試劑
const currentReagent = () => {
  return store.getters["analysis_setting/getSettingProps"].reagent;
};

// 執行資料集
async function runDataset(dataset_name) {
  const current_product = currentProduct();
  switch (current_product) {
    case 'fx':
      ref_import_fxs.value.runTestingDataset(dataset_name);
      break;
    case 'hd':
      ref_import_htd.value.runTestingDataset(dataset_name);
      break;
    case 'thal-import-beta':
      ref_import_thal_beta.value.runTestingDataset(dataset_name);
      break;
    case 'sma':
      ref_import_sma.value.runTestingDataset(dataset_name);
      break;
    case 'apoe-import':
      ref_import_apoe.value.runTestingDataset(dataset_name);
      break;
    case 'mthfr-import':
      ref_import_mthfr.value.runTestingDataset(dataset_name);
      break;
    case 'nudt15':
      ref_import_nudt15.value.runTestingDataset(dataset_name);
      break;
    default:
      break;
  }
}

// 掛載時
onMounted(async () => {
  // 檢查帳號狀態, 若未開通則跳轉到 not-active
  useValidateAccountStatus($q, router, store);

  // 取得 DevMode 開關
  is_dev_mode.value = await isDevMode();
});

// 監聽 Product
watch(currentProduct, async (newVal, oldVal) => {
  if (newVal !== oldVal){
    // 如果 Product 改變, 則清空 currentAnalysisID
    store.commit('analysis_setting/initCurrentAnalysisID');

    // 決定分析名稱
    const analysis_name = newVal === 'apoe-import' ? 'APOE'
                        : newVal === 'mthfr-import' ? 'MTHFR'
                        : newVal === 'nudt15' ? 'NUDT15'
                        : newVal === 'fx' ? 'FXS'
                        : newVal === 'hd' ? 'HTD'
                        : newVal === 'sma' ? 'SMA'
                        : newVal === 'thal-import-alpha' ? 'THAL_ALPHA'
                        : newVal === 'thal-import-beta' ? 'THAL_BETA'
                        : null;

    // 建立新的分析 ID
    const new_id = `analysis_${uuidv4()}`;
    store.commit('analysis_setting/updateCurrentAnalysisID', {
      analysis_name: analysis_name,
      analysis_uuid: new_id,
    });
  }
});

</script>
