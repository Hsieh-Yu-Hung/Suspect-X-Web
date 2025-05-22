<template>
  <q-card bordered :style="{ 'min-height': '100%' }">

    <!-- 警告視窗 -->
    <WarningDialog
      ref="warning_dialog"
      :error_message="dialog_error_message"
    />

    <!-- 標題 -->
    <q-card-section>
      <div class="text-h5 text-uppercase text-bold text-blue-grey-7">
        Import
      </div>
      <div class="text-subtitle1">
        Please select the corresponding standard well positions and sample result.
      </div>
    </q-card-section>

    <!-- 輸入面板 -->
    <q-card-section>
      <q-form @submit="onSubmit">

        <!-- qPCRImportSection -->
        <qPCRImportSection
          @update_dialog_error_message="updateDialogErrorMessage"
          @update_result_files="updateFiles"
          @update_wells="updateWells"
          ref="ref_qPCRImportSection" />

        <!-- 送出按鈕 -->
        <div class="row q-mt-lg justify-end">
          <q-btn label="Analyze" type="submit" color="blue-grey-7" />
        </div>

      </q-form>
    </q-card-section>

  </q-card>
</template>

<script setup>
// 導入模組
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar, QSpinnerFacebook } from 'quasar';
import { v4 as uuidv4 } from 'uuid';
import { useStore } from 'vuex';

// 導入 composable
import { setAnalysisID } from '@/composables/checkAnalysisStatus';
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';
import { submitWorkflow } from '@/composables/submitWorkflow';
import { ANALYSIS_RESULT, EXPORT_RESULT, update_userAnalysisData } from '@/firebase/firebaseDatabase';
import getTestingData from '@/composables/useGetTestingData';

// 元件
import WarningDialog from '@/components/WarningDialog.vue';
import qPCRImportSection from '@/components/ImportqPCRViews/qPCRImportSection.vue';

// Database Path
const dbMTHFRResultPath = "mthfr_result";
const dbNUDT15ResultPath = "nudt15_result";
// 取得 Quasar 和 store
const $q = useQuasar();
const store = useStore();
const router = useRouter();

// 使用者身份
const is_login = ref(false);
const user_info = ref(null);

// 控制警告視窗
const dialog_error_message = ref("");
const warning_dialog = ref(null);

// 當前的分析 ID
const currentAnalysisID = ref(null);

// 控制 qPCRImportSection
const ref_qPCRImportSection = ref(null);

// 取得 qPCRImportSection 的 resultFile, famFile, vicFile, Ctrlwell, NTCwell
const resultFile = ref(null);
const famFile = ref(null);
const vicFile = ref(null);
const Ctrlwell = ref(null);
const NTCwell = ref(null);

// props
const props = defineProps({
  analysis_name: {
    type: String,
    required: true,
  },
});

// MTHFR 評估結果
const mthfrAssessment = (value) => {
  if (value === 'low-risk') {
    return "Low risk";
  } else if (value === 'normal-risk') {
    return "Normal risk";
  } else if (value === 'high-risk') {
    return "High risk";
  } else if (value === 'inconclusive') {
    return "Inconclusive";
  } else {
    return "Invalid";
  }
};

const mthfrParseResult = (reagent, result) => {
  if (reagent == "accuinMTHFR2") {
    return [`c.677 [${result[0]}/${result[1]}]`, `c.1298 [${result[2]}/${result[3]}]`]
  }
  else {
    return [`c.677 [${result[0]}/${result[1]}]`]
  }
}

// NUDT15 評估結果
const nudt15Assessment = (value) => {
  if (value === 'low-risk') {
    return "Low risk";
  } else if (value === 'normal-risk') {
    return "Normal risk";
  } else if (value === 'high-risk') {
    return "High risk";
  } else if (value === 'inconclusive') {
    return "Inconclusive";
  } else {
    return "Invalid";
  }
};

// 取得 instrument 和 reagent
const getCurrentInstrument = () => {
  return store.getters["analysis_setting/getSettingProps"].instrument;
}

