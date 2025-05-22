<template>
  <q-card bordered>
    <q-card-section>

      <!-- 標題 -->
      <div class="text-h5 text-uppercase text-bold text-blue-grey-7">
        Input
      </div>

      <!-- 說明 -->
      <div class="text-subtitle1">
        Please input the ADH1B/ALDH2 corresponding sample results.
      </div>

      <!-- 上傳檔案 -->
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

      <!-- 結果表格 -->
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

          <template v-slot:body-cell-adh1b="props">
            <q-td class="col text-overline">
              <div :class="props.row.adh1b.ic
                ? 'row justify-center text-indigo text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.adh1b.ic ? 'indigo' : 'blue-grey'"
                  v-model="updateInput[props.key].adh1b.ic"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['adh1b', 'ic'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="IC (283 bp)"
                  dense
                />
              </div>
              <div :class="props.row.adh1b.mut
                ? 'row justify-center text-indigo text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.adh1b.mut ? 'indigo' : 'blue-grey'"
                  v-model="updateInput[props.key].adh1b.mut"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['adh1b', 'mut'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="MUT (128 bp)"
                  dense
                />
              </div>
              <div :class="props.row.adh1b.wt
                ? 'row justify-center text-indigo text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.adh1b.wt ? 'indigo' : 'blue-grey'"
                  v-model="updateInput[props.key].adh1b.wt"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['adh1b', 'wt'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="WT (206 bp)"
                  dense
                />
              </div>
            </q-td>
          </template>

          <template v-slot:body-cell-aldh2="props">
            <q-td class="col text-overline">
              <div :class="props.row.aldh2.ic
                ? 'row justify-center text-blue text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.aldh2.ic ? 'blue' : 'blue-grey'"
                  v-model="updateInput[props.key].aldh2.ic"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['aldh2', 'ic'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="IC (358 bp)"
                  dense
                />
              </div>
              <div :class="props.row.aldh2.mut
                ? 'row justify-center text-blue text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.aldh2.mut ? 'blue' : 'blue-grey'"
                  v-model="updateInput[props.key].aldh2.mut"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['aldh2', 'mut'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="MUT (292 bp)"
                  dense
                />
              </div>
              <div :class="props.row.aldh2.wt
                ? 'row justify-center text-blue text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.aldh2.wt ? 'blue' : 'blue-grey'"
                  v-model="updateInput[props.key].aldh2.wt"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['aldh2', 'wt'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="WT (116 bp)"
                  dense
                />
              </div>
            </q-td>
          </template>
          <template v-slot:body-cell-result="props">
            <q-td
              class='text-center text-blue-grey text-bold'
            >
              <div class="row justify-center" v-for="label in updateInput[props.key].resultLabel" :key="label">
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
  adh1b: {
    ic: true,
    wt: true,
    mut: false,
  },
  aldh2: {
    ic: true,
    wt: true,
    mut: false,
  },
  result: 'aagg',
  resultLabel: [ 'ADH1B c.143基因型[A/A]', 'ALDH2 c.1510基因型[G/G]' ],
  assessment: 'normal-risk',
  assessmentLabel: '一般風險基因型',
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
  // Alcohol
  {
    name: "adh1b",
    label: "ADH1B PCR",
    field: "adh1b",
    align: "center",
  },
  {
    name: "aldh2",
    label: "ALDH2 PCR",
    field: "aldh2",
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
  let resultAdh1b;
  let resultAldh2;
  let resultLabel = new Array();

  if (row.adh1b.ic && !row.adh1b.wt && row.adh1b.mut) {
    // +-+
    resultAdh1b = 'gg';
    resultLabel.push('ADH1B c.143基因型[G/G]');
  } else if (row.adh1b.ic && row.adh1b.wt && row.adh1b.mut) {
    // +++
    resultAdh1b = 'ag';
    resultLabel.push('ADH1B c.143基因型[A/G]');
  } else if (row.adh1b.ic && row.adh1b.wt && !row.adh1b.mut) {
    // ++-
    resultAdh1b = 'aa';
    resultLabel.push('ADH1B c.143基因型[A/A]');
  }

  if (row.aldh2.ic && row.aldh2.wt && !row.aldh2.mut) {
    // +-+
    resultAldh2 = 'gg';
    resultLabel.push('ALDH2 c.1510基因型[G/G]');
  } else if (row.aldh2.ic && row.aldh2.wt && row.aldh2.mut) {
    // +++
    resultAldh2 = 'ga';
    resultLabel.push('ALDH2 c.1510基因型[G/A]');
  } else if (row.aldh2.ic && !row.aldh2.wt && row.aldh2.mut) {
    // ++-
    resultAldh2 = 'aa';
    resultLabel.push('ALDH2 c.1510基因型[A/A]');
  }

  if (
    (resultAdh1b === 'aa' && resultAldh2 === 'gg') ||
    (resultAdh1b === 'ag' && resultAldh2 === 'gg')
  ) {
    return {
      result: resultAdh1b + resultAldh2,
      resultLabel: resultLabel,
      assessment: 'normal-risk',
      assessmentLabel: '一般風險基因型',
    }
  } else if (
    (resultAdh1b === 'aa' && resultAldh2 === 'ga') ||
    (resultAdh1b === 'aa' && resultAldh2 === 'aa') ||
    (resultAdh1b === 'ag' && resultAldh2 === 'ga') ||
    (resultAdh1b === 'ag' && resultAldh2 === 'aa') ||
    (resultAdh1b === 'gg' && resultAldh2 === 'gg') ||
    (resultAdh1b === 'gg' && resultAldh2 === 'ga') ||
    (resultAdh1b === 'gg' && resultAldh2 === 'aa')
  ) {
    return {
      result: resultAdh1b + resultAldh2,
      resultLabel: resultLabel,
      assessment: 'high-risk',
      assessmentLabel: '高風險基因型'
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

inputRows.value.forEach((row, index) => {
  row.index = index + 1;
});

onMounted(() => {

  // 取得使用者身份
  const { login_status } = updateGetUserInfo();
  is_login.value = login_status.value.is_login;
  user_info.value = login_status.value.user_info;

  // 取得 setting props
  currentSettingProps.value = store.getters["analysis_setting/getSettingProps"];

  // 若 store 有資料則載入
  const storeData = store.getters["export_page_setting/getExportResults"];
  if (storeData.length !== 0 && currentSettingProps.value.product === 'alcohol') {
    inputRows.value = storeData.map(p => {
      return {
        index: p.index,
        sampleId: p.sampleId,
        adh1b: {
          ic: p.adh1b_ic,
          wt: p.adh1b_wt,
          mut: p.adh1b_mut,
        },
        aldh2: {
          ic: p.aldh2_ic,
          wt: p.aldh2_wt,
          mut: p.aldh2_mut,
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
      }
    });
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
    adh1b: {
      ic: true,
      wt: true,
      mut: false,
    },
    aldh2: {
      ic: true,
      wt: true,
      mut: false,
    },
    result: 'aagg',
    resultLabel: ['ADH1B c.143基因型[A/A]', 'ALDH2 c.1510基因型[G/G]'],
    assessment: 'normal-risk',
    assessmentLabel: '一般風險基因型',
    index: idx + 1
  }]);
  inputRows.value.forEach((row, index) => {
    row.index = index + 1;
  });
};

// 監聽 subjectListFile 的變化
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

    let updatedInput = new Array();
    let updatedSubject = {};
    const subjectSampleIdLst = Object.keys(extract_result);
    const inputSampleIdLst = inputRows.value.map(obj => obj.sampleId)
    inputRows.value.forEach(row => {
      updatedInput.push(row);
    });

    subjectSampleIdLst.forEach((sampleId, idx) => {
      const index = inputSampleIdLst.length + idx + 1;

      if (!inputSampleIdLst.includes(sampleId)) {
        updatedInput.push({
          index: index,
          sampleId: sampleId,
          adh1b: {
            ic: true,
            wt: true,
            mut: false,
          },
          aldh2: {
            ic: true,
            wt: true,
            mut: false,
          },
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
  }
});

// 監聽 inputRows 的變化
watch(inputRows, () => {
  let updated = new Array();

  inputRows.value.forEach((row) => {
    updated.push({
      index: row.index,
      sampleId: row.sampleId,
      adh1b_ic: row.adh1b.ic,
      adh1b_wt: row.adh1b.wt,
      adh1b_mut: row.adh1b.mut,
      aldh2_ic: row.aldh2.ic,
      aldh2_wt: row.aldh2.wt,
      aldh2_mut: row.aldh2.mut,
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
</script>
