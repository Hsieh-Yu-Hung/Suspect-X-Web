<template>
  <q-card bordered>

    <!-- 警告視窗 -->
    <WarningDialog
      ref="warning_dialog"
      :error_message="dialog_error_message"
    />

    <q-card-section>

      <!-- 標題和模板檔案-->
      <div class="col">

        <!-- 標題 -->
        <div class="row text-h5 text-uppercase text-bold text-blue-grey-7">
          Subject Information
        </div>

        <!-- 模板檔案上傳和下載容器 -->
        <div class="row q-pb-xs q-mb-md">

          <!-- 模板檔案上傳 -->
          <div class="col">
            <q-file
              v-model="subjectFile"
              color="deep-orange-6"
              label="Subject information file"
              accept=".xlsx"
              lazy-rules
              use-chips
            >
              <template v-slot:before>
                <q-icon name="mdi-microsoft-excel" />
              </template>
            </q-file>
          </div>

          <!-- 模板檔案下載 -->
          <div class="col text-blue-grey-7 flex justify-end">
            <q-btn
              icon-right="download"
              size="md"
              label="Download template"
              @click="downloadTemplate"
            />
          </div>

        </div>

      </div>

      <!-- 樣本資訊表格 -->
      <q-table
        :rows="exportSampleInfo"
        :columns="visibleColumns"
        class="text-blue-grey-10"
        :v-model:pagination="{ rowsPerPage: 0 }"
        :rows-per-page-options="[0]"
        v-model:selected="selectedExport"
        row-key="index"
        selection="multiple"
        flat
        dense
        virtual-scroll
      >

        <!-- 結果欄位 -->
        <template v-slot:body-cell-result="props">

          <!-- Thal 特殊欄位 -->
          <q-td class="col" :props="props" v-if="showThalColumn">
            <div class="row justify-center text-bold"> HBA:   </div>
            <div class="row justify-center q-mb-sm">
              {{ 'A1' }} / {{ 'A2' }}
            </div>
            <div class="row justify-center q-mb-sm">-</div>
            <div class="row justify-center text-bold"> HBB: </div>
            <div class="row justify-center q-mb-sm">
              <div
                class="row justify-center"
                v-for="b in props.row.result.value.beta"
                :key="b"
              >
                {{ b.label }} {{ b.zygosity }}
              </div>
            </div>
            <div class="row justify-center q-mb-sm">-</div>
          </q-td>

          <!-- 其他欄位 -->
          <q-td class="col" :props="props" v-else>
            <div
              class="row justify-center"
              v-for="label in props.row.result.label"
              :key="label"
            >
              {{ label }}
            </div>
          </q-td>

        </template>

        <!-- 評估欄位 -->
        <template v-slot:body-cell-assessment="props">
          <q-td :props="props" :class="assessmentColor(props.row.assessment.value)">{{props.row.assessment.label}}</q-td>
        </template>

        <!-- 名稱欄位 -->
        <template v-slot:body-cell-name="props">
          <q-td style="min-width: 110px">
            <q-input
              v-model="editSubjectInfo[props.key].name"
              @update:model-value="(val) => editSubjectInfo = {index: props.key, col: 'name', update: val}"
              color="deep-orange"
              dense
              :disable="!editSubjectInfo[props.key].edit"
            />
          </q-td>
        </template>

        <!-- 生日欄位 -->
        <template v-slot:body-cell-birth="props">
          <q-td style="min-width: 180px; vertical-align: middle;">
            <q-input
              filled
              v-model="editSubjectInfo[props.key].birth"
              mask="####/##/##"
              color="deep-orange"
              :rules="[checkDate]"
              :disable="!editSubjectInfo[props.key].edit"
              dense
            >
              <template v-slot:append>
                <q-icon name="event" class="cursor-pointer">
                  <q-popup-proxy ref="qDateProxy" transition-show="scale" transition-hide="scale">
                    <q-date
                      v-model="editSubjectInfo[props.key].birth"
                      @input="() => $refs.qDateProxy.hide()"
                      @update:model-value="(val) => editSubjectInfo = {index: props.key, col: 'birth', update: val}"
                      mask="YYYY/MM/DD"
                      color="deep-orange"
                      minimal
                    ></q-date>
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
          </q-td>
        </template>

        <!-- 性別欄位 -->
        <template v-slot:body-cell-gender="props">
          <q-td>
          <q-radio
            size="xs"
            color="deep-orange"
            @update:model-value="(val) => editSubjectInfo = {index: props.key, col: 'gender', update: val}"
            v-model="editSubjectInfo[props.key].gender"
            checked-icon="task_alt"
            unchecked-icon="panorama_fish_eye"
            val="male"
            label="M"
            :disable="!editSubjectInfo[props.key].edit"
            dense
          />
          <q-radio
            size="xs"
            color="deep-orange"
            @update:model-value="(val) => editSubjectInfo = {index: props.key, col: 'gender', update: val}"
            v-model="editSubjectInfo[props.key].gender"
            checked-icon="task_alt"
            unchecked-icon="panorama_fish_eye"
            val="female"
            label="F"
            :disable="!editSubjectInfo[props.key].edit"
          />
          </q-td>
        </template>

        <!-- 身分證號欄位 -->
        <template v-slot:body-cell-idNumber="props">
          <q-td style="min-width: 120px">
            <q-input
              v-model="editSubjectInfo[props.key].idNumber"
              @update:model-value="(val) => editSubjectInfo = {index: props.key, col: 'idNumber', update: val}"
              color="deep-orange"
              dense
              :disable="!editSubjectInfo[props.key].edit"
            />
          </q-td>
        </template>

        <!-- 樣本類型欄位 -->
        <template v-slot:body-cell-type="props">
          <q-td style="min-width: 100px">
            <q-select
              v-model="editSubjectInfo[props.key].type"
              @update:model-value="(val) => editSubjectInfo = {index: props.key, col: 'type', update: val.value}"
              :options="typeOptions"
              color="deep-orange"
              label-color="deep-orange"
              behavior="menu"
              :disable="!editSubjectInfo[props.key].edit"
              map-options
              outlined
              dense
            />
          </q-td>
        </template>

        <!-- 採樣日期欄位 -->
        <template v-slot:body-cell-collectingDate="props">
          <q-td style="min-width: 180px">
            <q-input
              filled
              v-model="editSubjectInfo[props.key].collectingDate"
              mask="####/##/##"
              color="deep-orange"
              :rules="[checkDate]"
              :disable="!editSubjectInfo[props.key].edit"
              dense
            >
              <template v-slot:append>
                <q-icon name="event" class="cursor-pointer">
                  <q-popup-proxy ref="qDateProxy" transition-show="jump-up" transition-hide="scale">
                    <q-date
                      v-model="editSubjectInfo[props.key].collectingDate"
                      @input="() => $refs.qDateProxy.hide()"
                      @update:model-value="(val) => editSubjectInfo = {index: props.key, col: 'collectingDate', update: val}"
                      mask="YYYY/MM/DD"
                      color="deep-orange"
                      minimal
                    ></q-date>
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
          </q-td>
        </template>

        <!-- 收樣日期欄位 -->
        <template v-slot:body-cell-receivedDate="props">
          <q-td style="min-width: 180px">
            <q-input
              filled
              v-model="editSubjectInfo[props.key].receivedDate"
              mask="####/##/##"
              color="deep-orange"
              :rules="[checkDate]"
              :disable="!editSubjectInfo[props.key].edit"
              dense
            >
              <template v-slot:append>
                <q-icon name="event" class="cursor-pointer">
                  <q-popup-proxy ref="qDateProxy" transition-show="jump-up" transition-hide="scale">
                    <q-date
                      v-model="editSubjectInfo[props.key].receivedDate"
                      @input="() => $refs.qDateProxy.hide()"
                      @update:model-value="(val) => editSubjectInfo = {index: props.key, col: 'receivedDate', update: val}"
                      mask="YYYY/MM/DD"
                      color="deep-orange"
                      minimal
                    ></q-date>
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
          </q-td>
        </template>

      </q-table>

    </q-card-section>
  </q-card>
