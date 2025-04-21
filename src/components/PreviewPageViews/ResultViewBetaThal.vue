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
            :columns="displaySummaryColumns"
            :rows-per-page-options="[1000]"
          >
            <!-- 設定表格標題為粗體 -->
            <template v-slot:header-cell="props">
              <q-th :props="props" class="text-blue-grey-7" style="font-weight: bold; font-size: 1em;">
                {{ props.col.label }}
              </q-th>
            </template>

            <!-- 設定 QC Status 的顯示 -->
            <template v-slot:body-cell-qcStatus="props">
              <q-td :props="props">
                <q-chip
                  :color="props.row.qcStatus === 'Meet the criteria' ? 'cyan-4'
                        : props.row.qcStatus === 'Fail the criteria' ? 'red-8'
                        : 'blue-grey-4'"
                  text-color="white"
                  :label="props.row.qcStatus"
                  :icon="props.row.qcStatus === 'Meet the criteria' ? 'check_circle'
                        : props.row.qcStatus === 'Fail the criteria' ? 'pan_tool_alt'
                        : 'help'"
                  :style="props.row.qcStatus === 'Fail the criteria' ? 'cursor: pointer;' : 'cursor: default;'"
                  :clickable="props.row.qcStatus === 'Fail the criteria'"
                  @click="showQCMessage(props.row.qcStatus, props.row.qcMessage)"
                />
              </q-td>
            </template>

            <!-- 設定 Assessment 的顯示 -->
            <template v-slot:body-cell-assessment="props">
              <q-td :props="props">
                <q-chip
                  :color="props.row.assessment === 'Pathogenic Detected' ? 'red-8'
                        : props.row.assessment === 'Invalid' ? 'blue-grey-4': 'green-5'"
                  text-color="white"
                  :label="props.row.assessment"
                  :icon="props.row.assessment === 'Invalid' ? 'cancel'
                        : props.row.assessment === 'Pathogenic Detected' ? 'report'
                        : 'check_circle'"
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

      <!-- Basecall Viewer 圖表 -->
      <div class="q-mt-md" style="background-color: rgba(221, 232, 243, 0.2); border-radius: 10px; padding: 10px;">

        <!-- 標題和 Basecall File 選擇器 -->
        <div style="margin-bottom: 1em;">
          <div class="row text-h6" style="display: flex; justify-content: space-between; align-items: center;">
            <span> Basecall Viewer </span>
            <div class="q-pa-md" style="display: flex; flex-direction: row; align-items: center; gap: 0.5em;">
              <span class="text-subtitle1" style="font-weight: bold;">Current Displayed File:</span>
              <q-btn-dropdown no-caps flat color="primary" :label="currentDisplayBasecallFile" style="border: 1px solid #dedede; background-color: rgba(241, 255, 254, 0.2);">
                <q-list>
                  <q-item clickable v-close-popup @click="onBasecallFileClick(file)" v-for="file in currentBasecallFileList" :key="file">
                    <q-item-section>
                      <q-item-label>{{ file }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-btn-dropdown>
              <q-icon name="swipe_vertical" color="primary" />
            </div>
          </div>
          <div class="row" style="display: flex; flex-direction: column; justify-content: flex-start; align-items: flex-start; gap: 0.5em;">
            <span class="text-subtitle2 text-blue-grey-7" style="font-weight: bold;">Alignment Score1: {{ getCurrentDisplayAlign1Score }} </span>
            <span class="text-subtitle2 text-blue-grey-7" style="font-weight: bold;">Alignment Score2: {{ getCurrentDisplayAlign2Score }} </span>
          </div>
        </div>

        <!-- 顯示 Basecalling peaks-->
        <div ref="basecall_peaks_plot_container" id="basecall_peaks" class="row flex flex-center" :style="expandBaseCallViewPlot ? 'height: 40em; width: 100%;' : 'height: 100%; width: 100%;'"></div>

        <!-- 沒有圖顯示提示 -->
        <div ref="fail_to_plot_hint" class="row flex flex-center text-subtitle1 text-red-7 text-weight-bold" style="display: none;">
          <span> 檔案分析失敗, 請檢查原始檔案 </span>
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
                :color="displayAssessment === 'Pathogenic Detected' ? 'red-8'
                        : displayAssessment === 'Invalid' ? 'blue-grey-4'
                        : 'green-5'"
                text-color="white"
                :label="displayAssessment"
                :icon="displayAssessment === 'Invalid' ? 'cancel'
                        : displayAssessment === 'Pathogenic Detected' ? 'report'
                        : 'check_circle'"
              />
            </div>
          </div>
        </div>

        <!-- 結果表格 -->
        <div class="q-pa-md" :style="{display: currentSampleQCStatus === 'Invalid' || currentSampleQCStatus === 'fail-the-criteria' ? 'none' : 'block'}">

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
            :columns="displayResultColumns"
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
                    :color="ClinicalSignificance[item.replaceAll(' ', '_')].color"
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

  <!-- QC Message 視窗 -->
  <q-dialog v-model="show_qc_message_dialog" persistent>
    <q-card style="width: 1000px; max-width: 90vw;">
      <q-card-section>
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 15px; width: 100%;">
          <div class="flex flex-row items-center justify-center gap-2" style="width: 100%;">
            <q-icon name="warning" color="red" size="lg" />
            <span class="text-h6">QC Failed Message</span>
          </div>
          <div style="width: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center;">
            <div style="width: 100%; display: flex; flex-direction: column; align-items: flex-start; justify-content: center; gap: 1em; padding: 1em;">
              <div v-for="item in processed_qc_message" :key="item.file" style="display: flex; flex-direction: column; align-items: flex-start; justify-content: center; gap: 0.5em; width: 100%;">
                <q-chip color="grey-2" :label="`File: ${item.file}`" style="max-width: 100%; overflow: hidden; text-overflow: ellipsis;" />
                <span class="text-subtitle1" style="margin-left: 1.2em; white-space: pre-wrap; word-break: break-word;">Fail Reason: {{ item.message }}</span>
              </div>
            </div>
            <q-btn class="q-mt-md" label="關閉" color="primary" @click="show_qc_message_dialog = false" />
          </div>
        </div>
      </q-card-section>
    </q-card>
  </q-dialog>

</template>

<script setup>

// 導入模組
import { ref, onMounted, watch, computed } from 'vue';
import { useStore } from 'vuex';
import { update_userAnalysisData } from '@/firebase/firebaseDatabase';
import { getCurrentDisplayAnalysisID, getCurrentAnalysisResult } from '@/composables/checkAnalysisStatus.js';
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';
import { ClinicalSignificance, Consequence } from '@/composables/useInterpretClinvar.js';
import Plotly from 'plotly.js-dist';

// 定義變數
const showResult = ref(true);
const store = useStore();
const separator = '___SEP_ANNO___';

// 控制 QC Message 視窗
const show_qc_message_dialog = ref(false);
const displayed_qc_message = ref('');
const processed_qc_message = computed(() => {
  let report_list = [];
  const message_list = displayed_qc_message.value.split(';');
  message_list.forEach(item => {
    if (item.includes("File:") && item.includes(",")) {
      const file = item.split("File:")[1].trim().split(",")[0].trim();
      const message = item.split(",")[1].trim();
      report_list.push({
        file: file,
        message: message
      });
    }
  });
  return report_list;
});

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
    name: "qcStatus",
    align: "center",
    label: "QC Status",
    field: "qcStatus"
  },
  {
    name: "qcMessage",
    align: "center",
    label: "QC Message",
    field: "qcMessage"
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
const displaySummaryColumns = summaryColumns.filter(column => column.name !== 'qcMessage');

// 定義結果表格
const resultRows = ref([]);
const displayResultColumns = computed(() => {
  const preservedColumns = [
    'index',
    'genomicPosition',
    'refSeq',
    'altSeq',
    'variantClass',
    'genotype',
    'clinicalSignificance',
    'variantType',
    'variantName'
  ];
  return resultColumns.filter(column => preservedColumns.includes(column.name));
});
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
    field: (row) => row.Consequence === null ? 'N/A'
                  : (Consequence[row.Consequence] === undefined ? row.Consequence
                  : Consequence[row.Consequence].label)
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
const currentSampleQCStatus = ref('');

// 當前選擇顯示的 Basecall File
const currentBasecallFileList = ref([]);
const currentDisplayBasecallFile = ref('');

// 從 store 取得 plot_peak_data 和 plot_basecall_data
const plot_peak_data = computed(() => store.getters["Beta_thal_analysis_data/getPlotPeakData"]);
const plot_basecall_data = computed(() => store.getters["Beta_thal_analysis_data/getPlotBasecallData"]);
const basecall_peaks_plot_container = ref(null);
const fail_to_plot_hint = ref(null);
const expandBaseCallViewPlot = ref(false);

// 取得當前顯示圖表的 Alignment Score
const getCurrentDisplayAlign1Score = computed(() => {
  if (!currentAnalysisResult.value) return "N/A";
  const currentDisplayFile = currentDisplayBasecallFile.value
  const currentSampleName = currentSelectedSampleName.value
  const selected_alignment_scores = currentAnalysisResult.value.resultObj.find(item => item.sample_name === currentSampleName).alignment_score
  const alignment_Score = Object.keys(selected_alignment_scores).find(key => currentDisplayFile.includes(key))
  const alignment_ScoreDict = selected_alignment_scores[alignment_Score]
  return alignment_ScoreDict ? alignment_ScoreDict["align1Score"] : "N/A"
});
const getCurrentDisplayAlign2Score = computed(() => {
  if (!currentAnalysisResult.value) return "N/A";
  const currentDisplayFile = currentDisplayBasecallFile.value
  const currentSampleName = currentSelectedSampleName.value
  const selected_alignment_scores = currentAnalysisResult.value.resultObj.find(item => item.sample_name === currentSampleName).alignment_score
  const alignment_Score = Object.keys(selected_alignment_scores).find(key => currentDisplayFile.includes(key))
  const alignment_ScoreDict = selected_alignment_scores[alignment_Score]
  return alignment_ScoreDict? alignment_ScoreDict["align2Score"] : "N/A"
});

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
        const severity = row.ClinSigList.map(item => ClinicalSignificance[item.replaceAll(' ', '_')].severity_level);
        row["Severity"] = Math.max(...severity);
      }
      else {
        row["Severity"] = 0;
      }
    });

    // 挑出 Severity 最高的 row 當作結果回報
    const selected_Row = result_rows.sort((a, b) => b.Severity - a.Severity)[0];

    // 結果為 selected_Row 的 Name
    let ResultLabel = selected_Row ? (selected_Row.Name ? selected_Row.Name : 'Not detected') : 'Not detected';

    // 如果 selected_Row (最嚴重) 有包含 "Pathogenic" 或 "Likely pathogenic" 則回報 "β-thalassemia", 否則回報 "Not detected"
    const key_word_pathogenic = [ClinicalSignificance["Pathogenic"].value, ClinicalSignificance["Likely_pathogenic"].value];
    let AssessmentLabel = selected_Row ? (selected_Row.ClinSigList.some(item => key_word_pathogenic.includes(item)) ? "Pathogenic Detected" : "Not detected") : "Not detected";

    // 如果 qc_status 是 'fail-the-criteria' 則 result = N/A assessment = Invalid
    if (item.qc_status === 'fail-the-criteria') {
      ResultLabel = 'N/A';
      AssessmentLabel = 'Invalid';
    }

    return {
      index: index + 1,
      sampleName: item.sample_name,
      result: ResultLabel,
      assessment: AssessmentLabel,
      qcStatus: convertQCStatus(item.qc_status),
      qcMessage: item.qc_message
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
    const target_summary_row = summaryRows.value.find(row => row.sampleName === item.sampleId);
    item.assessment = target_summary_row.assessment;
    item.assessmentLabel = target_summary_row.assessment;
    item.result = target_summary_row.result;
    item.resultLabel = [target_summary_row.result];
  });

  // 更新 export results
  currentAnalysisResult.value.exportResult = export_result;

  // 更新至 firestore
  const dbBetaThalResultPath = 'thalbeta_result';
  update_userAnalysisData(user_info.value.uid, dbBetaThalResultPath, currentAnalysisResult.value, currentAnalysisResult.value.analysis_id);
}

