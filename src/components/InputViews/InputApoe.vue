<template>
  <q-card bordered>
    <q-card-section>
      <div class="text-h5 text-uppercase text-bold text-blue-grey-7">
        Input
      </div>
      <div class="text-subtitle1">
        Please input the APOE (AD) corresponding sample results.
      </div>
      <div class="row q-pb-lg q-gutter-sm">
        <div class="col">
          <q-file
            v-model="subjectListFile"
            use-chips
            color="deep-orange-6"
            label="Subject information list file from LIMS (.xls/.xlsx)"
            accept=".xls, .xlsx"
            lazy-rules
            dense
          >
            <template v-slot:before>
              <q-icon name="mdi-microsoft-excel" />
            </template>
          </q-file>
        </div>
      </div>
      <div class="row">
        <q-table
          :rows="inputRows"
          :columns="inputColumns"
          class="col"
          :v-model:pagination="{ rowsPerPage: 0 }"
          :rows-per-page-options="[0]"
          row-key="index"
          flat
          dense
          virtual-scroll
        >
          <template v-slot:body-cell-add="props">
            <!-- <q-td class="text-center" style="max-width: 50px"> -->
            <q-td class="text-center">
              <q-btn
                size="sm"
                text-color="blue-grey-7"
                icon="add"
                round
                dense
                flat
                @click="addRow(props.key)"
              />
            </q-td>
          </template>
          <template v-slot:body-cell-remove="props">
            <!-- <q-td class="text-center" style="max-width: 50px"> -->
            <q-td class="text-center">
              <q-btn
                v-if="inputRows.length !== 1"
                size="sm"
                text-color="blue-grey-7"
                icon="remove"
                round
                dense
                flat
                @click="removeRow(props.key)"
              />
            </q-td>
          </template>
          <template v-slot:body-cell-sampleId="props">
            <q-td>
              <q-input
                v-model="updateInput[props.key].sampleId"
                @update:model-value="(val) => updateInput = {index: props.key, col: 'sampleId', update: val}"
                color="deep-orange"
                class="q-mx-lg"
              />
            </q-td>
          </template>
          <template v-slot:body-cell-e2="props">
            <q-td :class="props.row.e2 ? 'text-center text-indigo text-bold' : 'text-center text-blue-grey text-bold'">
              <q-checkbox
                keep-color
                left-label
                size="lg"
                :color="props.row.e2 ? 'indigo' : 'blue-grey'"
                v-model="updateInput[props.key].e2"
                @update:model-value="(val) => updateInput = {index: props.key, col: 'e2', update: val}"
                checked-icon="add_circle"
                unchecked-icon="remove_circle"
                label="E2 (175 bp)"
                dense
              />
            </q-td>
          </template>
          <template v-slot:body-cell-e3="props">
            <q-td :class="props.row.e3 ? 'text-center text-blue text-bold' : 'text-center text-blue-grey text-bold'">
              <q-checkbox
                keep-color
                left-label
                size="lg"
                :color="props.row.e3 ? 'blue' : 'blue-grey'"
                v-model="updateInput[props.key].e3"
                @update:model-value="(val) => updateInput = {index: props.key, col: 'e3', update: val}"
                checked-icon="add_circle"
                unchecked-icon="remove_circle"
                label="E3 (174 bp)"
                dense
              />
            </q-td>
          </template>
          <template v-slot:body-cell-e4="props">
            <q-td :class="props.row.e4 ? 'text-center text-cyan text-bold' : 'text-center text-blue-grey text-bold'">
              <q-checkbox
                keep-color
                left-label
                size="lg"
                :color="props.row.e4 ? 'cyan' : 'blue-grey'"
                v-model="updateInput[props.key].e4"
                @update:model-value="(val) => updateInput = {index: props.key, col: 'e4', update: val}"
                checked-icon="add_circle"
                unchecked-icon="remove_circle"
                label="E4 (173 bp)"
                dense
              />
            </q-td>
          </template>
          <template v-slot:body-cell-result="props">
            <q-td
              class='text-center text-blue-grey text-bold'
              v-for="label in updateInput[props.key].resultLabel"
              :key="label"
            >
              {{ label }}
            </q-td>
          </template>
          <template v-slot:body-cell-assessment="props">
            <q-td class="text-center">
              <q-chip
                class="text-grey-9"
                :color="assessmentColor(updateInput[props.key].assessment)"
                :label="updateInput[props.key].assessmentLabel"
              />
            </q-td>
          </template>
        </q-table>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useStore } from "vuex";
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';
import { extract, downloadTemplate } from "@/composables/useExtract";
import { uploadFile_to_category } from "@/composables/storageManager";
import { useQuasar } from "quasar";

