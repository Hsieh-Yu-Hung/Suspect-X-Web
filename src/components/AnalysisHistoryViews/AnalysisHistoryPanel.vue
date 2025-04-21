<template>
  <div style="margin-bottom: 0.3em; display: flex; flex-direction: column; justify-content: flex-start; align-items: flex-start; border: 1px solid #e0e0e0; padding: 0.5em; border-radius: 0.5em;">

    <!-- 分析名稱/展開按鈕 -->
    <div style="display: flex; align-items: center; gap: 1em; justify-content: space-between; width: 100%; margin-bottom: 0.5em;">
      <span class="text-bold text-blue-grey-7 text-h6 text-uppercase">{{ props.analysisName }}</span>
    </div>

    <!-- 分析歷史列表 -->
    <div style="width: 100%;">
      <q-table
        :rows="analysisHistoryRows"
        :columns="displayAnalysisHistoryColumns"
        row-key="name"
        :rows-per-page-options="[1000]"
        dense
        flat
      >
        <template v-slot:body="props">
          <q-tr :props="props" :class="{ 'selected-row': props.row.id === selectedRecordId }">
            <q-td key="Date" :props="props">
              <div style="display: flex; flex-direction: column; align-items: center;">
                <span>{{ props.row.date.split(' ')[0] }}</span>
                <span>{{ props.row.date.split(' ')[1] }}</span>
              </div>
            </q-td>
            <q-td key="Name" :props="props">
              <div style="display: flex; align-items: center; gap: 1em; border: 1px solid #e0e0e0; border-radius: 0.5em; padding: 0.5em;">
                <q-input style="width: 100%;" v-model="props.row.name" dense color="green-8" :disable="!props.row.editable" />
                <q-btn :icon="!props.row.editable ? 'edit' : 'check'"
                       color="grey-2"
                       dense rounded no-caps label=""
                       :text-color="!props.row.editable ? 'black' : 'green-8'"
                       @click="editID(props.row.id)" />
              </div>
            </q-td>
            <q-td key="Config" :props="props">
              <div style="display: flex; flex-direction: column; align-items: center;">
                <q-chip :color="getInstrumentLabel(props.row.config.instrument).color" dense rounded no-caps :label="getInstrumentLabel(props.row.config.instrument).label" />
                <q-chip :color="getReagentLabel(props.row.config.reagent).color" dense rounded no-caps :label="getReagentLabel(props.row.config.reagent).label" />
              </div>
            </q-td>
            <q-td key="QC" :props="props">
              <div style="display: flex; flex-direction: column; align-items: center;">
                <span class="text-bold" :class="getQCLabelColor(getQCLabel(props.row.qc))">{{ getQCLabel(props.row.qc) }}</span>
              </div>
            </q-td>
            <q-td key="View" :props="props">
              <q-btn icon="visibility" glossy color="light-blue-1" dense rounded no-caps label="" text-color="indigo-6" @click="selectRecord(props.row.id)" />
            </q-td>
          </q-tr>
        </template>
      </q-table>
    </div>
  </div>
</template>

<script setup>
// 導入模組
import { ref, onMounted, computed } from 'vue';
import { useStore } from 'vuex';
import { useQuasar } from 'quasar';
import { getAnalysisResult, update_userAnalysisData } from '@/firebase/firebaseDatabase';
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';

// 使用者身份
const { login_status } = updateGetUserInfo();

// 定義 Store, Quasar
const store = useStore();
const $q = useQuasar();

// 當前選中的記錄 ID
const selectedRecordId = ref(null);

// Props
const props = defineProps({
  analysisName: {
    type: String,
    required: true
  }
});

// 定義 RECORD
const RECORD = (DATE, ID, NAME, INSTRUMENT, REAGENT, QC) => {
  const editable = false;
  return {
    date: DATE,
    id: ID,
    name: NAME,
    editable: editable,
    config: {
      instrument: INSTRUMENT,
      reagent: REAGENT
    },
    qc: QC
  }
}

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

