<template>
  <q-card bordered v-if="showResult">
    <q-card-section>
      <div class="row">

        <div class="col-5">
          <div class="col text-h5 text-uppercase text-bold text-blue-grey-7">
            Screening Result
          </div>
          <q-card flat>
            <q-card-section>
              <q-table
                :rows="resultTableApoeProps"
                :columns="columns"
                :v-model:pagination="{ rowsPerPage: 0 }"
                :rows-per-page-options="[0]"
                row-key="sampleId"
                flat
                dense
              >
              <template v-slot:body-cell-type="props">
                <q-td
                  class="col text-center text-blue-grey text-overline text-bold"
                >
                  <div class="row justify-center">
                    {{ props.row.apoeType }}
                  </div>
                </q-td>
              </template>
                <template v-slot:body-cell-assessment="props">
                  <q-td :props="props">
                    <q-chip
                      :key="props.value"
                      :color="assessmentColor(props.value)"
                      :label="assessment(props.value)"
                    />
                  </q-td>
                </template>
                <template v-slot:body-cell-showWellPosition="props">
                  <q-td class="text-center" :props="props">
                    <q-btn
                      push
                      :color="btnColor(props.key)"
                      :text-color="btnTextColor(props.key)"
                      round
                      icon="touch_app"
                      size="sm"
                      @click="showWellPosition(props.key)"
                    />
                  </q-td>
                </template>
              </q-table>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-7">
          <div class="col text-h5 text-uppercase text-bold text-blue-grey-7">
            Result Well Position
          </div>
          <q-card flat>
            <div class="q-pt-sm q-pl-md q-pr-md row justify-center">
              <q-chip dense color="white" text-color="cyan-2" icon="mdi-square">
                <div class="text-blue-grey-7">E2</div>
              </q-chip>
              <q-chip dense color="white" text-color="light-green-2" icon="mdi-square">
                <div class="text-blue-grey-7">E3</div>
              </q-chip>
              <q-chip dense color="white" text-color="purple-2" icon="mdi-square">
                <div class="text-blue-grey-7">E4</div>
              </q-chip>
            </div>

            <div class="q-pl-md q-pr-md well-grid-container">
              <!-- Empty corner cell for alignment -->
              <div class="corner-cell"></div>

              <!-- Column titles -->
              <div
                class="grid-col-title text-weight-bold text-blue-grey-7"
                v-for="col in wellCols"
                :key="col"
              >{{ col }}</div>

              <!-- Row titles and grid content -->
              <template v-for="row in 12" :key="row">
                <!-- Row title -->
                <div class="grid-row-title text-weight-bold text-blue-grey-7">{{ row }}</div>

                <!-- Grid content for the row -->
                <div v-for="col in wellCols" :key="col" class="grid-col">
                  <div class="button-container">
                    <q-btn
                      :color="getWellInfo(row, col).color"
                      :outline="getWellInfo(row, col).type === '' ? true : false"
                      style="width: 100%; height: 100%;"
                      square
                      unelevated
                    >
                      <template v-slot:default>
                        <div v-if="getWellInfo(row, col).sampleId.length > 0">
                          <div v-for="(s, idx) in getWellInfo(row, col).id" :key="s">
                            <div v-if="getWellInfo(row, col).sampleId[0] === showWellSampleId" class="text-caption text-weight-medium text-white">
                              <div>{{ s }}</div>
                            </div>
                            <div v-else :class="getWellInfo(row, col).textClass[idx]">
                              <div>{{ s }}</div>
                            </div>
                          </div>
                        </div>
                      </template>
                    </q-btn>
                  </div>
                </div>
              </template>
            </div>
          </q-card>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useStore } from 'vuex';

// 導入 composable
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';
import { getCurrentDisplayAnalysisID, getCurrentAnalysisResult } from '@/composables/checkAnalysisStatus.js';

// 取得 store
const store = useStore();

