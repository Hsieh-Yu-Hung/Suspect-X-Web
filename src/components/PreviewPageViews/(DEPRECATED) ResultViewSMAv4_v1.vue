<template>

  <!-- 警告視窗 -->
  <WarningDialog
    ref="warning_dialog"
    :error_message="dialog_error_message"
  />

  <div v-if="showResult">

    <!-- 結果評估版面 -->
    <q-card bordered>
      <q-card-section>

        <!-- 標題 -->
        <div class="row justify-center" style="display: flex; flex-direction: column; justify-content: center; align-items: center;">
          <span class="text-h5 text-bold text-blue-grey-7 text-uppercase">Screening results</span>
        </div>

        <!-- 評估結果內容 -->
        <div class="row" style="margin-top: 30px;">

          <!-- 評估結果 -->
          <div class="col result-box">
            <span class="row text-h6 text-bold text-blue-grey-7 text-uppercase justify-center">Assessment</span>
            <div class="col" style="margin-top: 20px; width: 100%;">
              <SMAv4AssessmentTable ref="assessment_table" :result_table_row="screening_table_rows" />
            </div>
          </div>

          <!-- 示意圖 -->
          <div class="col result-box">
            <span class="row text-h6 text-bold text-blue-grey-7 text-uppercase justify-center">Result Diagram</span>

            <!-- 分頁 -->
            <div class="q-pa-md">
              <q-carousel
                v-model="slide"
                transition-prev="slide-right"
                transition-next="slide-left"
                animated
                control-color="primary"
                class="rounded-borders"
              >

                <!-- Sample 頁面 -->
                <q-carousel-slide v-for="(option, index) in diagram_options" :key="index" :name="option.value" class="column no-wrap flex-center">
                  <div class="q-mt-md text-center">
                    <!-- 示意圖 -->
                    <div class="col" style="display: flex; justify-content: center; align-items: center; width: 100%;">
                      <img
                        v-if="option.smn1 > 0 && option.smn2 > 0"
                        :src="`diagram/${option.smn1}_${option.smn2}-1.svg`"
                        :alt="`${option.smn1}_${option.smn2}-1.svg`"
                        style="width: 100%; height: auto;">
                      <div v-else>
                        <span class="text-h6 text-bold text-red-8">Invalid Assessment</span>
                      </div>
                    </div>
                    <!-- 說明文字 -->
                    <div class="col" style="display: flex; justify-content: flex-start; align-items: center; width: 100%; margin-top: 30px;">
                      <span class="text-h6 text-bold text-grey-8">Sample: {{ option.value }}</span>
                    </div>
                  </div>
                </q-carousel-slide>
              </q-carousel>

              <!-- 頁面切換 -->
              <div class="row justify-center">
                <q-btn-toggle
                  glossy
                  v-model="slide"
                  :options="diagram_options"
                />
              </div>

            </div>

          </div>

        </div>
      </q-card-section>
    </q-card>

    <!-- (DEPRECATED) 結果表 -->

    <!--
    <q-card bordered style="margin-top: 25px; width: fit-content;">

      !-- 結果圖表版面 --
      <q-card-section>
        <div class="row" style="display: flex; flex-direction: row; justify-content: center; width: fit-content;">

          !-- 標題 --
          <div class="result-box" style="border: none;">
            <span class="text-h5 text-bold text-blue-grey-7 text-uppercase">Summary Data</span>
          </div>

          !-- 結果內容 --
          <div style="width: 100%; display: flex; flex-direction: row; flex-wrap: wrap; justify-content: center; align-items: center;">

            !-- 數值表格 --
            <div class="row q-pa-md" style="height: 720px;">

              !-- 開發工具 --
              <div :style="{ 'display': devPanelDisplay, 'width': '700px'}">
                <SMAv4DevlopPanel
                  :range_table="range_table"
                  ref="devPanel"
                  @update-range-table="updatePlotlyChart(line_display_selection)"/>
              </div>

              !-- 數值表格 --
              <div :style="{ 'display': dataPanelDisplay, 'min-width': '700px'}">
                <q-table
                  class="my-sticky-dynamic"
                  flat
                  bordered
                  :rows="screening_table_rows"
                  :columns="screening_table_columns"
                  row-key="no"
                  :visible-columns="visibleColumns"
                  :rows-per-page-options="[0, 10, 20]"
                  style="height: 680px; width: 700px;"
                  virtual-scroll
                >

                  !-- 標題區域 --
                  <template v-slot:top>
                    <div class="q-mg-md row" style="align-items: center;margin-top: 10px;">
                      <div class="row text-h6 text-bold text-blue-grey-7">
                        Summary Data
                      </div>
                      <div class="row">
                        <div class="q-ml-md row">
                          <q-btn
                            v-if="true"
                            class="row q-ma-sm"
                            color="purple"
                            padding="xs"
                            flat
                            icon="restart_alt"
                            label="Reset"
                            @click="reset_table_value"/>
                        </div>
                        <q-toggle
                          style="margin-right: 10px;"
                          v-model="show_standard_data"
                          label="Std."
                          color="red"
                        />
                        <q-toggle
                          style="margin-right: 20px;"
                          v-model="show_sample_data"
                          label="Sample"
                          color="teal"
                        />
                        <q-select
                          v-model="current_smn_options"
                          :options="smn_options"
                          :display-value="current_smn_options.toUpperCase()"
                          option-value="value"
                          options-cover
                          outlined
                          dense
                          options-dense
                          emit-value
                          map-options
                          style="min-width: 120px; margin-top: 5px; margin-inline: 10px;"
                        />
                        <q-select
                          v-model="visibleColumns"
                          multiple
                          outlined
                          dense
                          options-dense
                          :display-value="$q.lang.table.columns"
                          emit-value
                          map-options
                          :options="screening_table_columns"
                          option-value="name"
                          options-cover
                          style="min-width: 120px; margin-top: 5px;"
                        />
                      </div>
                    </div>
                  </template>

                  !-- 表格標題--
                  <template v-slot:header="props">
                    <q-tr>
                      <q-th key="no" :props="props"><div class="table-header"><span>No.</span></div></q-th>
                      <q-th key="sample" :props="props"><div class="table-header"><span>Sample</span></div></q-th>
                      <q-th key="smn" :props="props"><div class="table-header"><span>SMN</span></div></q-th>
                      <q-th key="ic" :props="props"><div class="table-header"><span>Internal Control</span></div></q-th>
                      <q-th key="tg" :props="props"><div class="table-header"><span>Target</span></div></q-th>
                      <q-th key="diff" :props="props"><div class="table-header"><span>delta T/C</span></div></q-th>
                      <q-th key="num" :props="props"><div class="table-header"><span>Copy Number</span></div></q-th>
                      <q-th key="type" :props="props"><div class="table-header"><span>Sample Type</span></div></q-th>
                    </q-tr>
                  </template>

                  !-- 表格內容 --
                  <template v-slot:body="props">
                    <q-tr
                      :props="props"
                      class="text-center"
                      v-show="((show_standard_data && props.row.type === 'standard') && (current_smn_options === 'SMN1/2' || props.row.smn === current_smn_options)) ||
                      ((show_sample_data && props.row.type === 'sample') && (current_smn_options === 'SMN1/2' || props.row.smn === current_smn_options))"
                    >
                      <q-td key="no" :props="props">
                        {{ props.row.no }}
                      </q-td>
                      <q-td key="sample" :props="props">
                        {{ props.row.sample_name }}
                      </q-td>
                      <q-td key="smn" :props="props">
                        {{ props.row.smn }}
                      </q-td>
                      <q-td key="ic" :props="props">
                        {{ props.row.ic }}
                      </q-td>
                      <q-td key="tg" :props="props">
                        {{ props.row.tg }}
                      </q-td>
                      <q-td key="diff" :props="props" style="min-width: 100px;">
                        <q-input
                          v-model.number="props.row.diff"
                          type="number"
                          dense
                          borderless
                          filled
                          step="0.01"
                          input-style="text-align: center;"
                          v-if="true"
                        />
                        <span v-else>{{ props.row.diff }}</span>
                      </q-td>
                      <q-td key="num" :props="props">
                        {{ props.row.num }}
                      </q-td>
                      <q-td key="type" :props="props">
                        {{ props.row.type }}
                      </q-td>
                    </q-tr>
                  </template>

                </q-table>
              </div>
            </div>

            !-- 圖表版面 --
            <div class="col q-pa-md std-curve-box">

              !-- 標題列 --
              <div class="row">
                <div class="row q-pa-md text-h6 text-bold text-blue-grey-7 center-content">
                  <span>Standard Curve Plot</span>
                </div>
                <q-btn
                  v-if="true"
                  class="row q-ma-sm"
                  color="teal"
                  padding="xs"
                  flat
                  icon="table_view"
                  label="Re-cal"
                  @click="calculateNewSmaRange"
                />
                <q-btn
                  v-if="true"
                  class="row q-ma-sm"
                  color="indigo"
                  padding="xs"
                  flat
                  icon="table_view"
                  label="Adjust"
                  @click="show_Range_control_panel"
                />
                <div class="q-mg-sm center-content">
                  <q-radio
                    keep-color
                    v-model="line_display_selection"
                    val="smn1"
                    label="SMN1"
                    color="red"
                  />
                  <q-radio
                    keep-color
                    v-model="line_display_selection"
                    val="smn2"
                    label="SMN2"
                    color="blue"
                  />
                </div>
              </div>

              !-- 互動式圖表 --
              <div ref="plotlyChart" style="width: 100%; height: 90%;"></div>
              </div>

          </div>

        </div>
      </q-card-section>

    </q-card>
    -->

  </div>

