<template>
  <q-card bordered>
    <q-card-section>
      <div class="text-h5 text-uppercase text-bold text-blue-grey-7">
        Lab Information
      </div>
      <q-form @submit="onExport">
        <div class="row justify-evenly q-gutter-xl">
          <q-input
            v-model="subjectOrder.labName"
            class="col"
            label="Laboratory"
            color="deep-orange"
          />
          <q-input
            v-model="subjectOrder.issuedPhysician"
            class="col"
            label="Authorized by"
            color="deep-orange"
          />
          <q-input
            v-model="subjectOrder.issuedContact"
            class="col"
            label="Contact"
            color="deep-orange"
          />
          <q-select
            v-model="exportOption"
            :options="exportOptions"
            label="Export Format"
            class="col"
            color="deep-orange"
            label-color="deep-orange"
            behavior="menu"
            :rules="[(val) => val || `Please select export format.`]"
            lazy-rules
            map-options
            outlined
          />
        </div>
        <div class="row justify-end">
          <q-btn
            label="Export"
            type="submit"
            color="blue-grey-7"
            size="lg"
          />
        </div>
      </q-form>
    </q-card-section>
  </q-card>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useStore } from "vuex";
import { useQuasar, QSpinnerDots } from "quasar";
import moment from "moment";
import { getCurrentDisplayAnalysisID, getCurrentAnalysisResult } from '@/composables/checkAnalysisStatus.js';
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';
import parseExportData from '@/composables/parseExportData.js';
import parseInputExport from '@/composables/parseInputExport.js';
import ExcelJS from 'exceljs';

// 使用者身份
const is_login = ref(false);
const user_info = ref(null);

// 取得 store 和 quasar
const $q = useQuasar();
const store = useStore();

// 選取樣本
const selectedSample = computed(() => store.getters["export_page_setting/getSelectedExport"]);

// 匯出格式
const exportOption = ref(null);
const subjectOrder = ref({
  labName: "",
  issuedContact: "",
  issuedPhysician: "",
});

// 保存當前分析結果
const currentAnalysisResult = ref(null);
const currentSettingProps = ref(null);
const currentDisplayAnalysis = ref({
  analysis_uuid: '',
  analysis_name: '',
});

// 更新 selectedExport
const selectedExport = computed({ get: () => store.getters["export_page_setting/getSelectedExport"] });

// 下拉式選單選項
const exportOptions = [
  // { label: 'PDF - 中文', value: 'pdf_zhTW'},
  // { label: 'PDF - English', value: 'pdf_enUS'},
  // { label: 'JSON - English', value: 'json_enUS'},
  // { label: 'JSON - 中文', value: 'json_zhTW'},
  { label: 'JSON', value: 'json_enUS' },
  { label: 'Excel', value: 'xlsx_enUS'},
];

// 取得產品匯出資訊
const getProductExportInfo = (product, reagent) => {
  let exportSample;
  let productExport;

  switch (product) {
    case 'fx':
      exportSample = parseExportData.exportFxProps(currentAnalysisResult.value, selectedExport.value);
      productExport = reagent === 'accuinFx1' ? 'FXSv1' : 'FXSv2';
      break;
    case 'hd':
      exportSample = parseExportData.exportHdProps(currentAnalysisResult.value, selectedExport.value);
      productExport = 'HTD';
      break;
    case 'apoe':
    case 'apoe-import':
      exportSample = parseExportData.exportApoeProps(currentAnalysisResult.value, selectedExport.value);
      productExport = 'APOE_AD';
      break;
    case 'sma':
      if (reagent === 'accuinSma4') {
        exportSample = parseExportData.exportSmaV4Props(currentAnalysisResult.value, selectedExport.value);
        productExport = 'SMAv4';
      } else {
        exportSample = parseExportData.exportSmaProps(currentAnalysisResult.value, selectedExport.value);
        productExport = 'SMA';
      }
      break;
    case 'nudt15':
      exportSample = parseExportData.exportNudt15Props(currentAnalysisResult.value, selectedExport.value);
      productExport = 'NUDT15';
      break;
    case 'mthfr-input':
    case 'mthfr-import':
      if (reagent === 'accuinMTHFR1' || reagent === 'accuinMTHFR3') {
        exportSample = parseExportData.exportMthfrv1Props(currentAnalysisResult.value, selectedExport.value);
        productExport = 'MTHFR_c677';
      } else if (reagent === 'accuinMTHFR2') {
        exportSample = parseExportData.exportMthfrv2Props(currentAnalysisResult.value, selectedExport.value);
        productExport = 'MTHFR_c677_c1298';
      }
      break;
    case 'cd':
      exportSample = [];
      productExport = 'DQ2_DQ8';
      break;
    case 'alcohol':
      exportSample =  [];
      productExport = 'ADH1B_ALDH2';
      break;
    case 'cvd':
      exportSample = [];
      productExport = 'APOE_CVD';
      break;
    case 'b27':
      exportSample = [];
      productExport = 'B27';
      break;
    case 'cyp1a2':
      exportSample = [];
      productExport = 'CYP';
      break;
    case 'notch3':
      exportSample = [];
      productExport = 'NOTCH3';
      break;
    case 'f2f5':
      exportSample = [];
      productExport = 'F2_F5';
      break;
    case 'pd':
      exportSample = [];
      productExport = 'LRRK2_GBA';
      break;
    case 'lct':
      exportSample = [];
      productExport = 'LCT';
      break;
    case 'hfe':
      exportSample = [];
      productExport = 'HFE';
      break;
    case 'thal':
      let inputData = store.getters["export_page_setting/getExportResults"];
      exportSample = parseInputExport.exportThalProps(inputData);
      productExport = 'THAL';
      break;
    default:
      exportSample = [];
      productExport = 'Unknown';
      break;
  }

  return {
    exportSample,
    productExport
  };
};

