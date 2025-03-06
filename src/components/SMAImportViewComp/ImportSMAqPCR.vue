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
          :std_control_number="2"
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
import { ref, onMounted } from 'vue';
import { useQuasar, QSpinnerFacebook } from 'quasar';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import { v4 as uuidv4 } from 'uuid';

// 導入 composable
import { setAnalysisID } from '@/composables/checkAnalysisStatus';
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';
import { submitWorkflow } from '@/composables/submitWorkflow';
import { ANALYSIS_RESULT, update_userAnalysisData, simplifyFilePath } from '@/firebase/firebaseDatabase';

// 元件
import WarningDialog from '@/components/WarningDialog.vue';
import qPCRImportSection from '@/components/ImportqPCRViews/qPCRImportSection.vue';

// Database Path
const dbSMAResultPath = "sma_result";

// 取得 quasar, store, router
const $q = useQuasar();
const store = useStore();
const router = useRouter();

// 控制警告視窗
const dialog_error_message = ref("");
const warning_dialog = ref(null);

// 使用者身份
const is_login = ref(false);
const user_info = ref(null);

// 當前的分析 ID
const currentAnalysisID = ref(null);

// 控制 qPCRImportSection
const ref_qPCRImportSection = ref(null);

// 取得 qPCRImportSection 的 resultFile, famFile, vicFile, Ctrlwell, NTCwell
const resultFile = ref(null);
const famFile = ref(null);
const vicFile = ref(null);
const cy5File = ref(null);
const Ctrlwell = ref(null);
const NTCwell = ref(null);

// 定義 SMA_RESULT
const SMA_RESULT = (analyzerVersion,SC1_Data, SC2_Data, NTC_Data, sampleDataList, SMA_parameters, resultList) => {
  return {
    analyzerVersion,
    SC1_Data,
    SC2_Data,
    NTC_Data,
    sampleDataList,
    SMA_parameters,
    resultList,
  }
}

// Functions

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
    CY5_file_path: cy5File.value ? cy5File.value.path : null,
  }

  // 取得 settingProps
  const currentSettingProps = store.getters["analysis_setting/getSettingProps"];

  // 執行 submitWorkflow
  const analysisResult = await submitWorkflow('SMA', InputData, user_info.value, currentSettingProps);

  // 檢查有沒有出錯
  if (analysisResult.status == 'success'){
    dialog_error_message.value = "";

    // 將 result 轉換成 Object
    const resultV1Obj = JSON.parse(analysisResult.result['v1']);
    const resultV2Obj = JSON.parse(analysisResult.result['v2']);
    const resultV3Obj = JSON.parse(analysisResult.result['v3']);

    const SMA_ResultV1 = SMA_RESULT(
      'v1',
      resultV1Obj.SC1Data,
      resultV1Obj.SC2Data,
      resultV1Obj.NTCData,
      resultV1Obj.sampleDataList,
      resultV1Obj.SMAparameters,
      resultV1Obj.resultList,
    )

    const SMA_ResultV2 = SMA_RESULT(
      'v2',
      resultV2Obj.SC1Data,
      resultV2Obj.SC2Data,
      resultV2Obj.NTCData,
      resultV2Obj.sampleDataList,
      resultV2Obj.SMAparameters,
      resultV2Obj.resultList,
    )

    const SMA_ResultV3 = SMA_RESULT(
      'v3',
      resultV3Obj.SC1Data,
      resultV3Obj.SC2Data,
      resultV3Obj.NTCData,
      resultV3Obj.sampleDataList,
      resultV3Obj.SMAparameters,
      resultV3Obj.resultList,
    )

    // 製作 ANALYSIS_RESULT
    const AnalysisResult = ANALYSIS_RESULT(
        "SMA",
        currentAnalysisID.value.analysis_uuid,
        {
          V1: resultV1Obj.config,
          V2: resultV2Obj.config,
          V3: resultV3Obj.config,
        },
        {
          V1: [simplifyFilePath(InputData.file_path)],
          V2: [simplifyFilePath(InputData.file_path)],
          V3: [simplifyFilePath(InputData.file_path)],
        },
        {
          V1: resultV1Obj.qc_status,
          V2: resultV2Obj.qc_status,
          V3: resultV3Obj.qc_status,
        },
        {
          V1: resultV1Obj.errMsg,
          V2: resultV2Obj.errMsg,
          V3: resultV3Obj.errMsg,
        },
        {
          V1: SMA_ResultV1,
          V2: SMA_ResultV2,
          V3: SMA_ResultV3,
        }
      );

    // 將結果存到 firestore
    update_userAnalysisData(user_info.value.uid, dbSMAResultPath, AnalysisResult, currentAnalysisID.value.analysis_uuid);

    // 更新 currentDisplayAnalysisID
    store.commit("analysis_setting/updateCurrentDisplayAnalysisID", {
      analysis_name: "SMA",
      analysis_uuid: currentAnalysisID.value.analysis_uuid,
    });

    // 更新 currentAnalysisID
    const new_id = `analysis_${uuidv4()}`;
    store.commit('analysis_setting/updateCurrentAnalysisID', {
      analysis_name: 'SMA',
      analysis_uuid: new_id,
    });
    currentAnalysisID.value = store.getters['analysis_setting/getCurrentAnalysisID'];

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
  else if (file_type == 'cy5File') {
    cy5File.value = ref_qPCRImportSection.value.cy5File;
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

// 初始化 inputss
function initInputs() {
  resultFile.value = null;
  famFile.value = null;
  vicFile.value = null;
  cy5File.value = null;
  Ctrlwell.value = null;
  NTCwell.value = null;
}

// 掛載時
onMounted(() => {
  // 取得使用者身份
  const { login_status } = updateGetUserInfo();
  is_login.value = login_status.value.is_login;
  user_info.value = login_status.value.user_info;

  // 先嘗試取得當前的分析 ID, 如果沒有則建立新的分析 ID
  currentAnalysisID.value = store.getters['analysis_setting/getCurrentAnalysisID'];
  setAnalysisID(store, 'SMA');

  // 初始化 inputss
  initInputs();
});

</script>
