<template>
  <q-card bordered :style="{ display: showResult ? 'block' : 'none' }">
    <q-card-section>
      <div class="row">

        <!-- 結果表格區塊 -->
        <div class="col" style="min-width: 500px;">

          <!-- 表格標題 -->
          <div class="col text-h5 text-uppercase text-bold text-blue-grey-7">
            Screening Result
          </div>

          <!-- 表格內容 -->
          <q-card flat>

            <!-- 選擇器區域 -->
            <q-card-section class="col q-pb-none">
              <div class="row">
                <div class="text-weight-medium self-center text-blue-grey-8">Exported SMN1 Result:</div>
                <q-radio
                  v-for="(option, idx) in analyzerOptions"
                  :key="'smn1-' + idx"
                  :class="option.class"
                  :color="option.color"
                  v-model="smn1Version"
                  checked-icon="task_alt"
                  :val="idx"
                  :label="option.label"
                  unchecked-icon="panorama_fish_eye"
                />
              </div>
              <div class="row">
                <div class="text-weight-medium self-center text-blue-grey-8">Exported SMN2 Result:</div>
                <q-radio
                  v-for="(option, idx) in analyzerOptions"
                  :key="'smn2-' + idx"
                  :class="option.class"
                  :color="option.color"
                  v-model="smn2Version"
                  checked-icon="task_alt"
                  :val="idx"
                  :label="option.label"
                  unchecked-icon="panorama_fish_eye"
                />
              </div>
            </q-card-section>

            <!-- 表格區域 -->
            <q-card-section style="border: 1px solid rgba(200, 200, 200, 0.3);">
              <q-table
                :rows="resultTableSmaProps"
                :columns="columns"
                :v-model:pagination="{ rowsPerPage: 10 }"
                :rows-per-page-options="[10]"
                row-key="sampleId"
                flat
                :visible-columns="getVisibleColumns()"
                dense
              >
                <!-- Header -->
                <template v-slot:header-cell-smnTypeCustom="props">
                  <q-th :props="props">
                    {{ props.col.label.replace('SMN1 : SMN2', '') }}<br>{{ props.col.label.replace('Analyzer Custom Result ', '') }}
                  </q-th>
                </template>
                <template v-slot:header-cell-smnType="props">
                  <q-th :props="props">
                    Exported Result <br> SMN1 : SMN2
                  </q-th>
                </template>
                <template v-slot:header-cell-smn1TypeAnalyzer2="props">
                  <q-th :props="props">
                    Analyzer QS3L<br>SMN1
                  </q-th>
                </template>
                <template v-slot:header-cell-smn2TypeAnalyzer2="props">
                  <q-th :props="props">
                    Analyzer QS3L<br>SMN2
                  </q-th>
                </template>
                <template v-slot:header-cell-smn1TypeAnalyzer3="props">
                  <q-th :props="props">
                    Analyzer Z480<br>SMN1
                  </q-th>
                </template>
                <template v-slot:header-cell-smn2TypeAnalyzer3="props">
                  <q-th :props="props">
                    Analyzer Z480<br>SMN2
                  </q-th>
                </template>

                <!-- Body -->
                <template v-slot:body-cell-smn1TypeAnalyzer1="props">
                  <q-td :props="props" class="bg-teal-1 text-teal-8">
                    {{ props.value }}
                  </q-td>
                </template>
                <template v-slot:body-cell-smn2TypeAnalyzer1="props">
                  <q-td :props="props" class="bg-lime-1 text-lime-10">
                    {{ props.value }}
                  </q-td>
                </template>
                <template v-slot:body-cell-smn1TypeAnalyzer2="props">
                  <q-td :props="props" class="bg-teal-1 text-teal-8">
                    {{ props.value }}
                  </q-td>
                </template>
                <template v-slot:body-cell-smn2TypeAnalyzer2="props">
                  <q-td :props="props" class="bg-lime-1 text-lime-10">
                    {{ props.value }}
                  </q-td>
                </template>
                <template v-slot:body-cell-smn1TypeAnalyzer3="props">
                  <q-td :props="props" class="bg-teal-1 text-teal-8">
                    {{ props.value }}
                  </q-td>
                </template>
                <template v-slot:body-cell-smn2TypeAnalyzer3="props">
                  <q-td :props="props" class="bg-lime-1 text-lime-10">
                    {{ props.value }}
                  </q-td>
                </template>
                <template v-slot:body-cell-assessment="props">
                  <q-td :props="props">
                    <q-chip
                      v-if="props.value !== 'Unfound'"
                      :key="props.value"
                      :color="interpretationColor(props.value)"
                      :label="props.value"
                    />
                    <q-avatar
                      v-else
                      color="grey-2"
                      text-color="yellow-10"
                      icon="warning"
                      size="md"
                    />
                  </q-td>
                </template>
                <template v-slot:body-cell-assessmentRaw="props">
                  <q-td :props="props">
                    <q-chip
                      v-if="props.value !== 'Unfound'"
                      :key="props.value"
                      :color="interpretationColor(props.value)"
                      :label="props.value"
                    />
                    <q-avatar
                      v-else
                      color="grey-2"
                      text-color="yellow-10"
                      icon="warning"
                      size="md"
                    />
                  </q-td>
                </template>
                <template v-slot:body-cell-showFigure="props">
                  <q-td class="text-center" :props="props">
                    <q-btn
                      push
                      :color="btnColor(props.row.well)"
                      :text-color="btnTextColor(props.row.well)"
                      round
                      icon="mdi-chart-bell-curve-cumulative"
                      size="md"
                      @click="showFigure(props.row.well, props.row.smn1Type[smn1Version], props.row.smn2Type[smn2Version])"
                      :disable="
                        props.row.assessment.value === 'inconclusive' || props.row.assessment.value === 'invalid'
                        ? true
                        : false"
                    />
                  </q-td>
                </template>
              </q-table>
            </q-card-section>

          </q-card>

        </div>

        <!-- 結果圖表區域 -->
        <div class="col" style="padding: 1em; min-width: 500px; min-height: 500px;">
          <div class="text-h5 text-uppercase text-bold text-blue-grey-7">
            SMA Result Figure
          </div>
          <div style="width: 100%; height: 100%; padding: 1.5em;">
            <q-card :class="showFigureType ? 'filled-figure' : 'empty-figure'" flat style="width: 100%; height: 100%;">
              <q-card-section class="q-pa-none" style="width: 100%; height: 100%;">
                <div class="q-pa-sm flex flex-center" style="width: 100%; height: 100%;">
                  <div class="flex flex-center" v-if="qc_status !== 'meet-the-criteria'">
                    <q-chip
                      color="white"
                      text-color="red-8"
                      icon="warning"
                      label="No result figure avaiable due to fail the criteria"
                    ></q-chip>
                  </div>
                  <div id="smaImg" v-else-if="showFigureType" class="col q-ma-none">
                    <div class="row text-grey-7 content-center text-subtitle2 q-mt-md q-ml-md">
                      * The figure illustrates the main types of combinations for SMN1 and SMN2 gene copies in SMA.
                    </div>
                    <div v-if="isNormal" class="row text-grey-7 content-center text-subtitle2 q-ml-md">
                      * This test can not exclude SMA silent carriers whose two SMN1 copies located in the same allele.
                    </div>
                    <div class="row justify-center q-mt-lg q-mb-none col-grow text-h6 text-blue-grey">
                        SMN1 : SMN2 = {{ showFigureType }}
                      </div>
                    <div class="row text-center q-ma-lg q-mb-xl col-grow">
                      <img
                        alt="SMA result figure"
                        :src="imgPath(showFigureType)"
                        style="width: 60%; height: auto; margin-left: auto; margin-right: auto"
                      >
                    </div>
                    <div v-if="popupShow" class="row bg-grey-3 q-mx-lg">
                      <div class="row text-grey-8 content-center text-subtitle2 q-ma-md">
                        * The figure illustrates the possible types of combinations for SMN1 and SMN2 gene copies in SMA.
                      </div>
                      <div class="row full-width">
                        <q-table
                          :rows="figRows"
                          :columns="figColumns"
                          :v-model:pagination="{ rowsPerPage: 10 }"
                          :rows-per-page-options="[10]"
                          class="col q-mx-xl q-mb-lg bg-grey-3 text-blue-grey"
                          row-key="index"
                          flat
                          hide-bottom
                        >
                          <template v-slot:body-cell-figure="props">
                            <q-td :props="props">
                              <img
                                :alt="'SMA combination figure ' + props.key"
                                :src="props.value"
                                style="width: 55%; height: auto; display:block;margin-left: auto; margin-right: auto;"
                              >
                            </q-td>
                          </template>
                        </q-table>
                      </div>
                    </div>
                  </div>
                  <div class="flex flex-center" style="width: 100%; height: 100%;" v-else>
                    <q-chip
                      color="white"
                      text-color="blue-grey-8"
                      icon="touch_app"
                      label="Please select the sample to show result figure"
                    ></q-chip>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>

      </div>
    </q-card-section>
  </q-card>
