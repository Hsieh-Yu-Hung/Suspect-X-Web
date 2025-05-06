<template>
  <q-card bordered>
    <q-card-section>
      <div class="text-h5 text-uppercase text-bold text-blue-grey-7">
        Input
      </div>
      <div class="text-subtitle1">
        Please input the F2/F5 corresponding sample results.
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

          <template v-slot:body-cell-f2="props">
            <q-td class="col text-overline">
              <div :class="props.row.f2.ic
                ? 'row justify-center text-indigo text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.f2.ic ? 'indigo' : 'blue-grey'"
                  v-model="updateInput[props.key].f2.ic"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['f2', 'ic'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="IC (327 bp)"
                  dense
                />
              </div>
              <div :class="props.row.f2.mut
                ? 'row justify-center text-indigo text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.f2.mut ? 'indigo' : 'blue-grey'"
                  v-model="updateInput[props.key].f2.mut"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['f2', 'mut'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="MUT (124 bp)"
                  dense
                />
              </div>
              <div :class="props.row.f2.wt
                ? 'row justify-center text-indigo text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.f2.wt ? 'indigo' : 'blue-grey'"
                  v-model="updateInput[props.key].f2.wt"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['f2', 'wt'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="WT (242 bp)"
                  dense
                />
              </div>
            </q-td>
          </template>

          <template v-slot:body-cell-f5="props">
            <q-td class="col text-overline">
              <div :class="props.row.f5.ic
                ? 'row justify-center text-blue text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.f5.ic ? 'blue' : 'blue-grey'"
                  v-model="updateInput[props.key].f5.ic"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['f5', 'ic'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="IC (333 bp)"
                  dense
                />
              </div>
              <div :class="props.row.f5.mut
                ? 'row justify-center text-blue text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.f5.mut ? 'blue' : 'blue-grey'"
                  v-model="updateInput[props.key].f5.mut"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['f5', 'mut'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="MUT (234 bp)"
                  dense
                />
              </div>
              <div :class="props.row.f5.wt
                ? 'row justify-center text-blue text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.f5.wt ? 'blue' : 'blue-grey'"
                  v-model="updateInput[props.key].f5.wt"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['f5', 'wt'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="WT (138 bp)"
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
  f2: {
    ic: true,
    wt: true,
    mut: false,
  },
  f5: {
    ic: true,
    wt: true,
    mut: false,
  },
  result: 'gggg',
  resultLabel: ['F2 c.20210基因型[G/G]', 'F5 c.1691基因型[G/G]'],
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

  // F2/F5
  {
    name: "f2",
    label: "F2 c.20210 PCR",
    field: "f2",
    align: "center",
  },
  {
    name: "f5",
    label: "F5 c.1691 PCR",
    field: "f5",
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
  let resultF2;
  let resultF5;
  let resultLabel = new Array();

  if (row.f2.ic && !row.f2.wt && row.f2.mut) {
    // +-+
    resultF2 = 'aa';
    resultLabel.push('F2 c.20210基因型[A/A]');
  } else if (row.f2.ic && row.f2.wt && row.f2.mut) {
    // +++
    resultF2 = 'ga';
    resultLabel.push('F2 c.20210基因型[G/A]');
  } else if (row.f2.ic && row.f2.wt && !row.f2.mut) {
    // ++-
    resultF2 = 'gg';
    resultLabel.push('F2 c.20210基因型[G/G]');
  }

  if (row.f5.ic && row.f5.wt && !row.f5.mut) {
    // +-+
    resultF5 = 'gg';
    resultLabel.push('F5 c.1691基因型[G/G]');
  } else if (row.f5.ic && row.f5.wt && row.f5.mut) {
    // +++
    resultF5 = 'ga';
    resultLabel.push('F5 c.1691基因型[G/A]');
  } else if (row.f5.ic && !row.f5.wt && row.f5.mut) {
    // ++-
    resultF5 = 'aa';
    resultLabel.push('F5 c.1691基因型[A/A]');
  }

  if (
    (resultF2 === 'gg' && resultF5 === 'gg')
  ) {
    return {
      result: resultF2 + resultF5,
      resultLabel: resultLabel,
      assessment: 'normal-risk',
      assessmentLabel: '一般風險基因型',
    }
  } else if (
    (resultF2 === 'gg' && resultF5 === 'ga') ||
    (resultF2 === 'gg' && resultF5 === 'aa') ||
    (resultF2 === 'ga' && resultF5 === 'gg') ||
    (resultF2 === 'ga' && resultF5 === 'ga') ||
    (resultF2 === 'ga' && resultF5 === 'aa') ||
    (resultF2 === 'aa' && resultF5 === 'gg') ||
    (resultF2 === 'aa' && resultF5 === 'ga') ||
    (resultF2 === 'aa' && resultF5 === 'aa')
  ) {
    return {
      result: resultF2 + resultF5,
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

// Methods
const removeRow = (idx) => {
  inputRows.value.splice(idx - 1, 1);
  inputRows.value.forEach((row, index) => {
    row.index = index + 1;
  });
};

const addRow = (idx) => {
  inputRows.value.splice(idx, 0, {
    sampleId: '',
    f2: {
      ic: true,
      wt: true,
      mut: false,
    },
    f5: {
      ic: true,
      wt: true,
      mut: false,
    },
    result: 'gggg',
    resultLabel: ['F2 c.20210基因型[G/G]', 'F5 c.1691基因型[G/G]'],
    assessment: 'normal-risk',
    assessmentLabel: '一般風險基因型',
    index: idx + 1
  });
  inputRows.value.forEach((row, index) => {
    row.index = index + 1;
  });
};

// 初始化索引
inputRows.value.forEach((row, index) => {
  row.index = index + 1;
});

// Watchers
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
          f2: {
            ic: true,
            wt: true,
            mut: false,
          },
          f5: {
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

watch(inputRows, (newVal) => {
  const updated = inputRows.value.map(row => ({
    index: row.index,
    sampleId: row.sampleId,
    f2_ic: row.f2.ic,
    f2_wt: row.f2.wt,
    f2_mut: row.f2.mut,
    f5_ic: row.f5.ic,
    f5_wt: row.f5.wt,
    f5_mut: row.f5.mut,
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

// 掛載時的處理
onMounted(() => {

  // 取得使用者身份
  const { login_status } = updateGetUserInfo();
  is_login.value = login_status.value.is_login;
  user_info.value = login_status.value.user_info;

  // 取得 setting props
  currentSettingProps.value = store.getters["analysis_setting/getSettingProps"];

  // 若 store 有資料則載入
  const storeData = store.getters["export_page_setting/getExportResults"];
  if (storeData.length > 0 && currentSettingProps.value.product === 'f2f5') {
    inputRows.value = storeData.map(p => ({
      index: p.index,
      sampleId: p.sampleId,
      f2: {
        ic: p.f2_ic,
        wt: p.f2_wt,
        mut: p.f2_mut,
      },
      f5: {
        ic: p.f5_ic,
        wt: p.f5_wt,
        mut: p.f5_mut,
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