</template>

<script setup>

// (DEPRECATED)
// import Plotly from 'plotly.js-dist';
// import { useRouter } from 'vue-router';
// import { useQuasar, QSpinnerFacebook } from 'quasar';
// import { update_userAnalysisData, ANALYSIS_RESULT, EXPORT_RESULT } from '@/firebase/firebaseDatabase';
// import { submitWorkflow } from '@/composables/submitWorkflow';
// import { v4 as uuidv4 } from 'uuid';
// import SMAv4DevlopPanel from './SMAv4DevlopPanel.vue';

// 導入模組
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex';
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';
import { getCurrentDisplayAnalysisID, getCurrentAnalysisResult } from '@/composables/checkAnalysisStatus.js';
import { setAnalysisID } from '@/composables/checkAnalysisStatus';

// 導入元件
import SMAv4AssessmentTable from './(DEPRECATED) SMAv4AssessmentTable.vue';
import WarningDialog from '@/components/WarningDialog.vue';



// 定義 screening_table_rows 的 Row
const ROW = (no, sample_name, smn, ic, tg, diff, num, type) => {
  return {
    no: no,
    sample_name: sample_name,
    smn: smn,
    ic: ic,
    tg: tg,
    diff: diff,
    num: num,
    type: type
  }
}

// (DEPRECATED)
/*

// 定義 diagram_options 的 option
const OPTION = (label, sample_name, smn1, smn2) => {
  return {
    label: label,
    value: sample_name,
    smn1: smn1,
    smn2: smn2
  }
}

// 定義 SMAv4 DATA
const SMAv4_DATA = (rfu_ic, rfu_tg, diff, type, smn, sample_name, copy_number, exp_group, label) => {
  return {
    internal_control: rfu_ic,
    target: rfu_tg,
    diff: diff,
    type: type,
    smn: smn,
    sample_name: sample_name,
    copy_number: copy_number,
    exp_group: exp_group,
    label: label
  }
}

// 定義 peak config
const PEAK_CONFIG = (smn,neg_range, pos_range, min_peak_count, RFU_threshold, peak_range, peak_size = -1, ic_peak_size = -1, tg_peak_size = -1) => {
  if (smn == 'smn1') {
    if (peak_size == -1) {
      console.error('PEAK_CONFIG: peak_size is not defined')
      return
    }
    return {
      Min_peak_count: min_peak_count,
      Negative_range: neg_range,
      Positive_range: pos_range,
      Peak_size: peak_size,
      RFU_threshold: RFU_threshold,
      peak_select_range: peak_range
    }
  } else if (smn == 'smn2') {
    if (ic_peak_size == -1 || tg_peak_size == -1) {
      console.error('PEAK_CONFIG: ic_peak_size or tg_peak_size is not defined')
      return
    }
    return {
      Min_peak_count: min_peak_count,
      Negative_range: neg_range,
      Positive_range: pos_range,
      internal_ctrl_size: ic_peak_size,
      target_size: tg_peak_size,
      RFU_threshold: RFU_threshold,
      peak_select_range: peak_range
    }
  } else {
    console.error('PEAK_CONFIG: smn is not smn1 or smn2')
  }
}

// 定義 SMA v4 的 result object
const SMAv4_RESULT = (
  STD_DATA,
  SAMPLE_DATA,
  COPY_NUMBER_RANGES,
  RESULT_LIST,
  PARAMETERS,
  INPUT_FILE_OBJ,
  USE_CONFIG_NAME
) => {
  // 目前沒有特殊處理, 直接回傳
  return {
    STD_DATA,
    SAMPLE_DATA,
    COPY_NUMBER_RANGES,
    RESULT_LIST,
    PARAMETERS,
    INPUT_FILE_OBJ,
    USE_CONFIG_NAME
  }
}
*/

// Consts
const store = useStore();

// (DEPRECATED)
// const $q = useQuasar();
// const router = useRouter();

/* (DEPRECATED) 控制互動式圖表 */
/*
const plotlyChart = ref(null);                                                    // Plotly 圖表的參考
const line_display_selection = ref('smn1')                                        // 圖表當前顯示的線
const show_annotations = ref([])                                                  // 圖表的文字標籤
const show_shapes = ref([])                                                       // 圖表的 standard range 顏色區塊
*/