// 分析歷史列表
const analysisHistoryRows = ref([]);
const analysisHistoryColumns = [
  {
    name: 'Date',
    label: 'Date',
    field: 'date',
    align: 'center',
    headerClasses: 'text-bold text-blue-grey-7'
  },
  {
    name: 'ID',
    label: 'ID',
    field: 'id',
  },
  {
    name: 'Name',
    label: 'Name',
    field: 'name',
    align: 'center',
    headerClasses: 'text-bold text-blue-grey-7'
  },
  {
    name: 'Config',
    label: 'Config',
    field: 'config',
    align: 'center',
    headerClasses: 'text-bold text-blue-grey-7'
  },
  {
    name: 'QC',
    label: 'QC',
    field: 'qc',
    align: 'center',
    headerClasses: 'text-bold text-blue-grey-7'
  },
  {
    name: 'View',
    label: '',
    field: 'view',
    align: 'center'
  }
];
const displayAnalysisHistoryColumns = computed(() => {
  return analysisHistoryColumns.filter(column => column.name !== 'ID');
});

// 控制展開
const isExpanded = ref(false);

// 取得當前分析資料庫路徑
const getCurrentAnalysisDatabasePath = (analysis_name) => {
  switch (analysis_name) {
    case AnalysisNames.APOE:
      return 'apoe_result';
    case AnalysisNames.FXS:
      return 'fxs_result';
    case AnalysisNames.SMA:
      return 'sma_result';
    case AnalysisNames.HTD:
      return 'htd_result';
    case AnalysisNames.MTHFR:
      return 'mthfr_result';
    case AnalysisNames.NUDT15:
      return 'nudt15_result';
    case AnalysisNames.SMAv4:
      return 'sma_v4_result';
    case AnalysisNames.THAL_BETA:
      return 'thalbeta_result';
    case AnalysisNames.THAL_ALPHA:
      return 'thalalpha_result';
    default:
      return analysis_name;
  }
}

// 編輯ID
async function editID(id) {

  // 顯示 Loading
  $q.loading.show({
    message: 'Updating Database...'
  });

  const row = analysisHistoryRows.value.find(row => row.id === id);
  if (row.editable) {

    // 取得該筆分析資料, 更新 analysis_label
    let editAnalysisResult = await getAnalysisResult(login_status.value.user_info.uid, props.analysisName, row.id);
    editAnalysisResult.analysis_label = row.name;

    // 更新該筆分析資料
    await update_userAnalysisData(
      login_status.value.user_info.uid,
      getCurrentAnalysisDatabasePath(props.analysisName),
      editAnalysisResult,
      editAnalysisResult.analysis_id
    );

    // 特殊處理 THAL_BETA
    if (props.analysisName === "THAL_BETA") {
      // 取得該筆分析資料, 更新 analysis_label
      let editAnalysisConfig = await getAnalysisResult(login_status.value.user_info.uid, "thalbeta_import_config", row.id);
      editAnalysisConfig.analysis_label = row.name;

      // 更新該筆分析資料
      await update_userAnalysisData(
        login_status.value.user_info.uid,
        "thalbeta_import_config",
        editAnalysisConfig,
        row.id
      );
    }

    // 設定為不可編輯
    row.editable = false;

  }
  else {
    // 設定為可編輯
    row.editable = true;
  }

  // 隱藏 Loading
  $q.loading.hide();
}

// 取得QC標籤
const getQCLabel = (qc) => {
  // 特殊處理 BetaThal
  if (props.analysisName === 'THAL_BETA') {
    if (qc.includes('fail-the-criteria')) {
      return 'Fail the Criteria';
    }
    else {
      return 'Meet the Criteria';
    }
  }

  // 特殊處理 SMAv4
  if (props.analysisName === 'SMA') {
    if (Object.values(qc).includes('fail-the-criteria')) {
      return 'Fail the Criteria';
    }
    else {
      return 'Meet the Criteria';
    }
  }

  // 其他分析
  else {
    switch (qc) {
      case 'meet-the-criteria':
        return 'Meet the Criteria';
      case 'fail-the-criteria':
        return 'Fail the Criteria';
      default:
        return 'Unknown';
    }
  }
}

// 取得QC標籤顏色
const getQCLabelColor = (qcLabel) => {
  switch (qcLabel) {
    case 'Meet the Criteria':
      return 'text-green-8';
    case 'Fail the Criteria':
      return 'text-red-8';
    default:
      return 'text-grey-7';
  }
}

// 取得 Instrument Label
const getInstrumentLabel = (instrument) => {
  switch (instrument) {
    case 'qsep100':
      return { label: 'Qsep 100', color: 'indigo-2' };
    case 'qs3':
      return { label: 'QuantStudio™ 3', color: 'teal-3' };
    case 'tower':
      return { label: 'qTOWER³', color: 'cyan-4' };
    case 'z480':
      return { label: 'Roche Cobas® z 480', color: 'blue-11' };
    case 'sanger':
      return { label: 'Sanger Sequencer', color: 'purple-2' };
    default:
      return { label: 'Unknown', color: 'grey-2' };
  }
}