// 簡化檔案路徑
const simplifyFilePath = (filePath) => { return filePath.split('/').pop(); }

// 當前選擇 Basecall File
const onBasecallFileClick = (file) => { currentDisplayBasecallFile.value = file; }

// 繪製互動式圖表
function plotBaseCallPeaks(plot_data, basecall_data) {

  // 獲取繪圖容器
  const container = document.getElementById('basecall_peaks');
  if (!container || !plot_data || !basecall_data) {
    // 移除當前的圖表
    basecall_peaks_plot_container.value.style.display = 'none';
    fail_to_plot_hint.value.style.display = 'flex';
    return;
  }
  else {
    basecall_peaks_plot_container.value.style.display = 'block';
    fail_to_plot_hint.value.style.display = 'none';
  }

  // 確保 x 軸長度一致
  if (plot_data.x_axis.length !== basecall_data.x_axis.length) {
    console.error('x_axis lengths do not match');
    return;
  }

  // 準備繪圖數據
  const traces = [];
  const colors = {
    peakA: '#26aa2e', // 綠色
    peakC: '#0000FF', // 藍色
    peakG: '#000000', // 黑色
    peakT: '#FF0000'  // 紅色
  };

  const names = {
    peakA: 'A',
    peakC: 'C',
    peakG: 'G',
    peakT: 'T'
  };

  // 添加水平線
  [1, 2, 3, 4].forEach(y => {
    traces.push({
      x: [Math.min(...plot_data.x_axis), Math.max(...plot_data.x_axis)],
      y: [y, y],
      mode: 'lines',
      line: {
        color: 'grey',
        width: 1,
        dash: 'solid'
      },
      showlegend: false,
      yaxis: 'y1'
    });
  });

  // 為每個樣本創建數據系列 (下半部分)
  Object.entries(plot_data).forEach(([key, values]) => {
    const x_list = plot_data.x_axis;
    const y_list = values;
    if (key !== 'x_axis') {
      traces.push({
        x: x_list,
        y: y_list,
        type: 'scatter',
        mode: 'lines',
        name: `${names[key]}`,
        line: {
          color: colors[key],
          width: 1
        },
        yaxis: 'y2',  // 指定使用第二個 y 軸
        legendgroup: 'peaks',  // 添加圖例分組
        legend: 'legend2'  // 指定使用第二個圖例
      });
    }
  });

  // 解析 basecalls 數據 (上半部分)
  const baseCallsData = {
    A: { x: [], y: [] },
    T: { x: [], y: [] },
    C: { x: [], y: [] },
    G: { x: [], y: [] }
  };

  const baseToY = {
    'A': 4,
    'T': 3,
    'C': 2,
    'G': 1
  };

  // 解析 basecalls 字典
  Object.entries(basecall_data.basecalls).forEach(([pos, value]) => {
    // 移除數字編號並分割bases
    const bases = value.split(':')[1].split('|');
    bases.forEach(base => {
      if (baseCallsData[base]) {
        baseCallsData[base].x.push(parseInt(pos));
        baseCallsData[base].y.push(baseToY[base]);
      }
    });
  });

  // 添加 basecalls 的散點圖
  Object.entries(baseCallsData).forEach(([base, data]) => {
    traces.push({
      x: data.x,
      y: data.y,
      type: 'scatter',
      mode: 'markers',
      name: base,
      marker: {
        color: colors[`peak${base}`],
        size: 8
      },
      yaxis: 'y1',  // 指定使用第一個 y 軸
      legendgroup: 'basecalls',  // 添加圖例分組
      legend: 'legend'  // 指定使用第一個圖例
    });
  });

  // 設置布局
  const layout = {
    title: 'Base Calling Peaks',
    grid: {
      rows: 2,
      columns: 1,
      pattern: 'independent',
      roworder: 'top to bottom'
    },
    xaxis: {
      title: 'Position',
      rangeslider: {},
      type: 'linear',
      range: [0, 1000]
    },
    yaxis: {
      title: {
        text: 'Basecalls',
        standoff: 20
      },
      domain: [0.7, 1],  // 上半部分佔 40%
      ticktext: ['G', 'C', 'T', 'A'],
      tickvals: [1, 2, 3, 4],
      range: [0.5, 4.5]
    },
    yaxis2: {
      title: {
        text: 'Signal Intensity',
        standoff: 20
      },
      domain: [0, 0.6]  // 下半部分佔 40%
    },
    showlegend: true,
    legend: {
      x: 1,
      xanchor: 'left',
      y: 1,
      yanchor: 'top',
      tracegroupgap: 0.5
    },
    legend2: {
      x: 1,
      xanchor: 'left',
      y: 0.4,
      yanchor: 'top',
      tracegroupgap: 0.5
    },
    margin: {
      l: 80,
      r: 150,  // 增加右邊距以容納圖例
      b: 50,
      t: 50,
      pad: 4
    },
  };

  // 設置配置選項
  const config = {
    responsive: true,
    displayModeBar: true,
    scrollZoom: false,
    dragmode: 'pan',
    modeBarButtonsToAdd: [
      {
        name: 'Reset Zoom',
        icon: Plotly.Icons.home,
        click: function(gd) {
          Plotly.relayout(gd, {
            'xaxis.autorange': true,
            'yaxis.autorange': true,
            'yaxis2.autorange': true
          });
        }
      }
    ]
  };

  // 繪製圖表
  Plotly.newPlot(container, traces, layout, config).then(function() {
    let verticalLine = null;
    let currentHoveredX = null;

    // 監聽滑鼠懸停事件
    container.on('plotly_hover', function(data) {
      const point = data.points[0];

      // 只處理上圖（basecalls）的點
      if (point.data.legendgroup === 'basecalls') {
        const x = point.x;

        // 如果懸停的 x 座標與當前不同，則更新垂直線
        if (x !== currentHoveredX) {
          currentHoveredX = x;

          // 如果已經有垂直線，則更新它
          if (verticalLine) {
            Plotly.deleteTraces(container, verticalLine);
          }

          // 創建新的垂直線
          const newTrace = {
            x: [x, x],
            y: [Math.min(...plot_data[Object.keys(plot_data).find(key => key !== 'x_axis')]),
               Math.max(...plot_data[Object.keys(plot_data).find(key => key !== 'x_axis')])],
            mode: 'lines',
            line: {
              color: 'rgba(0, 0, 0, 0.5)',
              width: 2,
              dash: 'solid'
            },
            hoverinfo: 'none',
            showlegend: false,
            yaxis: 'y2'
          };

          // 添加垂直線
          Plotly.addTraces(container, newTrace).then(function(gd) {
            verticalLine = gd.data.length - 1;
          });
        }
      }
    });

    // 監聽滑鼠離開事件
    container.on('plotly_unhover', function() {
      // 移除垂直線
      if (verticalLine !== null) {
        Plotly.deleteTraces(container, verticalLine);
        verticalLine = null;
        currentHoveredX = null;
      }
    });
  });
}