// 定義 MTHFR_RESULT 的格式
const MTHFR_RESULT = (controlData, NTCData, SampleDataList, resultList) => {
  return {
    controlData: controlData,
    NTCData: NTCData,
    SampleDataList: SampleDataList,
    resultList: resultList,
  }
}

// 定義 NUDT15_RESULT 的格式
const NUDT15_RESULT = (controlData, NTCData, SampleDataList, resultList) => {
  return {
    controlData: controlData,
    NTCData: NTCData,
    SampleDataList: SampleDataList,
    resultList: resultList,
  }
}

// Functions

// 初始化 inputss
function initInputs() {
  resultFile.value = null;
  famFile.value = null;
  vicFile.value = null;
  Ctrlwell.value = null;
  NTCwell.value = null;
}

// 更新 currentAnalysisID
function updateCurrentAnalysisID() {
  const new_id = `analysis_${uuidv4()}`;
  store.commit('analysis_setting/updateCurrentAnalysisID', {
    analysis_name: props.analysis_name,
    analysis_uuid: new_id,
  });
  currentAnalysisID.value = store.getters['analysis_setting/getCurrentAnalysisID'];
}

// 送出按鈕
async function onSubmit() {
  // *. 顯示 loading 視窗
  $q.loading.show({
    spinner: QSpinnerFacebook,
    spinnerColor: "deep-orange-6",
    spinnerSize: 100,
    message: "Analyzing...",
    messageColor: "white",
  });

  // 取得 inputData
  const InputData = {
    file_path: resultFile.value ? resultFile.value.path : null,
    control_well: Ctrlwell.value,
    ntc_well: NTCwell.value,
    FAM_file_path: famFile.value ? famFile.value.path : null,
    VIC_file_path: vicFile.value ? vicFile.value.path : null,
  }

  // 取得 settingProps
  const currentSettingProps = store.getters["analysis_setting/getSettingProps"];

  // 執行 submitWorkflow
  const analysisResult = await submitWorkflow(props.analysis_name, InputData, user_info.value, currentSettingProps);

  // 檢查有沒有出錯
  if (analysisResult.status == 'success'){
    dialog_error_message.value = "";

    // 將 result 轉換成 Object
    const resultObj = JSON.parse(analysisResult.result);

    if (props.analysis_name === "MTHFR") {
      // 製作 MTHFR_RESULT
      const MTHFR_Result = MTHFR_RESULT(
        resultObj.controlData,
        resultObj.ntcData,
        resultObj.sampleDataList,
        resultObj.resultList,
      );

      // 製作 EXPORT_RESULT
      const exportResult = MTHFR_Result.resultList.map((result, index) => {
        const wellPosition = resultObj.sampleDataList[index].well_position;
        return EXPORT_RESULT(
          index+1,
          result.sample_name,
          result.sample_type,
          mthfrParseResult(resultObj.config.reagent, result.sample_type),
          result.assessment,
          mthfrAssessment(result.assessment),
          wellPosition.X + wellPosition.Y
        );
      });

      // 製作 ANALYSIS_RESULT
      const AnalysisResult = ANALYSIS_RESULT(
        currentAnalysisID.value.analysis_name,
        currentAnalysisID.value.analysis_uuid,
        resultObj.config,
        [resultObj.controlData.sample_name],
        resultObj.qc_status,
        resultObj.errMsg,
        MTHFR_Result,
        exportResult
      );

      // 將結果存到 firestore
      update_userAnalysisData(user_info.value.uid, dbMTHFRResultPath, AnalysisResult, currentAnalysisID.value.analysis_uuid);

      // 更新 currentDisplayAnalysisID
      store.commit("analysis_setting/updateCurrentDisplayAnalysisID", {
        analysis_name: "MTHFR",
        analysis_uuid: currentAnalysisID.value.analysis_uuid,
      });
    }
    else if (props.analysis_name === "NUDT15") {
      // 製作 NUDT15_RESULT
      const NUDT15_Result = NUDT15_RESULT(
        resultObj.controlData,
        resultObj.ntcData,
        resultObj.sampleDataList,
        resultObj.resultList,
      );

      // 製作 EXPORT_RESULT
      const exportResult = NUDT15_Result.resultList ? NUDT15_Result.resultList.map((result, index) => {
        return EXPORT_RESULT(
          index+1,
          result.sample_name,
          result.sample_type,
          [result.sample_type.join("/")],
          result.assessment,
          nudt15Assessment(result.assessment),
          );
        }) : [];

      // 製作 ANALYSIS_RESULT
      const AnalysisResult = ANALYSIS_RESULT(
        currentAnalysisID.value.analysis_name,
        currentAnalysisID.value.analysis_uuid,
        resultObj.config,
        [resultObj.controlData ? resultObj.controlData.sample_name : ''],
        resultObj.qc_status,
        resultObj.errMsg,
        NUDT15_Result,
        exportResult
      );

      // 將結果存到 firestore
      update_userAnalysisData(user_info.value.uid, dbNUDT15ResultPath, AnalysisResult, currentAnalysisID.value.analysis_uuid);

      // 更新 currentDisplayAnalysisID
      store.commit("analysis_setting/updateCurrentDisplayAnalysisID", {
        analysis_name: "NUDT15",
        analysis_uuid: currentAnalysisID.value.analysis_uuid,
      });
    }

    // 更新 currentAnalysisID
    updateCurrentAnalysisID();

    // 初始化 inputResults (葉酸輸入)
    store.commit('MTHFR_analysis_data/initInputResults');

    // 清除 store 的 subjectInfoTable 和 LabInfomation
    store.commit("export_page_setting/initExportPageSetting");

    // 隱藏 loading 視窗
    $q.loading.hide();

    // 跳轉到分析結果頁面
    setTimeout(()=>{
      router.push({
        path: '/page-preview',
      });
    }, 500);
  }
  else if (analysisResult.status == 'error'){
    // 更新 currentAnalysisID
    updateCurrentAnalysisID();

    // 清空 resultFile, famFile, vicFile
    resultFile.value = null;
    famFile.value = null;
    vicFile.value = null;
    Ctrlwell.value = null;
    NTCwell.value = null;

    // 通知
    $q.notify({
      progress: true,
      message: "分析流程出了一點問題...",
      icon: 'mdi-alert-circle',
      color: 'deep-orange-6',
      position: 'top'
    });
    // 跳出警告視窗
    dialog_error_message.value = analysisResult.message;
    warning_dialog.value.open_warning_dialog();

    // 隱藏 loading 視窗
    $q.loading.hide();
  }
}