</template>

<script setup>
// 引入模組
import { ref, computed, watch, onMounted } from "vue";
import { useStore } from "vuex";
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';
import { getCurrentDisplayAnalysisID, getCurrentAnalysisResult } from '@/composables/checkAnalysisStatus.js';

// 定義 store
const store = useStore();

// 保存當前分析結果
const showResult = ref(true);
const { login_status } = updateGetUserInfo();
const currentAnalysisResult = ref(null);
const currentSettingProps = ref(null);
const currentDisplayAnalysis = ref({
  analysis_uuid: '',
  analysis_name: '',
});

// 取得資料
const reagent = ref("ACCUiN BioTech SMA v2");
const resultTableSmaProps = computed(() => store.getters["SMA_analysis_data/resultTableSmaProps"]);
const qc_status = ref('not-analyzed');

// 計算 SMN1 和 SMN2 版本
const smn1Version = ref(0);
const smn2Version = ref(reagent.value === "ACCUiN BioTech SMA v2" ? 1 : 0);

// 新增分析儀選項配置
const analyzerOptions = [
  {
    label: 'Analyzer QS3',
    class: 'text-overline text-blue-7',
    color: 'blue-7'
  },
  {
    label: 'Analyzer QS3L',
    class: 'text-overline text-blue-10',
    color: 'blue-10'
  },
  {
    label: 'Analyzer Z480',
    class: 'text-overline text-green-8',
    color: 'green-8'
  }
];

