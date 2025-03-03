<template>
  <q-card bordered :style="{display: showResult ? 'block' : 'none'}">
    <q-card-section>
      <div class="row">

        <div class="col-auto">
          <div class="col text-h5 text-uppercase text-bold text-blue-grey-7">
            Screening Result
          </div>
          <q-card flat>
            <q-card-section>
              <q-table
                :rows="resultTableFxProps"
                :columns="columns"
                :v-model:pagination="{ rowsPerPage: 0 }"
                :rows-per-page-options="[0]"
                row-key="sampleId"
                flat
                dense
              >
                <template v-slot:body-cell-assessment="props">
                  <q-td :props="props">
                    <div>
                      <q-chip
                        :key="props.value"
                        :color="interpretationColor(props.value)"
                        :label="props.value"
                      />
                    </div>
                  </q-td>
                </template>
                <template v-slot:body-cell-showRepeats="props">
                  <q-td class="text-center" :props="props">
                    <q-btn
                      push
                      :color="btnColor(props.key)"
                      :text-color="btnTextColor(props.key)"
                      round
                      icon="mdi-chart-bell-curve-cumulative"
                      size="md"
                      @click="showRepeats(props.key)"
                      :disable="
                        props.row.interpretation[0] !== 'Inconclusive'
                          ? props.row.interpretation[0] !== 'Invalid'
                              ? false
                              : true
                        : false"
                    />
                  </q-td>
                </template>
              </q-table>
            </q-card-section>
          </q-card>
        </div>

        <div class="col">
          <div class="col text-h5 text-uppercase text-bold text-blue-grey-7">
            Standard Curve
          </div>
          <q-card flat>
            <q-card-section>
              <div v-if="true">
                <div class="q-col-gutter-xs column justify-center">
                  <div class="q-mr-xl row justify-center">
                    <q-chip dense color="white" text-color="blue-grey-7" icon="remove">
                      <div style="color:#37474f">Standard Curve</div>
                    </q-chip>
                    <q-chip dense color="white" text-color="blue-6" icon="circle">
                      <div style="color:#37474f">Control</div>
                    </q-chip>
                    <q-chip dense color="white" text-color="purple-7" icon="circle" v-if="showChartId">
                      <div style="color:#37474f">{{ showChartId }}</div>
                    </q-chip>
                  </div>
                  <div class="q-mr-xl row justify-center">
                    <q-chip dense color="white" text-color="green-13" icon="mdi-square">
                      <div style="color:#37474f">Normal</div>
                    </q-chip>
                    <q-chip dense color="white" text-color="grey-13" icon="mdi-square">
                      <div style="color:#37474f">Intermediate</div>
                    </q-chip>
                    <q-chip dense color="white" text-color="yellow-8" icon="mdi-square">
                      <div style="color:#37474f">Premutation</div>
                    </q-chip>
                    <q-chip dense color="white" text-color="red-6" icon="mdi-square">
                      <div style="color:#37474f">Full Mutation</div>
                    </q-chip>
                  </div>
                  <div id="chart">
                    <canvas id="fxChart"></canvas>
                  </div>
                </div>
              </div>
              <div v-else>
                <div class="q-mx-md justify-start">
                  <q-chip
                    color="white"
                    text-color="red-8"
                    icon="warning"
                    label="No standard curve avaiable due to fail the criteria"
                  >
                  </q-chip>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from "vue";
import { useStore } from "vuex";
import Chart from 'chart.js/auto';
import annotationPlugin from 'chartjs-plugin-annotation';
import { getCurrentDisplayAnalysisID, getCurrentAnalysisResult } from '@/composables/checkAnalysisStatus.js';
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';

// 註冊 Chart.js 插件
Chart.register(annotationPlugin);

// 取得 store
const store = useStore();

// 控制結果版面顯示
const showResult = ref(true);

// 響應式變數
const showChartId = ref(null);
const windowWidth = ref(window.innerWidth); // 新增視窗寬度響應式變數

// 保存當前分析結果
const { login_status } = updateGetUserInfo();
const currentAnalysisResult = ref(null);
const currentSettingProps = ref(null);
const currentDisplayAnalysis = ref({
  analysis_uuid: '',
  analysis_name: '',
});

