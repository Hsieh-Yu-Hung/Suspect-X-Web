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

        <!-- FAM file -->
        <div class="q-gutter-sm" v-if="getCurrentReagent() == 'accuinMTHFR3'">
          <q-file
            v-model="famFile"
            use-chips
            color="deep-orange-6"
            stack-label
            label="FAM (465-533) result .txt file"
            :rules="[(val) => val || `Please select FAM result txt file`]"
            accept=".txt"
            lazy-rules
          >
            <template v-slot:before>
              <q-icon name="mdi-text-box-outline" />
            </template>
          </q-file>
        </div>

        <!-- VIC file -->
        <div class="q-gutter-sm" v-if="getCurrentReagent() == 'accuinMTHFR3'">
          <q-file
            v-model="vicFile"
            use-chips
            color="deep-orange-6"
            stack-label
            label="VIC/HEX (523-580) result .txt file"
            :rules="[(val) => val || `Please select VIC result txt file`]"
            accept=".txt"
            lazy-rules
          >
            <template v-slot:before>
              <q-icon name="mdi-text-box-outline" />
            </template>
          </q-file>
        </div>

        <!-- 上傳檔案 -->
        <div class="q-gutter-sm" v-if="getCurrentReagent() != 'accuinMTHFR3'">
          <q-file
            v-model="resultFile"
            use-chips
            color="deep-orange-6"
            stack-label
            label="Sample result"
            :rules="[(val) => val || `Please select ONE sample result`]"
            :accept="getCurrentInstrument() === 'qs3'? '.xlsx, .xls' : '.csv'"
            lazy-rules
          >
            <template v-slot:before>
              <q-icon :name="getCurrentInstrument() === 'qs3'? 'mdi-microsoft-excel' : 'mdi-file-delimited-outline'" />
            </template>
          </q-file>
        </div>

        <!-- 96-well plate positions Select: Title -->
        <div class="row">
          <q-icon
            name="mdi-pencil-circle-outline"
            size="sm"
            color="grey-7"
            label="96-well plate positions"
            class="q-ql-xs"
          />
          <q-item-label class="q-ml-sm" style="color: #757575; font-size: 90%">
            96-well plate positions
          </q-item-label>
        </div>

        <!-- 96-well plate positions Select: Control -->
        <div class="row">
          <div class="col">
            <q-select
              v-model="Ctrlwell.X"
              :options="wellXArray"
              color="deep-orange-6"
              options-dense
              stack-label
              label="Control"
              :rules="[(val) => WELL(val, Ctrlwell.Y) || `Please select row of Control`]"
              reactive-rules
            >
              <template v-slot:before>
                <q-icon name="" />
              </template>
            </q-select>
          </div>
          <div class="col">
            <q-select
              v-model="Ctrlwell.Y"
              :options="wellYArray"
              color="deep-orange-6"
              options-dense
              label=""
              :rules="[(val) => WELL(Ctrlwell.X, val) || `Please select column of Control`]"
              reactive-rules
            >
            </q-select>
          </div>
        </div>

        <!-- 96-well plate positions Select: NTC -->
        <div class="row">
          <div class="col">
            <q-select
              v-model="NTCwell.X"
              :options="wellXArray"
              color="deep-orange-6"
              options-dense
              stack-label
              label="NTC"
              :rules="[(val) => WELL(val, NTCwell.Y) || `Please select row of NTC`]"
              reactive-rules
            >
              <template v-slot:before>
                <q-icon name="" />
              </template>
            </q-select>
          </div>
          <div class="col">
            <q-select
              v-model="NTCwell.Y"
              :options="wellYArray"
              color="deep-orange-6"
              options-dense
              label=""
              :rules="[(val) => WELL(NTCwell.X, val) || `Please select column of NTC`]"
              reactive-rules
            >
            </q-select>
          </div>
        </div>

        <!-- 送出按鈕 -->
        <div class="row q-mt-lg justify-end">
          <q-btn label="Analyze" type="submit" color="blue-grey-7" />
        </div>

      </q-form>
    </q-card-section>
  </q-card>
</template>

<script setup>
// Import modules
import { ref, onMounted, watch } from 'vue';
import { useStore } from 'vuex';
import { useQuasar, QSpinnerFacebook } from 'quasar';
import { v4 as uuidv4 } from 'uuid';

// 元件
import WarningDialog from '@/components/WarningDialog.vue';

// 導入 composable
import { submitWorkflow } from '@/composables/submitWorkflow';
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';
import { CATEGORY_LIST, upload_files_to_storage } from '@/utility/storageManager';

// 取得 store, 和 Quasar
const store = useStore();
const $q = useQuasar();

// Definition
const WELL = (setX = null, setY = null) => {
  return { X: setX, Y: setY };
}

// consts
const resultFile = ref(null);
const famFile = ref(null);
const vicFile = ref(null);
const Ctrlwell = ref(WELL());
const NTCwell = ref(WELL());

// 使用者身份
const is_login = ref(false);
const user_info = ref(null);

