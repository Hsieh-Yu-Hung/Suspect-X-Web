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
        Please upload the Sanger Sequencer result <b>*.ab1</b> file.
      </div>
    </q-card-section>

    <!-- 輸入表單區 -->
    <q-card-section>
      <q-form class="q-gutter-sm" @submit="onSubmit">

        <!-- 上傳 Sanger Sequencer 結果 -->
        <q-file
          v-model="seqencingResultFile"
          append
          use-chips
          color="deep-orange-6"
          stack-label
          label="Seqencing result"
          :rules="[(val) => (val && val.length != 0) || `Please select the seqencing result file!`]"
          accept=".ab1"
          lazy-rules
        >
          <template v-slot:before>
            <q-icon name="mdi-dna" />
          </template>
        </q-file>

        <!-- 開發設定版面 -->
        <div class="q-mt-lg" style="width: 100%;">

          <!-- 開發設定標題 -->
          <div class="row">
            <span class="text-bold text-h6 text-blue-grey-7">
              Development Settings
            </span>
          </div>

          <!-- 開發設定參數:Left-Trim, Right-Trim -->
          <div style="margin-block: 20px;">
            <div class="row" style="display: flex; flex-direction: row; gap: 5em; align-items: center; margin-block: 2em;">
              <span class="col-2 text-subtitle1" style="margin-left: 1em;">Left-Trim</span>
              <q-input class="col-3" dense outlined v-model="left_trim" type="number" suffix="bp" :min="0" :max="1000000"/>
            </div>
            <div class="row" style="display: flex; flex-direction: row; gap: 5em; align-items: center; margin-block: 2em;">
              <span class="col-2 text-subtitle1" style="margin-left: 1em;">Right-Trim</span>
              <q-input class="col-3" dense outlined v-model="right_trim" type="number" suffix="bp" :min="0" :max="1000000"/>
            </div>
          </div>

          <!-- 開發設定參數: peak_ratio -->
          <div class="q-pa-md" style="width: 50%; display: flex; flex-direction: column; gap: 1em;">

            <div style="width: fit-content; display: flex; flex-direction: row; gap: 1em;">
              <span class="text-subtitle1">
                Peak Ratio
              </span>
              <q-badge color="secondary">
                Peak Ratio: {{ peak_ratio }} (0 to 1)
              </q-badge>
            </div>

            <q-slider v-model="peak_ratio" :min="0" :max="1" :step="0.01"/>
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
// 引入套件
import { ref, watch, onMounted } from 'vue';
import { useStore } from 'vuex';
import { v4 as uuidv4 } from 'uuid';
import { useRouter } from 'vue-router';
import { useQuasar, QSpinnerFacebook } from 'quasar';

// 導入 composable
import { submitWorkflow } from '@/composables/submitWorkflow';
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';
import { CATEGORY_LIST, upload_files_to_storage } from '@/composables/storageManager';
import { setAnalysisID } from '@/composables/checkAnalysisStatus';
import { ANALYSIS_RESULT, EXPORT_RESULT, update_userAnalysisData, simplifyFilePath } from '@/firebase/firebaseDatabase';

// 引入元件
import WarningDialog from '@/components/WarningDialog.vue';
import loggerV2 from '@/composables/loggerV2';

// 控制警告視窗
const dialog_error_message = ref("");
const warning_dialog = ref(null);

// 定義 ThalBeta 的 database 路徑
const dbThalBetaResultPath = "thalbeta_result";

// 導入 store, Quasar
const store = useStore();
const router = useRouter();
const $q = useQuasar();

// 使用者身份
const is_login = ref(false);
const user_info = ref(null);
const currentAnalysisID = ref(null);

// 表單資料 (檔案和參數)
const seqencingResultFile = ref(null);
const left_trim = ref(50);
const right_trim = ref(50);
const peak_ratio = ref(0.25);

// 定義 ThalBeta 的結果
const THAL_BETA_RESULT = (input_file, parameters, resultTable) => {
  return {
    input_file: input_file,
    parameters: parameters,
    resultTable: resultTable
  }
}

// Functions

