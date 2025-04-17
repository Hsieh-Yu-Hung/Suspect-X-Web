<template>
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

            <!-- 評估結果表格 -->
            <div class="col" style="margin-top: 20px; width: 100%;">
              <q-table
                :rows="assessmentTableRows"
                :columns="assessmentTableColumns"
                row-key="name"
                :v-model:pagination="{ rowsPerPage: 20 }"
                :rows-per-page-options="[20]"
              >
                <!-- Body -->
                <template v-slot:body-cell-Assessment="cell">
                  <q-td :props="cell">
                    <q-chip
                      :key="cell.value"
                      :color="interpretationColor(cell.value)"
                      :label="cell.value"
                    />
                  </q-td>
                </template>
                <template v-slot:body-cell-Show_Figure="cell">
                  <q-td :props="cell">
                    <q-btn
                      push
                      :color="btnColor(cell.row.sample)"
                      :text-color="btnTextColor(cell.row.sample)"
                      round
                      size="md"
                      icon="mdi-chart-bell-curve-cumulative"
                      @click="showFigure(cell.row.sample, cell.row.smn_number.split(':')[0], cell.row.smn_number.split(':')[1])"
                      :disable="cell.row.assessment === 'Invalid' ? true : false"
                    />
                  </q-td>
                </template>
              </q-table>
            </div>
          </div>

          <!-- 示意圖 -->
          <div v-if="true" class="col result-box">
            <span class="row text-h6 text-bold text-blue-grey-7 text-uppercase justify-center">Result Diagram</span>
            <div class="row">
              <q-card flat>
                <q-card-section class="q-pa-none">
                  <div class="q-pa-sm">
                    <div v-if="qc_status !== 'meet-the-criteria'">
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
                    <div v-else>
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
  </div>

</template>

<script setup>
// 導入模組
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex';
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';
import { getCurrentDisplayAnalysisID, getCurrentAnalysisResult } from '@/composables/checkAnalysisStatus.js';
import { setAnalysisID } from '@/composables/checkAnalysisStatus';

// Store
const store = useStore();

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

// 取得 QC 結果
const qc_status = ref('');

// 控制 ResultViewSMAv4 的顯示
const showResult = ref(true);

// 定義 Assessment 表格資料行
const assessmentTableRows = ref([]);
const assessmentTableColumns = ref([
  {
    name: 'Sample',
    label: 'Sample',
    field: 'sample',
    align: 'center',
  },
  {
    name: 'SMN_Number',
    label: 'SMN1:SMN2',
    field: 'smn_number',
    align: 'center',
  },
  {
    name: 'Assessment',
    label: 'Assessment',
    field: 'assessment',
    align: 'center',
  },
  {
    name: 'Show_Figure',
    label: 'Show Figure',
    field: 'show_figure',
    align: 'center',
  },
]);

// 定義一個 Row
const ROW = (sample_name, smn_number_string, assessment_string) => {
  return {
    sample: sample_name,
    smn_number: smn_number_string,
    assessment: assessment_string,
    show_figure: true,
  };
};

// 圖片顯示
const showFigureWell = ref(null);
const popupShow = ref(false);
const isNormal = ref(false);
const figRows = ref([]);
const showFigureType = ref(null);

// 圖片顯示列表
const popupLst = [
  '0:2',
  '0:3',
  '0:4',
  '1:1',
  '1:2',
  '1:3',
  '1:4',
  '2:0',
  '2:1',
  '2:2',
  '2:3',
  '2:4',
  '3:0',
  '3:1',
  '3:2',
  '3:3'
];