// 定義 FXS Result DATA
const FXS_RESULT_DATA = (result_list, qc, control, config) => {
  return {
    result: result_list,
    qc: qc,
    control: control,
    config: config
  }
}

// 定義 FXS Result
const FXS_RESULT = (sample_id , gender, position, interpretation, assessment) => {
  return {
    sample_id: sample_id,
    gender: gender,
    position: position,
    interpretation: interpretation,
    assessment: assessment
  }
}

// 定義 FXS QC
const FXS_QC = (status, linear) => {
  return {
    status: status,
    linear: linear
  }
}

// 定義 FXS Control
const FXS_CONTROL = (standard_1, standard_2, standard_3, standard_4) => {
  return {
    standard_1: standard_1,
    standard_2: standard_2,
    standard_3: standard_3,
    standard_4: standard_4
  }
}

// 監聽視窗寬度變化的函數
const handleResize = () => {
  windowWidth.value = window.innerWidth;
  // 更新圖表大小
  updateFxChart();
};

// 表格欄位定義
const columns = [
  {
    name: "sampleId",
    required: true,
    label: "Sample ID",
    align: "center",
    field: (row) => row.sampleId,
    format: (val) => `${val}`,
    sortable: true,
  },
  { name: "gender", label: "Gender", field: "gender", align: "center" },
  {
    name: "repeats",
    label: "Repeats No.",
    field: "repeats",
    align: "center",
  },
  {
    name: "assessment",
    label: "Assessment",
    field: "assessment",
    align: "center",
  },
  {
    label: "Show Repeats",
    align: "center",
    name: "showRepeats",
  },
];

// 取得 FXS 圖表
const fxChartProps = computed(
  () => store.getters["FXS_analysis_data/fxChartProps"]
);

// 取得 FXS 導出結果
const resultTableFxProps = computed(
  () => store.getters["FXS_analysis_data/resultTableFxProps"]
);

// 測試資料
const FXS_DISPLAY_RESULT = ref(null);

// 轉換 QC 字串
const getQCStatus = (status) => {
  if (status === "meet-the-criteria") {
    return "Meet the criteria";
  } else if (status === "fail-the-criteria") {
    return "Fail the criteria";
  } else {
    return "Invalid";
  }
}

// 取得線性
const getLinear = (control_qc_obj) => {
  const line1 = [control_qc_obj.line[0].x, control_qc_obj.line[0].y];
  const line2 = [control_qc_obj.line[1].x, control_qc_obj.line[1].y];
  return [line1, line2];
}

// 取得 FXS 結果, 整理
function update_FXS_RESULT_OBJ(fxs_result) {

  console.log(fxs_result);

  // 製作 QC
  const fxs_qc = FXS_QC(getQCStatus(fxs_result.qc_status), getLinear(fxs_result.resultObj.control_qc));

  // 製作 Control
  const control_list = Object.keys(fxs_result.resultObj.control_data);
  const fxs_control = control_list.length === 4 ? FXS_CONTROL(
      {bp: fxs_result.resultObj.control_data[0].peak_size, repeats_standard: fxs_result.resultObj.control_data[0].repeatNum},
      {bp: fxs_result.resultObj.control_data[1].peak_size, repeats_standard: fxs_result.resultObj.control_data[1].repeatNum},
      {bp: fxs_result.resultObj.control_data[2].peak_size, repeats_standard: fxs_result.resultObj.control_data[2].repeatNum},
      {bp: fxs_result.resultObj.control_data[3].peak_size, repeats_standard: fxs_result.resultObj.control_data[3].repeatNum}
    ) : control_list.length === 3 ? FXS_CONTROL(
      {bp: fxs_result.resultObj.control_data[0].peak_size, repeats_standard: fxs_result.resultObj.control_data[0].repeatNum},
      {bp: fxs_result.resultObj.control_data[1].peak_size, repeats_standard: fxs_result.resultObj.control_data[1].repeatNum},
      {bp: fxs_result.resultObj.control_data[2].peak_size, repeats_standard: fxs_result.resultObj.control_data[2].repeatNum}
    ) : null;

  // 如果 Control 資料不合法, 則跳出
  if (!fxs_control) {
    console.error("Control data is not valid");
    showResult.value = false;
    return;
  }

  // 製作 Result
  const resultList = Object.keys(fxs_result.resultObj.result);
  let result_list = [];
  resultList.forEach(sample => {
    const raw_res = fxs_result.resultObj.result[sample];
    const raw_data = fxs_result.resultObj.sample_data[sample];
    const peak_pos = raw_data.selected_fx_peaks.map(peak => ({
      repeats: peak.average_repeatNum,
      bp: peak.peak_size
    }));
    const result = FXS_RESULT(
      sample,
      raw_res.gender,
      peak_pos,
      raw_res.interpretation,
      raw_res.assessment
    );
    result_list.push(result);
  });

  // 製作 Result
  const result = FXS_RESULT_DATA(
    result_list,
    fxs_qc,
    fxs_control,
    fxs_result.config
  );

  FXS_DISPLAY_RESULT.value = result;
}

