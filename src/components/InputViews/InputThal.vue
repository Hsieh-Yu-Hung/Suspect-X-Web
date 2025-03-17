<template>
  <q-card bordered>
    <q-card-section>

      <!-- 標題 -->
      <div class="text-h5 text-uppercase text-bold text-blue-grey-7">
        Input
      </div>

      <!-- α/β Thal 描述文字 -->
      <div class="text-subtitle1">
        Please input the α/β Thal corresponding sample results by variant positions.
      </div>

      <!-- 樣本資訊檔案上傳 -->
      <div class="row q-pb-lg q-gutter-sm">
        <div class="col">
          <q-file
            v-model="subjectListFile"
            use-chips
            color="deep-orange-6"
            label="Subject information list file from LIMS (.xls or .xlsx)"
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

      <!-- 輸入表格 -->
      <div class="row">
        <q-table
          :rows="inputRows"
          :columns="inputColumns"
          :v-model:pagination="{ rowsPerPage: 0 }"
          :rows-per-page-options="[0]"
          class="col"
          row-key="index"
          flat
          dense
          virtual-scroll
        >
          <!-- 新增樣本按鈕 -->
          <template v-slot:body-cell-add="props">
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

          <!-- 刪除樣本按鈕 -->
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

          <!-- 樣本ID輸入框 -->
          <template v-slot:body-cell-sampleId="props">
            <q-td style="min-width: 180px">
              <q-input
                v-model="getInput[props.key].sampleId"
                @update:model-value="(val) => updateInput({index: props.key, col: 'sampleId', update: val})"
                color="deep-orange"
                class="q-mx-lg"
              />
            </q-td>
          </template>

          <!-- α-Thalassemia Variant(s) 選擇器 -->
          <template v-slot:body-cell-alpha="props">
            <q-td class="col-1 text-overline" style="width: 200px">
              <div class="row justify-center text-indigo">
                <q-select
                  filled
                  v-model="getInput[props.key].alpha"
                  use-input
                  multiple
                  max-values="2"
                  input-debounce="0"
                  color='indigo'
                  class="text-bold"
                  :options="alphaLst"
                  @filter="filterAlphaFn"
                  @update:model-value="(val) => updateInput({index: props.key, col: 'alpha', update: val})"
                >
                  <template v-slot:selected>
                    <span v-if="getInput[props.key].alpha.length === 1">
                      {{ getInput[props.key].alpha[0].label }} / {{ getInput[props.key].alpha[0].label }}
                    </span>
                    <span v-else-if="getInput[props.key].alpha.length > 1">
                      {{ getInput[props.key].alpha[0].label }} / {{ getInput[props.key].alpha[1].label }}
                    </span>
                  </template>
                  <template v-slot:option="scope">
                    <q-item v-bind="scope.itemProps">
                      <q-item-section side>
                        <q-checkbox
                          left-label
                          color="indigo"
                          v-model="scope.selected"
                          checked-icon="task_alt"
                          unchecked-icon="radio_button_unchecked"
                          @update:model-value="scope.toggleOption(scope.opt)"
                        />
                      </q-item-section>
                      <q-item-section>
                        <q-item-label>{{ scope.opt.label }}</q-item-label>
                      </q-item-section>
                    </q-item>
                  </template>
                </q-select>
              </div>
            </q-td>
          </template>

          <!-- β-Thalassemia Variant(s) 選擇器 -->
          <template v-slot:body-cell-beta="props">
            <q-td class="col text-overline" style="width: 200px">
              <div class="row justify-center text-blue text-bold">
                <q-select
                  filled
                  v-model="getInput[props.key].beta"
                  use-input
                  no-wrap
                  multiple
                  input-debounce="0"
                  color="blue"
                  :options="betaLst"
                  @filter="filterBetaFn"
                  @update:model-value="(val) => updateInput({index: props.key, col: 'beta', update: val})"
                >
                <template v-slot:selected-item="scope">
                  <q-chip
                    removable
                    dense
                    @remove="scope.removeAtIndex(scope.index)"
                    :tabindex="scope.tabindex"
                    color="grey-11"
                    text-color="blue"
                  >
                    <span class="text-bold text-overline">
                      {{ scope.opt.label }}
                    </span>
                    <span class="text-overline q-ml-sm">
                      {{ zygosityLabel[getZygosity[props.key - 1][scope.opt.label]] }}
                    </span>
                  </q-chip>
                </template>
                  <template v-slot:option="scope">
                    <q-item v-bind="scope.itemProps" :clickable="!scope.selected">
                      <q-item-section side>
                        <q-checkbox
                          left-label
                          color="blue"
                          v-model="scope.selected"
                          checked-icon="task_alt"
                          unchecked-icon="radio_button_unchecked"
                          @update:model-value="scope.toggleOption(scope.opt)"
                        />
                      </q-item-section>
                      <q-item-section>
                        <q-item-label>{{ scope.opt.label }}</q-item-label>
                        <q-item-label v-if="scope.opt.end" caption>
                          {{ scope.opt.chr }}: {{ scope.opt.start }} - {{ scope.opt.end }}
                        </q-item-label>
                        <q-item-label v-else caption>{{ scope.opt.chr }}: {{ scope.opt.start }}</q-item-label>

                        <q-btn-toggle
                          v-if="scope.selected"
                          v-model="getZygosity[props.key - 1][scope.opt.label]"
                          @update:model-value="(val) => updateInput({index: props.key, col: 'beta', scope: scope.opt.label, update: val})"
                          class="q-ma-sm"
                          no-caps
                          rounded
                          unelevated
                          toggle-color="blue"
                          color="white"
                          text-color="blue"
                          :options="[
                            { label: 'Heterozygous', value: 'hetro' },
                            { label: 'Homozygous', value: 'homo' },
                          ]"
                        />
                      </q-item-section>
                    </q-item>
                  </template>
                </q-select>
              </div>
            </q-td>
          </template>

          <!-- 結果顯示 -->
          <template v-slot:body-cell-result="props">
            <q-td class="text-center text-blue-grey">
              <q-list>
                <q-item>
                  <q-item-section>
                    <q-item-label class="text-overline text-bold" style="font-size: 13px">HBA:{{ props.key }}</q-item-label>
                    <q-item-label style="font-size: 14px"  v-if="Object.values(getInput)[props.key-1].alpha.length === 1">
                      {{ Object.values(getInput)[props.key-1].alpha[0].label }} / {{ Object.values(getInput)[props.key-1].alpha[0].label }}
                    </q-item-label>
                    <q-item-label style="font-size: 14px"  v-else-if="Object.values(getInput)[props.key-1].alpha.length > 1">
                      {{ Object.values(getInput)[props.key-1].alpha[0].label }} / {{ Object.values(getInput)[props.key-1].alpha[1].label }}
                    </q-item-label>
                    <q-item-label style="font-size: 14px" v-else>
                      -
                    </q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label class="text-overline text-bold" style="font-size: 13px">HBB:</q-item-label>
                    <span v-if="getInput[props.key].beta.length !== 0">
                      <q-item-label
                        style="font-size: 14px"
                        v-for="b in getInput[props.key].beta"
                        :key="b"
                        class="q-ma-xs"
                        no-wrap
                      >
                        {{ b.label }} {{ zygosityLabel[getZygosity[props.key - 1][b.label]] }}
                      </q-item-label></span>
                    <span v-else>
                      -
                    </span>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-td>
          </template>

          <!-- 評估結果 -->
          <template v-slot:body-cell-assessment="props">
            <q-td class="text-center">
              <q-chip
                class="text-grey-10"
                :color="assessmentColor(getInput[props.key].assessment)"
                :label="getInput[props.key].assessmentLabel"
              />
            </q-td>
          </template>

        </q-table>
      </div>

    </q-card-section>
  </q-card>