/* (DEPRECATED) 控制開發面板和表格 */
/*
const devPanel = ref(null)                                                        // 控制開發工具的參考
const show_standard_data = ref(true)                                              // 控制表格顯示 standard data
const show_sample_data = ref(true)                                                // 控制表格顯示 sample data
const devPanelDisplay = ref('none')                                               // 控制開發工具的顯示
const dataPanelDisplay = ref('block')                                             // 控制圖表的顯示
*/

/* Assessment 結果 */
const assessment_table = ref(null);
const screening_table_rows = ref([])
const diagram_options = ref([])
const slide = ref('')

// 取得使用者身份
const { login_status } = updateGetUserInfo();

// 保存當前分析結果
const currentAnalysisID = ref(null);
const currentAnalysisResult = ref(null);
const currentSettingProps = ref(null);
const currentDisplayAnalysis = ref({
  analysis_uuid: '',
  analysis_name: '',
});

// (DEPRECATED) 表格相關變數
/*
const visibleColumns = ref(['no', 'sample', 'smn', 'diff', 'num']);
const smn_options = ref([
  { label: 'SMN1/2', value: 'SMN1/2' },
  { label: 'SMN1', value: 'smn1' },
  { label: 'SMN2', value: 'smn2' }
]);
const current_smn_options = ref('SMN1/2');
const screening_table_columns = [
  { name: 'no', label: 'No.', align: 'center', field: 'no', sortable: true},
  { name: 'sample', required: true, label: 'Sample', align: 'center', field: 'sample', sortable: true},
  { name: 'smn', required: true, label: 'SMN', align: 'center', field: 'smn', sortable: true },
  { name: 'ic', label: 'Internal Control', align: 'center', field: 'ic', sortable: true },
  { name: 'tg', label: 'Target', align: 'center', field: 'tg', sortable: true },
  { name: 'diff', required: true, label: 'delta T/C', align: 'center', field: 'diff', sortable: true },
  { name: 'num', required: true, label: 'Copy Number', align: 'center', field: 'num', sortable: true },
  { name: 'type', label: 'Sample Type', align: 'center', field: 'type', sortable: true }
];
*/

// 其他變數
const original_rows = ref([]);

// (DEPRECATED) 設定 standard_data
/*
const standard_data = ref({
  'smn1': {
    'std1': { 'diff': 0 },
    'std2': { 'diff': 0 },
    'std3': { 'diff': 0 }
  },
  'smn2': {
    'std1': { 'diff': 0 },
    'std2': { 'diff': 0 },
    'std3': { 'diff': 0 }
  }
});
*/

// (DEPRECATED) 設定 SMA v4 的參數 (default)
/*
const default_peak_condition = {
  RANGE: {
    SMA1_IC_SIZE_RANGE: {min: 217, max: 265},
    SMA1_TG_SIZE_RANGE: {min: 111, max: 135},
    SMA2_SEARCH_RANGE: {min: 251, max: 337}
  },
  RFU_THRESHOLD: {
    SMN1_IC: 1,
    SMN1_TG: 1,
    SMN2: 1
  },
  PEAK_NUMBER_CHECK: {
    SMA1: 1,
    SMA2: 2
  },
  PEAK_SIZE: {
    SMA1_IC: 241,
    SMA1_TG: 123,
    SMA2_IC: 340,
    SMA2_TG: 306
  },
  PEAK_RANGE_DIV: {
    SMA1_IC: {
      Negative_range: 10,
      Positive_range: 10
    },
    SMA1_TG: {
      Negative_range: 10,
      Positive_range: 10
    },
    SMA2: {
      Negative_range: 10,
      Positive_range: 10
    }
  }
}
const current_peak_condition = ref(default_peak_condition)
const settingBackup = JSON.parse(JSON.stringify(current_peak_condition.value))
*/

// 控制警告視窗
const dialog_error_message = ref("");
const warning_dialog = ref(null);

// (DEPRECATED) 搜集 rfu 的資料
/*
const rfu_data = ref({
  smn1:{},
  smn2:{}
})
*/

// (DEPRECATED) 設定 range_table
/*
const range_table = ref({});
*/

// (DEPRECATED) 定義 Database 路徑
/*
const dbSMAv4ResultPath = 'sma_v4_result';
*/

// 控制 ResultViewSMAv4 的顯示
const showResult = ref(true);

/* Functions */

// 將 Sample 的資料更新到 screening_table_rows
function updateTableRowsSample(SMAv4_result) {

  // Sample List
  const sample_list = Object.keys(SMAv4_result.resultObj.RESULT_LIST);

  // index
  let index = 1;

  sample_list.forEach((sample_name) => {

    // SMN1
    const ROW_SMN1 = ROW(
      index, `${sample_name}-smn1`, "smn1",
      SMAv4_result.resultObj.SAMPLE_DATA.smn1[sample_name].ic_peak ? SMAv4_result.resultObj.SAMPLE_DATA.smn1[sample_name].ic_peak.peak_rfu : null,
      SMAv4_result.resultObj.SAMPLE_DATA.smn1[sample_name].tg_peak ? SMAv4_result.resultObj.SAMPLE_DATA.smn1[sample_name].tg_peak.peak_rfu : null,
      SMAv4_result.resultObj.SAMPLE_DATA.smn1[sample_name].rfu_diff,
      SMAv4_result.resultObj.RESULT_LIST[sample_name].smn1_copy_number,
      "sample"
    );
    index++;

    // SMN2
    const ROW_SMN2 = ROW(
      index, `${sample_name}-smn2`, "smn2",
      SMAv4_result.resultObj.SAMPLE_DATA.smn2[sample_name].ic_peak ? SMAv4_result.resultObj.SAMPLE_DATA.smn2[sample_name].ic_peak.peak_rfu : null,
      SMAv4_result.resultObj.SAMPLE_DATA.smn2[sample_name].tg_peak ? SMAv4_result.resultObj.SAMPLE_DATA.smn2[sample_name].tg_peak.peak_rfu : null,
      SMAv4_result.resultObj.SAMPLE_DATA.smn2[sample_name].rfu_diff,
      SMAv4_result.resultObj.RESULT_LIST[sample_name].smn2_copy_number,
      "sample"
    );
    index++;

    // 更新 screening_table_rows
    screening_table_rows.value.push(ROW_SMN1);
    screening_table_rows.value.push(ROW_SMN2);
  });

  // 將所有 STD 的資料更新到 screening_table_rows
  for (const smn of ['smn1', 'smn2']) {
    for (const std of ['std1', 'std2']) {
      const smn_std = SMAv4_result.resultObj.STD_DATA[smn][std];
      const ROW_STD = ROW(
        index,
        smn_std.group,
        smn_std.smn,
        smn_std.ic_peak ? smn_std.ic_peak.peak_rfu : null,
        smn_std.tg_peak ? smn_std.tg_peak.peak_rfu : null,
        smn_std.rfu_diff,
        smn_std.group[smn_std.group.length - 1],
        "standard"
      );
      screening_table_rows.value.push(ROW_STD);
      index++;
    }
  }

  // 紀錄原始數值
  original_rows.value = JSON.parse(JSON.stringify(screening_table_rows.value));
}