</template>

<script setup>
// 導入模組
import { ref, computed, onMounted, watch } from "vue";
import { useStore } from "vuex";
import { useQuasar, date } from 'quasar';
import moment from "moment";
import ExcelJS from 'exceljs';

// 導入 composable
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';
import { getCurrentDisplayAnalysisID, getCurrentAnalysisResult } from '@/composables/checkAnalysisStatus.js';
import { upload_files_to_storage } from '@/composables/storageManager';
import { ParseSubjectInfo } from '@/firebase/firebaseFunction';

// 導入元件
import WarningDialog from '@/components/WarningDialog.vue';

// 取得 store 和 quasar
const store = useStore();
const $q = useQuasar();

// 使用者身份
const is_login = ref(false);
const user_info = ref(null);

// 模板檔案
const subjectFile = ref(null);
const selected = ref([]);
const subjectInfo = ref({});

// 表格內容
const columns = [
  {
    name: "sampleId",
    label: "Sample ID",
    align: "center",
    field: "sampleId",
  },
  {
    name: "well",
    label: "Well",
    align: "center",
    field: "well",
  },
  {
    name: "result",
    label: "Results",
    field: row => row.result,
    format: val => val,
    align: "center",
  },
  {
    name: "assessment",
    label: "Assessment",
    field: row => row.assessment,
    format: val => val,
    align: "center",
  },
  {
    name: "name",
    label: "Name",
    field: "name",
    align: "center",
  },
  {
    name: "birth",
    label: "Date of birth",
    field: "birth",
    align: "center",
  },
  {
    name: "gender",
    label: "Gender",
    field: "gender",
    align: "center",
  },
  {
    name: "idNumber",
    label: "ID number",
    field: "idNumber",
    align: "center",
  },
  {
    name: "type",
    label: "Subject type",
    field: "type",
    align: "center",
  },
  {
    name: "collectingDate",
    label: "Collection date",
    field: "collectingDate",
    align: "center",
  },
  {
    name: "receivedDate",
    label: "Received date",
    field: "receivedDate",
    align: "center",
  },
];
const visibleColumns = ref(columns);

