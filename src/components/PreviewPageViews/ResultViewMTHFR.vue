<template>
  <q-card bordered :style="{display: showResult ? 'block' : 'none'}">
    <q-card-section>
      <div class="row">

        <div class="col">
          <div class="col text-h5 text-uppercase text-bold text-blue-grey-7">
            Screening Result
          </div>
          <q-card flat>
            <q-card-section>
              <q-table
                :rows="resultTableMthfrProps"
                :columns="columns"
                :visible-columns="currentReagent === 'ACCUiN BioTech MTHFR v1'
                  ? [
                      'sampleId',
                      'well',
                      'type',
                      'Genotype',
                      'assessment',
                      'folate',
                      'showDiagram'
                    ]
                  : currentReagent === 'ACCUiN BioTech MTHFR v3'
                    ? [
                        'sampleId',
                        'well',
                        'type',
                        'Genotype',
                        'assessment',
                        'showDiagram'
                      ]
                    : [
                        'sampleId',
                        'well',
                        'type',
                        'Genotype',
                        'assessment',
                        'folate',
                      ]"
                v-model:pagination="pagination"
                :rows-per-page-options="[0]"
                row-key="sampleId"
                flat
                dense
              >
              <template v-slot:body-cell-type="props">
                <q-td
                  class="col text-center text-blue-grey text-overline text-bold"
                >
                  <div
                    class="row justify-center"
                    v-for="label in props.row.mthfrType"
                    :key="label"
                  >
                    {{ label }}
                  </div>
                  <div>
                    {{ updateFolateLst[props.pageIndex] ? 'Folate ' + updateFolateLst[props.pageIndex] + ' ng/ml' : props.row.folate ? 'Folate ' + props.row.folate + ' ng/ml' : '' }}
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
                <template v-slot:body-cell-folate="props">
                  <q-td :props="props">
                    <q-input
                      v-model="updateFolateLst[props.pageIndex]"
                      @update:model-value="(val) => updateFolateLst = {index: props.key, value: val}"
                      color="deep-orange-6"
                      mask="#.##"
                      input-class="text-right"
                      reverse-fill-mask
                      stack-label
                    >
                    <template v-slot:after>
                      <div class="text-body2">
                        ng/ml
                      </div>
                    </template>
                    </q-input>
                  </q-td>
                </template>
                <template v-slot:body-cell-showDiagram="props">
                  <q-td class="text-center" :props="props">
                    <q-btn
                      push
                      :color="btnColor(props.row.well)"
                      :text-color="btnTextColor(props.row.well)"
                      round
                      icon="mdi-chart-bell-curve-cumulative"
                      size="md"
                      @click="showDiagram(props.row.well, props.row.type)"
                      :disable="
                        props.row.assessment !== 'inconclusive'
                        ? props.row.assessment !== 'invalid'
                          ? false
                          : true
                        : true"
                    />
                  </q-td>
                </template>
              </q-table>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-5" v-if="currentReagent === 'ACCUiN BioTech MTHFR v1' || currentReagent === 'ACCUiN BioTech MTHFR v3'">
          <div class="col text-h5 text-uppercase text-bold text-blue-grey-7">
            MTHFR Result Diagram
          </div>
          <q-card flat>
            <q-card-section>
              <div class="q-pa-md">
                <div v-if="currentQCStatus !== 'meet-the-criteria'">
                  <q-chip
                    color="white"
                    text-color="red-8"
                    icon="warning"
                    label="No result diagram avaiable due to fail the criteria"
                  ></q-chip>
                </div>
                <div id="mthfrImg" v-else-if="showDiagramType" class="row">
                  <div style="padding: 2em;">
                    <img
                      alt="MTHFR result diagram"
                      :src="imgPath(showDiagramType)"
                      style="width: 100%; height: auto;"
                    >
                  </div>
                </div>
                <div v-else>
                  <q-chip
                    color="white"
                    text-color="blue-grey-8"
                    icon="touch_app"
                    label="Please select the sample to show result diagram"
                  ></q-chip>
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
import { ref, onMounted, computed, watch, onUnmounted } from "vue";
import { useStore } from "vuex";
import { getCurrentDisplayAnalysisID, getCurrentAnalysisResult } from '@/composables/checkAnalysisStatus.js';
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';
import { update_userAnalysisData } from '@/firebase/firebaseDatabase';

// 取得 store
const store = useStore();

// 使用者身份
const is_login = ref(false);
const user_info = ref(null);

// 響應式變數
const showResult = ref(true);
const showDiagramWell = ref(null);
const showDiagramType = ref(null);
const folateLst = ref([]);
const currentReagent = ref('ACCUiN BioTech MTHFR v1'); // 預設
const currentQCStatus = ref('not-set');

// 保存當前分析結果
const { login_status } = updateGetUserInfo();
const currentAnalysisResult = ref(null);
const currentSettingProps = ref(null);
const currentDisplayAnalysis = ref({
  analysis_uuid: '',
  analysis_name: '',
});

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
    name: "well",
    label: "Well Position",
    align: "center",
    field: "well"
  },
  {
    name: "type",
    label: "Genotype",
    field: "mthfrType",
    align: "center"
  },
  {
    name: "assessment",
    align: "center",
    label: "Assessment Result",
    field: "assessment"
  },
  {
    name: "folate",
    align: "center",
    label: "folate Result",
    field: "folate"
  },
  {
    label: "Show Diagram",
    align: "center",
    name: "showDiagram",
  },
];