</template>

<script setup>
// 引入模組
import { ref, computed, watch, onMounted } from "vue";
import { useStore } from "vuex";
import { useQuasar } from 'quasar';
import { getThalassemia } from "@/composables/useGetThalDB";
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';
import { extract, downloadTemplate } from "@/composables/useExtract";
import { uploadFile_to_category } from "@/composables/storageManager";

// 使用 store, Quasar
const store = useStore();
const $q = useQuasar();

// 使用者身份
const is_login = ref(false);
const user_info = ref(null);

// 定義變數
const alphaRawLst = ref([]);
const betaRawLst = ref([]);
const alphaLst = ref([]);
const betaLst = ref([]);
const subjectListFile = ref(null);
const currentSettingProps = ref(null);

// 定義 ROW
const ROW = (sampleId, alpha, beta, result, resultLabel, assessment, assessmentLabel, index) => {
  return {
    sampleId: sampleId,
    alpha: alpha,
    beta: beta,
    result: result,
    resultLabel: resultLabel,
    assessment: assessment,
    assessmentLabel: assessmentLabel,
    index: index,
  }
}

// Default ROW
const defaultRow = ROW('', [], [], [['α2', 'α2'], []], [['α2', 'α2'], []], 'negative', '未檢出致病性基因突變', 1);

