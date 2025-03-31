<template>
  <q-card bordered :style="{display: showResult ? 'block' : 'none'}">
    <q-card-section>

      <!-- 標題 -->
      <div class="text-h5 text-uppercase text-bold text-blue-grey-7">
        Screening Result
      </div>

      <!-- Batch Summary 表格 -->
      <div class="q-mt-md" style="background-color: rgba(221, 232, 243, 0.2); border-radius: 10px; padding: 10px;">
        <div class="row text-h6">
          SUMMARY
        </div>
        <div class="row q-pa-md">
          <q-table
            style="width: 100%;"
            :rows="summaryRows"
            :columns="summaryColumns"
            :rows-per-page-options="[1000]"
          >
            <!-- 設定表格標題為粗體 -->
            <template v-slot:header-cell="props">
              <q-th :props="props" class="text-blue-grey-7" style="font-weight: bold; font-size: 1em;">
                {{ props.col.label }}
              </q-th>
            </template>

            <!-- 設定 Assessment 的顯示 -->
            <template v-slot:body-cell-assessment="props">
              <q-td :props="props">
                <q-chip
                  :color="props.row.assessment === 'Pathogenic Detected' ? 'red-8' : 'green-5'"
                  text-color="white"
                  :label="props.row.assessment"
                />
              </q-td>
            </template>

            <!-- 設定 showData 按鈕 -->
            <template v-slot:body-cell-showData="props">
              <q-td :props="props">
                <q-btn
                  dense
                  round
                  label=""
                  :color="currentSelectedSampleIndex === props.row.index ? 'blue-grey-7' : 'white'"
                  :text-color="currentSelectedSampleIndex === props.row.index ? 'white' : 'blue-grey-7'"
                  icon="ads_click"
                  @click="currentSelectedSampleIndex = props.row.index"
                />
              </q-td>
            </template>

          </q-table>
        </div>
      </div>

      <!-- 個別分析結果表格 -->
      <div class="q-mt-md" style="background-color: rgba(221, 232, 243, 0.2); border-radius: 10px; padding: 10px;">

        <!-- 標題 -->
        <div class="col text-h6">
          SELECTED SAMPLE : {{ currentSelectedSampleName || 'N/A' }}
        </div>

        <!-- 顯示當前被分析的檔案-->
        <div class="q-mt-md row justify-center items-center">

          <!-- 顯示當前被分析的檔案-->
          <div class="col" style="display: flex; flex-direction: row; align-items: left; gap: 1em;">
            <span class="text-subtitle2" style="font-weight: bold;">Current result is from file:</span>
            <span class="text-subtitle2" v-for="file in currentAnalysisFile" :key="file">{{ simplifyFilePath(file) }}</span>
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
          <div class="row" style="display: flex; align-items: center;" >
            <div class="col-2 text-h5 text-bold text-subtitle2 text-center" style="margin-block: 1em;">
              Assessment:
            </div>
            <div class="col text-h5 text-bold text-subtitle2 text-left" style="margin-block: 1em;">
              <q-chip
                :color="displayAssessment === 'Pathogenic Detected' ? 'red-8' : 'green-5'"
                text-color="white"
                :label="displayAssessment"
              />
            </div>
          </div>
        </div>

        <!-- 結果表格 -->
        <div class="q-pa-md">

          <!-- 顯示表格按鈕 -->
          <div class="col-2" style="display: flex; justify-content: right; align-items: center; margin-block: 1.3em;">
            <q-btn
              dense
              :label="toggleDisplayRecords ? 'Annotated' : 'All Variants'"
              :color="toggleDisplayRecords ? 'red-2' : 'lime-4'"
              :icon="toggleDisplayRecords ? 'crisis_alert' : 'visibility'"
              text-color="black"
              style="padding: 0 10px"
              @click="toggleDisplayRecords = !toggleDisplayRecords"
            />
          </div>

          <!-- 如果有資料則顯示表格 -->
          <q-table v-if="resultRows.length > 0"
            :rows="resultRows"
            :columns="resultColumns"
            :rows-per-page-options="[100]"
          >
            <!-- 設定表格標題為粗體 -->
            <template v-slot:header-cell="props">
              <q-th :props="props" class="text-blue-grey-7" style="font-weight: bold; font-size: 1em;">
                {{ props.col.label }}
              </q-th>
            </template>

            <!-- 特殊處理 Clinical Significance 的顯示 -->
            <template v-slot:body-cell-clinicalSignificance="props">
              <q-td :props="props">
                <div style="display: flex; flex-direction: column; align-items: center; gap: 0.5em;">
                <q-chip
                  v-for="item in props.row.ClinSigList"
                    :key="item"
                    :label="item"
                    :color="ClinicalSignificance[item.replace(' ', '_')].color"
                    text-color="white"
                  />
                </div>
              </q-td>
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
                <div style="width: 50em; white-space: wrap;">
                  <template v-if="props.value && props.value.includes(separator)">
                    <div v-for="(item, index) in props.value.split(separator)" :key="index">
                      {{ index + 1 }}. {{ item }}
                    </div>
                  </template>
                  <template v-else>
                    {{ props.value }}
                  </template>
                </div>
              </q-td>
            </template>

          </q-table>

          <!-- 如果沒有資料則顯示文字 -->
          <div v-else class="q-mt-md text-center text-subtitle1 text-blue-7">
            -- There is no HBB variant found by Tracy. --
          </div>

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
import { ClinicalSignificance, Consequence } from '@/composables/useInterpretClinvar.js';

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