// 響應式變數
const showResult = ref(true);
const wellLengend = ref('show');
const wellCols = ref(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']);
const showWellSampleId = ref(null);

// 保存當前分析結果
const { login_status } = updateGetUserInfo();
const currentAnalysisResult = ref(null);
const currentSettingProps = ref(null);
const currentDisplayAnalysis = ref({
  analysis_uuid: '',
  analysis_name: '',
});

// 定義 APOE 分析結果
const APOE_RESULT_DATA = (qc_status, control_data, result_list) => {
  return {
    qc: { qc_status },
    control: control_data,
    result: result_list,
  }
}

// 定義 APOE 控制資料
const APOE_WELL_DATA = (id, well, filename) => {
  return {
    id,
    well,
    filename,
  }
}

// 定義 APOE 控制資料
const APOE_CONTROL_DATA = (std1_e2, std1_e3, std1_e4, std2_e2, std2_e3, std2_e4) => {
  return {
    standard1: {
      e2: std1_e2,
      e3: std1_e3,
      e4: std1_e4,
    },
    standard2: {
      e2: std2_e2,
      e3: std2_e3,
      e4: std2_e4,
    },
  }
}

// 定義 APOE 結果資料
const APOE_RESULT = (e2_data, e3_data, e4_data, type, assessment) => {
  return {
    e2: e2_data,
    e3: e3_data,
    e4: e4_data,
    type,
    assessment,
  }
}

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
    name: "type",
    label: "Genotype",
    field: "apoeType",
    align: "center"
  },
  {
    name: "assessment",
    align: "center",
    label: "Assessment Result",
    field: "assessment"
  },
  {
    name: "showWellPosition",
    align: "center",
    label: "Show Well Position",
  }
];

// 表格資料
const resultTableApoeProps = computed(() => store.getters["APOE_analysis_data/resultTableApoeProps"]);
const resultWellInfo = computed(() => store.getters["APOE_analysis_data/resultWellInfo"]);

// 按鈕顏色
const btnColor = (sampleId) => {
  return showWellSampleId.value === sampleId ? "blue-grey-8" : "white";
};

// 按鈕文字顏色
const btnTextColor = (sampleId) => {
  return showWellSampleId.value === sampleId ? "white" : "blue-grey-8";
};

// 評估顏色
const assessmentColor = (value) => {
  if (value === "low-risk") {
    return "green-13";
  } else if (value.includes("normal-risk")) {
    return "yellow-8";
  } else if (value.includes("high-risk")) {
    return "deep-orange-5";
  } else {
    return "white";
  }
};

// 評估結果
const assessment = (value) => {
  if (value === 'low-risk') {
    return "Low risk";
  } else if (value === 'normal-risk') {
    return "Normal risk";
  } else if (value === 'high-risk') {
    return "High risk";
  } else if (value === 'inconclusive') {
    return "Inconclusive";
  } else {
    return "Invalid";
  }
};

// 顯示孔位置
function showWellPosition(sampleId) {
  if (showWellSampleId.value === sampleId) {
    showWellSampleId.value = null;
  } else {
    showWellSampleId.value = sampleId;
  }
}

// 取得孔資訊
function getWellInfo(row, col) {
  let well = `${col}${('0' + row).slice(-2)}`;
  let wellInfoArr = resultWellInfo.value[well];
  let typeColor = {
    'e2': 'cyan-1',
    'e3': 'light-green-1',
    'e4': 'purple-1',
  };
  let typeStrikeColor = {
    'e2': 'cyan-7',
    'e3': 'light-green-7',
    'e4': 'purple-7',
  };
  let textClass = {
    'sample': 'text-caption text-weight-medium text-blue-grey-7',
    'standard1': 'text-caption text-weight-medium text-blue-8',
    'standard2': 'text-caption text-weight-medium text-light-blue-8',
  };

  if (wellInfoArr && wellInfoArr.length > 0) {
    return {
      sampleId: wellInfoArr.map((info) => info.sampleId),
      id: wellInfoArr.map((info) => info.id),
      type: wellInfoArr.map((info) => info.type),
      sampleType: wellInfoArr.map((info) => info.sampleType),
      filename: wellInfoArr.map((info) => info.filename),
      textClass: wellInfoArr.map((info) => textClass[info.sampleType]),
      color: wellInfoArr.length > 1
        ? "grey-3"
        : wellInfoArr.some((info) => info.sampleId === showWellSampleId.value)
          ? typeStrikeColor[wellInfoArr[0].type]
          : typeColor[wellInfoArr[0].type],
    };
  } else {
    return {
      sampleId: [''],
      id: [''],
      type: '',
      sampleType: '',
      filename: '',
      textClass: 'grey-4',
      color: 'grey-4',
    };
  }
}