// (DEPRECATED) 更新 diagram_options
/*
function updateDiagram_options(SMAv4_result) {

  // Sample List
  const sample_list = Object.keys(SMAv4_result.resultObj.RESULT_LIST);

  // index
  let index = 1;

  sample_list.forEach((sample_name) => {
    const smn1_copy_number = SMAv4_result.resultObj.RESULT_LIST[sample_name].smn1_copy_number;
    const smn2_copy_number = SMAv4_result.resultObj.RESULT_LIST[sample_name].smn2_copy_number;
    const option = OPTION(index, sample_name, smn1_copy_number, smn2_copy_number);
    diagram_options.value.push(option);
    index++;
  });

  // 如果 diagram_options 有值, 則設置 slide 的值
  if (diagram_options.value.length > 0) {
    slide.value = diagram_options.value[0].value;
  }
}
*/

// (DEPRECATED) 重設表格
/*
function reset_table_value(){
  screening_table_rows.value = JSON.parse(JSON.stringify(original_rows.value));
}
*/

// (DEPRECATED) 判斷數值範圍
/*
function determineRange(data_matrix){
  // SMA1 (2:2 和 1:1 的差值) & (3:3 和 2:2 的差值)
  const sma1_diff_2_1 = data_matrix['smn1']['std2']['diff'] - data_matrix['smn1']['std1']['diff'];
  const sma1_diff_3_2 = data_matrix['smn1']['std3']['diff'] - data_matrix['smn1']['std2']['diff'];

  // SMA2 (2:1 和 1:1 的差值) & (3:3 和 2:2 的差值)
  const sma2_diff_2_1 = data_matrix['smn2']['std2']['diff'] - data_matrix['smn2']['std1']['diff'];
  const sma2_diff_3_2 = data_matrix['smn2']['std3']['diff'] - data_matrix['smn2']['std2']['diff'];

  // 計算判斷間距
  const SMA1_D1 = data_matrix['smn1']['std1']['diff']
  const SMA1_RANGES = {
    '1': {min: SMA1_D1, max: SMA1_D1 + sma1_diff_2_1/2},
    '2': {min: SMA1_D1 + sma1_diff_2_1/2, max: SMA1_D1 + sma1_diff_2_1/2 + sma1_diff_3_2/2},
    '3': {min: SMA1_D1 + sma1_diff_2_1/2 + sma1_diff_3_2/2, max: 0},
  }
  const SMA2_D1 = data_matrix['smn2']['std1']['diff']
  const SMA2_RANGES = {
    '1': {min: SMA2_D1, max: SMA2_D1 + sma2_diff_2_1/2},
    '2': {min: SMA2_D1 + sma2_diff_2_1/2, max: SMA2_D1 + sma2_diff_2_1/2 + sma2_diff_3_2/2},
    '3': {min: SMA2_D1 + sma2_diff_2_1/2 + sma2_diff_3_2/2, max: 0},
  }
  const SMA_RANGES = {
    'smn1': SMA1_RANGES,
    'smn2': SMA2_RANGES,
  }

  return SMA_RANGES;
}
*/

// (DEPRECATED) 計算新的 SMA 範圍
/*
function getNewSmaRange(data){
  const new_range = determineRange(data);
  const res = {}
  for (let smn in new_range){
    const smn_obj = {}
    for (let num in new_range[smn]){
      const obj = {
        min: new_range[smn][num].min,
        max: new_range[smn][num].max,
        label: smn,
        copy_number: num
      }
      smn_obj[num] = obj
    }
    res[smn] = smn_obj
  }
  return res;
}
*/

// (DEPRECATED) 計算新的 SMA 範圍
/*
function calculateNewSmaRange(){
  update_standard_data()
  const std_data_json = JSON.parse(JSON.stringify(standard_data.value))
  const new_range = getNewSmaRange(std_data_json)
  range_table.value = JSON.parse(JSON.stringify(new_range));
  devPanel.value.update_range_table_rows(new_range)
}
*/

// (DEPRECATED) 更新 standard_data
/*
function update_standard_data(){
  if (screening_table_rows.value.length == 0){return}
  standard_data.value = {
    'smn1': {
      'std1': {'diff': screening_table_rows.value.find(row => row.sample_name === 'std1' && row.smn === 'smn1').diff},
      'std2': {'diff': screening_table_rows.value.find(row => row.sample_name === 'std2' && row.smn === 'smn1').diff},
    },
    'smn2': {
      'std1': {'diff': screening_table_rows.value.find(row => row.sample_name === 'std1' && row.smn === 'smn2').diff},
      'std2': {'diff': screening_table_rows.value.find(row => row.sample_name === 'std2' && row.smn === 'smn2').diff},
    },
  }
}
*/

// (DEPRECATED) 更新 Range Table
/*
function updateRangeTable(SMAv4_result){
  const copy_number_range = SMAv4_result.resultObj.COPY_NUMBER_RANGES;
  range_table.value = {
    "smn1": {
      "1": {
          "min": copy_number_range.smn1['1'].MIN || 0,
          "max": copy_number_range.smn1['1'].MAX || 0,
          "label": "smn1",
          "copy_number": "1"
      },
      "2": {
          "min": copy_number_range.smn1['2'].MIN || 0,
          "max": copy_number_range.smn1['2'].MAX || 0,
          "label": "smn1",
          "copy_number": "2"
      },
      "3": {
          "min": copy_number_range.smn1['3'].MIN || 0,
          "max": copy_number_range.smn1['3'].MAX || 0,
          "label": "smn1",
          "copy_number": "3"
      }
    },
    "smn2": {
      "1": {
          "min": copy_number_range.smn2['1'].MIN || 0,
          "max": copy_number_range.smn2['1'].MAX || 0,
          "label": "smn2",
          "copy_number": "1"
      },
      "2": {
          "min": copy_number_range.smn2['2'].MIN || 0,
          "max": copy_number_range.smn2['2'].MAX || 0,
          "label": "smn2",
          "copy_number": "2"
      },
      "3": {
          "min": copy_number_range.smn2['3'].MIN || 0,
          "max": copy_number_range.smn2['3'].MAX || 0,
          "label": "smn2",
          "copy_number": "3"
      }
    }
  };
}
*/

