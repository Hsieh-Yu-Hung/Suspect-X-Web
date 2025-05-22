<template>
  <q-card bordered :style="{ 'min-height': '100%' }">

    <!-- 警告視窗 -->
    <WarningDialog
      ref="warning_dialog"
      :error_message="dialog_error_message"
    />

    <!-- 標題 -->
    <q-card-section>
      <div class="flex justify-between items-center">
        <div>
          <div class="text-h5 text-uppercase text-bold text-blue-grey-7">
            Import
          </div>
          <div class="text-subtitle1">
            Please select the corresponding control result and sample result.
          </div>
        </div>
      </div>
    </q-card-section>

    <!-- 輸入表單區 -->
    <q-card-section>
      <q-form class="q-gutter-sm" @submit="onSubmit">

        <div class="row flex justify-between items-flex-start" style="flex-direction: row; height: 100%;">

          <!-- 上傳檔案區 -->
          <div class="col">
            <!-- 控制組檔案 -->
            <q-file
              v-model="controlSampleFile"
              use-chips
              color="deep-orange-6"
              stack-label
              label="Control sample"
              :rules="[(val) => val || `Please select ONE control sample`]"
              accept=".xlsx"
              lazy-rules
            >
              <template v-slot:before>
                <q-icon name="mdi-microsoft-excel" />
              </template>
            </q-file>

            <!-- 測試組檔案 -->
            <q-file
              v-model="testingSampleFile"
              multiple
              append
              use-chips
              color="deep-orange-6"
              stack-label
              label="Testing samples"
              :rules="[(val) => (val && val.length != 0) || `Please select at least ONE testing sample`]"
              accept=".xlsx"
              lazy-rules
            >
              <template v-slot:before>
                <q-icon name="mdi-microsoft-excel" />
              </template>
            </q-file>
          </div>

        </div>

        <!-- 分析按鈕 -->
        <div class="row q-mt-lg justify-end">
          <q-btn label="Analyze" type="submit" color="blue-grey-7" />
        </div>

      </q-form>
    </q-card-section>

  </q-card>
</template>

<script setup>
// 導入模組
import { ref, onMounted, watch, computed } from 'vue';
import { useStore } from 'vuex';
import { useQuasar, QSpinnerFacebook } from 'quasar';
import { v4 as uuidv4 } from 'uuid';
import { useRouter } from 'vue-router';

// 導入 composable
import { submitWorkflow } from '@/composables/submitWorkflow';
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';
import { CATEGORY_LIST, upload_files_to_storage } from '@/composables/storageManager';
import { setAnalysisID } from '@/composables/checkAnalysisStatus';
import { ANALYSIS_RESULT, EXPORT_RESULT, update_userAnalysisData, simplifyFilePath } from '@/firebase/firebaseDatabase';

// 元件
import WarningDialog from '@/components/WarningDialog.vue';
import loggerV2 from '@/composables/loggerV2';

// 定義 FXS 的 result 格式
const FXS_RESULT = (control_data, sample_data, control_qc, result) => {
  return {
    control_data: control_data,
    sample_data: sample_data,
    control_qc: control_qc,
    result: result,
  }
}

// 定義 HTD_RESULT 的格式
const HTD_RESULT = (standard_control_data, result_and_data, errMsg) => {
  return {
    standard_control_data: standard_control_data,
    result_and_data: result_and_data,
    errMsg: errMsg,
  }
}

// 導入 store, Quasar
const store = useStore();
const router = useRouter();
const $q = useQuasar();

// props
const props = defineProps({
  analysis_name: {
    type: String,
    required: true,
  },
  testing_data: {
    type: Array,
    required: true,
  },
});

// 上傳分類 matrix
const categoryMatrix = {
  'FXS': CATEGORY_LIST.fx_import,
  'HTD': CATEGORY_LIST.htd_import,
}

// consts
const controlSampleFile = ref(null);
const testingSampleFile = ref(null);

// 使用者身份
const is_login = ref(false);
const user_info = ref(null);

// 當前的分析 ID
const currentAnalysisID = ref(null);

// 控制警告視窗
const dialog_error_message = ref("");
const warning_dialog = ref(null);

// Database Path
const dbFXSResultPath = "fxs_result";
const dbHTDResultPath = "htd_result";

/* Functions */

function initInputs() {
  controlSampleFile.value = null;
  testingSampleFile.value = null;
}

// FXS 解釋結果
const interpretationValue = (value) => {
  if (value === "normal") {
    return "normal";
  } else if (
    (value === "intermediate") ||
    (value === "normal/intermediate")
  ) {
    return "intermediate";
  } else if (
    (value === "premutation") ||
    (value === "normal/premutation") ||
    (value === "intermediate/premutation")
  ) {
    return "premutation";
  } else if (
    (value === "full-mutation") ||
    (value === "normal/full-mutation") ||
    (value === "intermediate/full-mutation") ||
    (value === "premutation/full-mutation")
  ) {
    return "full";
  } else if (value === "inconclusive"){
    return "inconclusive";
  } else {
    return "invalid";
  }
};