// 控制顯示的結果列表
const toggleDisplayRecords = ref(true);
const displayResult = ref('N/A');
const displayAssessment = ref('N/A');

// 擷取 Genome Position
const getGenomePosition = (row) => {
  return `${row.adjusted_position.chr} : ${row.adjusted_position.start} - ${row.adjusted_position.end}`;
}

// 定義 Summary 表格
const summaryRows = ref([]);
const summaryColumns = [
  {
    name: "index",
    align: "center",
    label: "No.",
    field: "index"
  },
  {
    name: "sampleName",
    align: "center",
    label: "Sample Name",
    field: "sampleName"
  },
  {
    name: "result",
    align: "center",
    label: "Result",
    field: "result"
  },
  {
    name: "assessment",
    align: "center",
    label: "Assessment",
    field: "assessment"
  },
  {
    name: "showData",
    align: "center",
    label: "See more details",
    field: "showData"
  }
]

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
    name: "clinicalSignificance",
    align: "center",
    label: "Clinical Significance",
    field: (row) => row.ClinicalSignificance ? row.ClinicalSignificance.split('/'): ''
  },
  {
    name: "variantType",
    align: "center",
    label: "Variant Type",
    field: (row) => row.Consequence ? Consequence[row.Consequence].label : ''
  },
  {
    name: "variantName",
    align: "center",
    label: "Variant Name",
    field: "Name"
  },
  {
    name: "disease",
    align: "left",
    label: "Disease",
    field: (row) => {
      const FilterList = ["not specified", "not provided", "conditions"];
      return row.PhenotypeList ? row.PhenotypeList.split('|').filter(item => !FilterList.some(filter => item.includes(filter))).join(', ') : '';
    }
  },
];

// 當前選擇的Sample index
const currentSelectedSampleIndex = ref(1);
const currentSelectedSampleName = ref('');
const currentAnalysisFile = ref([]);

// 更新 summaryRows
function updateSummaryRows() {
  const summarize = currentAnalysisResult.value.resultObj.map((item, index) => {

    // 取得 result_rows 並增加細節
    const result_rows = item.resultTable.rows;
    result_rows.forEach(row => {

      // 處理 ClinicalSignificance
      if (row.ClinicalSignificance) {
        // 將 ; 轉換為 /
        if (row.ClinicalSignificance.includes(';')) {
          row.ClinicalSignificance = row.ClinicalSignificance.replace(';', '/');
        }
        // 將 ClinicalSignificance 轉換為列表
        row["ClinSigList"] = row.ClinicalSignificance.split('/');
      }
      else {
        row["ClinSigList"] = [];
      }

      // 計算嚴重度(取最嚴重)
      if (row.ClinSigList.length > 0) {
        const severity = row.ClinSigList.map(item => ClinicalSignificance[item.replace(' ', '_')].severity_level);
        row["Severity"] = Math.max(...severity);
      }
      else {
        row["Severity"] = 0;
      }
    });

    // 挑出 Severity 最高的 row 當作結果回報
    const selected_Row = result_rows.sort((a, b) => b.Severity - a.Severity)[0];

    // 結果為 selected_Row 的 Name
    const ResultLabel = selected_Row.Name;

    // 如果 selected_Row (最嚴重) 有包含 "Pathogenic" 或 "Likely pathogenic" 則回報 "β-thalassemia", 否則回報 "Not detected"
    const key_word_pathogenic = [ClinicalSignificance["Pathogenic"].value, ClinicalSignificance["Likely_pathogenic"].value];
    const AssessmentLabel = selected_Row.ClinSigList.some(item => key_word_pathogenic.includes(item)) ? "Pathogenic Detected" : "Not detected";

    return {
      index: index + 1,
      sampleName: item.sample_name,
      result: ResultLabel,
      assessment: AssessmentLabel
    }
  })

  // 更新 displayResult 和 displayAssessment
  displayResult.value = summarize[currentSelectedSampleIndex.value - 1].result;
  displayAssessment.value = summarize[currentSelectedSampleIndex.value - 1].assessment;

  // 更新 summaryRows
  summaryRows.value = summarize;
}