// (DEPRECATED) 更新圖表
/*
function updatePlotlyChart(display, x_axis=[1,2,3]){

  // 確保 DOM 元素存在
  if (!plotlyChart.value) return;

  // 取得 sample 的 diff 值
  function getDiffValue(sampleName) {
    const row = screening_table_rows.value.find(row => row.sample_name === sampleName);
    return row ? row.diff : 0; // 如果找不到，返回 0 或其他預設值
  }

  // 取得 standard 的 diff 值
  function getSTDdiffValue(std, smn) {
    const row = screening_table_rows.value.find(row => row.sample_name === std && row.smn === smn);
    return row ? row.diff : 0; // 如果找不到，返回 0 或其他預設值
  }

  // 建立 trace
  function buildTrace(smn, smn_color){

    // 從 screening_table_rows 中取得 diff 的值
    const smn_data_points = {
      x: [1, 2, 3],
      y: [
        getSTDdiffValue('std1', smn),
        getSTDdiffValue('std2', smn),
        getSTDdiffValue('std3', smn)
      ]
    }
    // 建立 trace
    const smn_trace = {
      x: smn_data_points.x,
      y: smn_data_points.y,
      mode: 'lines+markers',
      type: 'scatter',
      name: smn,
      line: {
        color: smn_color
      }
    };
    return smn_trace
  }

  // 紀錄所有 ｙ值, 以決定顯示範圍
  function determineDisplayYaxisRange(padding_factor=0.1){

    // 紀錄所有 ｙ值
    let y_values = {
      'smn1': [],
      'smn2': []
    }

    // 紀錄所有 ｙ值 standard
    y_values['smn1'].push(...standard_diff_value.smn1.y)
    y_values['smn2'].push(...standard_diff_value.smn2.y)

    // 紀錄所有 ｙ值 sample
    for (const smn of ['smn1', 'smn2']){
      for (let i = 0; i < smn_sample_info[smn].length; i++){
        const diff_value = getDiffValue(smn_sample_info[smn].name[i])
        y_values[smn].push(diff_value)
      }
    }

    // 決定顯示範圍
    const display_y_range = {
      'smn1': [Math.min(...y_values['smn1']) - padding_factor * Math.min(...y_values['smn1']), Math.max(...y_values['smn1']) + padding_factor * Math.max(...y_values['smn1'])],
      'smn2': [Math.min(...y_values['smn2']) - padding_factor * Math.min(...y_values['smn2']), Math.max(...y_values['smn2']) + padding_factor * Math.max(...y_values['smn2'])],
    }
    return display_y_range
  }

  // 製作 standard range
  function makeStandardRange(display, range_data){
    let standard_range = []
    const smn_range_data = range_data.filter(row => row.label === display)
    for (let range in range_color){
      let min = smn_range_data.find(row => row.num === range) ? smn_range_data.find(row => row.num === range).min : -999
      let max = smn_range_data.find(row => row.num === range) ? smn_range_data.find(row => row.num === range).max : 999
      if (range == '0'){max = smn_range_data.find(row => row.num === '1').min}
      if (range == '3'){max = 999}
      const smn_range = {
        type: 'rect',
        xref: 'paper',
        yref: 'y',
        x0: 0, x1: 1,
        y0: min,
        y1: max,
        fillcolor: range_color[range],
        opacity: 0.2,
        line: {width: 0}
      }
      standard_range.push(smn_range)
    }
    return standard_range
  }

  // 製作 sample annotation
  function makeSampleAnnotation(display){
    let annotations = []
    const smn_data =  screening_table_rows.value.filter(row => row.smn === display && row.type === 'sample')
    smn_data.forEach(sample => {
      const anno = {
        x: 3.6,
        y: sample.diff,
        text: sample.sample_name,
        showarrow: false,
        xanchor: 'left',
        font: { size: 12, color: 'gray' },
      }
      annotations.push(anno)
    })
    return annotations
  }

  // 製作 standard annotation
  function makeStandardAnnotation(range){
    // 設定標準範圍的顏色
    const annotation_color = {
      "0": "rgb(255, 0, 0)",
      "1": "rgb(255, 195, 0)",
      "2": "rgb(155, 165, 0)",
      "3": "rgb(0, 155, 0)"
    }
    let annotations = []
    for (let i = 0; i < range.length; i++){
      let y = range[i].y1 * 0.98
      if (i == 3){y = range[i].y0 * 1.02}
      const anno = {
        x: -0.1,
        y: y,
        text: "Copy: " + i,
        showarrow: false,
        xanchor: 'left',
        font: { size: 10, color: annotation_color[i] },
      }
      annotations.push(anno)
    }
    return annotations
  }

  // 統整最後要呈現的 trace
  function makeSampleTraces(display){
    let trace = []
    // 加入 sample 的線
    for (let i = 0; i < smn_sample_info[display].length; i++){
      const id = "No." + smn_sample_info[display].number[i]
      if (trace.some(line => line.name === id)){
        continue
      }
      const diff_value = getDiffValue(smn_sample_info[display].name[i])
      const smn_sample_line = {
        x: [0.5, 3.5],
        y: [diff_value, diff_value],
        mode: 'lines+markers',
        name: "No." + smn_sample_info[display].number[i],
        type: 'scatter',
        line: { color: "black", dash: 'dash' }
      }
      trace.push(smn_sample_line)
    }
    return trace
  }

  // 從 standard 中取得 diff 的值
  const standard_diff_value = {}
  for (const ismn of ['smn1', 'smn2']){
    standard_diff_value[ismn] = {
      'x': [1, 2, 3],
      'y': [
        getSTDdiffValue('std1', ismn),
        getSTDdiffValue('std2', ismn),
        getSTDdiffValue('std3', ismn)
      ]
    }
  }

  // 取得 sample 資料
  const smn_sample_info ={}
  for (const ismn of ['smn1', 'smn2']){
    smn_sample_info[ismn] = {
      'name': screening_table_rows.value.filter(row => row.smn === ismn && row.type === 'sample').map(row => row.sample_name),
      'number': screening_table_rows.value.filter(row => row.smn === ismn && row.type === 'sample').map(row => row.no),
      'length': screening_table_rows.value.filter(row => row.smn === ismn && row.type === 'sample').length
    }
  }

  // 建立 trace
  const smn1_trace = buildTrace('smn1', 'red')
  const smn2_trace = buildTrace('smn2', 'blue')

  // 根據所有ｙ值, 以決定顯示範圍
  const display_y_range = determineDisplayYaxisRange()

  // 取得 range_table 的資料
  const range_data = devPanel.value.range_table_rows

  // 設定標準範圍的顏色
  const range_color = {
    "0": "rgba(255, 0, 0, 0.5)",
    "1": "rgba(255, 165, 0, 0.5)",
    "2": "rgba(255, 255, 0, 0.5)",
    "3": "rgba(0, 255, 0, 0.5)"
  }

  // 製作 standard range
  const standard_range = display == 'smn1' ? makeStandardRange('smn1', range_data) : makeStandardRange('smn2', range_data)
  show_shapes.value = standard_range

  // 設定 annotations
  const annotations = display == 'smn1' ? makeSampleAnnotation('smn1') : makeSampleAnnotation('smn2')
  for (let i = 0; i < annotations.length; i++){
    for (let j = i+1; j < annotations.length; j++){
      if (Math.abs(annotations[i].y - annotations[j].y) < 0.03){
        annotations[i].y = annotations[i].y <= annotations[j].y ? annotations[i].y * 0.985 : annotations[i].y * 1.015
        annotations[j].y = annotations[j].y <= annotations[i].y ? annotations[j].y * 0.985 : annotations[j].y * 1.015
      }
    }
  }
  const standard_annotations = display == 'smn1' ? makeStandardAnnotation(standard_range) : makeStandardAnnotation(standard_range)
  show_annotations.value = annotations.concat(standard_annotations)

  // 設定 layout
  const layout = {
    title: 'Copy Number vs RFU',
    xaxis: { title: 'Copy Number', tickvals:x_axis, range: [-0.2, 5], zeroline: false },
    yaxis: { title: 'Normalized RFU', zeroline: false, showgrid: false, range: display_y_range[line_display_selection.value]},
    legend: {orientation: 'h', x: 0, y: -0.3},
    annotations: show_annotations.value,
    shapes: show_shapes.value
  };

  // 顯示圖表
  if (display == 'smn1'){
    const trace_to_display = [smn1_trace].concat(makeSampleTraces('smn1'))
    Plotly.newPlot(plotlyChart.value, trace_to_display, layout);
  } else if (display == 'smn2'){
    const trace_to_display = [smn2_trace].concat(makeSampleTraces('smn2'))
    Plotly.newPlot(plotlyChart.value, trace_to_display, layout);
  } else {
    const trace_to_display = [smn1_trace].concat(makeSampleTraces('smn1'))
    Plotly.newPlot(plotlyChart.value, trace_to_display, layout);
  }
}
*/