// 取得 Reagent Label
const getReagentLabel = (reagent) => {
  switch (reagent) {
    case 'accuinFx1':
      return { label: 'ACCUiN BioTech Fragile X v1', color: 'amber-2' };
    case 'accuinFx2':
      return { label: 'ACCUiN BioTech Fragile X v2', color: 'amber-4' };
    case 'accuinSma1':
      return { label: 'ACCUiN BioTech SMA v1', color: 'deep-orange-2' };
    case 'accuinSma2':
      return { label: 'ACCUiN BioTech SMA v2', color: 'deep-orange-3' };
    case 'accuinSma3':
      return { label: 'ACCUiN BioTech SMA v3', color: 'deep-orange-4' };
    case 'accuinSma4':
      return { label: 'SMA CE v1', color: 'pink-3' };
    case 'accuinMTHFR1':
      return { label: 'ACCUiN BioTech MTHFR v1', color: 'light-green-2' };
    case 'accuinMTHFR2':
      return { label: 'ACCUiN BioTech MTHFR v2', color: 'light-green-4' };
    case 'accuinMTHFR3':
      return { label: 'ACCUiN BioTech MTHFR v3', color: 'green-4' };
    case 'accuinNUDT151':
      return { label: 'ACCUiN BioTech NUDT15 v1', color: 'lime-2' };
    case 'accuinNUDT152':
      return { label: 'ACCUiN BioTech NUDT15 v2', color: 'lime-5' };
    case 'accuinHD1':
      return { label: 'ACCUiN BioTech HTD v1', color: 'brown-3' };
    case 'accuinApoe1':
      return { label: 'ACCUiN BioTech APOE v1', color: 'red-3' };
    case 'accuinTHALAlpha':
      return { label: 'ACCUiN BioTech THAL Alpha', color: 'deep-purple-2' };
    case 'accuinTHALBeta':
      return { label: 'ACCUiN BioTech THAL Beta', color: 'deep-purple-11' };
    default:
      return { label: 'Unknown', color: 'grey-2' };
  }
}

// 更新 Row
async function updateAnalysisHistoryRows() {
  const analysisResult = await getAnalysisResult(login_status.value.user_info.uid, props.analysisName);
  if (props.analysisName === 'SMA') {
    analysisHistoryRows.value = analysisResult.map(result => RECORD(result.analysis_time, result.analysis_id, result.analysis_label, result.config.V1.instrument, result.config.V1.reagent, result.qc_status));
  }
  else {
    analysisHistoryRows.value = analysisResult.map(result => RECORD(result.analysis_time, result.analysis_id, result.analysis_label, result.config.instrument, result.config.reagent, result.qc_status));
  }
}

// 選中 Record
function selectRecord(id) {
  selectedRecordId.value = id;

  // 更新當前選中呈現的檔案表格
  store.commit('analysis_history_data/set_current_display_record_id', id);
  store.commit('analysis_history_data/set_current_selected_product', props.analysisName);

  // 更新當前選中呈現的 ResultView
  const selectedAnalysisID = {
    analysis_name: props.analysisName,
    analysis_uuid: id
  }
  store.commit('analysis_setting/updateCurrentDisplayAnalysisID', selectedAnalysisID);
}

// 更新當前選中呈現的 Record ID
function updateCurrentDisplayRecordID() {
  // 取得 Store 中的當前選中呈現的 Record ID
  const storeSelectedRecordId = store.getters['analysis_history_data/getCurrentDisplayRecordID'];

  // 如果 Store 中沒有當前選中呈現的 Record ID，則設定為 selectedRecordId
  if (!storeSelectedRecordId) {
    store.commit('analysis_history_data/set_current_display_record_id', selectedRecordId.value);
  }
  else {
    selectedRecordId.value = storeSelectedRecordId;
  }
}

// 掛載
onMounted(() => {
  updateAnalysisHistoryRows();
  updateCurrentDisplayRecordID();
});

</script>

<style scoped>
.expand-analysis {
  height: 100%;
  overflow: auto;
}
.collapse-analysis {
  height: 4em;
  overflow: hidden;
}
.selected-row {
  background-color: #fff9c4 !important;
  border: 1px solid black !important;
}
</style>