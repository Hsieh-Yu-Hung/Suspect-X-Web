<template>
  <q-card bordered style="width: 100%;">
    <q-card-section>
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span class="text-h5 text-uppercase text-bold text-blue-grey-7">Testing Table</span>
        <q-btn icon="play_circle" color="primary" label="Run All" class="q-ml-md" @click="runAllDataset" />
      </div>
      <div class="q-pa-md">
        <q-table
          :rows="display_dataset_rows"
          :columns="dataset_columns"
          row-key="name"
          :rows-per-page-options="[1000]"
          class="testing-table"
        >
          <!--標題-->
          <template v-slot:header-cell-execute>
            <q-th class="header-cell-text">Execute </q-th>
          </template>
          <template v-slot:header-cell-name>
            <q-th class="header-cell-text">Dataset Name </q-th>
          </template>
          <template v-slot:header-cell-group>
            <q-th class="header-cell-text">Group </q-th>
          </template>
          <template v-slot:header-cell-config>
            <q-th class="header-cell-text">Config </q-th>
          </template>
          <template v-slot:header-cell-qc>
            <q-th class="header-cell-text">QC </q-th>
          </template>
          <template v-slot:header-cell-result>
            <q-th class="header-cell-text">Result </q-th>
          </template>
          <template v-slot:header-cell-assessment>
            <q-th class="header-cell-text">Assessment </q-th>
          </template>
          <template v-slot:header-cell-validation>
            <q-th class="header-cell-text">Validation </q-th>
          </template>

          <!--執行-->
          <template v-slot:body-cell-execute="props">
            <q-td :props="props" class="text-center">
              <q-btn dense round icon="play_circle" color="pink-4" label="" @click="runDataset(props.row.name)" />
            </q-td>
          </template>
          <template v-slot:body-cell-group="props">
            <q-td :props="props" class="text-center">
              <span :class="props.row.group === 'Positive' ? 'positive-color' : props.row.group === 'Negative' ? 'neutral-color' : 'grey-color'">{{ props.row.group }}</span>
            </q-td>
          </template>
          <template v-slot:body-cell-config="props">
            <q-td :props="props" class="text-center">
              <div class="row q-gutter-sm justify-center" style="display: flex; flex-direction: column; justify-content: center; align-items: center;">
                <q-chip color="primary" text-color="white" icon="biotech" v-if="props.row.config.instrument">
                  {{ props.row.config.instrument }}
                </q-chip>
                <q-chip color="teal" text-color="white" icon="science" v-if="props.row.config.reagent">
                  {{ props.row.config.reagent }}
                </q-chip>
              </div>
            </q-td>
          </template>
          <template v-slot:body-cell-qc="props">
            <q-td :props="props" class="text-center">
              <span :class="props.row.qc === 'Passed' ? 'positive-color' : props.row.qc === 'Failed' ? 'negative-color' : 'grey-color'">{{ props.row.qc }}</span>
              <span> / </span>
              <span :class="props.row.qc_answer === 'Passed' ? 'positive-color' : props.row.qc_answer === 'Failed' ? 'negative-color' : 'grey-color'">{{ props.row.qc_answer }}</span>
            </q-td>
          </template>
          <template v-slot:body-cell-validation="props">
            <q-td :props="props" class="text-center">
              <div class="row q-gutter-sm justify-center" style="display: flex; flex-direction: column; justify-content: center; align-items: center;">
                <q-chip
                  @click="showAnswerDialog(props.row)"
                  clickable
                  :color="props.row.validation === 'ok' ? 'positive' : props.row.validation === 'error' ? 'negative' : 'grey'"
                  text-color="white"
                  :icon="props.row.validation === 'ok' ? 'check_circle' : props.row.validation === 'error' ? 'error' : 'help'">
                  {{ props.row.validation === 'ok' ? 'OK' : props.row.validation === 'error' ? 'Error' : 'Not Set' }}
                </q-chip>
              </div>
            </q-td>
          </template>
          <template v-slot:body-cell-result="props">
            <q-td :props="props" class="text-center">
              <div class="row q-gutter-sm justify-center" style="display: flex; flex-direction: column; justify-content: center; align-items: center;">
                <span>{{ props.row.result.valid_number }} / {{ props.row.result.total_number }}</span>
                <q-chip
                  :color="props.row.result.validation === 'valid' ? 'positive' : props.row.result.validation === 'invalid' ? 'negative' : 'grey'"
                  text-color="white"
                  :icon="props.row.result.validation === 'valid' ? 'check_circle' : props.row.result.validation === 'invalid' ? 'error' : 'help'">
                  {{ props.row.result.validation === 'valid' ? 'Valid' : props.row.result.validation === 'invalid' ? 'Invalid' : 'Not Set' }}
                </q-chip>
              </div>
            </q-td>
          </template>
          <template v-slot:body-cell-assessment="props">
            <q-td :props="props" class="text-center">
              <div class="row q-gutter-sm justify-center" style="display: flex; flex-direction: column; justify-content: center; align-items: center;">
                <span>{{ props.row.assessment.valid_number }} / {{ props.row.assessment.total_number }}</span>
                <q-chip
                  :color="props.row.assessment.validation === 'valid' ? 'positive' : props.row.assessment.validation === 'invalid' ? 'negative' : 'grey'"
                  text-color="white"
                  :icon="props.row.assessment.validation === 'valid' ? 'check_circle' : props.row.assessment.validation === 'invalid' ? 'error' : 'help'">
                  {{ props.row.assessment.validation === 'valid' ? 'Valid' : props.row.assessment.validation === 'invalid' ? 'Invalid' : 'Not Set' }}
                </q-chip>
              </div>
            </q-td>
          </template>
        </q-table>
      </div>
      <CompareResultDialog
        v-model="showDialog"
        :rowData="selectedRow"
      />
    </q-card-section>
  </q-card>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import getTestingData from '@/composables/useGetTestingData';