// 表格相關定義
const columns = [
  {
    name: "sampleId",
    required: true,
    label: "Sample ID",
    align: "center",
    field: "sampleId",
    format: (val) => `${val}`,
  },
  {
    name: "well",
    label: "Well",
    align: "center",
    field: "well"
  },
  {
    name: "rnp_smn1",
    label: "RNP-SMN1 CT",
    align: "center",
    field: "rnp_smn1"
  },
  {
    name: "rnp_smn2",
    label: "RNP-SMN2 CT",
    align: "center",
    field: "rnp_smn2"
  },
  {
    name: "smn1TypeAnalyzer1",
    label: 'SMN1',
    align: "center",
    field: (row) => row.assessment.value === 'inconclusive' || row.assessment.value === 'invalid'
      ? '-'
      : row.smn1Type[0],
  },
  {
    name: "smn1TypeAnalyzer2",
    label: "Analyzer QS3L SMN1",
    align: "center",
    field: (row) => row.assessment.value === 'inconclusive' || row.assessment.value === 'invalid'
      ? '-'
      : row.smn1Type[1],
  },
  {
    name: "smn1TypeAnalyzer3",
    label: 'Analyzer Z480 SMN1',
    align: "center",
    field: (row) => row.assessment.value === 'inconclusive' || row.assessment.value === 'invalid'
      ? '-'
      : row.smn1Type[2],
  },
  {
    name: "smn2TypeAnalyzer1",
    label: 'SMN2',
    align: "center",
    field: (row) => row.assessment.value === 'inconclusive' || row.assessment.value === 'invalid'
      ? '-'
      : row.smn2Type[0],
  },
  {
    name: "smn2TypeAnalyzer2",
    label: "Analyzer QS3L SMN2",
    align: "center",
    field: (row) => row.assessment.value === 'inconclusive' || row.assessment.value === 'invalid'
      ? '-'
      : row.smn2Type[1],
  },
  {
    name: "smn2TypeAnalyzer3",
    label: 'Analyzer Z480 SMN2',
    align: "center",
    field: (row) => row.assessment.value === 'inconclusive' || row.assessment.value === 'invalid'
      ? '-'
      : row.smn2Type[2],
  },
  {
    name: "smnType",
    label: "SMN1 : SMN2",
    align: "center",
    field: (row) => row.assessment.value === 'inconclusive' || row.assessment.value === 'invalid'
      ? '-'
      : `${row.smn1Type[smn1Version.value]}:${row.smn2Type[smn2Version.value]}`,
  },
  {
    name: "assessment",
    align: "center",
    label: "Assessment",
    field: (row) => smnTypeInterpretation(row.smn1Type[smn1Version.value], row.smn2Type[smn2Version.value]).label,
  },
  {
    name: "assessmentRaw",
    align: "center",
    label: "Assessment-Raw",
    field: (row) => row.assessment.label,
  },
  {
    label: "Show Figure",
    align: "center",
    name: "showFigure",
  },
];