// (DEPRECATED) 顯示 Range control panel
/*
function show_Range_control_panel(){
  if (devPanelDisplay.value == 'none' && dataPanelDisplay.value == 'block'){
    devPanelDisplay.value = 'block'
    dataPanelDisplay.value = 'none'
  } else if (devPanelDisplay.value == 'block' && dataPanelDisplay.value == 'none'){
    devPanelDisplay.value = 'none'
    dataPanelDisplay.value = 'block'
  }
}
*/

// (DEPRECATED) 更新current_peak_condition
/*
function update_current_peak_condition(){
  const current_peak_settings = store.getters['SMAv4_analysis_data/getSMAv4ReanalysePeakSettings']
  const new_smn1_IC_range = current_peak_settings.smn1.internalControlPeak.peak_select_range
  const new_smn1_TG_range = current_peak_settings.smn1.targetPeak.peak_select_range
  const new_smn2_range = current_peak_settings.smn2.peak_condition.peak_select_range
  const new_smn1_IC_RFU_threshold = current_peak_settings.smn1.internalControlPeak.RFU_threshold
  const new_smn1_TG_RFU_threshold = current_peak_settings.smn1.targetPeak.RFU_threshold
  const new_smn2_RFU_threshold = current_peak_settings.smn2.peak_condition.RFU_threshold
  const newSMN1_min_IC_peak_count = current_peak_settings.smn1.internalControlPeak.Min_peak_count
  const newSMN1_min_TG_peak_count = current_peak_settings.smn1.targetPeak.Min_peak_count
  const newSMN2_min_peak_count = current_peak_settings.smn2.peak_condition.Min_peak_count
  const newSMN1_IC_size = current_peak_settings.smn1.internalControlPeak.Peak_size
  const newSMN1_TG_size = current_peak_settings.smn1.targetPeak.Peak_size
  const newSMN2_IC_size = current_peak_settings.smn2.peak_condition.internal_ctrl_size
  const newSMN2_TG_size = current_peak_settings.smn2.peak_condition.target_size
  const newSMN1_IC_neg_range = current_peak_settings.smn1.internalControlPeak.Negative_range
  const newSMN1_IC_pos_range = current_peak_settings.smn1.internalControlPeak.Positive_range
  const newSMN1_TG_neg_range = current_peak_settings.smn1.targetPeak.Negative_range
  const newSMN1_TG_pos_range = current_peak_settings.smn1.targetPeak.Positive_range
  const newSMN2_neg_range = current_peak_settings.smn2.peak_condition.Negative_range
  const newSMN2_pos_range = current_peak_settings.smn2.peak_condition.Positive_range
  current_peak_condition.value.RANGE.SMA1_IC_SIZE_RANGE = new_smn1_IC_range
  current_peak_condition.value.RANGE.SMA1_TG_SIZE_RANGE = new_smn1_TG_range
  current_peak_condition.value.RANGE.SMA2_SEARCH_RANGE = new_smn2_range
  current_peak_condition.value.RFU_THRESHOLD.SMN1_IC = new_smn1_IC_RFU_threshold
  current_peak_condition.value.RFU_THRESHOLD.SMN1_TG = new_smn1_TG_RFU_threshold
  current_peak_condition.value.RFU_THRESHOLD.SMN2 = new_smn2_RFU_threshold
  current_peak_condition.value.PEAK_NUMBER_CHECK.SMA1 = newSMN1_min_IC_peak_count
  current_peak_condition.value.PEAK_NUMBER_CHECK.SMA2 = newSMN1_min_TG_peak_count
  current_peak_condition.value.PEAK_NUMBER_CHECK.SMA2 = newSMN2_min_peak_count
  current_peak_condition.value.PEAK_SIZE.SMA1_IC = newSMN1_IC_size
  current_peak_condition.value.PEAK_SIZE.SMA1_TG = newSMN1_TG_size
  current_peak_condition.value.PEAK_SIZE.SMA2_IC = newSMN2_IC_size
  current_peak_condition.value.PEAK_SIZE.SMA2_TG = newSMN2_TG_size
  current_peak_condition.value.PEAK_RANGE_DIV.SMA1_IC.Negative_range = newSMN1_IC_neg_range
  current_peak_condition.value.PEAK_RANGE_DIV.SMA1_IC.Positive_range = newSMN1_IC_pos_range
  current_peak_condition.value.PEAK_RANGE_DIV.SMA1_TG.Negative_range = newSMN1_TG_neg_range
  current_peak_condition.value.PEAK_RANGE_DIV.SMA1_TG.Positive_range = newSMN1_TG_pos_range
  current_peak_condition.value.PEAK_RANGE_DIV.SMA2.Negative_range = newSMN2_neg_range
  current_peak_condition.value.PEAK_RANGE_DIV.SMA2.Positive_range = newSMN2_pos_range
}
*/