const normalLst = [
  '4:0',
  '4:1',
  '4:2',
  '4:3',
  '3:0',
  '3:1',
  '3:2',
  '3:3',
  '3:4',
  '2:0',
  '2:1',
  '2:2',
  '2:3',
  '2:4',
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

/* Functions */

// 解釋 SMN 類型
function smnTypeInterpretation(smn1, smn2) {
  let type = String(smn1) + String(smn2);

  // Defined interpretation
  function isNormal(typeArray) {
    return [
      "20",
      "21",
      "22",
      "23",
      "24",
      "30",
      "31",
      "32",
      "33",
      "34",
      "41",
      "42",
      "43",
      "44",
    ].includes(typeArray);
  }
  function isCarrier(typeArray) {
    return ["10", "11", "12", "13", "14"].includes(typeArray);
  }
  function isAffected(typeArray) {
    return ["01", "02", "03", "04"].includes(typeArray);
  }

  if (isNormal(type)) {
    // Defined "Noraml" by SMN1:SMN2 =
    // 2:0 or 2:1 or 2:2 or 2:3 or 2:4 or
    // 3:0 or 3:1 or 3:2 or 3:3 or 3:4 or
    // 4:1 or 4:2 or 4:3 or 4:4
    return {
      value: "normal",
      label: "Normal",
    };;
  } else if (isCarrier(type)) {
    // Defined "SMA carrier" by SMN1:SMN2 =
    // 1:0 or 1:1 or 1:2 or 1:3 or 1:4
    return {
      value: "carrier",
      label: "SMA carrier",
    };
  } else if (isAffected(type)) {
    return {
      value: "affected",
      label: "SMA affected",
    };
  } else {
    // Defined "Invalid" (nonsense value) by SMN1:SMN2 =
    // 0:0
    return {
      value: "invalid",
      label: "Invalid",
    };
  }
};

// 更新 Assessment 表格資料行
function updateAssessmentTableRows(){
  const ResultList = currentAnalysisResult.value.resultObj.RESULT_LIST;
  Object.keys(ResultList).forEach(sample => {
    const smn1 = ResultList[sample].smn1_copy_number;
    const smn2 = ResultList[sample].smn2_copy_number;
    const assessment = smnTypeInterpretation(smn1, smn2);
    let smn_number = ResultList[sample].typeStr;
    assessmentTableRows.value.push(ROW(sample, smn_number, assessment.label, '', ''));
  });
}

// 解釋 SMN 類型顏色
const interpretationColor = (value) => {
  if (value === "Normal") {
    return "green-13";
  } else if (value === "SMA carrier") {
    return "yellow-7";
  } else if (value.includes("SMA affected")) {
    return "deep-orange-5";
  } else {
    return "grey-4";
  }
};

// Show Figure 按鈕文字顏色
const btnTextColor = (well) => {
  if (showFigureWell.value === well) {
    return "white"
  } else {
    return "blue-grey-8"
  }
};

// Show Figure 按鈕顏色
const btnColor = (well) => {
  if (showFigureWell.value === well) {
    return "blue-grey-8"
  } else {
    return "white"
  }
};

// 取得圖片路徑
const imgPath = (type) => {
  if (popupLst.includes(type)) {
    popupShow.value = true;
  } else {
    popupShow.value = false;
  }
  if (normalLst.includes(type)) {
    isNormal.value = true;
  } else {
    isNormal.value = false;
  }
  return `diagram/${type.replace(":", "_")}-1.svg`;
};

// 顯示圖片
function showFigure (well, smn1, smn2) {
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

// 取得圖片列表
function getFigRows(smn1Type, smn2Type) {
  let showFigRows = new Array();
  const type = `${smn1Type}:${smn2Type}`;
  const typeDir = `diagram/combinations/${smn1Type}_${smn2Type}/`;

  if (['0:2', '0:3', '1:1', '2:0', '3:0'].includes(type)) {
    for (let i = 0; i < 2; i++) {
      showFigRows.push({
        index: i + 1,
        figure: `${typeDir}${smn1Type}_${smn2Type}-${i+1}.svg`,
      })
    }
  } else if (['0:4', '1:2', '2:1'].includes(type)) {
    for (let i = 0; i < 3; i++) {
      showFigRows.push({
        index: i + 1,
        figure: `${typeDir}${smn1Type}_${smn2Type}-${i+1}.svg`,
      })
    }
  } else if (['1:3', '3:1'].includes(type)) {
    for (let i = 0; i < 4; i++) {
      showFigRows.push({
        index: i + 1,
        figure: `${typeDir}${smn1Type}_${smn2Type}-${i+1}.svg`,
      })
    }
  } else if (['1:4', '2:2'].includes(type)) {
    for (let i = 0; i < 5; i++) {
      showFigRows.push({
        index: i + 1,
        figure: `${typeDir}${smn1Type}_${smn2Type}-${i+1}.svg`,
      })
    }
  } else if (['2:3', '3:2'].includes(type)) {
    for (let i = 0; i < 6; i++) {
      showFigRows.push({
        index: i + 1,
        figure: `${typeDir}${smn1Type}_${smn2Type}-${i+1}.svg`,
      })
    }
  } else if (['3:3'].includes(type)) {
    for (let i = 0; i < 8; i++) {
      showFigRows.push({
        index: i + 1,
        figure: `${typeDir}${smn1Type}_${smn2Type}-${i+1}.svg`,
      })
    }
  }

  return showFigRows
};

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

  // 更新 QC 結果
  qc_status.value = currentAnalysisResult.value.qc_status;

  // 更新 Assessment 表格資料行
  updateAssessmentTableRows();

  // 先嘗試取得當前的分析 ID, 如果沒有則建立新的分析 ID
  currentAnalysisID.value = store.getters['analysis_setting/getCurrentAnalysisID'];
  setAnalysisID(store, 'SMAv4');
})
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
  min-width:40em;
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