// 當前 Export Results, Export Sample Info
const current_exportResults = ref([]);
const exportResults = computed(() => {
  return current_exportResults.value.map(row => ({
    index: row.index,
    sampleId: row.sampleId,
    well: row.well ? row.well : null,
    result: {
      label: row.assessment === 'invalid' || row.resultLabel === 'inconclusive'
        ? '-'
        : row.resultLabel,
      value: row.assessment === 'invalid' || row.resultLabel === 'inconclusive'
        ? '-'
        : row.result,
    },
    assessment: {
      label: row.assessmentLabel,
      value: row.assessment,
    }
  }));
});
const exportSampleInfo = computed({
  get: () => {
    return exportResults.value.map(result => {
      var subject = result.index in subjectInfo.value
        ? subjectInfo.value[result.index]
        : {
          name: "",
          birth: "",
          gender: "",
          idNumber: "",
          type: "",
          collectingDate: "",
          receivedDate: "",
          edit: selected.value.includes(result.index) ? false : true
        };
      return {
        index: result.index,
        sampleId: result.sampleId,
        well: result.well ? result.well : null,
        result: {
          label: result.result.label,
          value: result.result.value,
        },
        assessment: {
          label: result.assessment.label,
          value: result.assessment.value,
        },
        name: subject.name,
        birth: subject.birth,
        gender: subject.gender,
        idNumber: subject.idNumber,
        type: subject.type,
        collectingDate: subject.collectingDate,
        receivedDate: subject.receivedDate,
        edit: subject.edit
      }
    })
  }
});

// 保存當前分析結果
const currentAnalysisResult = ref(null);
const currentSettingProps = ref(null);
const currentDisplayAnalysis = ref({
  analysis_uuid: '',
  analysis_name: '',
});