// (DEPRECATED) 製作 labeled_rfu_data
/*
function makeLabeledRFUData(currentAnalysisResult){

  // 初始化 labeled_rfu_data
  let labeled_rfu_data = {
    smn1: {},
    smn2: {}
  }

  // 製作 standard 的 labeled_rfu_data
  const std_data = currentAnalysisResult.resultObj.STD_DATA
  for (const smn of ['smn1', 'smn2']){
    for (const std of ['std1', 'std2', 'std3']){
      const DATA = SMAv4_DATA(
        std_data[smn][std].ic_peak.peak_rfu,
        std_data[smn][std].tg_peak.peak_rfu,
        std_data[smn][std].rfu_diff,
        'standard', smn, `${smn}_${std}`,
        std[std.length-1], std, smn
      )
      labeled_rfu_data[smn][std] = DATA
    }
  }

  // 加入 Sample 的 labeled_rfu_data
  const sample_data = currentAnalysisResult.resultObj.SAMPLE_DATA
  const sample_result = currentAnalysisResult.resultObj.RESULT_LIST
  for (const smn of ['smn1', 'smn2']){
    for (const sample of Object.keys(sample_data[smn])){
      const DATA = SMAv4_DATA(
        sample_data[smn][sample].ic_peak.peak_rfu,
        sample_data[smn][sample].tg_peak.peak_rfu,
        sample_data[smn][sample].rfu_diff,
        'sample', smn, sample,
        smn === 'smn1' ? sample_result[sample].smn1_copy_number : sample_result[sample].smn2_copy_number,
        `${sample}-${smn}`, smn
      )
      labeled_rfu_data[smn][sample] = DATA
    }
  }
  return labeled_rfu_data
}
*/

// (DEPRECATED) 搜集 rfu_data
/*
function gatherRFUData(){

  // 使用表格的數值更新 rfu_data
  function updateRFUData(){
    const current_table_data = JSON.parse(JSON.stringify(screening_table_rows.value))
    if (current_table_data.length > 0){
      for (const smn of ['smn1', 'smn2']){
        for (const item in rfu_data.value[smn]){
          const new_diff = current_table_data.find(row => row.type === 'sample' ? row.sample_name === `${item}-${smn}` && row.smn === smn : row.sample_name === item && row.smn === smn)
          rfu_data.value[smn][item]['diff'] = new_diff.diff
        }
      }
    }
  }

  const labeled_rfu_data = makeLabeledRFUData(currentAnalysisResult.value)

  for (const smn of ['smn1', 'smn2']){
    for (const sample in labeled_rfu_data[smn]){
      const sample_data = {}
      sample_data['internal_control'] = labeled_rfu_data[smn][sample]['internal_control']
      sample_data['target'] = labeled_rfu_data[smn][sample]['target']
      sample_data['diff'] = labeled_rfu_data[smn][sample]['diff']
      sample_data['type'] = labeled_rfu_data[smn][sample]['type']
      sample_data['smn'] = labeled_rfu_data[smn][sample]['smn']
      sample_data['sample_name'] = labeled_rfu_data[smn][sample]['sample_name']
      rfu_data.value[smn][sample] = sample_data
    }
  }

  updateRFUData()
}
*/

// (DEPRECATED) 轉換 peak_condition 的格式
/*
function convertPeakConditionFormat(peak_condition){
  const new_peak_condition = {
    smn1: {
      internalControlPeak: PEAK_CONFIG('smn1',
        peak_condition.PEAK_RANGE_DIV.SMA1_IC.Negative_range,
        peak_condition.PEAK_RANGE_DIV.SMA1_IC.Positive_range,
        peak_condition.PEAK_NUMBER_CHECK.SMA1,
        peak_condition.RFU_THRESHOLD.SMN1_IC,
        peak_condition.RANGE.SMA1_IC_SIZE_RANGE,
        peak_condition.PEAK_SIZE.SMA1_IC
      ),
      targetPeak: PEAK_CONFIG('smn1',
        peak_condition.PEAK_RANGE_DIV.SMA1_TG.Negative_range,
        peak_condition.PEAK_RANGE_DIV.SMA1_TG.Positive_range,
        peak_condition.PEAK_NUMBER_CHECK.SMA1,
        peak_condition.RFU_THRESHOLD.SMN1_TG,
        peak_condition.RANGE.SMA1_TG_SIZE_RANGE,
        peak_condition.PEAK_SIZE.SMA1_TG
      ),
    },
    smn2: {
      peak_condition: PEAK_CONFIG('smn2',
        peak_condition.PEAK_RANGE_DIV.SMA2.Negative_range,
        peak_condition.PEAK_RANGE_DIV.SMA2.Positive_range,
        peak_condition.PEAK_NUMBER_CHECK.SMA2,
        peak_condition.RFU_THRESHOLD.SMN2,
        peak_condition.RANGE.SMA2_SEARCH_RANGE,
        -1,
        peak_condition.PEAK_SIZE.SMA2_IC,
        peak_condition.PEAK_SIZE.SMA2_TG
      )
    }
  }
  return new_peak_condition
}
*/

// (DEPRECATED) 取得 control_ids
/*
const getControlID = (smav4InputFilesObj) => {

  // 取得檔名並且移除附檔名
  const simplifyFilePath = (file_path) => {
    if (!file_path) return '';

    // 先取得檔案名稱（移除路徑）
    const fileName = file_path.split('/').pop();

    // 移除附檔名
    return fileName.replace(/\.[^.]+$/, '');
  }

  return [
    simplifyFilePath(smav4InputFilesObj.smn1_std1),
    simplifyFilePath(smav4InputFilesObj.smn1_std2),
    simplifyFilePath(smav4InputFilesObj.smn1_std3),
    simplifyFilePath(smav4InputFilesObj.smn2_std1),
    simplifyFilePath(smav4InputFilesObj.smn2_std2),
    simplifyFilePath(smav4InputFilesObj.smn2_std3),
  ]
}
*/

// 轉換 smn 的格式
/*
const smnTypeInterpretation = (smn1, smn2) => {
  const type = String(smn1) + String(smn2);

  const isNormal = (typeArray) => [
    "20", "21", "22", "23", "24",
    "30", "31", "32", "33", "34",
    "41", "42", "43", "44"
  ].includes(typeArray);

  const isCarrier = (typeArray) => ["10", "11", "12", "13", "14"].includes(typeArray);
  const isAffected = (typeArray) => ["01", "02", "03", "04"].includes(typeArray);

  if (isNormal(type)) {
    return { value: "normal", label: "Normal" };
  } else if (isCarrier(type)) {
    return { value: "carrier", label: "SMA carrier" };
  } else if (isAffected(type)) {
    return { value: "affected", label: "SMA affected" };
  } else {
    return { value: "invalid", label: "Invalid" };
  }
};
*/