import { createRObject, createDObject } from '@/types/testingTebleObj';
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';
import { useStore } from 'vuex';
import { useQuasar } from 'quasar';
import { submitWorkflow } from '@/composables/submitWorkflow.js';
import CompareResultDialog from '@/components/AdminPageViewComp/OtherSettingSection/RAForms/CompareResultDialog.vue';
import { getReagent, getParsedResult } from '@/composables/useRunTestings';

// 取得 store, $q
const store = useStore();
const $q = useQuasar();

// props
const props = defineProps({
  current_product: {
    type: String,
    required: true,
  },
  current_reagent: {
    type: String,
    required: true,
  },
});

// emit
const emit = defineEmits(['runDataset']);

// 取得 Dataset Name
const dataset_name = computed(() => {
  switch (props.current_product) {
    case 'fx':
      return 'FXS';
    case 'hd':
      return 'HTD';
    case 'sma':
      if (props.current_reagent === 'accuinSma4') {
        return 'SMA_CE';
      }
      else {
        return 'SMA';
      }
    case 'thal-import-alpha':
      return 'ALPHA-THAL';
    case 'thal-import-beta':
      return 'BETA-THAL';
    case 'nudt15':
      return 'NUDT15';
    case 'apoe-import':
      return 'APOE';
    case 'mthfr-import':
      return 'MTHFR';
    default:
      return props.current_product;
  }
});

// 定義 dataset_rows
const dataset_rows = computed(() => {
  return testing_data.value.map((item) => {
    return {
      name: item.name,
      group: item.group,
      config: {
        instrument: item.instrument || '未指定',
        reagent: item.reagent || '未指定',
      },
      qc_answer: item.qc,
      qc: 'not-set',
      result: item.result,
      assessment: item.assessments,
      validation: 'not-set',
    };
  });
});
const display_dataset_rows = ref([]);

// 定義 dataset_columns
const dataset_columns = ref([
  {
    name: 'execute',
    label: 'Execute',
    field: 'execute',
    align: 'center',
    sortable: true,
    headerStyle: 'text-align: center'
  },
  {
    name: 'name',
    label: 'Dataset Name',
    field: 'name',
    align: 'center',
    sortable: true,
    headerStyle: 'text-align: center'
  },
  {
    name: 'group',
    label: 'Group',
    field: 'group',
    align: 'center',
    sortable: true,
    headerStyle: 'text-align: center'
  },
  {
    name: 'config',
    label: 'Configs',
    field: 'config',
    align: 'center',
    format: val => `${val.instrument} / ${val.reagent}`,
    sortable: true,
    headerStyle: 'text-align: center'
  },
  {
    name: 'qc',
    label: 'QC',
    field: 'qc',
    align: 'center',
    sortable: true,
    headerStyle: 'text-align: center'
  },
  {
    name: 'result',
    label: 'Result',
    field: 'result',
    align: 'center',
    sortable: true,
    headerStyle: 'text-align: center'
  },
  {
    name: 'assessment',
    label: 'Assessment',
    field: 'assessment',
    align: 'center',
    sortable: true,
    headerStyle: 'text-align: center'
  },
  {
    name: 'validation',
    label: 'Validation',
    field: 'validation',
    align: 'center',
    sortable: true,
    headerStyle: 'text-align: center'
  },
]);

// 測試資料集
const testing_data = ref([]);

// 使用者身份
const is_login = ref(false);
const user_info = ref(null);

// 對話框控制
const showDialog = ref(false);
const selectedRow = ref([]);

// 顯示答案對照頁面
function showAnswerDialog(row) {
  selectedRow.value = row;
  showDialog.value = true;
}