const typeOptions = [
  { label: 'Blood', value: 'blood' },
  { label: 'Chorionic villi', value: 'chorionicVilli' },
  { label: 'Amniotic fluid', value: 'amnioticFluid' },
  { label: 'Cord blood', value: 'cordBlood' },
  { label: 'DBS', value: 'dbs' },
  { label: 'Buccal swab', value:'buccalSwab' },
  { label: 'FFPE', value:'ffpe' },
  { label: 'FFPE + Blood', value: 'ffpeBlood' },
  { label: 'RNA', value: 'rna' },
  { label: 'Others', value: 'others'},
];

// 控制 Thal column 顯示
const showThalColumn = ref(false);

/* Functions */

// 下載模板檔案
async function downloadTemplate() {
  try {
    // 使用 prompt 讓使用者輸入檔名
    let userFilename = prompt(
      "請輸入檔案名稱 (不需要副檔名):",
      moment(new Date()).format('YYYYMMDD') + '_subject_info'
    );

    // 如果使用者取消，則不下載
    if (userFilename === null) {
      return;
    }

    // 確保檔名不為空
    if (userFilename.trim() === '') {
      userFilename = moment(new Date()).format('YYYYMMDD') + '_subject_info';
    }

    // 添加副檔名
    const defaultFilename = userFilename.trim() + '.xlsx';

    // 準備要導出的數據
    const exportData = exportSampleInfo.value ?
      exportSampleInfo.value.map(row => ({
        'sampleId': row.sampleId,
        'name': row.name,
        'birth': row.birth,
        'gender': row.gender,
        'idNumber': row.idNumber,
        'type': row.type,
        'collectingDate': row.collectingDate,
        'receivedDate': row.receivedDate,
      })) : [];

    // 使用 ExcelJS 創建工作簿
    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet('Subject Info');

    // 定義標題行
    const headers = [
      'Sample ID',
      'Name',
      'Date of birth\n(YYYY/MM/DD)',
      'Gender\n(Female/Male/男/女)',
      'ID Number',
      'Type\n(Blood/Chorionic villi/Amniotic fluid/Cord blood/DBS/Buccal swab/FFPE/FFPE + Blood/RNA/Others)',
      'Collecting Date\n(YYYY/MM/DD)',
      'Received Date\n(YYYY/MM/DD)'
    ];

    // 添加標題行
    const headerRow = worksheet.addRow(headers);

    // 設定標題行樣式
    headerRow.eachCell((cell, colNumber) => {
      // 設定字體為 Arial、粗體和藍色
      cell.font = {
        name: 'Arial',
        bold: true,
        color: { argb: 'FF4774AA' }  // ARGB 格式，FF 是不透明度
      };

      // 設定對齊方式
      cell.alignment = {
        horizontal: 'center',
        vertical: 'middle',
        wrapText: true
      };

      // 設定背景色（可選）
      cell.fill = {
        type: 'pattern',
        pattern: 'solid',
        fgColor: { argb: 'FFF2F2F2' }  // 淺灰色背景
      };

      // 設定邊框（可選）
      cell.border = {
        top: { style: 'thin' },
        left: { style: 'thin' },
        bottom: { style: 'thin' },
        right: { style: 'thin' }
      };
    });

    // 設置列寬 - F 欄寬度設為 40，其他欄位 11
    worksheet.columns = [
      { width: 22 },  // A 欄 - Sample ID
      { width: 22 },  // B 欄 - Name
      { width: 22 },  // C 欄 - Date of birth
      { width: 22 },  // D 欄 - Gender
      { width: 22 },  // E 欄 - ID Number
      { width: 80 },  // F 欄 - Type (較寬以容納長文字)
      { width: 22 },  // G 欄 - Collecting Date
      { width: 22 }   // H 欄 - Received Date
    ];

    // 設定行高自動適應內容
    worksheet.properties.defaultRowHeight = 20; // 預設行高
    headerRow.height = 50; // 標題行高度設定較高以容納多行文字

    // 添加數據行
    if (exportData.length > 0) {
      exportData.forEach(row => {
        const dataRow = worksheet.addRow([
          row.sampleId,
          row.name,
          row.birth,
          row.gender,
          row.idNumber,
          row.type,
          row.collectingDate,
          row.receivedDate
        ]);

        // 設定數據行的樣式（可選）
        dataRow.eachCell((cell) => {
          // 設定字體為 Arial
          cell.font = {
            name: 'Arial'
          };

          cell.alignment = {
            horizontal: 'center',
            vertical: 'middle'
          };

          cell.border = {
            top: { style: 'thin' },
            left: { style: 'thin' },
            bottom: { style: 'thin' },
            right: { style: 'thin' }
          };
        });
      });
    }

    // 凍結頂部行（可選）
    worksheet.views = [
      { state: 'frozen', xSplit: 0, ySplit: 1, topLeftCell: 'A2', activeCell: 'A2' }
    ];

    // 生成並下載文件
    const buffer = await workbook.xlsx.writeBuffer();
    const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const url = URL.createObjectURL(blob);

    // 創建下載連結並觸發下載
    const a = document.createElement('a');
    a.href = url;
    a.download = defaultFilename;
    a.click();
    URL.revokeObjectURL(url);

    $q.notify(`模板已下載: ${defaultFilename}`);
  } catch (err) {
    console.error(err);
    $q.notify({
      type: 'negative',
      message: `模板下載失敗, 請重新嘗試!`,
    });
  }
}