const figColumns = [
  {
    name: "index",
    label: "Combination #",
    align: "center",
    field: "index",
  },
  {
    name: "figure",
    label: "Figure",
    align: "center",
    field: "figure"
  },
];

// 圖表相關狀態
const popupShow = ref(false);
const isNormal = ref(false);
const showFigureWell = ref(null);
const showFigureType = ref(null);
const figRows = ref([]);

// 常量定義
const popupLst = [
  '0:2', '0:3', '0:4', '1:1', '1:2', '1:3', '1:4',
  '2:0', '2:1', '2:2', '2:3', '2:4', '3:0', '3:1', '3:2', '3:3'
];

const normalLst = [
  '4:0', '4:1', '4:2', '4:3', '3:0', '3:1', '3:2',
  '3:3', '3:4', '2:0', '2:1', '2:2', '2:3', '2:4',
];

// 定義 SMA 結果
const SMA_RESULT_DATA = (qc_status, result_list) => {
  return {
    qc: {
      status: qc_status,
    },
    sample: result_list,
  };
};

// 定義 SMA 結果
const SMA_RESULT = (sample_name, well, rnp_smn1, rnp_smn2, smn1Type_list, smn2Type_list) => {
  return {
    name: sample_name,
    well: well,
    rnp_smn1: rnp_smn1,
    rnp_smn2: rnp_smn2,
    smn1Type: smn1Type_list,
    smn2Type: smn2Type_list,
  };
};

// 方法定義
const getVisibleColumns = () => {
  return [
    'sampleId',
    'well',
    'rnp_smn1',
    'rnp_smn2',
    'smn1TypeAnalyzer1',
    'smn1TypeAnalyzer2',
    'smn1TypeAnalyzer3',
    'smn2TypeAnalyzer1',
    'smn2TypeAnalyzer2',
    'smn2TypeAnalyzer3',
    'smnType',
    'assessment',
    'assessmentRaw',
    'showFigure',
  ]
}

const getFigRows = (smn1Type, smn2Type) => {
  let showFigRows = [];
  const type = `${smn1Type}:${smn2Type}`;
  const typeDir = `diagram/combinations/${smn1Type}_${smn2Type}/`;

  const combinations = {
    '0:2': 2, '0:3': 2, '1:1': 2, '2:0': 2, '3:0': 2,
    '0:4': 3, '1:2': 3, '2:1': 3,
    '1:3': 4, '3:1': 4,
    '1:4': 5, '2:2': 5,
    '2:3': 6, '3:2': 6,
    '3:3': 8
  };

  const count = combinations[type] || 0;
  for (let i = 0; i < count; i++) {
    showFigRows.push({
      index: i + 1,
      figure: `${typeDir}${smn1Type}_${smn2Type}-${i+1}.svg`,
    });
  }

  return showFigRows;
};

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

