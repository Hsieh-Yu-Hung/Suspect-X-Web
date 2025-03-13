<template>
  <q-card bordered>
    <q-card-section>
      <div class="row">

        <div class="col">
          <div class="col text-h5 text-uppercase text-bold text-blue-grey-7">
            Screening Result
          </div>
          <q-card flat>
            <q-card-section>
              <q-table
                :rows="resultTableNudt15Props"
                :columns="columns"
                :visible-columns="[
                  'sampleId',
                  'well',
                  'type',
                  'Genotype',
                  'assessment',
                ]"
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
                  <div
                    class="row justify-center"
                    v-for="label in props.row.nudt15Type"
                    :key="label"
                  >
                    {{ label }}
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
              </q-table>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useStore } from 'vuex';
import { getCurrentDisplayAnalysisID, getCurrentAnalysisResult } from '@/composables/checkAnalysisStatus.js';
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';

// 取得 store
const store = useStore();

// 響應式變數
const showResult = ref(true);

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
    field: "nudt15Type",
    align: "center"
  },
  {
    name: "assessment",
    align: "center",
    label: "Assessment Result",
    field: "assessment"
  },
];

// 表格資料
const resultTableNudt15Props = computed(() => store.getters["NUDT15_analysis_data/resultTableNudt15Props"]);

// 定義 NUDT15 Result
const NUDT15_RESULT = (sampleList) => {
  return {
    sample: sampleList
  }
}

// 定義 NUDT15 Sample Res
const NUDT15_Sample_RES = (sample_name, well, type_array, assessment) => {
  return {
    name: sample_name,
    well: well,
    type: type_array,
    assessment: assessment
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

// 更新 resultTableNudt15Props
function updateResTable(nudt15_result){

  // 取得 sample_list
  const sample_list = nudt15_result.resultObj.resultList.map(item=>item.sample_name)

  // 更新 resultTableNudt15Props
  let results = [];
  sample_list.forEach(sample=>{
    const SampleData = nudt15_result.resultObj.SampleDataList
    const SampleResult = nudt15_result.resultObj.resultList
    const sample_res = NUDT15_Sample_RES(
      sample,
      `${SampleData.find(item=>item.sample_name === sample).well_position.X}${SampleData.find(item=>item.sample_name === sample).well_position.Y}`,
      SampleResult.find(item=>item.sample_name === sample).sample_type,
      SampleResult.find(item=>item.sample_name === sample).assessment
    )
    results.push(sample_res)
  })

  // 製作 NUDT15RESULT
  const NUDT15RESULT = NUDT15_RESULT(results)

  // 更新 resultTableNudt15Props
  store.commit("NUDT15_analysis_data/updateNudt15Result", NUDT15RESULT);
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

  // 更新 res_table
  updateResTable(currentAnalysisResult.value)


  // 如果沒有表格資料, 則跳出
  if (!resultTableNudt15Props.value) {
    return;
  }
});
</script>