// FXS 結果評估標籤
const interpretationLabel = (value) => {
  if (value === "normal") {
    return "Normal";
  } else if (
    (value === "intermediate") ||
    (value === "normal/intermediate")
  ) {
    return "Intermediate";
  } else if (
    (value === "premutation") ||
    (value === "normal/premutation") ||
    (value === "intermediate/premutation")
  ) {
    return "Premutation";
  } else if (
    (value === "full-mutation") ||
    (value === "normal/full-mutation") ||
    (value === "intermediate/full-mutation") ||
    (value === "premutation/full-mutation")
  ) {
    return "Full";
  } else if (value === "inconclusive"){
    return "Inconclusive";
  } else {
    return "Invalid";
  }
}

// HTD 結果評估值
const HTD_assessmentValue = (value) => {
  if (value === "normal") {
    return "Normal";
  } else if (value === "intermediate") {
    return "Intermediate";
  } else if (value === "penetrance") {
    return "Reduced penetrance";
  } else if (value === "full-penetrance") {
    return "Full penetrance";
  } else if (value === "inconclusive") {
    return "Inconclusive";
  } else {
    return "Invalid";
  }
};

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
    controlPath: controlSampleFile.value ? controlSampleFile.value.path : null,
    samplePathList: testingSampleFile.value ? testingSampleFile.value.map((file) => {return file.path}) : [],
  }

  // 取得 settingProps
  const currentSettingProps = store.getters["analysis_setting/getSettingProps"];

  // 執行 submitWorkflow
  const analysisResult = await submitWorkflow(props.analysis_name, InputData, user_info.value, currentSettingProps);

  // 檢查有沒有出錯
  if (analysisResult.status == 'success'){

    // 初始化 error message
    dialog_error_message.value = "";

    // 將 result 轉換成 Object
    const resultObj = JSON.parse(analysisResult.result);

    // 如果分析名稱是 FXS, 則使用 FXS_RESULT
    if (props.analysis_name === 'FXS') {

      // 製作 FXS_RESULT
      const FXS_Result = FXS_RESULT(
        resultObj.control_data,
        resultObj.sample_data,
        resultObj.control_qc,
        resultObj.result);

      // 製作 EXPORT_RESULT
      const sample_ids = resultObj.result ? Object.keys(resultObj.result) : [];
      const exportResult = sample_ids.map((sample_id, index) => {
        let result_list = resultObj.sample_data[sample_id].selected_fx_peaks.map(peak => peak.average_repeatNum);
        if (result_list.length === 1) {
          result_list = [result_list[0], result_list[0]];
        }
        return EXPORT_RESULT(
          index+1,
          sample_id,
          result_list.join("/"),
          [result_list.join("/")],
          interpretationValue(resultObj.result[sample_id].assessment),
          interpretationLabel(resultObj.result[sample_id].assessment)
        );
      });

      // 製作 ANALYSIS_RESULT
      const AnalysisResult = ANALYSIS_RESULT(
        currentAnalysisID.value.analysis_name,
        currentAnalysisID.value.analysis_uuid,
        resultObj.config,
        [simplifyFilePath(controlSampleFile.value.name)],
        resultObj.qc_status,
        "",
        FXS_Result,
        exportResult
      );

      // 將結果存到 firestore
      update_userAnalysisData(user_info.value.uid, dbFXSResultPath, AnalysisResult, currentAnalysisID.value.analysis_uuid);

      // 更新 currentDisplayAnalysisID
      store.commit("analysis_setting/updateCurrentDisplayAnalysisID", {
        analysis_name: "FXS",
        analysis_uuid: currentAnalysisID.value.analysis_uuid,
      });
    }
    else if (props.analysis_name === 'HTD') {
      // 製作 HTD_RESULT
      const HTD_Result = HTD_RESULT(
        resultObj.standard_control_data,
        resultObj.result,
        resultObj.errMsg
      );

      // 製作 EXPORT_RESULT
      const sample_ids = HTD_Result.result_and_data ? Object.keys(HTD_Result.result_and_data) : [];
      const exportResult = sample_ids.map((sample_id, index) => {
        let result_list = HTD_Result.result_and_data[sample_id].selected_target_peaks.map(peak => peak.repeat_num);
        if (result_list.length === 1) {
          result_list = [result_list[0], result_list[0]];
        }
        return EXPORT_RESULT(
          index+1,
          sample_id,
          result_list.join(" / "),
          [result_list.join(" / ")],
          HTD_Result.result_and_data[sample_id].assessment,
          HTD_assessmentValue(HTD_Result.result_and_data[sample_id].assessment)
        );
      });

      // 製作 ANALYSIS_RESULT
      const AnalysisResult = ANALYSIS_RESULT(
        currentAnalysisID.value.analysis_name,
        currentAnalysisID.value.analysis_uuid,
        resultObj.config,
        [simplifyFilePath(controlSampleFile.value.name)],
        resultObj.qc_status,
        "",
        HTD_Result,
        exportResult
      );

      // 將結果存到 firestore
      update_userAnalysisData(user_info.value.uid, dbHTDResultPath, AnalysisResult, currentAnalysisID.value.analysis_uuid);

      // 更新 currentDisplayAnalysisID
      store.commit("analysis_setting/updateCurrentDisplayAnalysisID", {
        analysis_name: "HTD",
        analysis_uuid: currentAnalysisID.value.analysis_uuid,
      });
    }

    // 更新 currentAnalysisID
    updateCurrentAnalysisID();

    // 隱藏 loading 視窗
    $q.loading.hide();

    // 清除 store 的 subjectInfoTable 和 LabInfomation
    store.commit("export_page_setting/initExportPageSetting");

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

    // 清空 controlSampleFile 和 testingSampleFile
    initInputs();

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

// 選擇後上傳檔案
async function uploadFile(files, type) {
  // 如果沒有檔案, 則返回
  if (!files) return;

  // 顯示 loading 視窗
  $q.loading.show();

  // 存到當前使用者
  const user_uid = user_info.value.uid;

  // 存到 data 資料夾
  const analysis_name = store.getters['analysis_setting/getCurrentAnalysisID'].analysis_name;
  const analysis_uuid = store.getters['analysis_setting/getCurrentAnalysisID'].analysis_uuid;
  const category = categoryMatrix[analysis_name];
  const subDir = type;

  // 上傳檔案
  const uploading = await Promise.all(files.map(async (file) => {
    return await upload_files_to_storage(
      file, user_uid, category, analysis_uuid, subDir
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
    const source = 'ImportPCRTmpl.vue line.297';
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

// 取得試劑
const getReagent = (dataset_class, reagent) => {
  let reagent_value = null;
  let reagent_label = null;
  switch (dataset_class) {
    case 'FXS':
      switch (reagent) {
        case 'FXS_v1':
          reagent_value = 'accuinFx1';
          reagent_label = 'ACCUiN BioTech Fragile X v1';
          break;
        case 'FXS_v2':
          reagent_value = 'accuinFx2';
          reagent_label = 'ACCUiN BioTech Fragile X v2';
          break;
        default:
          break;
      }
    case 'HTD':
      switch (reagent) {
        case 'HTD_v1':
          reagent_value = 'accuinHD1';
          reagent_label = 'ACCUiN BioTech HTD v1';
          break;
        default:
          break;
      }
    default:
      break;
  }
  return {
    reagent_value: reagent_value,
    reagent_label: reagent_label,
  }
}

// 執行測試資料集
async function runTestingDataset(dataset_name) {

  // 取得測試資料集
  const testing_data = props.testing_data.find(item => item.dataset_name === dataset_name);

  // 決定該 Dataset 使用的儀器和試劑
  const usedInstrument = testing_data.instrument;
  const { reagent_value, reagent_label } = getReagent(testing_data.dataset_class, testing_data.reagent);

  // 取得 settingProps
  const currentSettingProps = store.getters["analysis_setting/getSettingProps"];
  const updatedSettingProps = {
    ...currentSettingProps,
    instrument: usedInstrument,
    reagent: reagent_value,
    reagentLabel: reagent_label,
  }

  // 更新 settingProps
  store.commit("analysis_setting/updateSettingProps", updatedSettingProps);

  // 創建一個空的 Blob 物件作為檔案內容
  const emptyBlob = new Blob([''], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });

  // 載入 Control Sample - 創建模擬 File 物件
  const controlFileName = testing_data.controlFile.split('/').pop();
  const controlFileObj = new File([emptyBlob], controlFileName, {
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  });
  // 添加 path 屬性
  Object.defineProperty(controlFileObj, 'path', {
    value: testing_data.controlFile,
    writable: true
  });
  controlSampleFile.value = controlFileObj;

  // 載入 Testing Samples - 創建模擬 File 物件
  testingSampleFile.value = testing_data.sampleFiles.map(file => {
    const fileName = file.split('/').pop();
    const fileObj = new File([emptyBlob], fileName, {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    });
    // 添加 path 屬性
    Object.defineProperty(fileObj, 'path', {
      value: file,
      writable: true
    });
    return fileObj;
  });

  // 送出
  onSubmit();
}

// Expose
defineExpose({
  runTestingDataset,
});

// 掛載時
onMounted(async () => {
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

// 監聽 controlSampleFile
watch(controlSampleFile, async(newVal, oldVal) => {
  if (newVal !== oldVal) {
    if (newVal && newVal.size) {
      await uploadFile([newVal], 'control');
    }
  }
});

// 監聽 testingSampleFile
watch(testingSampleFile, async(newVal, oldVal) => {
  if (newVal && newVal !== oldVal) {
    if (newVal.length > 0 && newVal[0].size) {
      await uploadFile(newVal, 'samples');
    }
  }
});

</script>