// 表格資料
const resultTableMthfrProps = computed(() => store.getters["MTHFR_analysis_data/resultTableMthfrProps"]);

// 轉換 reagent 名稱
const getReagentName = () => {
  if (currentAnalysisResult.value.config.reagent === 'accuinMTHFR1') {
    return 'ACCUiN BioTech MTHFR v1';
  } else if (currentAnalysisResult.value.config.reagent === 'accuinMTHFR2') {
    return 'ACCUiN BioTech MTHFR v2';
  } else if (currentAnalysisResult.value.config.reagent === 'accuinMTHFR3') {
    return 'ACCUiN BioTech MTHFR v3';
  } else {
    return 'ACCUiN BioTech MTHFR v1';
  }
}

// 定義 MTHFR 結果
const MTHFR_Result = (reagent, qc_status, result_list) => {
  return {
    config : { reagent: reagent },
    qc : { qc_status: qc_status },
    sample: result_list,
    standard: reagent === 'accuinMTHFR2' ?
    {
      c677: 'C/T',
      c1298: 'A/C'
    } : null
  }
}

// 定義 MTHFR sample result
const MTHFR_SAMPLE_RES = (sample_name, well, type_array, assessment) => {
  return {
    name: sample_name,
    well: well,
    type: type_array,
    assessment: assessment,
  }
}

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

// 圖片路徑
const imgPath = (type) => {
  const imgType = type[0].toLowerCase() + '_' + type[1].toLowerCase();
  return 'diagram/' + imgType + '.svg';
};

// 按鈕文字顏色
const btnTextColor = (well) => {
  return showDiagramWell.value === well ? "white" : "blue-grey-8";
};

// 按鈕顏色
const btnColor = (well) => {
  return showDiagramWell.value === well ? "blue-grey-8" : "white";
};

// 顯示圖表
function showDiagram(well, type) {
  if (showDiagramWell.value === well) {
    showDiagramWell.value = null;
    showDiagramType.value = null;
  } else {
    showDiagramWell.value = well;
    showDiagramType.value = type;
  }
}

// 更新葉酸列表
const updateFolateLst = computed({
  get: () => folateLst.value,
  set: (val) => {
    folateLst.value[val.index] = val.value;
  }
});

// 更新表格資料
function updateResultTableMthfrProps(MTHFR_result) {
  const reagent = MTHFR_result.config.reagent;
  const sampleList = MTHFR_result.resultObj.resultList.map((item) => item.sample_name);
  let results = [];
  sampleList.forEach((sample) => {
    const sampleRes = MTHFR_result.resultObj.resultList.find((item) => item.sample_name === sample);
    const sampleData = MTHFR_result.resultObj.SampleDataList.find((item) => item.sample_name === sample);
    const sampleResObj = MTHFR_SAMPLE_RES(
      sampleRes.sample_name,
      `${sampleData.well_position.X}${sampleData.well_position.Y}`,
      sampleRes.sample_type,
      sampleRes.assessment
    );
    results.push(sampleResObj);
  });

  // 製作 MTHFR 結果
  const MTHFRresult = MTHFR_Result(reagent, MTHFR_result.qc_status, results);

  // 更新到store
  store.commit("MTHFR_analysis_data/updateMthfrResult", MTHFRresult);

  // 更新 QC 狀態
  currentQCStatus.value = MTHFR_result.qc_status;
}

// 監聽 folateLst 變化
watch(folateLst, (newVal) => {

  // 如果沒有表格資料, 則跳出
  if (!resultTableMthfrProps.value) {
    return;
  }

  // 加入葉酸列表
  resultTableMthfrProps.value.forEach((row, index) => {
    row.folate = newVal[index];
  });

  // 更新葉酸列表
  store.commit("MTHFR_analysis_data/updateInputResults", [...folateLst.value]);

}, { deep: true });

// 生命週期鉤子
onMounted(async () => {
  // 取得使用者身份
  const { login_status } = updateGetUserInfo();
  is_login.value = login_status.value.is_login;
  user_info.value = login_status.value.user_info;

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

  // 取得 reagent 更新
  currentReagent.value = getReagentName();

  // 更新表格資料
  updateResultTableMthfrProps(currentAnalysisResult.value);

  // 如果沒有表格資料, 則跳出
  if (!resultTableMthfrProps.value) {
    return;
  }

  // 取得輸入結果
  const inputResults = store.getters["MTHFR_analysis_data/getInputResults"];
  folateLst.value = [...inputResults];
});

// 離開頁面時才將葉酸資訊 更新至 firestore
onUnmounted(() => {

  // 葉酸資訊 更新至 firestore
  let AnalysisResult = JSON.parse(JSON.stringify(currentAnalysisResult.value));

  // 先移除所包含 Folate 的項目
  AnalysisResult.exportResult.forEach((item) => {
    item.resultLabel = item.resultLabel.filter((label) => !label.includes('Folate'));
  });

  // 加入葉酸資訊
  AnalysisResult.exportResult.forEach((item) => {
    const sample_data = resultTableMthfrProps.value.find((row) => row.sampleId === item.sampleId);
    if (sample_data.folate) {
      item.resultLabel.push('Folate ' + sample_data.folate + ' ng/ml');
    }
  });

  // 更新至 firestore
  const dbMTHFRResultPath = 'mthfr_result';
  update_userAnalysisData(user_info.value.uid, dbMTHFRResultPath, AnalysisResult, currentAnalysisResult.value.analysis_id);

});

const pagination = ref({ rowsPerPage: 0 });
</script>