// 修改 runExportJSON 函數以直接下載 JSON 檔案
function runExportJSON(exportObj) {
  const jsonData = JSON.stringify(exportObj);
  const blob = new Blob([jsonData], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${exportObj.result.testing.sample.id}_${exportObj.product.name}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  return Promise.resolve({ isExported: true });
}

// 修改 downloadReportFile 函數以使用 ExcelJS
async function downloadReportFile(data) {
  const savePath = data[0];
  const sampleLst = data[1];
  const info = data[2];
  const product = data[2].product;
  const exportFilename = savePath.split('/').pop();

  const v = data[2].softwareVersion;
  const nucleusV = data[2].analysisPackage;
  const currentDate = moment();

  const writeInfo = [
    `ACCUiNspection software version: ${v}`,
    `Analysis package: ${nucleusV}`,
    `Product: ${info.product}`,
    `Instrument: ${info.instrument}`,
    `Reagent: ${info.reagent}`,
    `Ananlyzer: ${info.analyzer.join(', ')}`,
    `Control ID: ${info.controlId}`,
    `Laboratory: ${info.labName}`,
    `Contact: ${info.issuedContact}`,
    `Authorized by: ${info.issuedPhysician}`,
    `Analyzed on: ${info.assessmentTime}`,
    `Exported on: ${currentDate.format("YYYY-MM-DD HH:mm:ss")}`,
  ].map(info => [info]);

  const genderOutput = {
    female: 'Female',
    male: 'Male',
  };
  const typeOutput = {
    'blood': 'Blood',
    'chorionicVilli': 'Chorionic villi',
    'amnioticFluid': 'Amniotic fluid',
    'cordBlood': 'Cord blood',
    'dbs': 'DBS',
    'others': 'Others',
    'buccalSwab': 'Buccal swab',
    'ffpe': 'FFPE',
    'ffpeBlood': 'FFPE + Blood',
    'rna': 'RNA',
  };
  const headers = product === 'MTHFR_c677'
    ? [ 'Sample ID', 'Well Position', 'Results', 'Assessment', 'QC', 'Name', 'Date of birth', 'Gender', 'ID Number', 'Type', 'Collecting Date', 'Received Date', 'Laboratory', 'Contact', 'Authorized by', 'Reporting Date' ]
    : [ 'Sample ID', 'Results', 'Assessment', 'QC', 'Name', 'Date of birth', 'Gender', 'ID Number', 'Type', 'Collecting Date', 'Received Date', 'Laboratory', 'Contact', 'Authorized by', 'Reporting Date' ];

  try {
    const writeSample = product === 'MTHFR_c677'
      ? sampleLst.map(row => [
        row.sampleId,
        row.well,
        row.results,
        row.assessment,
        row.qc,
        row.name,
        row.birth,
        genderOutput[row.gender] ? genderOutput[row.gender] : "",
        row.idNumber,
        typeOutput[row.type] ? typeOutput[row.type] : "",
        row.collectingDate,
        row.receivedDate,
        info.labName,
        info.issuedContact,
        info.issuedPhysician,
        row.reportingDate,
      ])
      : sampleLst.map(row => [
        row.sampleId,
        row.results,
        row.assessment,
        row.qc,
        row.name,
        row.birth,
        genderOutput[row.gender] ? genderOutput[row.gender] : "",
        row.idNumber,
        typeOutput[row.type] ? typeOutput[row.type] : "",
        row.collectingDate,
        row.receivedDate,
        info.labName,
        info.issuedContact,
        info.issuedPhysician,
        row.reportingDate,
      ]);

    // 使用 ExcelJS 生成 Excel 檔案
    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet(exportFilename.replace('.xlsx', ''));

    // 新增資料行
    const addInfoRow = worksheet.addRows(writeInfo);
    worksheet.addRow();
    const headerRow = worksheet.addRow(headers);
    const writeSampleRows = worksheet.addRows(writeSample);

    // 設定欄寬
    worksheet.columns = [
      { width: 50 },  // A 欄 - Sample ID
      { width: 16 },  // B 欄 - Results
      { width: 16 },  // C 欄 - Assessment
      { width: 16 },  // D 欄 - QC
      { width: 16 },  // E 欄 - Name
      { width: 16 },  // F 欄 - Date of birth
      { width: 16 },  // G 欄 - Gender
      { width: 16 },  // H 欄 - ID Number
      { width: 16 },  // I 欄 - Type
      { width: 16 },  // J 欄 - Collecting Date
      { width: 16 },  // K 欄 - Received Date
      { width: 16 },  // L 欄 - Laboratory
      { width: 16 },  // M 欄 - Contact
      { width: 16 },  // N 欄 - Authorized by
      { width: 16 },  // O 欄 - Reporting Date
    ];

    // 設定 addInfoRow 樣式
    addInfoRow.forEach((row) => {
      row.eachCell((cell, colNumber) => {
        cell.font = {
          name: 'Calibri',
          color: { argb: '4774AA' } // 設定字體顏色
        };
      });
    });

    // 設定字體樣式
    headerRow.eachCell((cell, colNumber) => {
      cell.font = {
        name: 'Calibri',
        bold: true,
        color: { argb: '4774AA' } // 設定字體顏色
      };
      cell.alignment = {
        horizontal: 'center',
        vertical: 'middle',
        wrapText: false
      };
    });

    // 表格內容設定樣式
    writeSampleRows.forEach((row) => {
      row.eachCell((cell, colNumber) => {
        if (colNumber === 1) {
          cell.font = {
            name: 'Calibri',
            bold: true,
          };
        }
        else {
          cell.font = {
            name: 'Calibri',
          };
        }
        cell.alignment = {
          horizontal: 'center',
          vertical: 'middle',
          wrapText: false
        };
      });
    });

    // 下載 Excel 檔案
    const buffer = await workbook.xlsx.writeBuffer();
    const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = exportFilename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    return Promise.resolve(savePath);
  } catch (err) {
    console.error(err);
    return Promise.reject(savePath);
  }
}

// Export
const onExport = async () => {

  if (selectedSample.value.length > 0) {
    $q.loading.show({
      spinner: QSpinnerDots,
      message: `Exporting report...`,
      messageColor: 'white',
      spinnerColor: 'deep-orange-6',
    });

    const lang = exportOption.value.value.split('_')[1];
    const format = exportOption.value.value.split('_')[0];

    // 備份 selectedSample
    let selectedSample_backup = JSON.parse(JSON.stringify(selectedSample.value));

    // 特殊處理 Thal 的 export
    if (currentSettingProps.value.product === 'thal') {
      selectedSample_backup.forEach(sample => {
        const alpha_result_label = `Alpha: ${sample.result.label.alpha.type.join('/')}`;
        const beta_result_label = `Beta: ${sample.result.label.beta.type.join(';')}`;
        sample.result.label = [alpha_result_label, beta_result_label];
      });
    }

    try {
      const { exportSample, productExport } = getProductExportInfo(
        currentSettingProps.value.product,
        currentSettingProps.value.reagent,
      );

      if (format === 'json') {
        const reportAll = exportSample.length;

        $q.loading.show({
          spinner: QSpinnerDots,
          message: `Exporting report... 0 / ${reportAll}`,
          messageColor: 'white',
          spinnerColor: 'deep-orange-6',
        });

        for (let [idx, s] of exportSample.entries()) {
          const exportObj = {
            version: "v3",
            product: {
              name: productExport
            },
            format: {
              lang: lang,
              client: "ACCUIN"
            },
            export: {
              path: '', // 不再需要路徑
            },
            info: {
              laboratory: {
                lab: subjectOrder.value.labName,
                collectionDate: s.collectingDate,
                receivingDate: s.receivedDate,
                reportingDate: moment().format("YYYY/MM/DD"),
              },
              subject: s.subject,
              order: {
                name: subjectOrder.value.issuedPhysician,
                contact: subjectOrder.value.issuedContact
              }
            },
            result: s.result
          };

          const res = await runExportJSON(exportObj);

          if (res.isExported) {
            $q.loading.show({
              spinner: QSpinnerDots,
              message: `Exporting report... ${idx+1} / ${reportAll}`,
              messageColor: 'white',
              spinnerColor: 'deep-orange-6',
            });
            $q.notify(`Sample: ${exportObj.result.testing.sample.id} is exported`);
          } else {
            $q.notify(`Sample: ${exportObj.result.testing.sample.id} is failed to export`);
          }
        }
      } else if (format === 'xlsx') {
        const defaultFilename = productExport + '_' + moment(new Date()).format('YYYYMMDD') + '.xlsx';

        $q.loading.show({
          spinner: QSpinnerDots,
          message: `Exporting results to Excel...`,
          messageColor: 'white',
          spinnerColor: 'deep-orange-6',
        });

        const usedSelectedSample = currentSettingProps.value.product === 'thal' ? selectedSample_backup : selectedSample.value;

        const saveExcel = await downloadReportFile([
          defaultFilename,
          usedSelectedSample.map((s) => {
            return {
              sampleId: s.sampleId,
              well: s.well ? s.well : '-',
              results: s.assessment.value === 'invalid' || s.assessment.value === 'inconclusive'
                ? '-'
                : currentSettingProps.value.product === 'thal' ? s.result.label.join(' ; ')
                : s.result.label.join(' / '),
              assessment: s.assessment.label,
              qc: s.assessment.value === 'inconclusive' ? 'Fail' : 'Pass',
              name: s.name,
              birth: s.birth,
              gender: s.gender,
              idNumber: s.idNumber,
              type: s.type,
              receivedDate: s.receivedDate,
              collectingDate: s.collectingDate,
              reportingDate: moment().format("YYYY/MM/DD"),
            }
          }),
          {
            product: productExport,
            instrument: currentAnalysisResult.value.config.instrument,
            analyzer: [ "ACCUiN BioTech Analyzer" ],
            reagent: currentAnalysisResult.value.config.reagent,
            assessmentTime: currentAnalysisResult.value.analysis_time,
            controlId: Array.isArray(currentAnalysisResult.value.control_ids)
              ? currentAnalysisResult.value.control_ids.join(', ')
              : currentAnalysisResult.value.control_ids,
            labName: subjectOrder.value.labName,
            issuedPhysician: subjectOrder.value.issuedPhysician,
            issuedContact: subjectOrder.value.issuedContact,
            softwareVersion: process.env.VUE_APP_SOFTWARE_VERSION,
            analysisPackage: process.env.VUE_APP_ANALYSIS_PACKAGE,
          },
        ]);

        $q.notify(`${saveExcel} is exported`);
      } else {
        $q.notify({
          type: 'warning',
          message: "目前不支援 JSON 和 Excel 外其他格式.",
        });
      }
    } catch (err) {
      console.error(err);
      $q.loading.hide();
      $q.notify({
        type: 'negative',
        message: `Failed to export reports. Error: ${err}`,
      });
    } finally {
      setTimeout(() => {
        $q.loading.hide();
      }, 300);
    }
  } else {
    $q.notify({
      type: 'negative',
      message: `Please select at least ONE sample to export.`,
    });
  }
};

// 掛載時
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

  // 載入 LAB information
  const labInfo = store.getters["export_page_setting/getLabInfomation"];
  subjectOrder.value.labName = labInfo.laboratory;
  subjectOrder.value.issuedPhysician = labInfo.authorized;
  subjectOrder.value.issuedContact = labInfo.contact;

  // 載入 exportOption
  const storeExportOption = store.getters["export_page_setting/getExportOption"];
  exportOption.value = storeExportOption;
})

// 監聽 subjectOrder
watch(subjectOrder, (newVal) => {
  store.commit("export_page_setting/updateLabInfomation", {
    laboratory: newVal.labName,
    authorized: newVal.issuedPhysician,
    contact: newVal.issuedContact,
  });
}, { deep: true });

// 監聽 exportOption
watch(exportOption, (newVal) => {
  store.commit("export_page_setting/updateExportOption", {
    label: newVal.label,
    value: newVal.value,
  });
});

</script>
