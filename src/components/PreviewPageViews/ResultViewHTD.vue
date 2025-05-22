<template>
  <q-card bordered :style="{display: showResult ? 'block' : 'none'}">
    <q-card-section>
      <div class="row">

        <div class="col">
          <div class="text-h5 text-uppercase text-bold text-blue-grey-7">
            Screening Result
          </div>
          <q-card flat>
            <q-card-section>
              <q-table
                :rows="resultTableHdProps"
                :columns="columns"
                :v-model:pagination="{ rowsPerPage: 0 }"
                :rows-per-page-options="[0]"
                row-key="sample_id"
                flat
                dense
              >
                <template v-slot:body-cell-assessment="props">
                  <q-td :props="props">
                    <div>
                      <q-chip
                        :key="props.value"
                        :color="assessmentColor(props.value)"
                        :label="assessmentValue(props.value)"
                      />
                    </div>
                  </q-td>
                </template>
                <template v-slot:body-cell-showChart="props">
                  <q-td class="text-center" :props="props">
                    <q-btn
                      push
                      :color="btnColor(props.row.sampleId)"
                      :text-color="btnTextColor(props.row.sampleId)"
                      round
                      icon="mdi-chart-bell-curve"
                      size="md"
                      @click="showChart(props.row.sampleId)"
                      :disable="
                        props.row.assessment !== 'inconclusive'
                          ? props.row.assessment !== 'invalid'
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
          <div class="text-h5 text-uppercase text-bold text-blue-grey-7">
            Result Line Chart
          </div>
          <q-card flat>
            <q-card-section>
              <div v-if="hdQCStatus === 'meet-the-criteria'">
                <div :style="{ display: closeHint ? 'block' : 'none' }">
                  <div id="chart">
                    <canvas id="hdChart"></canvas>
                  </div>
                </div>
                <div :style="{ display: closeHint ? 'none' : 'block' }">
                  <div class="q-mx-md justify-start">
                    <q-chip
                      color="white"
                      text-color="blue-grey-8"
                      icon="touch_app"
                      label="Please select sample line chart from screening results"
                    >
                    </q-chip>
                  </div>
                </div>
              </div>
              <div v-else>
                <div class="q-mx-md justify-start">
                  <q-chip
                    color="white"
                    text-color="red-8"
                    icon="warning"
                    label="No HTD line chart avaiable due to fail the criteria"
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
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';
import { getCurrentDisplayAnalysisID, getCurrentAnalysisResult } from '@/composables/checkAnalysisStatus.js';

// 註冊 Chart.js 插件
Chart.register(annotationPlugin);

// 取得 store
const store = useStore();

// 響應式變數
const showChartId = ref(null);
const closeHint = ref(false);

// 表格欄位定義
const columns = [
  {
    name: "sampleId",
    required: true,
    label: "Sample ID",
    align: "center",
    field: (row) => row.sampleId,
    format: (val) => `${val}`,
  },
  {
    name: "repeats",
    label: "Repeats",
    field: "repeats",
    align: "center",
  },
  {
    name: "assessment",
    align: "center",
    label: "Assessment",
    field: "assessment",
  },
  {
    label: "Line Chart",
    name: "showChart",
    align: "center",
  },
];

// 保存當前分析結果
const { login_status } = updateGetUserInfo();
const currentAnalysisResult = ref(null);
const currentSettingProps = ref(null);
const currentDisplayAnalysis = ref({
  analysis_uuid: '',
  analysis_name: '',
});

// 所有 HTD 結果資料
const hdResult = ref(null);
const hdQCStatus = ref('');
const hdChartProps = computed(
  () => store.getters["HTD_analysis_data/hdChartProps"]
);
const resultTableHdProps = computed(
  () => store.getters["HTD_analysis_data/resultTableHdProps"]
);

// 控制是否顯示結果
const showResult = ref(true);

// 定義 HTD result
const HTD_RESULT_DATA = (qc_status, resultList, controls) => {
  return {
    qc: { status: qc_status },
    result: resultList,
    control: controls,
  };
};