// 將 result_matrix 轉換為 DObject
const createDatasetObject = (dataset_name, result_matrix) => {
  const result_anwserArrary = result_matrix.map((item) => {
    return createRObject(item.sample_id, item.result, 'result');
  });
  const assessment_anwserArrary = result_matrix.map((item) => {
    return createRObject(item.sample_id, item.assessment, 'assessment');
  });
  const testingArrary = []
  return {
    result: createDObject(dataset_name, result_anwserArrary, testingArrary),
    assessment: createDObject(dataset_name, assessment_anwserArrary, testingArrary),
  }
}

// 刷新表格
async function refreshTable() {
  // 取得測試資料集
  testing_data.value = await getTestingData(dataset_name.value);

  // 將 result_matrix 轉換為 DObject
  testing_data.value.forEach((t_data) => {
    const matrix = createDatasetObject(t_data.name, t_data.result_matrix);
    dataset_rows.value.find(row => row.name === t_data.name).result = matrix.result;
    dataset_rows.value.find(row => row.name === t_data.name).assessment = matrix.assessment;
  });

  // 設定 display_dataset_rows
  display_dataset_rows.value = dataset_rows.value;
}

// 執行所有資料集
async function runAllDataset() {

  // 判斷是否使用 PCR 分析
  const isPCR = (dataset_class) => {
    return ['FXS', 'HTD'].includes(dataset_class);
  }

  // 判斷是否使用 qPCR 分析
  const isQPCR = (dataset_class) => {
    return ['MTHFR', 'NUDT15'].includes(dataset_class);
  }

  // 判斷是否為 APOE
  const isAPOE = (dataset_class) => {
    return dataset_class === 'APOE';
  }

  // 判斷是否為 Beta-Thal
  const isBetaThal = (dataset_class) => {
    return dataset_class === 'BETA-THAL';
  }

  // 判斷是否為 SMA
  const isSMA = (dataset_class) => {
    return dataset_class === 'SMA';
  }

  // 判斷是否為 SMA_CE
  const isSMA_CE = (dataset_class) => {
    return dataset_class === 'SMA_CE';
  }

  // 解析 APOE sample 檔案
  const parseAPOESample = (sample_files) => {
    const group_list = [...new Set(sample_files.map((file) => file.group))];
    return group_list.map((group) => {
      return {
        sampleId: `APOE-Sample-${group}`,
        filePathList: sample_files.filter((file) => file.group === group).map((file) => file.path)
      }
    })
  }

  // 執行所有資料集
  try {
    const totalTasks = testing_data.value.length;
    let completedTasks = 0;

    $q.loading.show({
      message: `處理進度：${completedTasks}/${totalTasks}`
    });

    const promises = testing_data.value.map(async (t_data, index) => {
      // 添加延遲
      await new Promise(resolve => setTimeout(resolve, index * 200));

      // 取得 inputData
      const inputData = isPCR(t_data.dataset_class) ? {
        controlPath: t_data.controlFile,
        samplePathList: t_data.sampleFiles
                      }
                      : isQPCR(t_data.dataset_class) ? {
                        file_path: t_data.file ? t_data.file : null,
                        control_well: [{X: t_data.controlWell[0], Y: t_data.controlWell.substring(1)}],
                        ntc_well: {X: t_data.NTCWell[0], Y: t_data.NTCWell.substring(1)},
                        FAM_file_path: t_data.FAM ? t_data.FAM : null,
                        VIC_file_path: t_data.VIC ? t_data.VIC : null,
                      }
                      : isAPOE(t_data.dataset_class) ? {
                        control1PathList: t_data.sc1_files,
                        control2PathList: t_data.sc2_files,
                        samplePathList: parseAPOESample(t_data.sample_files)
                      }
                      : isBetaThal(t_data.dataset_class) ? {
                        sample_name: t_data.name,
                        file_path: t_data.sample_files[0].files,
                        left_trim: t_data.leftTrim,
                        right_trim: t_data.rightTrim,
                        peak_ratio: t_data.peakRatio
                      }
                      : isSMA_CE(t_data.dataset_class) ? {
                        file_path: {
                          smn1_samples: t_data.SMN1_Samples.map((sample) => sample.path),
                          smn1_std1: t_data.SMN1_SC_C.map((sample) => sample.path)[0],
                          smn1_std2: t_data.SMN1_SC_N.map((sample) => sample.path)[0],
                          smn2_samples: t_data.SMN2_Samples.map((sample) => sample.path),
                          smn2_std1: t_data.SMN2_SC_C.map((sample) => sample.path)[0],
                          smn2_std2: t_data.SMN2_SC_N.map((sample) => sample.path)[0],
                        }
                      }
                      : isSMA(t_data.dataset_class) ? {
                        file_path: t_data.file ? t_data.file : null,
                        control_well: t_data.SC1Well && t_data.SC2Well ? [
                          {X: t_data.SC1Well[0], Y: t_data.SC1Well.substring(1)},
                          {X: t_data.SC2Well[0], Y: t_data.SC2Well.substring(1)},
                        ] : null,
                        ntc_well: t_data.NTCWell ? {
                          X: t_data.NTCWell[0], Y: t_data.NTCWell.substring(1)
                        } : null,
                        FAM_file_path: t_data.FAM ? t_data.FAM : null,
                        VIC_file_path: t_data.VIC ? t_data.VIC : null,
                        CY5_file_path: t_data.CY5 ? t_data.CY5 : null,
                        parameters: null,
                      }
      : null;

      // 執行 submitWorkflow
      const usedDatasetClass =  t_data.dataset_class === 'BETA-THAL' ? 'THAL_BETA' // 特殊處理 Beta-Thal
                              : t_data.dataset_class === 'SMA_CE' ? 'SMA'       // 特殊處理 SMA_CE
                              : t_data.dataset_class;
      const resultMatrix = await onSubmit(usedDatasetClass, inputData, t_data.reagent, t_data.instrument);
      const targetData = display_dataset_rows.value.find((row) => {
        if (t_data.dataset_name){
          return row.name === t_data.dataset_name;
        } else {
          return row.name === t_data.name;
        }
      });
      targetData.qc = resultMatrix.qc;
      targetData.result.testing_set = resultMatrix.results;
      targetData.assessment.testing_set = resultMatrix.assessments;

      // 進行驗證
      targetData.result.validate();
      targetData.assessment.validate();
      if (targetData.result.validation === 'valid' &&
          targetData.assessment.validation === 'valid' &&
          targetData.qc === targetData.qc_answer) {
        targetData.validation = 'ok';
      } else {
        targetData.validation = 'error';
      }

      // 更新進度
      completedTasks++;
      $q.loading.show({
        message: `處理進度：${completedTasks}/${totalTasks}`
      });
    });

    await Promise.all(promises);
    $q.loading.hide();
  } catch (error) {
    $q.loading.hide();
    $q.notify({
      message: "Error during running workflow.",
      color: 'negative',
      icon: 'error',
      position: 'top',
    });
    console.error('執行資料集時發生錯誤：', error);
  }
}