// 更新 dialog_error_message
function updateDialogErrorMessage(message) {
  dialog_error_message.value = message;
  warning_dialog.value.open_warning_dialog();
}

// 更新 resultFile, famFile, vicFile
function updateFiles(file_type) {
  if (file_type == 'resultFile') {
    resultFile.value = ref_qPCRImportSection.value.resultFile;
  }
  else if (file_type == 'famFile') {
    famFile.value = ref_qPCRImportSection.value.famFile;
  }
  else if (file_type == 'vicFile') {
    vicFile.value = ref_qPCRImportSection.value.vicFile;
  }
}

// 更新 wells
function updateWells(well_type) {
  if (well_type == 'Ctrlwells') {
    Ctrlwell.value = ref_qPCRImportSection.value.Ctrlwells;
  }
  else if (well_type == 'NTCwell') {
    NTCwell.value = ref_qPCRImportSection.value.NTCwell;
  }
}

// 取得試劑
const getReagent = (dataset_class, reagent) => {
  switch (dataset_class) {
    case "MTHFR":
      switch (reagent) {
        case "MTHFR_v1":
          return { reagent_value: "accuinMTHFR1", reagent_label: "ACCUiN BioTech MTHFR v1" };
        case "MTHFR_v2":
          return { reagent_value: "accuinMTHFR2", reagent_label: "ACCUiN BioTech MTHFR v2" };
        case "MTHFR_v3":
          return { reagent_value: "accuinMTHFR3", reagent_label: "ACCUiN BioTech MTHFR v3" };
        default:
          return { reagent_value: null, reagent_label: null };
      }
    case "NUDT15":
      switch (reagent) {
        case "NUDT15_v1":
          return { reagent_value: "accuinNUDT151", reagent_label: "ACCUiN BioTech NUDT15 v1" };
        case "NUDT15_v2":
          return { reagent_value: "accuinNUDT152", reagent_label: "ACCUiN BioTech NUDT15 v2" };
        default:
          return { reagent_value: null, reagent_label: null };
      }
    default:
      return { reagent_value: null, reagent_label: null };
  }
}

