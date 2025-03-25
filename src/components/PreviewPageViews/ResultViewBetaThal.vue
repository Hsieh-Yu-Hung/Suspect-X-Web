<template>
  <q-card bordered :style="{display: showResult ? 'block' : 'none'}">
    <q-card-section>

      <!-- 標題 -->
      <div class="text-h5 text-uppercase text-bold text-blue-grey-7">
        Screening Result
      </div>

      <!-- 顯示當前被分析的檔案-->
      <div class="q-mt-md row justify-center items-center">

        <!-- 顯示當前被分析的檔案-->
        <div class="col text-subtitle2">
          Current result is from file: '{{ currentAnalysisFile || 'N/A' }}'
        </div>

        <div class="col-2" style="display: flex; justify-content: right; align-items: center;">
          <q-btn
            dense
            :label="toggleDisplayRecords ? 'Pathogenic' : 'All Variants'"
            :color="toggleDisplayRecords ? 'red-2' : 'lime-4'"
            :icon="toggleDisplayRecords ? 'crisis_alert' : 'visibility'"
            text-color="black"
            style="padding: 0 10px"
            @click="toggleDisplayRecords = !toggleDisplayRecords"
          />
        </div>
      </div>

      <!-- Assessment / Result 標籤-->
      <div class="row q-mt-md" style="display: block;">

        <!-- 顯示 Result -->
        <div class="row">
          <div class="col-2 text-h5 text-bold text-subtitle2 text-center" style="margin-block: 1em;">
            Result:
          </div>
          <div class="col text-h5 text-bold text-subtitle2 text-left" style="margin-block: 1em;">
            {{ displayResult }}
          </div>
        </div>

        <!-- 顯示 Assessment -->
        <div class="row">
          <div class="col-2 text-h5 text-bold text-subtitle2 text-center" style="margin-block: 1em;">
            Assessment:
          </div>
          <div class="col text-h5 text-bold text-subtitle2 text-left" style="margin-block: 1em;">
            {{ displayAssessment }}
          </div>
        </div>
      </div>

      <!-- 結果表格 -->
      <div class="q-mt-md">

        <!-- 如果有資料則顯示表格 -->
        <q-table v-if="resultRows.length > 0"
          :rows="resultRows"
          :columns="resultColumns"
          :rows-per-page-options="[100]"
        >
          <!-- 設定表格標題為粗體 -->
          <template v-slot:header-cell="props">
            <q-th :props="props" class="text-blue-grey-7 text-bold">
              {{ props.col.label }}
            </q-th>
          </template>

          <!-- 特殊處理 Variant Type 的顯示 -->
          <template v-slot:body-cell-variantType="props">
            <q-td :props="props">
              <template v-if="props.value && props.value.includes(separator)">
                <div v-for="(item, index) in props.value.split(separator)" :key="index">
                  {{ index + 1 }}. {{ item }}
                </div>
              </template>
              <template v-else>
                {{ props.value }}
              </template>
            </q-td>
          </template>

          <!-- 特殊處理 Variant Name 的顯示 -->
          <template v-slot:body-cell-variantName="props">
            <q-td :props="props">
              <template v-if="props.value && props.value.includes(separator)">
                <div v-for="(item, index) in props.value.split(separator)" :key="index">
                  {{ index + 1 }}. {{ item }}
                </div>
              </template>
              <template v-else>
                {{ props.value }}
              </template>
            </q-td>
          </template>

          <!-- 特殊處理 Disease 的顯示 -->
          <template v-slot:body-cell-disease="props">
            <q-td :props="props">
              <template v-if="props.value && props.value.includes(separator)">
                <div v-for="(item, index) in props.value.split(separator)" :key="index">
                  {{ index + 1 }}. {{ item }}
                </div>
              </template>
              <template v-else>
                {{ props.value }}
              </template>
            </q-td>
          </template>

        </q-table>

        <!-- 如果沒有資料則顯示文字 -->
        <div v-else class="q-mt-md text-center text-subtitle1 text-blue-7">
          -- There is no HBB variant found by Tracy. --
        </div>

      </div>

    </q-card-section>
  </q-card>
</template>

<script setup>

// 導入模組
import { ref, onMounted, watch } from 'vue';
import { useStore } from 'vuex';
import { update_userAnalysisData } from '@/firebase/firebaseDatabase';
import { getCurrentDisplayAnalysisID, getCurrentAnalysisResult } from '@/composables/checkAnalysisStatus.js';
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';

// 定義變數
const showResult = ref(true);
const store = useStore();
const separator = '___SEP_ANNO___';

// 使用者身份
const is_login = ref(false);
const user_info = ref(null);

// 保存當前分析結果
const { login_status } = updateGetUserInfo();
const currentAnalysisResult = ref(null);
const currentSettingProps = ref(null);
const currentDisplayAnalysis = ref({
  analysis_uuid: '',
  analysis_name: '',
});
const currentAnalysisFile = ref('');