// 執行資料集
async function runDataset(dataset_name) {
  emit('runDataset', dataset_name);
}

/** onSubmit 功能 */
async function onSubmit(AnalysisName, InputData, reagent, instrument) {

  // 取得試劑, 儀器
  const { reagent_value, reagent_label } = getReagent(dataset_name.value, reagent);
  const usedInstrument = instrument;

  // 取得 settingProps
  const currentSettingProps = store.getters["analysis_setting/getSettingProps"];
  const updateSettingProps = {
    ...currentSettingProps,
    reagent: reagent_value,
    reagentLabel: reagent_label,
    instrument: usedInstrument,
  }

  // 執行 submitWorkflow
  const analysisResult = await submitWorkflow(AnalysisName, InputData, user_info.value, updateSettingProps);
  if (analysisResult.status == 'success') {
    // 解析結果
    const parsedResult = getParsedResult(AnalysisName, reagent, analysisResult);
    return parsedResult;
  }
  else if (analysisResult.status == 'error' || !analysisResult.results) {
    $q.notify({
      message: "Error during running workflow.",
      color: 'negative',
      icon: 'error',
      position: 'top',
    });
    console.error(analysisResult.message);
    throw new Error(analysisResult.message);
  }
}

// Expose
defineExpose({
  refreshTable,
});

// 定義 onMounted
onMounted(async () => {
  // 取得使用者身份
  const { login_status } = updateGetUserInfo();
  is_login.value = login_status.value.is_login;
  user_info.value = login_status.value.user_info;

  // 刷新表格
  await refreshTable();
});

// 監聽 current_product 的變化
watch(() => props.current_product, async (newVal, oldVal) => {
  if (newVal !== oldVal) {
    await refreshTable();
  }
});

// 監聽 current_reagent 的變化
watch(() => props.current_reagent, async (newVal, oldVal) => {
  if (newVal !== oldVal) {
    await refreshTable();
  }
});
</script>

<style>
.testing-table .q-table__middle td {
  text-align: center;
}

.testing-table th {
  text-align: center !important;
}

.testing-table .q-table__title {
  text-align: center;
}

.header-cell-text {
  text-align: center;
  font-weight: bold;
  font-size: 0.8rem;
}

.positive-color {
  font-weight: bold;
  color: #008000;
}

.negative-color {
  font-weight: bold;
  color: #FF0000;
}

.neutral-color {
  font-weight: bold;
  color: #1f26e7;
}

.grey-color {
  font-weight: bold;
  color: #808080;
}
</style>