// 取得儀器
const getInstrument = (instrument) => {
  switch (instrument) {
    case "qs3":
      return { instrument_value: "qs3", instrument_label: "QuantStudio™ 3" };
    case "tower":
      return { instrument_value: "tower", instrument_label: "qTOWER³" };
    case "z480":
      return { instrument_value: "z480", instrument_label: "Roche Cobas® z 480" };
    default:
      return null;
  }
}

// 製作檔案
function makeFile(file_path) {

  if (file_path == null) {
    return null;
  }

  // 創建一個空的 Blob 物件作為檔案內容
  const emptyBlob = new Blob([''], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });

  // 載入 Result File - 創建模擬 File 物件
  const resultFileName = file_path.split('/').pop();
  const resultFileObj = new File([emptyBlob], resultFileName, {
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  });
  // 添加 path 屬性
  Object.defineProperty(resultFileObj, 'path', {
    value: file_path,
    writable: true
  });
  return resultFileObj;
}

// 運行 Testing Dataset
async function runTestingDataset(dataset_name) {
  // 取得 testing_data
  const testing_data = await getTestingData(props.analysis_name);
  const selected_dataset = testing_data.find((item) => item.name === dataset_name);

  // 決定該 Dataset 使用的儀器和試劑
  const usedInstrument = selected_dataset.instrument;
  const { reagent_value, reagent_label } = getReagent(selected_dataset.dataset_class, selected_dataset.reagent);
  const { instrument_value, instrument_label } = getInstrument(usedInstrument);

  // 取得 settingProps
  const currentSettingProps = store.getters["analysis_setting/getSettingProps"];
  const updatedSettingProps = {
    ...currentSettingProps,
    instrument: instrument_value,
    instrumentLabel: instrument_label,
    reagent: reagent_value,
    reagentLabel: reagent_label,
  }

  // 更新 settingProps
  store.commit("analysis_setting/updateSettingProps", updatedSettingProps);

  // 製作檔案
  resultFile.value = makeFile(selected_dataset.resultFile);
  famFile.value = makeFile(selected_dataset.FAM);
  vicFile.value = makeFile(selected_dataset.VIC);

  // Wells
  Ctrlwell.value = [{
    X: selected_dataset.controlWell[0],
    Y: selected_dataset.controlWell.substring(1),
  }];
  NTCwell.value = {
    X: selected_dataset.NTCWell[0],
    Y: selected_dataset.NTCWell.substring(1),
  };

  // 執行 onSubmit
  onSubmit();
}

// Expose
defineExpose({
  runTestingDataset
});


// 掛載時
onMounted(() => {
  // 取得使用者身份
  const { login_status } = updateGetUserInfo();
  is_login.value = login_status.value.is_login;
  user_info.value = login_status.value.user_info;

  // 先嘗試取得當前的分析 ID, 如果沒有則建立新的分析 ID
  currentAnalysisID.value = store.getters['analysis_setting/getCurrentAnalysisID'];
  setAnalysisID(store, props.analysis_name);

  // 初始化 inputss
  initInputs();
});

// 監聽 instrument
watch(getCurrentInstrument, () => {
  // 當 instrument 改變時, 初始化 inputss
  initInputs();
});

</script>