const store = useStore();
const $q = useQuasar();
const subjectListFile = ref(null);
const currentSettingProps = ref(null);

// 使用者身份
const is_login = ref(false);
const user_info = ref(null);

// Input result table
const inputRows = ref([{
  sampleId: '',
  e2: false,
  e3: false,
  e4: false,
  result: '-',
  resultLabel: ['-'],
  assessment: 'invalid',
  assessmentLabel: 'Invalid',
}]);

const inputColumns = [
  {
    name: 'add',
    field: 'add',
  },
  {
    name: 'remove',
    field: 'remove',
  },
  {
    name: 'index',
    label: '#',
    field: 'index',
    sortable: true,
  },
  {
    name: "sampleId",
    label: "Sample ID",
    align: "center",
    field: "sampleId",
  },

  // APOE
  {
    name: "e2",
    label: "E2 PCR",
    field: "e2",
    align: "center",
  },
  {
    name: "e3",
    label: "E3 PCR",
    field: "e3",
    align: "center",
  },
  {
    name: "e4",
    label: "E4 PCR",
    field: "e4",
    align: "center",
  },

  {
    name: "result",
    label: "Result",
    field: "resultLabel",
    align: "center",
  },
  {
    name: "assessment",
    label: "Assessment",
    field: "assessmentLabel",
    align: "center",
  },
];

const resultAssessment = (row) => {
  const list = [ row.e2, row.e3, row.e4 ];
  if (list[0] && !list[1] && !list[2]) {
    return {
      result: 'e2e2',
      resultLabel: ['APOE基因型E2/E2'],
      assessment: 'low-risk',
      assessmentLabel: '低風險基因型',
    }
  } else if (!list[0] && list[1] && !list[2]) {
    return {
      result: 'e3e3',
      resultLabel: ['APOE基因型E3/E3'],
      assessment: 'normal-risk',
      assessmentLabel: '一般風險基因型',
    }
  } else if (!list[0] && !list[1] && list[2]) {
    return {
      result: 'e4e4',
      resultLabel: ['APOE基因型E4/E4'],
      assessment: 'high-risk',
      assessmentLabel: '高風險基因型',
    }
  } else if (list[0] && list[1] && !list[2]) {
    return {
      result: 'e2e3',
      resultLabel: ['APOE基因型E2/E3'],
      assessment: 'low-risk',
      assessmentLabel: '低風險基因型',
    }
  } else if (list[0] && !list[1] && list[2]) {
    return {
      result: 'e2e4',
      resultLabel: ['APOE基因型E2/E4'],
      assessment: 'high-risk',
      assessmentLabel: '高風險基因型',
    }
  } else if (!list[0] && list[1] && list[2]) {
    return {
      result: 'e3e4',
      resultLabel: ['APOE基因型E3/E4'],
      assessment: 'high-risk',
      assessmentLabel: '高風險基因型',
    }
  } else {
    return {
      result: '-',
      resultLabel: ['-'],
      assessment: 'invalid',
      assessmentLabel: 'Invalid',
    }
  }
};

const assessmentColor = (assessment) => {
  if (assessment === "low-risk") {
    return "green-13";
  } else if (assessment === "normal-risk") {
    return "orange-5";
  } else if (assessment === "high-risk") {
    return "red";
  } else {
    return "grey-5";
  }
};

const updateInput = computed({
  get: () => {
    let updatedInput = {};
    inputRows.value.map(sample => {
      updatedInput[sample.index] = {
        ...sample,
        result: resultAssessment(sample).result,
        resultLabel: resultAssessment(sample).resultLabel,
        assessment: resultAssessment(sample).assessment,
        assessmentLabel: resultAssessment(sample).assessmentLabel,
      };
    })
    return updatedInput
  },
  set: (val) => {
    inputRows.value[val.index - 1][val.col] = val.update;
  }
});