// 控制顯示的結果列表
const toggleDisplayRecords = ref(true);
const displayResult = ref('尚未決定');
const displayAssessment = ref('尚未決定');

// 擷取 Genome Position
const getGenomePosition = (row) => {
  return `${row.adjusted_position.chr} : ${row.adjusted_position.start} - ${row.adjusted_position.end}`;
}

// 定義結果表格
const resultRows = ref([]);
const resultColumns = [
  {
    name: "index",
    align: "center",
    label: "",
    field: "index"
  },
  {
    name: "genomicPosition",
    align: "center",
    label: "Genomic Position",
    field: getGenomePosition
  },
  {
    name: "refSeq",
    align: "center",
    label: "Ref",
    field: "ref"
  },
  {
    name: "altSeq",
    align: "center",
    label: "Alt",
    field: "alt"
  },
  {
    name: "variantClass",
    align: "center",
    label: "Variant Class",
    field: "type"
  },
  {
    name: "genotype",
    align: "center",
    label: "Genotype",
    field: "genotype"
  },
  {
    name: "variantType",
    align: "center",
    label: "Variant Type",
    field: "Variant_Type"
  },
  {
    name: "variantName",
    align: "center",
    label: "Variant Name",
    field: "Present_Name"
  },
  {
    name: "disease",
    align: "left",
    label: "Disease",
    field: "Disease_Type"
  },
];

// 更新結果表格和當前被分析的檔案
function updateResultTable(result) {
  // 載入 resultRows, 排序
  resultRows.value = result.resultObj.resultTable.rows;
  resultRows.value.sort((a, b) => {
    const variantTypeA = a.Disease_Type || '';
    const variantTypeB = b.Disease_Type || '';
    if (variantTypeA === variantTypeB) return 0;
    return variantTypeA > variantTypeB ? -1 : 1;
  });

  const file_name = result.resultObj.input_file;
  currentAnalysisFile.value = file_name.split('/').pop();
}

// 調整表格顯示
const adjustTableDisplay = () => {
  // 如果 toggleDisplayRecords 為 false, 則將 resultRows 中Disease_Type, Present_Name, Variant_Type 都是 null的行移除
  if (toggleDisplayRecords.value) {
    resultRows.value = resultRows.value.filter(row => row.Disease_Type !== null && row.Present_Name !== null && row.Variant_Type !== null);
  }
  // 否則重新載入 resultRows
  else {
    updateResultTable(currentAnalysisResult.value);
  }
}

// 更新導出結果
function updateExportResults() {
  const ResultData = Object.values(currentAnalysisResult.value.resultObj);
  let export_result = JSON.parse(JSON.stringify(currentAnalysisResult.value.exportResult));
  export_result.forEach(item => {
    item.assessment = displayAssessment.value;
    item.assessmentLabel = displayAssessment.value;
    item.result = displayResult.value;
    item.resultLabel = [displayResult.value];
  });

  // 更新 export results
  currentAnalysisResult.value.exportResult = export_result;

  // 更新至 firestore
  const dbBetaThalResultPath = 'thalbeta_result';
  update_userAnalysisData(user_info.value.uid, dbBetaThalResultPath, currentAnalysisResult.value, currentAnalysisResult.value.analysis_id);
}

// 掛載時執行
onMounted(async () => {
  // 取得使用者身份
  const { login_status } = updateGetUserInfo();
  is_login.value = login_status.value.is_login;
  user_info.value = login_status.value.user_info;

  // 取得 currentDisplayAnalysisID
  currentDisplayAnalysis.value = getCurrentDisplayAnalysisID();

  // 取得 setting props (為了特殊處理 SMAv4)
  currentSettingProps.value = store.getters["analysis_setting/getSettingProps"];

  // 取得當前分析結果 by 使用者 id, 分析名稱, 分析 id
  currentAnalysisResult.value = await getCurrentAnalysisResult(login_status, currentSettingProps);

  // 如果當前分析結果不存在, 則跳出
  if (!currentAnalysisResult.value) {
    showResult.value = false;
    return;
  }

  // 更新結果表格和當前被分析的檔案
  updateResultTable(currentAnalysisResult.value);

  // 如果列表中所有項目的 Disease_Type, Present_Name, Variant_Type 都是 null, 則 toggleDisplayRecords 設為 false
  if (resultRows.value.every(row => row.Disease_Type === null && row.Present_Name === null && row.Variant_Type === null)) {
    toggleDisplayRecords.value = false;
  }
  else {
    toggleDisplayRecords.value = true;
  }

  // 調整表格顯示
  adjustTableDisplay();

  // 更新導出結果
  updateExportResults();
});

// 監控 toggleDisplayRecords 的變化
watch(toggleDisplayRecords, () => {
  adjustTableDisplay();
});
</script>