// 轉換 QC status 文字
function convertQCStatus(qcStatus) {
  if (qcStatus === 'meet-the-criteria') {
    return 'Meet the criteria';
  }
  else if (qcStatus === 'fail-the-criteria') {
    return 'Fail the criteria';
  }
  else {
    return 'N/A';
  }
}

// 顯示 QC Message
function showQCMessage(qcStatus, qcMessage) {
  // 如果 qcStatus 是 'Meet the criteria' 則不顯示 QC Message
  if (qcStatus === 'Meet the criteria') {
    return;
  }
  // 如果 qcStatus 是 'Fail the criteria' 則顯示 QC Message
  else {
    displayed_qc_message.value = qcMessage;
    show_qc_message_dialog.value = true;
  }
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

  // 更新 currentBasecallFileList
  currentBasecallFileList.value = currentAnalysisFile.value.map(file => simplifyFilePath(file));
  currentDisplayBasecallFile.value = currentBasecallFileList.value[0];

  // 更新 currentSampleQCStatus
  currentSampleQCStatus.value = currentAnalysisResult.value.resultObj[currentSelectedSampleIndex.value - 1].qc_status;
});

// 監控 toggleDisplayRecords 的變化
watch(toggleDisplayRecords, () => {
  adjustTableDisplay();
});

