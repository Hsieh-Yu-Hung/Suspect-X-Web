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

      <!-- APOE -->
      <div class="col " v-if="currentProduct() == 'apoe-import'">
        <ImportApoe class="q-ma-none" />
      </div>

      <!-- MTHFR -->
      <div class="col " v-else-if="currentProduct() == 'mthfr-import'">
        <ImportMthfr class="q-ma-none" />
      </div>

      <!-- NUDT15 -->
      <div class="col " v-else-if="currentProduct() == 'nudt15'">
        <ImportNudt15 class="q-ma-none" />
      </div>

      <!-- FXS -->
      <div class="col " v-else-if="currentProduct() == 'fx'">
        <ImportFXS class="q-ma-none" />
      </div>

      <!-- HTD -->
      <div class="col " v-else-if="currentProduct() == 'hd'">
        <ImportHTD class="q-ma-none" />
      </div>

      <!-- SMA -->
      <div class="col " v-else-if="currentProduct() == 'sma'">
        <ImportSMA class="q-ma-none" />
      </div>

    </div>

  </q-page>
</template>

<script setup>
/* Import modules */
import { onMounted, watch } from 'vue';
import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';
import { v4 as uuidv4 } from 'uuid';

// Import views
import ImportApoe from '@/components/ImportViews/ImportApoe.vue';
import ImportMthfr from '@/components/ImportViews/ImportMthfr.vue';
import ImportNudt15 from '@/components/ImportViews/ImportNudt15.vue';
import ImportFXS from '@/components/ImportViews/ImportFXS.vue';
import ImportHTD from '@/components/ImportViews/ImportHTD.vue';
import ImportSMA from '@/components/ImportViews/ImportSMA.vue';

// 導入模組 composable
import { useValidateAccountStatus } from '@/composables/accessStoreUserInfo.js';

// 導入元件
import AnalysisSettings from '@/components/AnalysisSettings.vue';

// 取得 Quasar 和 Router 和 store
const $q = useQuasar();
const router = useRouter();
const store = useStore();

// 取得 settingProps, 當前產品
const currentProduct = () => {
  return store.getters["analysis_setting/getSettingProps"].product;
};

// 掛載時
onMounted(() => {
  // 檢查帳號狀態, 若未開通則跳轉到 not-active
  useValidateAccountStatus($q, router, store);
});

// 監聽 Product
watch(currentProduct, (newVal, oldVal) => {
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