// 定義 HTD result
const HTD_RESULT = (sample_id, sample_qc, repeats, assessment, bp, peak_data) => {
  return {
    sample_id: sample_id,
    internalQc: { status: sample_qc },
    repeats: repeats,
    assessment: assessment,
    bp: bp,
    raw: peak_data,
  };
};

// 定義 Peak data
const HTD_PEAK_DATA = (bp, rfu, repeats) => {
  return {
    bp: bp,
    rfu: rfu,
    repeats: repeats,
  };
};

// 定義 HTD control
const HTD_CONTROL = (std1_bp, std2_bp) => {
  return {
    control: {
      standard_1: {
        bp: std1_bp,
      },
      standard_2: {
        bp: std2_bp,
      },
    },
  };
};

// 結果評估顏色
const assessmentColor = (value) => {
  if (value === "normal") {
    return "green-13";
  } else if (value === "intermediate") {
    return "grey-5";
  } else if (value === "penetrance") {
    return "yellow-8";
  } else if (value === "full-penetrance") {
    return "red";
  } else {
    return "white";
  }
};

// 結果評估值
const assessmentValue = (value) => {
  if (value === "normal") {
    return "Normal";
  } else if (value === "intermediate") {
    return "Intermediate";
  } else if (value === "penetrance") {
    return "Reduced penetrance";
  } else if (value === "full-penetrance") {
    return "Full penetrance";
  } else if (value === "inconclusive") {
    return "Inconclusive";
  } else {
    return "Invalid";
  }
};

// 按鈕顏色
const btnColor = (id) => {
  return id === showChartId.value ? "blue-grey-8" : "white";
};

// 按鈕文字顏色
const btnTextColor = (id) => {
  return id === showChartId.value ? "white" : "blue-grey-8";
};

// 顯示圖表
function showChart(id) {
  showChartId.value = id;
  store.commit("HTD_analysis_data/updateShowHdChartId", id);
  closeHint.value = true;
  updateChart();
}

// 更新圖表
function updateChart() {
  if (hdChartProps.value) {
    document.getElementById("hdChart")?.remove();
    const canvas = document.createElement('canvas');
    canvas.id = "hdChart";
    document.getElementById("chart").appendChild(canvas);
    new Chart(document.getElementById('hdChart'), hdChartProps.value);
  }
}

// 更新 hdResult
function updateHdResult(analysis_result) {
  // 製作 control obj
  const control = HTD_CONTROL(
    analysis_result.resultObj.standard_control_data ? analysis_result.resultObj.standard_control_data[0].peak_size : '-',
    analysis_result.resultObj.standard_control_data ? analysis_result.resultObj.standard_control_data[1].peak_size : '-'
  );

  // 製作 result obj
  let result_list = [];
  const sample_list = analysis_result.resultObj.result_and_data ? Object.keys(analysis_result.resultObj.result_and_data) : [];
  sample_list.forEach((sample_id) => {
    const data = analysis_result.resultObj.result_and_data[sample_id];
    const repeats = data.selected_target_peaks.map((item) => item.repeat_num);
    const bp = data.selected_target_peaks.map((item) => item.peak_size);
    const peak_data = data.selected_target_peaks.map((item) => HTD_PEAK_DATA(item.peak_size, item.peak_rfu, item.repeat_num));
    const result = HTD_RESULT(sample_id, data.sample_qc_status, repeats, data.assessment, bp, peak_data);
    result_list.push(result);
  });

  // 更新 hdResult
  hdResult.value = HTD_RESULT_DATA(analysis_result.qc_status, result_list, control);
  store.commit("HTD_analysis_data/updateHdResult", hdResult.value);
  hdQCStatus.value = analysis_result.qc_status;
}

// 處理視窗大小變化
function handleResize() {
  updateChart();
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

  // 更新 hdResult
  updateHdResult(currentAnalysisResult.value);
});

// 組件卸載時移除事件監聽器
onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});

</script>