// 更新 exportSampleInfo
function updateCurrentExportResults() {
  const currentResult = currentAnalysisResult.value.exportResult;
  current_exportResults.value = currentResult;
}

// 更新 selectedExport
const selectedExport = computed({
  get: () => store.getters["analysis_setting/getSelectedExport"],
  set: (val) => {
    store.commit("analysis_setting/updateSelectedExport", val);
    selected.value = val.map(selected => selected.index);
  }
});

// 更新 editSubjectInfo
const editSubjectInfo = computed({
  get: () => {
    let editSubjectInfo = {};
    exportSampleInfo.value.map(sample => {
      editSubjectInfo[sample.index] = {
        name: sample.name,
        birth: sample.birth,
        gender: sample.gender,
        idNumber: sample.idNumber,
        type: sample.type,
        collectingDate: sample.collectingDate,
        receivedDate: sample.receivedDate,
        edit: selected.value.includes(sample.index) ? false : true
      }
    });
    return editSubjectInfo;
  },
  set: (val) => {
    const defaultSubjectInfo = {
      name: "",
      birth: "",
      gender: "",
      idNumber: "",
      type: "",
      collectingDate: "",
      receivedDate: "",
      edit: selected.value.includes(val.index) ? false : true
    };
    if (!subjectInfo.value[val.index]) {
      subjectInfo.value[val.index] = defaultSubjectInfo;
    }
    subjectInfo.value[val.index][val.col] = val.update;
  }
});

// 控制警告視窗
const dialog_error_message = ref("");
const warning_dialog = ref(null);

// 更新 visibleColumns
const getVisibleColumns = (reagent) => {
  if (reagent === 'accuinMTHFR3') {
    return columns;
  } else {
    if (reagent && columns) {
      const selectedColumns = columns.filter(col => col.name !== 'well');
      visibleColumns.value = selectedColumns;
    }
  }
};

// 檢查日期格式
function checkDate(val) {
  return date.isValid(val) || 'Invalid date.';
}

// 評估欄位顏色
const assessmentColor = (value) => {
  if (
    (value === "low-risk") ||
    (value === "negative") ||
    (value === "normal") ||
    (value === "hd-normal")
  ) {
    return "text-green-8 text-weight-bold";
  } else if (
    (value === "intermediate") ||
    (value === "hd-intermediate")
  ) {
    return "text-grey-7 text-weight-bold";
  } else if (
    (value === "normal-risk") ||
    (value === "premutation") ||
    (value === "carrier") ||
    (value === "hd-penetrance")
  ) {
    return "text-yellow-8 text-weight-bold";
  } else if (
    (value === "high-risk") ||
    (value === "positive") ||
    (value === "full") ||
    (value === "full-penetrance") ||
    (value === "affected") ||
    (value === "hd-full") ||
    (value === "alpha") ||
    (value === "beta") ||
    (value === "alphabeta") ||
    (value === "affected")
  ) {
    return "text-red-8 text-weight-bold";
  } else {
    return "text-grey-10 text-weight-bold";
  }
};