// 更新結果表格和當前被分析的檔案
function updateResultTable(currentSelectedSampleIndex) {

  // 選擇 result
  const result = currentAnalysisResult.value.resultObj[currentSelectedSampleIndex - 1];

  // 載入 resultRows, 排序
  resultRows.value = result.resultTable.rows;
  resultRows.value.sort((a, b) => {
    const variantTypeA = a.Disease_Type || '';
    const variantTypeB = b.Disease_Type || '';
    if (variantTypeA === variantTypeB) return 0;
    return variantTypeA > variantTypeB ? -1 : 1;
  });

  // 更新當前被分析的檔案
  currentAnalysisFile.value = result.input_file.split(',');

  // 更新當前選擇的 Sample Name
  currentSelectedSampleName.value = result.sample_name;

}

// 調整表格顯示
const adjustTableDisplay = () => {
  // 如果 toggleDisplayRecords 為 false, 則將 resultRows 中Disease_Type, Present_Name, Variant_Type 都是 null的行移除
  if (toggleDisplayRecords.value) {
    resultRows.value = resultRows.value.filter(
      row => row.clinicalSignificance !== null &&
      row.Name !== null && row.Consequence !== null &&
      row.PhenotypeList !== null
    );
  }
  // 否則重新載入 resultRows
  else {
    updateResultTable(currentSelectedSampleIndex.value);
  }
}

// 更新導出結果
function updateExportResults() {
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

// 簡化檔案路徑
const simplifyFilePath = (filePath) => {
  return filePath.split('/').pop();
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

  // 更新 summaryRows
  updateSummaryRows();

  // 更新結果表格
  updateResultTable(currentSelectedSampleIndex.value);

  // 調整表格顯示
  adjustTableDisplay();

  // 更新導出結果
  updateExportResults();
});

// 監控 toggleDisplayRecords 的變化
watch(toggleDisplayRecords, () => {
  adjustTableDisplay();
});

// 監控 currentSelectedSampleIndex 的變化
watch(currentSelectedSampleIndex, () => {
  updateResultTable(currentSelectedSampleIndex.value);
  adjustTableDisplay();

  // 更新 displayResult 和 displayAssessment
  const summarize = currentAnalysisResult.value.resultObj.map((item, index) => {

    // 取得 result_rows 並增加細節
    const result_rows = item.resultTable.rows;
    result_rows.forEach(row => {

      // 處理 ClinicalSignificance
      if (row.ClinicalSignificance) {
        // 將 ; 轉換為 /
        if (row.ClinicalSignificance.includes(';')) {
          row.ClinicalSignificance = row.ClinicalSignificance.replace(';', '/');
        }
        // 將 ClinicalSignificance 轉換為列表
        row["ClinSigList"] = row.ClinicalSignificance.split('/');
      }
      else {
        row["ClinSigList"] = [];
      }

      // 計算嚴重度(取最嚴重)
      if (row.ClinSigList.length > 0) {
        const severity = row.ClinSigList.map(item => ClinicalSignificance[item.replace(' ', '_')].severity_level);
        row["Severity"] = Math.max(...severity);
      }
      else {
        row["Severity"] = 0;
      }
    });

    // 挑出 Severity 最高的 row 當作結果回報
    const selected_Row = result_rows.sort((a, b) => b.Severity - a.Severity)[0];

    // 結果為 selected_Row 的 Name
    const ResultLabel = selected_Row.Name;

    // 如果 selected_Row (最嚴重) 有包含 "Pathogenic" 或 "Likely pathogenic" 則回報 "β-thalassemia", 否則回報 "Not detected"
    const key_word_pathogenic = [ClinicalSignificance["Pathogenic"].value, ClinicalSignificance["Likely_pathogenic"].value];
    const AssessmentLabel = selected_Row.ClinSigList.some(item => key_word_pathogenic.includes(item)) ? "Pathogenic Detected" : "Not detected";

    return {
      index: index + 1,
      sampleName: item.sample_name,
      result: ResultLabel,
      assessment: AssessmentLabel
    }
  })

  // 更新 displayResult 和 displayAssessment
  displayResult.value = summarize[currentSelectedSampleIndex.value - 1].result;
  displayAssessment.value = summarize[currentSelectedSampleIndex.value - 1].assessment;
});

</script>