const removeRow = (idx) => {
  inputRows.value.splice(idx - 1, 1);
  inputRows.value.forEach((row, index) => {
    row.index = index + 1;
  });
};

const addRow = (idx) => {
  inputRows.value.splice(idx, 0, ...[{
    sampleId: '',
    e2: false,
    e3: false,
    e4: false,
    result: '-',
    resultLabel: ['-'],
    assessment: 'invalid',
    assessmentLabel: 'Invalid',
    index: idx + 1
  }]);
  inputRows.value.forEach((row, index) => {
    row.index = index + 1;
  });
};

// 初始化索引
inputRows.value.forEach((row, index) => {
  row.index = index + 1;
});

// 監聽 subjectListFile 變化
watch(subjectListFile, async (newVal, oldVal) => {
  if (newVal && newVal !== oldVal) {
    try {
      // 取得使用者身份
      const user_uid = user_info.value.uid;
      const analysis_uuid = 'LIMS_files';
      const category = 'subject_info';

      // 顯示 loading 視窗
      $q.loading.show();

      // 上傳檔案
      await uploadFile_to_category([newVal], user_uid, analysis_uuid, category);

      // 解析檔案
      const extract_result = await extract(newVal);
      let updatedInput = new Array();
      let updatedSubject = {};

      const subjectSampleIdLst = Object.keys(extract_result);
      const inputSampleIdLst = inputRows.value.map(obj => obj.sampleId);

      inputRows.value.forEach(row => {
        updatedInput.push(row);
      });

      subjectSampleIdLst.forEach((sampleId, idx) => {
        const index = inputSampleIdLst.length + idx + 1;

        if (!inputSampleIdLst.includes(sampleId)) {
          updatedInput.push({
            index: index,
            sampleId: sampleId,
            e2: false,
            e3: false,
            e4: false,
            result: '-',
            resultLabel: ['-'],
            assessment: 'invalid',
            assessmentLabel: 'Invalid',

            // 新增以下屬性
            birth: extract_result[sampleId].birth,
            collectingDate: extract_result[sampleId].collectingDate,
            edit: extract_result[sampleId].edit,
            gender: extract_result[sampleId].gender,
            idNumber: extract_result[sampleId].idNumber,
            name: extract_result[sampleId].name,
            receivedDate: extract_result[sampleId].receivedDate,
            type: extract_result[sampleId].type,
          });
        }

        updatedSubject[sampleId] = extract_result[sampleId];
      });

      inputRows.value = updatedInput;

      $q.loading.hide();
    } catch (error) {
      console.error("Error extracting subject info:", error);
      $q.loading.hide();
    }
  }
});

// 監聽 inputRows 變化
watch(inputRows, (newVal) => {
  let updated = new Array();

  inputRows.value.forEach((row) => {
    updated.push({
      ...row,
      result: resultAssessment(row).result,
      resultLabel: resultAssessment(row).resultLabel,
      assessment: resultAssessment(row).assessment,
      assessmentLabel: resultAssessment(row).assessmentLabel,

      // 新增以下屬性
      birth: row.birth ? row.birth : '',
      collectingDate: row.collectingDate ? row.collectingDate : '',
      edit: row.edit ? row.edit : '',
      gender: row.gender ? row.gender : '',
      idNumber: row.idNumber ? row.idNumber : '',
      name: row.name ? row.name : '',
      receivedDate: row.receivedDate ? row.receivedDate : '',
      type: row.type ? row.type : '',
    });
  });

  // 更新 store 中的 exportResults
  store.commit("export_page_setting/updateExportResults", updated);

  // 更新產品資訊
  const currentProduct = currentSettingProps.value ? currentSettingProps.value.product : '';
  store.commit("export_page_setting/updateExportedProduct", currentProduct);
}, { deep: true });

// 掛載時檢查 exportResults
onMounted(() => {

  // 取得使用者身份
  const { login_status } = updateGetUserInfo();
  is_login.value = login_status.value.is_login;
  user_info.value = login_status.value.user_info;

  // 取得 setting props
  currentSettingProps.value = store.getters["analysis_setting/getSettingProps"];

  // 若 store 有資料則載入
  const storeData = store.getters["export_page_setting/getExportResults"];
  if (storeData && storeData.length !== 0) {
    inputRows.value = storeData;
  }
});
</script>
