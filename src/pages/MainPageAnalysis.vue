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

    </div>

  </q-page>
</template>

<script setup>
/* Import modules */
import { ref, onMounted, watch } from 'vue';
import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';

// Import views
import ImportApoe from '@/components/ImportViews/ImportApoe.vue';
import ImportMthfr from '@/components/ImportViews/ImportMthfr.vue';

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

// 取得 settingProps, 當前試劑
const currentReagent = () => {
  return store.getters["analysis_setting/getSettingProps"].reagent;
};

// 掛載時
onMounted(() => {
  // 檢查帳號狀態, 若未開通則跳轉到 not-active
  // useValidateAccountStatus($q, router, store);
});

// 監聽 Product
watch(currentProduct, () => {
  // 如果 Product 改變, 則清空 currentAnalysisID
  store.commit('analysis_setting/initCurrentAnalysisID');
});

</script>
