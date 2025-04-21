<template>
  <q-page class="flex no-wrap">

    <!-- 分析歷史總覽區 -->
    <q-card class="q-ma-sm" style="min-width: 52em; height: 100%; overflow: auto;">

      <!-- 標題 -->
      <q-card-section style="display: flex; justify-content: space-between; align-items: center;">
        <div style="display: flex; align-items: center;">
          <span class="text-subtitle1 text-bold text-blue-grey-7">Product:</span>
          <div style="display: flex; align-items: center; gap: 10px; margin-left: 10px;">
            <q-select
              dense
              v-model="currentDisplayProduct"
              :options="productOptions"
              option-label="label"
              option-value="value"
              class="q-ml-sm"
              style="width: 10em;"
              color="deep-orange-6" outlined
             />
          </div>
        </div>
        <div class="text-h5 text-bold text-uppercase text-blue-grey-7" style="display: flex; align-items: center; gap: 10px; margin-right: 0.5em;">
          <q-icon size="1.5em" name="history" />
          <span>Analysis History</span>
        </div>
      </q-card-section>

      <!-- 分隔線 -->
      <q-separator />

      <!-- 歷史列表 -->
      <q-card-section>

        <!-- 依照 Analysis 名稱分類 -->
        <div style="width: 50em;">

          <!-- APOE -->
          <AnalysisHistoryPanel :analysisName="AnalysisNames.APOE" :style="{ display: currentDisplayProduct.value === AnalysisNames.APOE ? 'block' : 'none' }" />

          <!-- FXS -->
          <AnalysisHistoryPanel :analysisName="AnalysisNames.FXS" :style="{ display: currentDisplayProduct.value === AnalysisNames.FXS ? 'block' : 'none' }" />

          <!-- SMA -->
          <AnalysisHistoryPanel :analysisName="AnalysisNames.SMA" :style="{ display: currentDisplayProduct.value === AnalysisNames.SMA ? 'block' : 'none' }" />

          <!-- HTD -->
          <AnalysisHistoryPanel :analysisName="AnalysisNames.HTD" :style="{ display: currentDisplayProduct.value === AnalysisNames.HTD ? 'block' : 'none' }" />

          <!-- MTHFR -->
          <AnalysisHistoryPanel :analysisName="AnalysisNames.MTHFR" :style="{ display: currentDisplayProduct.value === AnalysisNames.MTHFR ? 'block' : 'none' }" />

          <!-- NUDT15 -->
          <AnalysisHistoryPanel :analysisName="AnalysisNames.NUDT15" :style="{ display: currentDisplayProduct.value === AnalysisNames.NUDT15 ? 'block' : 'none' }" />

          <!-- SMAv4 -->
          <AnalysisHistoryPanel :analysisName="AnalysisNames.SMAv4" :style="{ display: currentDisplayProduct.value === AnalysisNames.SMAv4 ? 'block' : 'none' }" />

          <!-- THAL_BETA -->
          <AnalysisHistoryPanel :analysisName="AnalysisNames.THAL_BETA" :style="{ display: currentDisplayProduct.value === AnalysisNames.THAL_BETA ? 'block' : 'none' }" />

          <!-- THAL_ALPHA -->
          <AnalysisHistoryPanel :analysisName="AnalysisNames.THAL_ALPHA" :style="{ display: currentDisplayProduct.value === AnalysisNames.THAL_ALPHA ? 'block' : 'none' }" />

        </div>
      </q-card-section>

    </q-card>

    <!-- 檔案列表區 -->
    <q-card class="q-ma-sm" style="min-width: 53em; height: 100%">

      <!-- 標題 -->
      <q-card-section>
        <div class="text-h5 text-bold text-uppercase text-blue-grey-7" style="display: flex; justify-content: flex-end; align-items: center; gap: 10px; margin-right: 0.5em;">
          <q-icon size="1.5em" name="folder_open" />
          <span>File Bucket</span>
        </div>
      </q-card-section>

      <!-- 分隔線 -->
      <q-separator />

      <!-- Inputs 檔案列表 -->
      <q-card-section>
        <FileIOTable
          tableTitle="Inputs"
          tableSource="input"
          ref="inputTable"
        />
      </q-card-section>

      <!-- 分隔線 -->
      <q-separator />

      <!-- Outputs 檔案列表 -->
      <q-card-section>
        <FileIOTable
          tableTitle="Outputs"
          tableSource="output"
          ref="outputTable"
        />
      </q-card-section>

    </q-card>

  </q-page>
</template>

<script setup>
// 導入模組
import { ref, onMounted, watch, nextTick } from 'vue';
import { useStore } from 'vuex';
import AnalysisHistoryPanel from '../components/AnalysisHistoryViews/AnalysisHistoryPanel.vue';
import FileIOTable from '../components/AnalysisHistoryViews/FileIOTable.vue';

// 定義 Store
const store = useStore();

// 定義 Ref
const inputTable = ref(null);
const outputTable = ref(null);

// 定義 Analysis 名稱
const AnalysisNames = {
  APOE: 'APOE',
  FXS: 'FXS',
  SMA: 'SMA',
  HTD: 'HTD',
  MTHFR: 'MTHFR',
  NUDT15: 'NUDT15',
  SMAv4: 'SMAv4',
  THAL_BETA: 'THAL_BETA',
  THAL_ALPHA: 'THAL_ALPHA',
}

const getFormalAnalysisName = (analysisName) => {
  switch (analysisName) {
    case AnalysisNames.APOE:
      return 'APOE';
    case AnalysisNames.FXS:
      return 'FXS';
    case AnalysisNames.SMA:
      return 'SMA';
    case AnalysisNames.HTD:
      return 'HTD';
    case AnalysisNames.MTHFR:
      return 'MTHFR';
    case AnalysisNames.NUDT15:
      return 'NUDT15';
    case AnalysisNames.SMAv4:
      return 'SMA CE';
    case AnalysisNames.THAL_BETA:
      return '(Name) THAL_BETA';
    case AnalysisNames.THAL_ALPHA:
      return '(Name) THAL_ALPHA';
  }
}

// 當前選中的 Product
const productOptions = Object.values(AnalysisNames).map(name => ({
  label: getFormalAnalysisName(name),
  value: name,
}));
const currentDisplayProduct = ref(productOptions[0]);

// 更新當前選中呈現的 Product
function updateCurrentDisplayProduct() {
  // 取得 Store 中的當前選中呈現的 Product
  const storeDisplayProduct = store.getters['analysis_history_data/getCurrentDisplayProduct'];

  // 如果 Store 中沒有當前選中呈現的 Product，則設定為 currentDisplayProduct
  if (!storeDisplayProduct) {
    store.commit('analysis_history_data/set_current_display_product', currentDisplayProduct.value);
  }
  else {
    currentDisplayProduct.value = storeDisplayProduct;
  }
}

// 掛載
onMounted(async () => {
  // 更新當前選中呈現的 Product
  updateCurrentDisplayProduct();
});

// 監聽 currentDisplayProduct
watch(currentDisplayProduct, (newValue, oldValue) => {
  if (newValue !== oldValue) {
    // 清除 Table Data
    inputTable.value.clearTableData();
    outputTable.value.clearTableData();

    // 更新當前選中呈現的 Product
    store.commit('analysis_history_data/set_current_display_product', newValue);
  }
});

</script>