// 選擇後上傳檔案
async function uploadFile(files) {

  // 如果沒有檔案, 則返回
  if (!files) return;

  // 顯示 loading 視窗
  $q.loading.show();

  // 存到當前使用者
  const user_uid = user_info.value.uid;

  // 存到 data 資料夾
  const analysis_uuid = currentDisplayAnalysis.value.analysis_uuid;
  const category = 'subject_info';

  // 上傳檔案
  const uploading = await Promise.all(files.map(async (file) => {
    return await upload_files_to_storage(
      file, user_uid, category, analysis_uuid
    ).then((response) => {return response;});
  }));

  // 初始化 error message
  dialog_error_message.value = "";

  // 檢查是否有 error
  if (uploading.some(res => res.status === 'error')) {

    // 找出 error 的檔案
    const error_file = uploading.filter(res => res.status === 'error');

    // 印出 error 的檔案
    const error_message = error_file.map(res => res.message).join(', \n');

    // 設定 dialog_error_message, 跳出警告視窗
    dialog_error_message.value = error_message;
    warning_dialog.value.open_warning_dialog();

    // 印出 error message
    const message = error_message;
    const source = 'ReportPreview.vue line.753';
    const user = user_info.value.email;
    loggerV2.error(message, source, user);
  }

  // 更新 files 中 file 的 path
  else {
    files.forEach((file) => {
      file.path = uploading.find((res) => res.file === file.name).storage_path;
    });
  }

  // 隱藏 loading 視窗
  $q.loading.hide();
}

// 上傳並解析 subject Info
async function uploadAndParseSubjectInfo(file) {

  let subject_info = [];

  // 如果沒有檔案, 則返回
  if (!file) return;

  // 顯示 loading 視窗
  $q.loading.show();

  // 上傳檔案
  await uploadFile([file]);

  // 解析檔案
  const input = {file_path: subjectFile.value.path};
  const parsedResult = await ParseSubjectInfo(input);

  // 初始化 warning_dialog
  dialog_error_message.value = '';

  // 如果解析結果是 success, 則更新 subject Info
  if (parsedResult.data.status === 'success') {
    subject_info = parsedResult.data.result;
  }
  else if (parsedResult.data.status === 'error') {
    dialog_error_message.value = parsedResult.data.message;
    warning_dialog.value.open_warning_dialog();
  }

  // 隱藏 loading 視窗
  $q.loading.hide();

  return subject_info;
}

/* 掛載時 */
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
    return;
  }

  // 更新 Export Results
  updateCurrentExportResults();

  // 更新 visibleColumns
  const used_analysis_name = currentAnalysisResult.value.analysis_name;
  const used_reagent = used_analysis_name !== 'SMA' ? currentAnalysisResult.value.config.reagent : currentAnalysisResult.value.config.V1.reagent;
  getVisibleColumns(used_analysis_name, used_reagent);

  // 取得 current_Selected_index
  const current_Selected_index = selectedExport.value.map(selected => selected.index);
  const current_Selected_export = exportSampleInfo.value.filter(selected => current_Selected_index.includes(selected.index));
  store.commit("analysis_setting/updateSelectedExport", current_Selected_export);
});

// 監聽 subjectFile
watch(subjectFile, async (newVal, oldVal) => {
  // 如果 newVal 和 oldVal 不同, 則上傳檔案
  if (newVal && newVal !== oldVal) {
    subjectInfo.value = await uploadAndParseSubjectInfo(newVal);

    // 清空 selectedExport
    selectedExport.value = [];
  }
});

</script>