// 更新 APOE 分析結果
function updateAPOEAnalysisResult(apoeResult) {
  // 解析 well 資料
  function parseWellData(controlList, targetPeakGroup) {
    return APOE_WELL_DATA(
      controlList.find(item => item.peak_group === targetPeakGroup).sample_id,
      controlList.find(item => item.peak_group === targetPeakGroup).well,
      controlList.find(item => item.peak_group === targetPeakGroup).file_name
    );
  }

  // 解析 result 資料
  function parseResultData(sampleData, sampleResult) {
    return APOE_RESULT(
      parseWellData(sampleData, 'E2'),
      parseWellData(sampleData, 'E3'),
      parseWellData(sampleData, 'E4'),
      sampleResult.rfu_status.map(item => item.peak_group).sort((a, b) => {
        // 按照 E2, E3, E4 的順序排序
        const order = { 'E2': 1, 'E3': 2, 'E4': 3 };
        return order[a] - order[b];
      }),
      sampleResult.assessment
    )
  }

  // 製作 control
  const control1_list = apoeResult.resultObj.control1List
  const control2_list = apoeResult.resultObj.control2List
  const std1_e2 = parseWellData(control1_list, 'E2')
  const std1_e3 = parseWellData(control1_list, 'E3')
  const std1_e4 = parseWellData(control1_list, 'E4')
  const std2_e2 = parseWellData(control2_list, 'E2')
  const std2_e3 = parseWellData(control2_list, 'E3')
  const std2_e4 = parseWellData(control2_list, 'E4')
  const controlData = APOE_CONTROL_DATA(std1_e2, std1_e3, std1_e4, std2_e2, std2_e3, std2_e4)

  // 製作 result
  const sampleList = Object.keys(apoeResult.resultObj.assessmentResult)
  let resultList = []
  sampleList.forEach(sampleId => {
    const sampleData = apoeResult.resultObj.sampleObjList[sampleId]
    const sampleResult = apoeResult.resultObj.assessmentResult[sampleId]
    resultList.push(parseResultData(sampleData, sampleResult))
  })

  // 統整 result
  const result = APOE_RESULT_DATA(
    apoeResult.qc_status,
    controlData,
    resultList
  )

  // 更新 store
  store.commit("APOE_analysis_data/updateApoeResult", result);
}

// 生命週期鉤子
onMounted(async () => {
  // 取得 currentDisplayAnalysisID
  currentDisplayAnalysis.value = getCurrentDisplayAnalysisID();

  // 取得 setting props
  currentSettingProps.value = store.getters["analysis_setting/getSettingProps"];

  // 取得當前分析結果
  currentAnalysisResult.value = await getCurrentAnalysisResult(login_status, currentSettingProps);

  // 如果當前分析結果不存在, 則跳出
  if (!currentAnalysisResult.value) {
    showResult.value = false;
    return;
  }

  // 更新 APOE 分析結果
  updateAPOEAnalysisResult(currentAnalysisResult.value);

  // 更新導出結果
  const updated = resultTableApoeProps.value.map((row, index) => ({
    index: index + 1,
    sampleId: row.sampleId,
    result: row.type.join(""),
    resultLabel: [row.apoeType],
    assessment: row.assessment,
    assessmentLabel: assessment(row.assessment)
  }));

  store.commit("APOE_analysis_data/updateExportResults", updated);
});
</script>

<style>
.well-grid-container {
  display: grid;
  grid-template-columns: auto repeat(8, 12%); /* 8 columns */
}
.grid-col-title {
  padding: 10px; /* Padding within column ti tles */
  display: flex; /* Align contents vertically */
  justify-content: center; /* Align contents horizontally */
  align-items: center; /* Align contents vertically */
}
.grid-row-title {
  padding: 10px; /* Padding within row titles */
  display: flex; /* Align contents vertically */
  justify-content: center; /* Align contents horizontally */
  align-items: center; /* Align contents vertically */
}
.grid-col {
  border: 0px solid #e0e0e0; /* Optional: Add borders for better visualization */
  padding: None; /* Optional: Add padding for better spacing */
  display: flex; /* Align contents vertically */
  justify-content: center; /* Align contents horizontally */
  align-items: center; /* Align contents vertically */
}
.button-container {
  width: 100%; /* Set width to 100% */
  height: 100%; /* Set height to 100% */
  display: flex; /* Ensure the button is centered vertically and horizontally */
  justify-content: center; /* Center button horizontally */
  align-items: center;
}
</style>