// (DEPRECATED) 重新分析
/*
async function reAnalysisSMAv4(){
  $q.loading.show({
    spinner: QSpinnerFacebook,
    spinnerColor: "deep-orange-6",
    spinnerSize: 100,
    message: "Analyzing...",
    messageColor: "white",
  });

  // 取得 re_analyse_selection
  const re_analyse_selection = Object.values(store.getters['SMAv4_analysis_data/getSMAv4ReanalyseSelection'])

  // 更新 current_peak_condition
  if (re_analyse_selection.includes('new_peak')){
    update_current_peak_condition()
  } else {
    current_peak_condition.value = settingBackup
  }

  // 搜集 rfu_data
  if (re_analyse_selection.includes('new_std')){
    gatherRFUData()
  } else {
    rfu_data.value = undefined
  }

  // 取得 input_file_obj
  const smav4InputFilesObj = currentAnalysisResult.value.resultObj.INPUT_FILE_OBJ
  const inputPeakCondition = convertPeakConditionFormat(current_peak_condition.value)

  // 取得 control_ids
  const control_ids = getControlID(smav4InputFilesObj);

  // inputData
  const InputData = {
    file_path: smav4InputFilesObj,
    peak_condition: inputPeakCondition,
  }

  // 取得 settingProps
  const currentSettingProps = store.getters["analysis_setting/getSettingProps"];

  // 執行 submitWorkflow
  const analysisResult = await submitWorkflow('SMA', InputData, login_status.value.user_info, currentSettingProps);

  // 檢查有沒有出錯
  if (analysisResult.status == 'success'){
    dialog_error_message.value = "";

    // 將 result 中 Infinity 轉換成 null
    const resultStr = analysisResult.result.replace(/Infinity/g, 'null');
    const resultObj = JSON.parse(resultStr);

    // 製作 SMAv4_RESULT
    const SMAv4_Result = SMAv4_RESULT(
      resultObj.STD_DATA,
      resultObj.SAMPLE_DATA,
      resultObj.COPY_NUMBER_RANGES,
      resultObj.RESULT_LIST,
      resultObj.PARAMETERS,
      smav4InputFilesObj,
      currentAnalysisResult.value.resultObj.USE_CONFIG_NAME
    );

    // 製作 EXPORT_RESULT
    const sample_list = Object.keys(SMAv4_Result.RESULT_LIST);
    const exportResult = sample_list.map((sample_name, index)=>{
      const smn1 = SMAv4_Result.RESULT_LIST[sample_name].smn1_copy_number;
      const smn2 = SMAv4_Result.RESULT_LIST[sample_name].smn2_copy_number;
      const smnAssessment = smnTypeInterpretation(smn1, smn2);
      return EXPORT_RESULT(
        index+1,
        sample_name,
        SMAv4_Result.RESULT_LIST[sample_name].typeStr,
        [SMAv4_Result.RESULT_LIST[sample_name].typeStr],
        smnAssessment.value,
        smnAssessment.label
      )
    })

    // 製作 ANALYSIS_RESULT
    const AnalysisResult = ANALYSIS_RESULT(
      "SMAv4",
      currentAnalysisID.value.analysis_uuid,
      resultObj.config,
      control_ids,
      resultObj.qc_status,
      resultObj.errMsg,
      SMAv4_Result,
      exportResult
    );

    // 將結果存到 firestore
    update_userAnalysisData(login_status.value.user_info.uid, dbSMAv4ResultPath, AnalysisResult, currentAnalysisID.value.analysis_uuid);

    // 更新 currentDisplayAnalysisID
    store.commit("analysis_setting/updateCurrentDisplayAnalysisID", {
      analysis_name: "SMAv4",
      analysis_uuid: currentAnalysisID.value.analysis_uuid,
    });

    // 更新 currentAnalysisID
    const new_id = `analysis_${uuidv4()}`;
    store.commit('analysis_setting/updateCurrentAnalysisID', {
      analysis_name: 'SMAv4',
      analysis_uuid: new_id,
    });
    currentAnalysisID.value = store.getters['analysis_setting/getCurrentAnalysisID'];

    // 重新整理頁面
    setTimeout(()=>{
      router.go(0);
      $q.loading.hide();
    }, 1500);
  }
  else if (analysisResult.status == 'error'){
    // 通知
    $q.notify({
      progress: true,
      message: "分析流程出了一點問題...",
      icon: 'mdi-alert-circle',
      color: 'deep-orange-6',
      position: 'top'
    });
    // 跳出警告視窗
    dialog_error_message.value = analysisResult.message;
    warning_dialog.value.open_warning_dialog();

    // 隱藏 loading 視窗
    $q.loading.hide();
  }
}

// 定義 expose
defineExpose({
  reAnalysisSMAv4
})

*/

// (DEPRECATED) Emits
/*
const emit = defineEmits(['updatePeakSettings']);
*/

// (DEPRECATED) function
/*
function call_updatePeakSettings(newPeakSettings){
  emit('updatePeakSettings', newPeakSettings);
}
*/

// 掛載時
onMounted(async () => {

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

  // (DEPRECATED) 更新 peak_condition
  // const inputPeakCondition = convertPeakConditionFormat(currentAnalysisResult.value.resultObj.PARAMETERS)
  // call_updatePeakSettings(inputPeakCondition)

  // 更新表格內容
  updateTableRowsSample(currentAnalysisResult.value);
  // updateDiagram_options(currentAnalysisResult.value);

  // (DEPRECATED) 更新 Range Table
  // updateRangeTable(currentAnalysisResult.value);
  // devPanel.value.init_range_table_rows();

  // 更新 standard_data
  // update_standard_data();

  // 更新 Assessment 表格資料行, 取得 range_table_rows
  assessment_table.value.updateRangeTableRows();

  // (DEPRECATED) 更新 current_peak_condition
  // update_current_peak_condition();

  // 搜集 rfu_data
  // gatherRFUData();

  // 先嘗試取得當前的分析 ID, 如果沒有則建立新的分析 ID
  currentAnalysisID.value = store.getters['analysis_setting/getCurrentAnalysisID'];
  setAnalysisID(store, 'SMAv4');

  // (DEPRECATED) 顯示圖表
  // nextTick(() => {
  //   updatePlotlyChart(line_display_selection.value);
  // });
})

// (DEPRECATED) 組件卸載
/*
onUnmounted(() => {
  // 清除圖表
  if (plotlyChart.value) {
    Plotly.purge(plotlyChart.value);
  }
});
*/

// (DEPRECATED) 偵測 line_display_selection 的變化
/*
watch(line_display_selection, (newVal) => {
  // 更新圖表
  updatePlotlyChart(newVal)
})
*/

// (DEPRECATED) 偵測 screening_table_rows 的變化
/*
watch(screening_table_rows, () => {
  // 更新圖表
  updatePlotlyChart(line_display_selection.value)
}, { deep: true })
*/

</script>

<style scoped>
.table-header{
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
}
.center-content {
  display: flex;
  flex-direction: row;
  align-items: center;
  width: fit-content;
}
.result-box{
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 1px solid #e0e0e0;
  margin-inline: 10px;
  padding-inline: 10px;
}
.std-curve-box{
  height: 683px;
  min-width: 600px;
  max-width: 720px;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  background-color:white;
}
</style>