// 監控 currentSelectedSampleIndex 的變化
watch(currentSelectedSampleIndex, () => {

  // 更新結果表格
  updateResultTable(currentSelectedSampleIndex.value);

  // 調整表格顯示
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
        const severity = row.ClinSigList.map(item => ClinicalSignificance[item.replaceAll(' ', '_')].severity_level);
        row["Severity"] = Math.max(...severity);
      }
      else {
        row["Severity"] = 0;
      }
    });

    // 挑出 Severity 最高的 row 當作結果回報
    const selected_Row = result_rows.sort((a, b) => b.Severity - a.Severity)[0];

    // 結果為 selected_Row 的 Name
    let ResultLabel = selected_Row ? (selected_Row.Name ? selected_Row.Name : 'Not detected') : 'Not detected';

    // 如果 selected_Row (最嚴重) 有包含 "Pathogenic" 或 "Likely pathogenic" 則回報 "β-thalassemia", 否則回報 "Not detected"
    const key_word_pathogenic = [ClinicalSignificance["Pathogenic"].value, ClinicalSignificance["Likely_pathogenic"].value];
    let AssessmentLabel = selected_Row ? (selected_Row.ClinSigList.some(item => key_word_pathogenic.includes(item)) ? "Pathogenic Detected" : "Not detected") : "Not detected";

    // 如果 qc_status 是 'fail-the-criteria' 則 result = N/A assessment = Invalid
    if (item.qc_status === 'fail-the-criteria') {
      ResultLabel = 'N/A';
      AssessmentLabel = 'Invalid';
    }

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

  // 更新 currentBasecallFileList 和 currentDisplayBasecallFile
  currentBasecallFileList.value = currentAnalysisFile.value.map(file => simplifyFilePath(file));
  currentDisplayBasecallFile.value = currentBasecallFileList.value[0];

  // 更新 currentSampleQCStatus
  currentSampleQCStatus.value = summarize[currentSelectedSampleIndex.value - 1].assessment;
});

// 監控 currentDisplayBasecallFile 的變化
watch(currentDisplayBasecallFile, (newVal, oldVal) => {

  const canPlot = () => {
    if (newVal !== oldVal &&  plot_peak_data.value[currentSelectedSampleName.value]) {
      expandBaseCallViewPlot.value = true;
      return true;
    }
    else {
      expandBaseCallViewPlot.value = false;
      return false;
    }
  }

  // 繪製互動式圖表
  if (canPlot()) {
    const selected_file_name = currentDisplayBasecallFile.value.split('.')[0];
    const toPlotPeakData = plot_peak_data.value[currentSelectedSampleName.value][selected_file_name];
    const toPlotBasecallData = plot_basecall_data.value[currentSelectedSampleName.value][selected_file_name];
    plotBaseCallPeaks(toPlotPeakData, toPlotBasecallData);
  }
});

</script>