const interpretationColor = (value) => {
  const colors = {
    "Normal": "green-13",
    "SMA carrier": "yellow-7",
    "Invalid": "white"
  };
  return value.includes("SMA affected") ? "deep-orange-5" : colors[value] || "white";
};

const imgPath = (type) => {
  popupShow.value = popupLst.includes(type);
  isNormal.value = normalLst.includes(type);
  return `diagram/${type.replace(":", "_")}-1.svg`;
};

const btnTextColor = (well) => showFigureWell.value === well ? "white" : "blue-grey-8";
const btnColor = (well) => showFigureWell.value === well ? "blue-grey-8" : "white";

const showFigure = (well, smn1, smn2) => {
  if (showFigureWell.value === well) {
    showFigureWell.value = null;
    showFigureType.value = null;
    figRows.value = [];
  } else {
    showFigureWell.value = well;
    showFigureType.value = `${smn1}:${smn2}`;
    figRows.value = getFigRows(smn1, smn2);
  }
};

// 更新導出結果
const updateExportResults = () => {
  const updated = resultTableSmaProps.value.map((row, index) => {
    const smn1 = row.smn1Type[smn1Version.value];
    const smn2 = row.smn2Type[smn2Version.value];
    const smnInterpretation = qc_status.value === 'meet-the-criteria'
      ? smnTypeInterpretation(smn1, smn2)
      : { value: 'inconclusive', label: 'Inconclusive' };

    return {
      index: index + 1,
      sampleId: row.sampleId,
      result: qc_status.value === 'meet-the-criteria'
        ? `${smn1}:${smn2}`
        : '-',
      resultLabel: qc_status.value === 'meet-the-criteria'
        ? [`${smn1}:${smn2}`]
        : ['-'],
      assessment: smnInterpretation.value.includes("affected")
        ? "affected"
        : smnInterpretation.value,
      assessmentLabel: smnInterpretation.label
    };
  });

  store.commit("SMA_analysis_data/updateExportResults", updated);
};

// 更新 SMA 結果
function updateSmaResult(smaResult) {

  // 取得 sample list
  const sampleList = smaResult.resultObj.V1.sampleDataList.map(item => item.sample_name);

  if (!smaResult.resultObj.V1.resultList) {
    return;
  }

  // 製作 result list
  let sma_resultList = [];
  sampleList.forEach(sample_name => {
    const sampleData = smaResult.resultObj.V1.sampleDataList.find(item => item.sample_name === sample_name);
    const well = `${sampleData.well_position.X}${sampleData.well_position.Y}`;
    const rnp_smn1 = sampleData.normalized_smn1 || 0;
    const rnp_smn2 = sampleData.normalized_smn2 || 0;
    let smn1Type = [];
    let smn2Type = [];
    for (const version of ['V1', 'V2', 'V3']) {
      const resultObj = smaResult.resultObj[version].resultList.find(item => item.sample_name === sample_name);
      smn1Type.push(resultObj.smn1_Type);
      smn2Type.push(resultObj.smn2_Type);
    }
    sma_resultList.push(SMA_RESULT(sample_name, well, rnp_smn1, rnp_smn2, smn1Type, smn2Type));
  });

  // 更新 qc_status
  qc_status.value = smaResult.qc_status.V1;

  // 儲存 SMA 結果
  const SMA_RES_DATA = SMA_RESULT_DATA(smaResult.qc_status.V1, sma_resultList);
  store.commit("SMA_analysis_data/updateSmaResult", SMA_RES_DATA);
}

// 生命週期鉤子
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

  // 更新 SMA 結果
  updateSmaResult(currentAnalysisResult.value);

  // 更新 export results
  updateExportResults();
});

// 監聽器
watch([smn1Version, smn2Version], () => {
  updateExportResults();
});

</script>

<style scoped>
.empty-figure {
  background-color: rgba(200, 200, 200, 0.1);
  border: 1px dashed grey;
}
.filled-figure {
  background-color: white;
  border: 1px dashed grey;
}
</style>