// 選擇後上傳檔案
async function uploadFile(files) {

  // 如果沒有檔案, 則返回
  if (!files) return;

  // 顯示 loading 視窗
  $q.loading.show();

  // 存到當前使用者
  const user_uid = user_info.value.uid;

  // 存到 data 資料夾
  const analysis_name = store.getters['analysis_setting/getCurrentAnalysisID'].analysis_name;
  const analysis_uuid = store.getters['analysis_setting/getCurrentAnalysisID'].analysis_uuid;
  const category = CATEGORY_LIST.thal_beta_import;

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
    const source = 'ImportThalBeta.vue line.125';
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

// 提交表單
const onSubmit = async () => {

  // *. 顯示 loading 視窗
  $q.loading.show({
    spinner: QSpinnerFacebook,
    spinnerColor: "deep-orange-6",
    spinnerSize: 100,
    message: "Analyzing...",
    messageColor: "white",
  });

  // 取得 uploaded_file_path
  const beta_thal_input_data = {
    file_path: seqencingResultFile.value.path,
    left_trim: left_trim.value,
    right_trim: right_trim.value,
    peak_ratio: peak_ratio.value
  }

  // 取得 settingProps
  const currentSettingProps = store.getters["analysis_setting/getSettingProps"];

  // 執行 submitWorkflow
  const analysisResult = await submitWorkflow('THAL_BETA', beta_thal_input_data, user_info.value, currentSettingProps);

  // 檢查有沒有出錯
  if (analysisResult.status == 'success'){
    dialog_error_message.value = "";

    // 將 result 轉換成 Object
    const resultObj = JSON.parse(analysisResult.result);

    // 製作 THAL_BETA_RESULT
    const THAL_BETA_Result = THAL_BETA_RESULT(
      resultObj.input_file,
      resultObj.parameters,
      resultObj.result
    );

    // 製作 EXPORT_RESULT
    const exportResult = EXPORT_RESULT(1, simplifyFilePath(THAL_BETA_Result.input_file), "", "", "", "");

    // 製作 ANALYSIS_RESULT
    const AnalysisResult = ANALYSIS_RESULT(
      currentAnalysisID.value.analysis_name,
      currentAnalysisID.value.analysis_uuid,
      resultObj.config,
      ["N/A"],
      resultObj.qc_status,
      resultObj.errMsg,
      THAL_BETA_Result,
      [exportResult]
    );

    // 將結果存到 firestore
    update_userAnalysisData(user_info.value.uid, dbThalBetaResultPath, AnalysisResult, currentAnalysisID.value.analysis_uuid);

    // 更新 currentDisplayAnalysisID
    store.commit("analysis_setting/updateCurrentDisplayAnalysisID", {
      analysis_name: "THAL_BETA",
      analysis_uuid: currentAnalysisID.value.analysis_uuid,
    });

    // 更新 currentAnalysisID
    const new_id = `analysis_${uuidv4()}`;
    store.commit('analysis_setting/updateCurrentAnalysisID', {
      analysis_name: "THAL_BETA",
      analysis_uuid: new_id,
    });
    currentAnalysisID.value = store.getters['analysis_setting/getCurrentAnalysisID'];

    // 清除 store 的 subjectInfoTable 和 LabInfomation
    store.commit("export_page_setting/initExportPageSetting");

    // *. 隱藏 loading 視窗
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

    // *. 隱藏 loading 視窗
    $q.loading.hide();
  }
}

// 掛載時
onMounted(() => {
  // 取得使用者身份
  const { login_status } = updateGetUserInfo();
  is_login.value = login_status.value.is_login;
  user_info.value = login_status.value.user_info;

  // 先嘗試取得當前的分析 ID, 如果沒有則建立新的分析 ID
  currentAnalysisID.value = store.getters['analysis_setting/getCurrentAnalysisID'];
  setAnalysisID(store, 'THAL_BETA');
});

// 監聽 controlSampleFile
watch(seqencingResultFile, async(newVal, oldVal) => {
  if (newVal !== oldVal) {
    await uploadFile([newVal]);
  }
});

</script>