// 控制警告視窗
const dialog_error_message = ref("");
const warning_dialog = ref(null);

// 當前的分析 ID
const currentAnalysisID = ref(null);

// 下拉式選單選項, 96-well plate positions
const wellXArray = ref(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']);
const wellYArray = ref(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']);

// 取得 settingProps
function getCurrentInstrument() {
  return store.getters["analysis_setting/getSettingProps"].instrument;
}
function getCurrentReagent() {
  return store.getters["analysis_setting/getSettingProps"].reagent;
}

// functions
async function onSubmit() {
  // *. 顯示 loading 視窗
  $q.loading.show({
    spinner: QSpinnerFacebook,
    spinnerColor: "deep-orange-6",
    spinnerSize: 100,
    message: "Analyzing...",
    messageColor: "white",
  });

  // 輸入
  let checkList = [];
  if (resultFile.value) checkList.push(resultFile.value);
  if (famFile.value) checkList.push(famFile.value);
  if (vicFile.value) checkList.push(vicFile.value);

  const MthfrInputData = {
    file_path: resultFile.value ? resultFile.value.path : null,
    control_well: Ctrlwell.value,
    ntc_well: NTCwell.value,
    instrument: getCurrentInstrument(),
    reagent: getCurrentReagent(),
    FAM_file_path: famFile.value ? famFile.value.path : null,
    VIC_file_path: vicFile.value ? vicFile.value.path : null,
  }

  // 取得 settingProps
  const currentSettingProps = store.getters["analysis_setting/getSettingProps"];

  // 執行 submitWorkflow
  const analysisResult = await submitWorkflow(checkList, 'MTHFR', MthfrInputData, user_info.value, currentSettingProps);

  // 檢查有沒有出錯
  if (analysisResult.status == 'success'){
    dialog_error_message.value = "";

    // 印出 analysisResult, 從這裡繼續
    console.log("analysisResult",analysisResult.result);
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
  }

  // 更新 currentAnalysisID
  const new_id = `analysis_${uuidv4()}`;
  store.commit('analysis_setting/updateCurrentAnalysisID', {
    analysis_name: "MTHFR",
    analysis_uuid: new_id,
  });
  currentAnalysisID.value = store.getters['analysis_setting/getCurrentAnalysisID'];

  // *. 隱藏 loading 視窗
  $q.loading.hide();

}

// 選擇後上傳檔案
async function uploadFile(file, analysisID, subDir) {

  // 如果沒有檔案, 則返回
  if (!file) return;

  // 顯示 loading 視窗
  $q.loading.show();

  // 存到當前使用者
  const user_uid = user_info.value.uid;

  // 存到 Apoe data 資料夾
  const category = CATEGORY_LIST.mthfr_import;

  // 上傳檔案
  const uploading = await upload_files_to_storage(
    file, user_uid, category, analysisID, subDir
  );

  // 初始化 error message
  dialog_error_message.value = "";

  // 檢查是否有 error
  if (uploading.status === 'error'){
    dialog_error_message.value = uploading.message;
    warning_dialog.value.open_warning_dialog();
  }
  else {
    file.path = uploading.storage_path;
  }

  // 隱藏 loading 視窗
  $q.loading.hide();
}

// 掛載時
onMounted(() => {
  // 取得使用者身份
  const { login_status } = updateGetUserInfo();
  is_login.value = login_status.value.is_login;
  user_info.value = login_status.value.user_info;

  // 先嘗試取得當前的分析 ID, 如果沒有則建立新的分析 ID
  currentAnalysisID.value = store.getters['analysis_setting/getCurrentAnalysisID'];
  if (currentAnalysisID.value.analysis_uuid == null) {
    const new_id = `analysis_${uuidv4()}`;
    store.commit('analysis_setting/updateCurrentAnalysisID', {
      analysis_name: "MTHFR",
      analysis_uuid: new_id,
    });
  }
});

// 監聽 resultFile
watch(resultFile, (newVal, oldVal) => {
  if (newVal !== oldVal){
    const subDir = getCurrentInstrument();
    uploadFile(newVal, currentAnalysisID.value.analysis_uuid, subDir);
  }
});

// 監聽 famFile
watch(famFile, (newVal, oldVal) => {
  if (newVal !== oldVal){
    const subDir = getCurrentInstrument();
    uploadFile(newVal, currentAnalysisID.value.analysis_uuid, subDir);
  }
});

// 監聽 vicFile
watch(vicFile, (newVal, oldVal) => {
  if (newVal !== oldVal){
    const subDir = getCurrentInstrument();
    uploadFile(newVal, currentAnalysisID.value.analysis_uuid, subDir);
  }
});

// 監聽 currentInstrument
watch(getCurrentInstrument, () => {
  // 如果 currentInstrument 變化, 則清除 resultFile
  resultFile.value = null;
  famFile.value = null;
  vicFile.value = null;
  Ctrlwell.value = WELL();
  NTCwell.value = WELL();
});

</script>