// Input result table
const inputRows = ref([defaultRow]);
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

  // Thal
  {
    name: "alpha",
    label: "α-Thalassemia Variant(s)",
    field: "alpha",
    align: "center",
  },
  {
    name: "beta",
    label: "β-Thalassemia Variant(s)",
    field: "beta",
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

const zygosityLabel = {
  'hetro' : 'Heterozygous',
  'homo': 'Homozygous',
  'Heterozygous' : 'Heterozygous',    // lazy code
  'Homozygous': 'Homozygous'    // lazy code
};

const resultAssessment = (row) => {
  let resultAlpha = new Array();
  let resultBeta = new Array();
  let resultAlphaLabel = new Array();
  let resultBetaLabel = new Array();

  // alpha
  if (row.alpha.length === 1) {
    resultAlpha.push(row.alpha[0].value)
    resultAlpha.push(row.alpha[0].value)
    resultAlphaLabel.push(row.alpha[0].label);
    resultAlphaLabel.push(row.alpha[0].label);
  } else if (row.alpha.length === 2) {
    row.alpha.map(a => resultAlpha.push(a.value));
    row.alpha.map(a => resultAlphaLabel.push(a.label));
  }

  // beta
  if (row.beta.length !== 0) {
    row.beta.map(b => resultBeta.push(b.value));
    row.beta.map(b => resultBetaLabel.push(b.label));
  }

  if (
    resultAlpha.every(a => a === 'α2')
    && resultAlpha.length !== 0
    && resultBeta.length === 0
  ) {
    return {
      result: [resultAlpha, resultBeta],
      resultLabel: [resultAlphaLabel, resultBetaLabel],
      assessment: 'negative',
      assessmentLabel: '未檢出致病性基因突變',
    }
  } else if (
    resultAlpha.some(a => a !== 'α2')
    && resultAlpha.length !== 0
    && resultBeta.length === 0
  ) {
    return {
      result: [resultAlpha, resultBeta],
      resultLabel: [resultAlphaLabel, resultBetaLabel],
      assessment: 'alpha',
      assessmentLabel: 'α型地中海貧血',
    }
  } else if (
    resultAlpha.every(a => a === 'α2')
    && resultAlpha.length !== 0
    && resultBeta.length !== 0
  ) {
    return {
      result: [resultAlpha, resultBeta],
      resultLabel: [resultAlphaLabel, resultBetaLabel],
      assessment: 'beta',
      assessmentLabel: 'β型地中海貧血',
    }
  } else if (
    resultAlpha.some(a => a !== 'α2')
    && resultAlpha.length !== 0
    && resultBeta.length !== 0
  ) {
    return {
      result: [resultAlpha, resultBeta],
      resultLabel: [resultAlphaLabel, resultBetaLabel],
      assessment: 'alphabeta',
      assessmentLabel: 'α和β型地中海貧血',
    }
  } else {
    return {
      result: [[], []],
      resultLabel: [[], []],
      assessment: 'invalid',
      assessmentLabel: 'Invalid',
    }
  }
};

const assessmentColor = (assessment) => {
  if (assessment === "negative") {
    return "green-13";
  } else if (
    assessment === "alpha" ||
    assessment === "beta" ||
    assessment === "alphabeta"
  ) {
    return "red";
  } else {
    return "grey-5";
  }
};

// 計算屬性
const getInput = computed(() => {
  let updatedInput = {};
  inputRows.value.map(sample => {
    updatedInput[sample.index] = {
      ...sample,
      result: resultAssessment(sample).result,
      resultLabel: resultAssessment(sample).resultLabel,
      assessment: resultAssessment(sample).assessment,
      assessmentLabel: resultAssessment(sample).assessmentLabel,
    };
  });
  return updatedInput;
});

const getZygosity = computed(() => {
  let sampleArr = new Array();
  let betaObj;

  inputRows.value.map(sample => {
    betaObj = sample.beta.reduce((acc, obj) => {
      acc[obj.label] = obj.zygosity;
      return acc;
    }, {});
    sampleArr.push(betaObj);
  });
  return sampleArr;
});

// 方法
const removeRow = (idx) => {
  inputRows.value.splice(idx - 1, 1);
  inputRows.value.forEach((row, index) => {
    row.index = index + 1;
  });
};

const addRow = (idx) => {
  // 直接使用 alphaRawLst.value，因為它已經是解析完成的值
  const alpha = alphaRawLst.value;

  inputRows.value.splice(idx, 0, {
    sampleId: '',
    alpha: alpha.filter(r => r.label === 'α2'),
    beta: [],
    result: [['α2', 'α2'], []],
    resultLabel: [['α2', 'α2'], []],
    assessment: 'negative',
    assessmentLabel: '未檢出致病性基因突變',
    index: idx + 1
  });

  // 重新編號所有行
  inputRows.value.forEach((row, index) => {
    row.index = index + 1;
  });
};

const updateInput = (val) => {
  let updated;

  if (val.scope) {
    // for update zygosity ONLY
    let arr = inputRows.value[val.index - 1][val.col].map(p => ({ ...p }));
    updated = arr.map(obj => {
      if (obj.label === val.scope) {
        return { ...obj, zygosity: val.update };
      }
      return obj;
    });
  } else if (Array.isArray(val.update)) {
    updated = val.update.map(obj => {
      return { ...obj }
    });
  } else {
    updated = val.update
  }

  inputRows.value[val.index - 1][val.col] = updated;
};

const filterAlphaFn = (val, update, abort) => {
  update(() => {
    const needle = val.toLowerCase();
    alphaLst.value = alphaRawLst.value.filter(v => {
      return v.label.toLowerCase().indexOf(needle) > -1 ||
        (Number(needle) >= Number(v.start) && Number(needle) <= Number(v.end))
    });
  });
};

const filterBetaFn = (val, update, abort) => {
  update(() => {
    const needle = val.toLowerCase();
    if (val) {
      betaLst.value = betaRawLst.value.filter(v =>
        v.label.toLowerCase().indexOf(needle) > -1 ||
        (Number(needle) >= Number(v.start) && Number(needle) <= Number(v.end))
      );
    } else {
      // 當 val 為空時，只過濾 common 屬性，不進行第二次過濾
      betaLst.value = betaRawLst.value.filter(v => v.common);
    }
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

    // 使用已經 resolve 的 extract_result，不再重複呼叫 extract
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
        // 直接使用 alphaRawLst.value，不再使用 .then()
        updatedInput.push({
          index: index,
          sampleId: sampleId,
          alpha: alphaRawLst.value.filter(r => r.label === 'α2'),
          beta: [],
          result: [['α2', 'α2'], []],
          resultLabel: [['α2', 'α2'], []],
          assessment: 'negative',
          assessmentLabel: '未檢出致病性基因突變',

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

    // 更新 inputRows
    inputRows.value = updatedInput;

    // 隱藏 loading 視窗
    $q.loading.hide();
  }
});

watch(inputRows, (newVal) => {

  let updated = new Array();

  newVal.forEach((row, index) => {
    let rowResult = resultAssessment(row).result;
    let rowAssessment = resultAssessment(row).assessment;
    let rowAssessmentLabel = resultAssessment(row).assessmentLabel;

    updated.push({
      index: row.index,
      sampleId: row.sampleId,
      result: {
        alpha: row.alpha,
        beta: row.beta.map(b => {
          return { ...b, zygosity: zygosityLabel[b.zygosity] }
        }),
      },
      resultLabel: {
        alpha: {
          type: rowResult[0],
          category: rowAssessment.replace('beta', '') === ''
            ? 'negative'
            : rowAssessment.replace('beta', ''),
        },
        beta: {
          type: rowResult[1],
          category: rowAssessment.replace('alpha', '') === ''
            ? 'negative'
            : rowAssessment.replace('alpha', ''),
        }
      },
      assessment: rowAssessment,
      assessmentLabel: rowAssessmentLabel,

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

  // 更新 store 中的 subjectInfo
  const Xsubi = store.getters["export_page_setting/getXsubi"];
  if (Xsubi.length > 0) {
    updated.forEach(item => {
      item.birth = Xsubi.find(x => x.index === item.index).birth ? Xsubi.find(x => x.index === item.index).birth : '';
      item.collectingDate = Xsubi.find(x => x.index === item.index).collectingDate ? Xsubi.find(x => x.index === item.index).collectingDate : '';
      item.edit = Xsubi.find(x => x.index === item.index).edit ? Xsubi.find(x => x.index === item.index).edit : '';
      item.gender = Xsubi.find(x => x.index === item.index).gender ? Xsubi.find(x => x.index === item.index).gender : '';
      item.idNumber = Xsubi.find(x => x.index === item.index).idNumber ? Xsubi.find(x => x.index === item.index).idNumber : '';
      item.name = Xsubi.find(x => x.index === item.index).name ? Xsubi.find(x => x.index === item.index).name : '';
      item.receivedDate = Xsubi.find(x => x.index === item.index).receivedDate ? Xsubi.find(x => x.index === item.index).receivedDate : '';
      item.type = Xsubi.find(x => x.index === item.index).type ? Xsubi.find(x => x.index === item.index).type : '';
    });
  }

  // 更新 store 中的 exportResults
  store.commit("export_page_setting/updateExportResults", updated);

  // 更新產品資訊
  const currentProduct = currentSettingProps.value ? currentSettingProps.value.product : '';
  store.commit("export_page_setting/updateExportedProduct", currentProduct);
}, { deep: true });

// 生命週期鉤子
onMounted(async () => {

  // 取得使用者身份
  const { login_status } = updateGetUserInfo();
  is_login.value = login_status.value.is_login;
  user_info.value = login_status.value.user_info;

  // 取得 setting props
  currentSettingProps.value = store.getters["analysis_setting/getSettingProps"];

  // 取得 α/β Thal database 資料
  alphaRawLst.value = await getThalassemia('alpha');
  betaRawLst.value = await getThalassemia('beta');

  // 如果 alphaRawLst.value 和 betaRawLst.value 都存在，則進行過濾
  if (alphaRawLst.value && betaRawLst.value) {
    if (alphaLst.value.length > 0) {
      inputRows.value = inputRows.value.map(row => {
        return {
          index: row.index,
          sampleId: row.sampleId,
          alpha: alphaLst.value.filter(r => row.result[0].includes(r.label)),
          beta: row.beta,
          result: row.result,
          resultLabel: row.resultLabel,
          assessment: row.assessment,
          assessmentLabel: row.assessmentLabel,
        }
      });
    }
  }

  // 如果只有一個樣本，且 alpha 為空，則將 alpha 設為 α2 (預設)
  if (inputRows.value.length === 1 && inputRows.value[0].alpha.length === 0) {
    inputRows.value[0].alpha = alphaRawLst.value.filter(r => r.label === 'α2');
  }

  // 若 store 有資料則載入
  const storeData = store.getters["export_page_setting/getExportResults"];
  const default_result = {
    alpha: [
      {
        chr: "",
        common: true,
        disease: "-",
        end: null,
        gene: "-",
        label: "α2",
        start: null,
        type: "Wild Type",
        value: "α2",
        zygosity: "hetro"
      }
    ],
    beta: []
  }
  const default_result_label = {
    alpha: {
      type: ['α2', 'α2'],
      category: "negative",
    },
    beta: {
      type: [],
      category: "negative",
    }
  }
  if (storeData.length > 0) {
    inputRows.value = storeData.map(p => {
      return {
        index: p.index,
        sampleId: p.sampleId,
        alpha: p.result.alpha ? p.result.alpha : default_result.alpha,
        beta: p.result.beta ? p.result.beta : default_result.beta,
        result: p.result.alpha ? [[...new Set(p.resultLabel.alpha.type)], p.resultLabel.beta.type] : default_result,
        resultLabel: p.result.alpha ? [[...new Set(p.resultLabel.alpha.type)], p.resultLabel.beta.type] : default_result_label,
        assessment: p.assessment,
        assessmentLabel: p.assessmentLabel,
      }
    });
  }

  // 更新索引
  inputRows.value.forEach((row, index) => {
    row.index = index + 1;
  });
});
</script>
