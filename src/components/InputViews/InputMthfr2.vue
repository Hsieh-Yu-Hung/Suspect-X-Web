<template>
  <q-card bordered>
    <q-card-section>
      <div class="text-h5 text-uppercase text-bold text-blue-grey-7">
        Input
      </div>
      <div class="text-subtitle1">
        Please input the MTHFR2 corresponding sample results.
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
        <div class="col-3 flex justify-center" style="width: fit-content;">
          <q-btn
            label="Download Template"
            color="grey-7"
            icon="mdi-file-download"
            flat
            dense
            @click="downloadTemplate"
          />
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
                @update:model-value="(val) => updateInput = {index: props.key, col: ['sampleId'], update: val}"
                color="deep-orange"
                class="q-mx-lg"
              />
            </q-td>
          </template>
          <template v-slot:body-cell-c677="props">
            <q-td class="col text-overline">
              <div :class="props.row.c677.fam
                ? 'row justify-center text-indigo text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.c677.fam ? 'indigo' : 'blue-grey'"
                  v-model="updateInput[props.key].c677.fam"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['c677', 'fam'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="FAM [T]"
                  dense
                />
              </div>
              <div :class="props.row.c677.vic
                ? 'row justify-center text-indigo text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.c677.vic ? 'indigo' : 'blue-grey'"
                  v-model="updateInput[props.key].c677.vic"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['c677', 'vic'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="VIC [C]"
                  dense
                />
              </div>
            </q-td>
          </template>
          <template v-slot:body-cell-c1298="props">
            <q-td class="col text-overline">
              <div :class="props.row.c1298.rox
                ? 'row justify-center text-blue text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.c1298.rox ? 'blue' : 'blue-grey'"
                  v-model="updateInput[props.key].c1298.rox"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['c1298', 'rox'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="ROX [C]"
                  dense
                />
              </div>
              <div :class="props.row.c1298.tamra
                ? 'row justify-center text-blue text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.c1298.tamra ? 'blue' : 'blue-grey'"
                  v-model="updateInput[props.key].c1298.tamra"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['c1298', 'tamra'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="TAMRA [A]"
                  dense
                />
              </div>
            </q-td>
          </template>
          <template v-slot:body-cell-result="props">
            <q-td
              class='col text-center text-blue-grey text-overline text-bold'
            >
              <div
                class="row justify-center"
                v-for="label in updateInput[props.key].resultLabel"
                :key="label"
              >
                {{ label }}
              </div>
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
import { useQuasar } from 'quasar';
import { extract, downloadTemplate } from "@/composables/useExtract";
import { updateGetUserInfo } from "@/composables/accessStoreUserInfo";
import { uploadFile_to_category } from "@/composables/storageManager";

// 使用 store, Quasar
const store = useStore();
const $q = useQuasar();

// 使用者身份
const is_login = ref(false);
const user_info = ref(null);
const currentSettingProps = ref(null);
const subjectListFile = ref(null);

// Input result table
const inputRows = ref([{
  sampleId: '',
  c677: {
    fam: false,
    vic: false
  },
  c1298: {
    rox: false,
    tamra: false,
  },
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

  // MTHFR
  {
    name: "c677",
    label: "c.677 PCR",
    field: "c677",
    align: "center",
  },
  {
    name: "c1298",
    label: "c.1298 PCR",
    field: "c1298",
    align: "center",
  },

  {
    name: "result",
    label: "Result",
    field: "result",
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
  let resultc677;
  let resultc1298;
  let resultLabel = new Array();

  // c667 result
  if (!row.c677.fam && row.c677.vic) {
    resultc677 = 'cc';
    resultLabel.push("MTHFRc.677基因型[C/C]");
  } else if (row.c677.fam && row.c677.vic) {
    resultc677 = 'ct';
    resultLabel.push("MTHFRc.677基因型[C/T]");
  } else if (row.c677.fam && !row.c677.vic) {
    resultc677 = 'tt';
    resultLabel.push("MTHFRc.677基因型[T/T]");
  }

  // c1298 result
  if (!row.c1298.rox && row.c1298.tamra) {
    resultc1298 = 'aa';
    resultLabel.push("MTHFRc.1298基因型[A/A]");
  } else if (row.c1298.rox && row.c1298.tamra) {
    resultc1298 = 'ac';
    resultLabel.push("MTHFRc.1298基因型[A/C]");
  } else if (row.c1298.rox && !row.c1298.tamra) {
    resultc1298 = 'cc';
    resultLabel.push("MTHFRc.1298基因型[C/C]");
  }

  if (
    (resultc677 === 'cc' && resultc1298 === 'aa')
  ) {
    return {
      result: resultc677 + resultc1298,
      resultLabel: resultLabel,
      assessment: 'low-risk',
      assessmentLabel: '低風險基因型',
    }
  } else if (
    (resultc677 === 'cc' && resultc1298 === 'ac') ||
    (resultc677 === 'cc' && resultc1298 === 'cc') ||
    (resultc677 === 'ct' && resultc1298 === 'aa')
  ) {
    return {
      result: resultc677 + resultc1298,
      resultLabel: resultLabel,
      assessment: 'normal-risk',
      assessmentLabel: '一般風險基因型',
    }
  } else if (
    (resultc677 === 'ct' && resultc1298 === 'ac') ||
    (resultc677 === 'ct' && resultc1298 === 'cc') ||
    (resultc677 === 'tt' && resultc1298 === 'aa') ||
    (resultc677 === 'tt' && resultc1298 === 'ac') ||
    (resultc677 === 'tt' && resultc1298 === 'cc')
  ) {
    return {
      result: resultc677 + resultc1298,
      resultLabel: resultLabel,
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
    if (val.col.length === 1) {
      inputRows.value[val.index - 1][val.col[0]] = val.update;
    } else if (val.col.length === 2) {
      inputRows.value[val.index - 1][val.col[0]][val.col[1]] = val.update;
    }
  }
});

const removeRow = (idx) => {
  inputRows.value.splice(idx - 1, 1);
  inputRows.value.forEach((row, index) => {
    row.index = index + 1;
  });
};

const addRow = (idx) => {
  inputRows.value.splice(idx, 0, {
    sampleId: '',
    c677: {
      fam: false,
      vic: false,
    },
    c1298: {
      rox: false,
      tamra: false,
    },
    result: '-',
    resultLabel: ['-'],
    assessment: 'invalid',
    assessmentLabel: 'Invalid',
    index: idx + 1
  });
  inputRows.value.forEach((row, index) => {
    row.index = index + 1;
  });
};

// Initialize index
inputRows.value.forEach((row, index) => {
  row.index = index + 1;
});

// Watches
watch(subjectListFile, async (newVal, oldVal) => {
  if (newVal && newVal !== oldVal) {

    // 取得使用者身份
    const user_uid = user_info.value.uid;
    const analysis_uuid = 'LIMS_files';
    const category = 'subject_info';

    // 顯示 loading 視窗
    $q.loading.show();

    // 上傳檔案
    await uploadFile_to_category([newVal], user_uid, analysis_uuid, category, true);

    // 解析檔案
    const extract_result = await extract(newVal);
    let updatedInput = [...inputRows.value];
    let updatedSubject = {};

    const subjectSampleIdLst = Object.keys(extract_result);
    const inputSampleIdLst = inputRows.value.map(obj => obj.sampleId);

    subjectSampleIdLst.forEach((sampleId, idx) => {
      const index = inputSampleIdLst.length + idx + 1;

      if (!inputSampleIdLst.includes(sampleId)) {
        updatedInput.push({
          index: index,
          sampleId: sampleId,
          c677: { fam: false, vic: false },
          c1298: { rox: false, tamra: false },
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

    // 關閉 loading 視窗
    $q.loading.hide();
  }
});

watch(inputRows, () => {
  const updated = inputRows.value.map(row => ({
    index: row.index,
    sampleId: row.sampleId,
    c677_fam: row.c677.fam,
    c677_vic: row.c677.vic,
    c1298_rox: row.c1298.rox,
    c1298_tamra: row.c1298.tamra,
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
  }));
  // 更新 store 中的 exportResults
  store.commit("export_page_setting/updateExportResults", updated);

  // 更新產品資訊
  const currentProduct = currentSettingProps.value ? currentSettingProps.value.product : '';
  store.commit("export_page_setting/updateExportedProduct", currentProduct);
}, { deep: true });

onMounted(() => {

  // 取得使用者身份
  const { login_status } = updateGetUserInfo();
  is_login.value = login_status.value.is_login;
  user_info.value = login_status.value.user_info;

  // 取得 setting props
  currentSettingProps.value = store.getters["analysis_setting/getSettingProps"];

  // 若 store 有資料則載入
  const storeData = store.getters["export_page_setting/getExportResults"];
  if (storeData.length > 0 && currentSettingProps.value.product === 'mthfr-input' && currentSettingProps.value.reagent === 'accuinMTHFR2') {
    inputRows.value = storeData.map(p => ({
      index: p.index,
      sampleId: p.sampleId,
      c677: {
        fam: p.c677_fam,
        vic: p.c677_vic,
      },
      c1298: {
        rox: p.c1298_rox,
        tamra: p.c1298_tamra,
      },
      result: p.result,
      resultLabel: p.resultLabel,
      assessment: p.assessment,
      assessmentLabel: p.assessmentLabel,

      // 新增以下屬性
      birth: p.birth ? p.birth : '',
      collectingDate: p.collectingDate ? p.collectingDate : '',
      edit: p.edit ? p.edit : '',
      gender: p.gender ? p.gender : '',
      idNumber: p.idNumber ? p.idNumber : '',
      name: p.name ? p.name : '',
      receivedDate: p.receivedDate ? p.receivedDate : '',
      type: p.type ? p.type : '',
    }));
  }
});

</script>