// 解釋結果的顏色
const interpretationColor = (value) => {
  if (value === "Normal") {
    return "green-13";
  } else if (
    (value === "Intermediate") ||
    (value === "Normal/Intermediate")
  ) {
    return "grey-5";
  } else if (
    (value === "Premutation") ||
    (value === "Normal/Premutation") ||
    (value === "Intermediate/Premutation")
  ) {
    return "yellow-8";
  } else if (
    (value === "Full mutation") ||
    (value === "Normal/Full mutation") ||
    (value === "Intermediate/Full mutation") ||
    (value === "Premutation/Full mutation")
  ) {
    return "red";
  } else {
    return "white";
  }
};

// 解釋結果
const interpretation = (value) => {
  if (value === "Normal") {
    return "normal";
  } else if (
    (value === "Intermediate") ||
    (value === "Normal/Intermediate")
  ) {
    return "intermediate";
  } else if (
    (value === "Premutation") ||
    (value === "Normal/Premutation") ||
    (value === "Intermediate/Premutation")
  ) {
    return "premutation";
  } else if (
    (value === "Full mutation") ||
    (value === "Normal/Full mutation") ||
    (value === "Intermediate/Full mutation") ||
    (value === "Premutation/Full mutation")
  ) {
    return "full";
  } else if ("Inconclusive"){
    return "inconclusive";
  } else {
    return "invalid";
  }
};

// 按鈕顏色
const btnColor = (id) => {
  return showChartId.value === id ? "blue-grey-8" : "white";
};

// 按鈕文字顏色
const btnTextColor = (id) => {
  return showChartId.value === id ? "white" : "blue-grey-8";
};

// 更新圖表
function updateFxChart() {
  if (fxChartProps.value) {
    document.getElementById("fxChart")?.remove();
    const canvas = document.createElement('canvas');
    canvas.id = "fxChart";
    document.getElementById("chart").appendChild(canvas);
    new Chart(document.getElementById('fxChart'), fxChartProps.value);
  }
}

// 顯示重複次數
function showRepeats(id) {
  if (showChartId.value === id) {
    showChartId.value = null;
    store.commit("FXS_analysis_data/updateShowFxChartId", null);
  } else {
    showChartId.value = id;
    store.commit("FXS_analysis_data/updateShowFxChartId", id);
  }
  // 更新圖表
  updateFxChart();
}

// 生命週期鉤子
onMounted(async () => {

  // 添加視窗大小變化的事件監聽器
  window.addEventListener('resize', handleResize);

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

  // 更新 FXS 結果
  update_FXS_RESULT_OBJ(currentAnalysisResult.value);

  // 創建圖表
  if (fxChartProps.value) {
    new Chart(document.getElementById('fxChart'), fxChartProps.value);
    store.commit("FXS_analysis_data/updateShowFxChartId", null);
  }

  // 將測試資料載入
  store.commit("FXS_analysis_data/updateFragileXResult", FXS_DISPLAY_RESULT.value);

  // 更新圖表
  updateFxChart();

  // 更新導出結果
  const updated = resultTableFxProps.value.map((row, index) => ({
    index: index + 1,
    sampleId: row.sampleId,
    result: row.position,
    resultLabel: [row.repeats],
    assessment: interpretation(row.assessment),
    assessmentLabel: row.assessment
  }));

  store.commit("FXS_analysis_data/updateExportResults", updated);

});

// 組件卸載時移除事件監聽器
onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
#chart {
  width: 100%;
  height: 100%;
}
</style>
