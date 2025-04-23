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
import { Consequence } from '@/composables/useInterpretClinvar.js';
import ExcelJS from 'exceljs';
import { uploadFileToStorage } from '@/firebase/firebaseStorage';

// 產品列表
const productList = ['APOE_AD', 'FXSv1', 'FXSv2', 'HTD', 'MTHFR_c677', 'MTHFR_c677_c1298', 'NUDT15', 'SMA', 'SMAv4', 'THAL_ALPHA', 'THAL_BETA'];

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

// 取得分析產品名稱
const getAnalysisProductName = (analysis_name) => {
  switch (analysis_name) {
    case 'APOE':
      return 'apoe-import';
    case 'MTHFR':
      return 'mthfr-import';
    case 'NUDT15':
      return 'nudt15';
    case 'FXS':
      return 'fx';
    case 'HTD':
      return 'hd';
    case 'SMA':
      return 'sma';
    case 'THAL_BETA':
      return 'thal-import-beta';
    default:
      return null;
  }
}


// 取得產品匯出資訊
const getProductExportInfo = (product, reagent) => {
  let exportSample;
  let productExport;

  const inputData = store.getters["export_page_setting/getExportResults"];

  switch (product) {
    case 'thal-import-beta':
      exportSample = parseExportData.exportThalBetaProps(currentAnalysisResult.value, selectedExport.value);
      productExport = 'THAL_BETA';
      break;
    case 'fx':
      exportSample = parseExportData.exportFxProps(currentAnalysisResult.value, selectedExport.value);
      productExport = reagent === 'accuinFx1' ? 'FXSv1' : 'FXSv2';
      break;
    case 'hd':
      exportSample = parseExportData.exportHdProps(currentAnalysisResult.value, selectedExport.value);
      productExport = 'HTD';
      break;
    case 'apoe':
      exportSample = parseInputExport.exportApoeProps(inputData);
      productExport = 'APOE_AD';
      break;
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
      if (reagent === 'accuinMTHFR1' || reagent === 'accuinMTHFR3') {
        exportSample = parseInputExport.exportMthfrv1Props(inputData);
        productExport = 'MTHFR_c677';
      } else if (reagent === 'accuinMTHFR2') {
        exportSample = parseInputExport.exportMthfrv2Props(inputData);
        productExport = 'MTHFR_c677_c1298';
      }
      break;
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
      exportSample = parseInputExport.exportCdProps(inputData);
      productExport = 'DQ2_DQ8';
      break;
    case 'alcohol':
      exportSample = parseInputExport.exportAlcoholProps(inputData);
      productExport = 'ADH1B_ALDH2';
      break;
    case 'cvd':
      exportSample = parseInputExport.exportCvdProps(inputData);
      productExport = 'APOE_CVD';
      break;
    case 'b27':
      exportSample = parseInputExport.exportB27Props(inputData);
      productExport = 'B27';
      break;
    case 'cyp1a2':
      exportSample = parseInputExport.exportCyp1a2Props(inputData);
      productExport = 'CYP';
      break;
    case 'notch3':
      exportSample = parseInputExport.exportNotch3Props(inputData);
      productExport = 'NOTCH3';
      break;
    case 'f2f5':
      exportSample = parseInputExport.exportF2f5Props(inputData);
      productExport = 'F2_F5';
      break;
    case 'pd':
      exportSample = parseInputExport.exportPdProps(inputData);
      productExport = 'LRRK2_GBA';
      break;
    case 'lct':
      exportSample = parseInputExport.exportLctProps(inputData);
      productExport = 'LCT';
      break;
    case 'hfe':
      exportSample = parseInputExport.exportHfeProps(inputData);
      productExport = 'HFE';
      break;
    case 'thal':
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
async function runExportJSON(exportObj) {
  try {
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

    // 上傳到 Firebase Storage (如果 product 在 productList 中)
    if (productList.includes(exportObj.product.name)) {
      const file = new File([blob], `${exportObj.result.testing.sample.id}_${exportObj.product.name}.json`, { type: 'application/json' });
      const upload_path = `${user_info.value.uid}/${convertStorageFolderName(exportObj.product.name)}/${currentAnalysisResult.value.analysis_id}/${exportObj.result.testing.sample.id}_${exportObj.product.name}.json`;
      const uploadResult = await uploadFileToStorage(file, upload_path);
      if (uploadResult.status === 'error') {
        console.error('Failed to upload file to Firebase Storage:', uploadResult.message);
        $q.notify({
          type: 'negative',
          message: `Failed to upload file to Firebase Storage: ${uploadResult.message}`,
        });
      }
    }

    return Promise.resolve({ isExported: true });
  } catch (err) {
    console.error(err);
    return Promise.reject({ isExported: false });
  }
}

// 解析 ThalBeta 的 row_content
const parsedThalBetaRow = (row_content) => {
  if (!row_content) return "";
  const seperator = '___SEP_ANNO___';
  if (row_content && row_content.includes(seperator)) {
    const split_content = row_content.split(seperator);
    return split_content.map((content, index) => `${index + 1}. ${content.trim()}`).join('\n');
  }
  return row_content;
};

// 加入 beta thal 的表格
const addBetaThalTables = (workbook, result, index) => {

  // 取得 thalbetaHeader 和 resultData
  const thalbetaHeader = [ 'Genomic Position', 'Ref', 'Alt', 'Variant Class', 'Genotype', 'Clinical Significance', 'Variant Type', 'Variant Name', 'Disease' ];
  const resultData = result.resultTable;

  // 為每個結果創建新的工作表，使用索引來區分
  const worksheet = workbook.addWorksheet(`${result.sample_name}`);

  // 加入結果表格
  const thalbetaHeaderRow = worksheet.addRow(thalbetaHeader);
  const writeThalbetaResultRow = resultData.rows.map(row => [
    `${row.adjusted_position.chr}:${row.adjusted_position.start}-${row.adjusted_position.end}`,
    row.ref,
    row.alt,
    row.type,
    row.genotype,
    parsedThalBetaRow(row.ClinicalSignificance),
    Consequence[row.Consequence] ? parsedThalBetaRow(Consequence[row.Consequence].label) : row.Consequence,
    parsedThalBetaRow(row.Name),
    parsedThalBetaRow(row.PhenotypeList),
  ]);

  // 寫入結果表格
  const thalbetaResultRow = worksheet.addRows(writeThalbetaResultRow);
  worksheet.addRow();

  // 設定結果表格樣式
  thalbetaHeaderRow.eachCell((cell, colNumber) => {
    cell.font = {
      name: 'Calibri',
      bold: true,
      size: 11,
      color: { argb: '4774AA' }
    };
    cell.alignment = {
      horizontal: 'center',
      vertical: 'middle',
      wrapText: false
    };
  });

  // 設定結果表格樣式
  thalbetaResultRow.forEach(row => {
    row.eachCell((cell, colNumber) => {
      cell.font = {
        name: 'Calibri',
      };
      cell.alignment = {
        horizontal: 'center',
        vertical: 'middle',
        wrapText: false
      };
      if (colNumber === 9) {
        cell.alignment = {
          horizontal: 'left',
          vertical: 'middle',
          wrapText: false
        };
      }
    });
  });

  // 設定欄寬
  worksheet.columns = [
    { width: 28 },  // A 欄 - Genomic Position
    { width: 8 },   // B 欄 - Ref
    { width: 8 },   // C 欄 - Alt
    { width: 20 },  // D 欄 - Variant Class
    { width: 20 },  // E 欄 - Genotype
    { width: 25 },  // F 欄 - Clinical Significance
    { width: 20 },  // G 欄 - Variant Type
    { width: 50 },  // H 欄 - Variant Name
    { width: 30 },  // I 欄 - Disease
  ];
};

// 轉換firebase storage 存檔資料夾名稱
const convertStorageFolderName = (product) => {
  switch (product) {
    case 'APOE_AD':
      return 'APOE_results';
    case 'FXSv1':
      return 'FXS_results';
    case 'FXSv2':
      return 'FXS_results';
    case 'HTD':
      return 'HTD_results';
    case 'MTHFR_c677':
      return 'MTHFR_results';
    case 'MTHFR_c677_c1298':
      return 'MTHFR_results';
    case 'NUDT15':
      return 'NUDT15_results';
    case 'SMA':
      return 'SMA_results';
    case 'SMAv4':
      return 'SMAv4_results';
    case 'THAL_ALPHA':
      return 'THAL_ALPHA_results';
    case 'THAL_BETA':
      return 'THAL_BETA_results';
  }
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

    // 如果 product 是 THAL_BETA 則寫入 THAL_BETA 表格
    if (product === 'THAL_BETA') {
      const all_results = currentAnalysisResult.value.resultObj;
      all_results.forEach((result, index) => {
        addBetaThalTables(workbook, result, index);
      });
    }

    // 加入結果表格
    const headerRow = worksheet.addRow(headers);
    const writeSampleRows = worksheet.addRows(writeSample);

    // 設定欄寬
    worksheet.columns = [
      { width: 50 },  // A 欄 - Sample ID
      { width: 20 },  // B 欄 - Results
      { width: 20 },  // C 欄 - Assessment
      { width: 20 },  // D 欄 - QC
      { width: 20 },  // E 欄 - Name
      { width: 20 },  // F 欄 - Date of birth
      { width: 20 },  // G 欄 - Gender
      { width: 20 },  // H 欄 - ID Number
      { width: 20 },  // I 欄 - Type
      { width: 20 },  // J 欄 - Collecting Date
      { width: 20 },  // K 欄 - Received Date
      { width: 20 },  // L 欄 - Laboratory
      { width: 20 },  // M 欄 - Contact
      { width: 20 },  // N 欄 - Authorized by
      { width: 20 },  // O 欄 - Reporting Date
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

    // 產生 Excel 檔案的 buffer
    const buffer = await workbook.xlsx.writeBuffer();
    const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });

    // 下載 Excel 檔案
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = exportFilename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    // 上傳到 Firebase Storage (如果 product 在 productList 中)
    if (productList.includes(product)) {
      const file = new File([blob], exportFilename, { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const upload_path = `${user_info.value.uid}/${convertStorageFolderName(product)}/${currentAnalysisResult.value.analysis_id}/${exportFilename}`;
      const uploadResult = await uploadFileToStorage(file, upload_path);

      if (uploadResult.status === 'error') {
        console.error('Failed to upload file to Firebase Storage:', uploadResult.message);
        $q.notify({
          type: 'negative',
          message: `Failed to upload file to Firebase Storage: ${uploadResult.message}`,
        });
      }
    }

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
        currentAnalysisResult.value && currentSettingProps.value.instrument !== ""  && currentSettingProps.value.reagent !== "" ? getAnalysisProductName(currentAnalysisResult.value.analysis_name) : currentSettingProps.value.product,
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
              qc: s.assessment.value === 'inconclusive' || s.assessment.value === 'QC Failed' ? 'Fail' : 'Pass',
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
            instrument: currentSettingProps.value.instrument !== "" &&
              currentSettingProps.value.reagent !== "" ?
              (currentAnalysisResult.value ?
                currentAnalysisResult.value.config.instrument :
                'N/A'
              ) : 'NA',
            analyzer: ["ACCUiN BioTech Analyzer"],
            reagent: currentSettingProps.value.instrument !== "" &&
              currentSettingProps.value.reagent !== "" ?
              (currentAnalysisResult.value ?
                currentAnalysisResult.value.config.reagent :
                'N/A'
              ) : 'NA',
            assessmentTime: currentSettingProps.value.instrument !== "" &&
              currentSettingProps.value.reagent !== "" ?
              (currentAnalysisResult.value ?
                currentAnalysisResult.value.analysis_time :
                'N/A'
              ) : 'NA',
            controlId: currentSettingProps.value.instrument !== "" &&
              currentSettingProps.value.reagent !== "" ?
              (currentAnalysisResult.value ?
                Array.isArray(currentAnalysisResult.value.control_ids) ?
                  currentAnalysisResult.value.control_ids.join(', ') :
                  currentAnalysisResult.value.control_ids :
                'N/A'
              ) : 'NA',
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
