<template>
  <q-card bordered>
    <q-card-section>
      <div class="text-h5 text-uppercase text-bold text-blue-grey-7">
        Input
      </div>
      <div class="text-subtitle1">
        Please input the LCT corresponding sample results.
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

          <template v-slot:body-cell-lct13910="props">
            <q-td class="col text-overline">
              <div :class="props.row.lct13910.ic
                ? 'row justify-center text-indigo text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.lct13910.ic ? 'indigo' : 'blue-grey'"
                  v-model="updateInput[props.key].lct13910.ic"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['lct13910', 'ic'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="IC (303 bp)"
                  dense
                />
              </div>
              <div :class="props.row.lct13910.mut
                ? 'row justify-center text-indigo text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.lct13910.mut ? 'indigo' : 'blue-grey'"
                  v-model="updateInput[props.key].lct13910.mut"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['lct13910', 'mut'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="T (232 bp)"
                  dense
                />
              </div>
              <div :class="props.row.lct13910.wt
                ? 'row justify-center text-indigo text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.lct13910.wt ? 'indigo' : 'blue-grey'"
                  v-model="updateInput[props.key].lct13910.wt"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['lct13910', 'wt'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="C (125 bp)"
                  dense
                />
              </div>
            </q-td>
          </template>

          <template v-slot:body-cell-lct22018="props">
            <q-td class="col text-overline">
              <div :class="props.row.lct22018.ic
                ? 'row justify-center text-blue text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.lct22018.ic ? 'blue' : 'blue-grey'"
                  v-model="updateInput[props.key].lct22018.ic"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['lct22018', 'ic'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="IC (312 bp)"
                  dense
                />
              </div>
              <div :class="props.row.lct22018.mut
                ? 'row justify-center text-blue text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.lct22018.mut ? 'blue' : 'blue-grey'"
                  v-model="updateInput[props.key].lct22018.mut"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['lct22018', 'mut'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="A (234 bp)"
                  dense
                />
              </div>
              <div :class="props.row.lct22018.wt
                ? 'row justify-center text-blue text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.lct22018.wt ? 'blue' : 'blue-grey'"
                  v-model="updateInput[props.key].lct22018.wt"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['lct22018', 'wt'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="G (132 bp)"
                  dense
                />
              </div>
            </q-td>
          </template>
          <template v-slot:body-cell-result="props">
            <q-td
              class='text-center text-blue-grey text-bold'
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

// 輸入結果表格
const inputRows = ref([{
  sampleId: '',
  lct13910: {
    ic: false,
    wt: false,
    mut: false,
  },
  lct22018: {
    ic: false,
    wt: false,
    mut: false,
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

  // LCT
  {
    name: "lct13910",
    label: "LCT 13910 PCR",
    field: "lct13910",
    align: "center",
  },
  {
    name: "lct22018",
    label: "LCT 22018 PCR",
    field: "lct22018",
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

// 方法
const resultAssessment = (row) => {
  let resultLct13910;
  let resultLct22018;
  let resultLabel = new Array();

  if (row.lct13910.ic && !row.lct13910.mut && row.lct13910.wt) {
    // +-+
    resultLct13910 = 'cc';
    resultLabel.push('LCT-13910基因型[C/C]');
  } else if (row.lct13910.ic && row.lct13910.mut && row.lct13910.wt) {
    // +++
    resultLct13910 = 'ct';
    resultLabel.push('LCT-13910基因型[C/T]');
  } else if (row.lct13910.ic && row.lct13910.mut && !row.lct13910.wt) {
    // ++-
    resultLct13910 = 'tt';
    resultLabel.push('LCT-13910基因型[T/T]');
  }

  if (row.lct22018.ic && !row.lct22018.mut && row.lct22018.wt) {
    // +-+
    resultLct22018 = 'gg';
    resultLabel.push('LCT-22018基因型[G/G]');
  } else if (row.lct22018.ic && row.lct22018.mut && row.lct22018.wt) {
    // +++
    resultLct22018 = 'ga';
    resultLabel.push('LCT-22018基因型[G/A]');
  } else if (row.lct22018.ic && row.lct22018.mut && !row.lct22018.wt) {
    // ++-
    resultLct22018 = 'aa';
    resultLabel.push('LCT-22018基因型[A/A]');
  }

  if (
    (resultLct13910 === 'ct' && resultLct22018 === 'ga') ||
    (resultLct13910 === 'ct' && resultLct22018 === 'aa') ||
    (resultLct13910 === 'tt' && resultLct22018 === 'ga') ||
    (resultLct13910 === 'tt' && resultLct22018 === 'aa')
  ) {
    return {
      result: resultLct13910 + resultLct22018,
      resultLabel: resultLabel,
      assessment: 'normal-risk',
      assessmentLabel: '一般風險基因型',
    }
  } else if (
    (resultLct13910 === 'cc' && resultLct22018 === 'gg') ||
    (resultLct13910 === 'cc' && resultLct22018 === 'ga') ||
    (resultLct13910 === 'cc' && resultLct22018 === 'aa') ||
    (resultLct13910 === 'ct' && resultLct22018 === 'gg') ||
    (resultLct13910 === 'tt' && resultLct22018 === 'gg')
  ) {
    return {
      result: resultLct13910 + resultLct22018,
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
  if (storeData.length > 0 && currentSettingProps.value.product === 'lct') {
    inputRows.value = storeData.map(p => ({
      index: p.index,
      sampleId: p.sampleId,
      lct13910: {
        ic: p.lct13910_ic,
        wt: p.lct13910_wt,
        mut: p.lct13910_mut,
      },
      lct22018: {
        ic: p.lct22018_ic,
        wt: p.lct22018_wt,
        mut: p.lct22018_mut,
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

// 方法
const removeRow = (idx) => {
  inputRows.value.splice(idx - 1, 1);
  inputRows.value.forEach((row, index) => {
    row.index = index + 1;
  });
};

const addRow = (idx) => {
  inputRows.value.splice(idx, 0, {
    sampleId: '',
    lct13910: {
      ic: false,
      wt: false,
      mut: false,
    },
    lct22018: {
      ic: false,
      wt: false,
      mut: false,
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

// 監聽器
watch(subjectListFile, async (newVal, oldVal) => {
  if (newVal && newVal !== oldVal) {
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
          lct13910: {
            ic: false,
            wt: false,
            mut: false,
          },
          lct22018: {
            ic: false,
            wt: false,
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

    // 隱藏 loading 視窗
    $q.loading.hide();
  }
});

watch(inputRows, (newVal) => {
  const updated = newVal.map(row => ({
    index: row.index,
    sampleId: row.sampleId,
    lct13910_ic: row.lct13910.ic,
    lct13910_wt: row.lct13910.wt,
    lct13910_mut: row.lct13910.mut,
    lct22018_ic: row.lct22018.ic,
    lct22018_wt: row.lct22018.wt,
    lct22018_mut: row.lct22018.mut,
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

</script>
