<template>
  <q-card bordered :style="{ 'min-height': '100%' }">

    <!-- SMA v4 開發模式設定面板 -->
    <q-card-section>

      <!-- 警告視窗 -->
      <WarningDialog
        ref="warning_dialog"
        :error_message="dialog_error_message"
      />

      <!-- 標題 -->
      <div class="text-h5 text-uppercase text-bold text-blue-grey-7" style="margin-top: 1em;">
        Import
      </div>

      <!-- 功能區域 -->
      <div class="row justify-between" style="margin-top: 15px;">

        <!-- 說明文字 -->
        <span class="text-subtitle1">Please upload the corresponding standard control and sample result Excel files.</span>

        <!-- 功能按鈕區 -->
        <div style="margin-top: 1.5em;">
          <q-toggle style="margin-right: 1em;" v-model="usedSMN" :label="usedSMN === 'smn1' ? 'SMN1' : 'SMN2'" color="teal" false-value="smn1" true-value="smn2" />
          <q-btn style="margin-right: 0.5em;" color="primary" icon="mdi-upload" label="Upload" @click="smav4FileInputs.$el.click();"/>
          <q-btn-group push>
            <q-btn color="deep-orange" push glossy icon="save_as" label="New" @click="saveConfig('', true, false)"/>
            <q-btn color="brown-5" push glossy icon="auto_mode" label="Save" @click="saveConfig(currentDisplayedConfig, false, false)" ref="saveConfigBtn"/>
          </q-btn-group>
        </div>

        <!-- 隱藏的 file input -->
        <q-file
          ref="smav4FileInputs"
          multiple
          accept=".xlsx, .xls"
          style="display: none;"
          v-model="smav4FilesSelected"
        />

      </div>

    </q-card-section>

    <!-- SMA v4 檔案輸入區 -->
    <q-card-section>
      <q-form @submit="onSubmit" v-if="smav4Files.length > 0 || Object.keys(configs).length > 0">

        <!-- 顯示檔案管理區 -->
        <div style="display: flex; flex-direction: row; align-items: flex-start; justify-content: center;">

          <!-- 當前檔案顯示區 -->
          <div class="q-pa-md" style="width: 70%;">

            <!-- 檔案標題列 -->
            <div class="row" style="align-items: center; justify-content: space-between;">
              <span class="text-h5 text-bold text-grey-7 text-uppercase">File Bucket: {{ currentDisplayedConfig }}</span>
              <div class="row justify-start text-grey-7" v-if="smav4Files.length === 0">
                -- Click the upload button to add files. --
              </div>
            </div>

            <!-- 檔案列表 -->
            <div class="q-mt-md">
              <q-list bordered>
                <q-item v-for="file in smav4Files" :key="file.file_name" >

                  <!-- 檔案圖示 -->
                  <q-item-section avatar style="width: 30vw; display: flex; flex-wrap: nowrap; flex-direction: row; align-items: center; justify-content: flex-start;">
                    <q-icon color="indigo-6" name="mdi-microsoft-excel" />
                    <span style="margin-left: 1em; min-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" class="text-grey-7">{{ file.file_name }}</span>
                  </q-item-section>

                  <!-- SMN type Radio button -->
                  <q-item-section style="width: 65%; display: flex; flex-direction: row; align-items: center; justify-content: flex-end;">
                    <div class="q-gutter-sm">
                      <q-radio v-model="file.smnType" checked-icon="task_alt" unchecked-icon="panorama_fish_eye" val="smn1" label="SMN1" color="teal" />
                      <q-radio v-model="file.smnType" checked-icon="task_alt" unchecked-icon="panorama_fish_eye" val="smn2" label="SMN2" color="teal" />
                    </div>

                    <!-- Experiment type Dropdown button -->
                    <div style="margin-left: 15px;">
                      <q-btn-dropdown :color="typeColor[file.expType]" :label="getFormalSCName(file.expType)">
                        <q-list>
                          <q-item clickable v-close-popup @click="file.expType = 'std1'">
                            <q-item-section>
                              <q-item-label>{{ getFormalSCName("std1") }}</q-item-label>
                            </q-item-section>
                          </q-item>

                          <q-item clickable v-close-popup @click="file.expType = 'std2'">
                            <q-item-section>
                              <q-item-label>{{ getFormalSCName("std2") }}</q-item-label>
                            </q-item-section>
                          </q-item>

                          <q-item clickable v-close-popup @click="file.expType = 'sample'">
                            <q-item-section>
                              <q-item-label>{{ getFormalSCName("sample") }}</q-item-label>
                            </q-item-section>
                          </q-item>
                        </q-list>
                      </q-btn-dropdown>

                      <!-- Delete button -->
                      <q-btn style="margin-left: 15px;" size="md" outline icon="mdi-delete" color="grey" padding="sm" @click="deleteSMAv4File(file)"/>
                    </div>

                  </q-item-section>

                </q-item>
              </q-list>
            </div>

            <!-- 驗證訊息 -->
            <div class="row q-mt-lg justify-start">
              <span class="text-subtitle1" :style="{ 'color': messageColor }">{{ validateErrorMessage }}</span>
            </div>

          </div>

          <!-- 設定紀錄區-->
          <div class="q-pa-md" style="width: 35%;">

            <!-- 設定紀錄列表標題和搜尋框 -->
            <div class="row" style="display: flex; flex-direction: row; align-items: center; justify-content: space-between;">
              <span class="text-h5 text-bold text-grey-7">Configurations</span>
              <q-input dense rounded outlined v-model="searchConfig" label="Search Config" >
                <template v-slot:prepend>
                  <q-icon style="margin-right: 10px;" name="search" />
                </template>
              </q-input>
            </div>

            <!-- 設定檔列表 -->
            <div v-if="configs.length > 0" class="q-mt-md" style="max-height: 500px; overflow-y: auto; border: 1px solid #e0e0e0;">
              <q-list bordered>
                <div v-for="config in configs" :key="config.name" v-show="config.display">
                  <q-item clickable @click="currentDisplayedConfig = config.name" :class="currentDisplayedConfig === config.name? 'bg-indigo-1' : ''">
                    <q-item-section avatar>
                      <q-icon color="blue-grey-6" name="save" />
                    </q-item-section>
                    <q-item-section>
                      <label v-if="!config.edit">{{ config.name }}</label>
                      <q-input v-else v-model="editingConfigName" type="text" :borderless="false" dense :error="!config.validate" :error-message="config.errorMsg" :rules="[validateConfigName(config, editingConfigName)]" />
                    </q-item-section>
                    <q-item-section>
                      <div style="display: flex; flex-direction: row; align-items: flex-end; justify-content: flex-end;">
                        <q-btn :color="config.edit? 'green-8' : 'primary'" :icon="config.edit? 'mdi-check' : 'mdi-pencil'" flat @click.stop="editConfig(config)" padding="xs"/>
                        <q-btn color="red-8" icon="mdi-close" flat @click.stop="deleteConfig(config)" padding="xs"/>
                      </div>
                    </q-item-section>
                  </q-item>
                </div>
              </q-list>
            </div>
            <div v-else style="margin-top: 1em; text-align: center;">
              <span class="text-grey-7 text-bold"> -- No configuration found. -- </span>
            </div>

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
// import module
import { ref, onMounted, watch } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import { useQuasar, QSpinnerFacebook } from 'quasar';
import { v4 as uuidv4 } from 'uuid';

// 導入 composable
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';
import { setAnalysisID } from '@/composables/checkAnalysisStatus';
import { upload_files_to_storage } from '@/composables/storageManager';
import { CATEGORY_LIST } from '@/composables/storageManager';
import { update_userAnalysisData, getData, dataset_list, ANALYSIS_RESULT, EXPORT_RESULT } from '@/firebase/firebaseDatabase';
import { deleteData } from '@/firebase/firebaseDatabase';
import { submitWorkflow } from '@/composables/submitWorkflow';
import loggerV2 from '@/composables/loggerV2';

// import component
import WarningDialog from '@/components/WarningDialog.vue';

// 定義 Database 路徑
const dbSMAv4ResultPath = 'sma_v4_result';

// 使用者身份
const is_login = ref(false);
const user_info = ref(null);

// 當前的分析 ID
const currentAnalysisID = ref(null);

// 控制警告視窗
const dialog_error_message = ref("");
const warning_dialog = ref(null);

// utility
const store = useStore();
const $q = useQuasar();
const router = useRouter();
const getCurrentInstrument = () => {
  return store.getters["analysis_setting/getSettingProps"].instrument;
}

/* UI 顯示相關 */
const messageColor = ref('red');
const validateErrorMessage = ref('');
const typeColor = {
  std1: 'red-4',
  std2: 'pink-4',
  sample: 'teal-4',
}
const usedSMN = ref('smn1');

/* Config 相關 */
const searchConfig = ref('');                     // 搜尋列用 Config name
const configs = ref([]);                          // Config 列表
const loadedConfigs = ref([]);                    // Database 載入的 Config
const currentDisplayedConfig = ref('');           // 當前顯示 Config name
const editingConfigName = ref('');                // 編輯中的 Config name
const databaseConfigPath = 'smav4_import_config'; // Database 中 Config 的路徑

// 定義 config (UI 顯示用)
const DISPLAY_CONFIG = (new_name) => {
  const defined_config = {
    name: new_name,
    editable: false,
    display: true,
    validate: true,
    errorMsg: '',
  }
  return defined_config;
}

// 取得 Database 中的 Config
const getConfigsFromDatabase = async () => {
  const dataPath = `${dataset_list.user_analysis}/${user_info.value.uid}/${databaseConfigPath}`;
  const response = await getData(dataPath);
  if (response.status === 'success') {
    return response.data;
  }
  else {
    console.error(response.message);
    return [];
  }
}

// 更新 configs
async function updateConfigs() {

  // 取得 Database 中的 Config
  const configs_from_database = await getConfigsFromDatabase();

  // 清空 configs 和 loadedConfigs
  configs.value = [];
  loadedConfigs.value = [];

  // 將 Database 中的 Config 加入到 configs 和 loadedConfigs
  configs_from_database.forEach((load_config) => {
    configs.value.push(DISPLAY_CONFIG(load_config.id));
    loadedConfigs.value.push(load_config);
  });
}

// 儲存 Config
async function saveConfig(config_name, clear_smav4Files = true, mute = true) {
  // 顯示 loading 視窗
  $q.loading.show();

  // 設定 Config 名稱
  let setConfigName = null;

  // 如果 name 不存在, 新增 Config
  if (config_name === '') {

    // (DEPRECATED) 重置 peakSetting
    // peakSettingRef.value.resetSettings();

    // 如果 clear_smav4Files 為 true, 則清空 smav4Files
    if (clear_smav4Files) {
      smav4Files.value = [];
    }

    // 新增 Config
    const new_config_name = `config_${generateConfigID()}`;
    configs.value.push(DISPLAY_CONFIG(new_config_name));
    setConfigName = new_config_name;

    // 設定當前顯示的 Config
    currentDisplayedConfig.value = new_config_name;
  }
  // 如果 name 存在, 更新現有的 Config
  else {
    setConfigName = config_name;
    currentDisplayedConfig.value = config_name;
  }

  // 更新資料庫
  const data = {files: smav4Files.value, peak_condition: currentPeakCondition.value};
  if (setConfigName !== null) {
    update_userAnalysisData(user_info.value.uid, databaseConfigPath, data, setConfigName);
  } else {
    console.error("Config save failed: setConfigName is null");
  }

  // 隱藏 loading 視窗
  $q.loading.hide();

  // 通知
  if (config_name !== '' && !mute) {
    $q.notify({
      message: 'Config saved',
      color: 'green',
      icon: 'mdi-check',
      position: 'top',
      timeout: 300,
      progress: true,
    });
  }
}

// 編輯設定檔
async function editConfig(target_config) {

  // 如果 validate 為 false, 則不進行編輯
  if (target_config.validate === false) {return;}

  // 切換編輯狀態
  target_config.edit = !target_config.edit;

  // 如果編輯狀態為 false, 則更新設定檔名稱
  if (target_config.edit === false) {

    const dataPath = `${dataset_list.user_analysis}/${user_info.value.uid}/${databaseConfigPath}`;
    await deleteData(dataPath, target_config.name);

    // 更新設定檔名稱
    target_config.name = editingConfigName.value;

    // 更新 database
    await saveConfig(target_config.name, false, false);
  }
  else {
    editingConfigName.value = target_config.name;
  }
}

// 檢查新輸入的設定檔名稱
function validateConfigName(target_config, val) {
  if (!val || val.trim() === '') {
    target_config.validate = false;
    target_config.errorMsg = '請輸入名稱';
  }
  else if (configs.value.some(config => config.name === val) && target_config.name !== val) {
    target_config.validate = false;
    target_config.errorMsg = '名稱已經被使用';
  }
  else {
    target_config.validate = true;
    target_config.errorMsg = '';
  }
}

// 刪除設定檔
async function deleteConfig(config) {
  // 刪除 Database 中的 Config
  const dataPath = `${dataset_list.user_analysis}/${user_info.value.uid}/${databaseConfigPath}`;
  await deleteData(dataPath, config.name);

  // 更新設定檔和當前顯示的設定檔
  await updateConfigs();
  if (configs.value.length > 0) {
    currentDisplayedConfig.value = configs.value[0].name;
  } else {
    currentDisplayedConfig.value = '';
  }
}

// 產生唯一 ID
function generateConfigID() {
  return Math.random().toString(36).substring(5, 10) + Math.random().toString(36).substring(5, 10);
}

// 依照搜尋列更新設定檔顯示
watch(searchConfig, (new_search) => {
  for (const item in configs.value) {
    configs.value[item].display = configs.value[item].name.includes(new_search);
  }
});

// 依照當前顯示的 Config ID 更新設定檔
watch(currentDisplayedConfig, async (new_config) => {
  // 初始化 validateErrorMessage
  validateErrorMessage.value = ''

  // 更新設定檔
  await updateConfigs();

  // 取得當前顯示的 Config
  const current_config = loadedConfigs.value.find((config) => config.id === new_config);

  // 將 Config 的 files 更新到 smav4Files
  if (current_config) {
    smav4Files.value = current_config.files;
  } else {
    smav4Files.value = [];
  }
});

/* 檔案設定相關 */
const smav4Files = ref([]);             // 顯示用
const smav4FileInputs = ref(null);      // 儲存檔案用
const smav4FilesSelected = ref([]);     // 選擇的檔案

// 定義 SMA v4 檔案
const DEFINED_SMAV4FILE = (file_name, file_path) => {
  const defined_file = {
    file_name: file_name,
    path: file_path,
    smnType: usedSMN.value,
    expType: 'sample',
  }
  return defined_file;
}

// 選擇檔案後立即上傳
async function uploadFile(file_list) {

  // 顯示 loading 視窗
  $q.loading.show();

  // 存到當前使用者
  const user_uid = user_info.value.uid;

  // 存到 SMA data 資料夾
  const category = CATEGORY_LIST.sma_import;

  // 上傳檔案
  const uploading = await Promise.all(file_list.map(async (file) => {
    return await upload_files_to_storage(
      file, user_uid, category, currentAnalysisID.value.analysis_uuid, getCurrentInstrument()
    ).then((response) => {return response;});
  }));

  // 初始化 error message
  dialog_error_message.value = "";

  // 檢查是否有 error
  if (uploading.some(res => res.status === 'error')) {

    // 找出 error 的檔案
    const error_file = uploading.filter(res => res.status === 'error');

    // 印出 error 的檔案
    let error_message = error_file.map(res => res.message).join(';');

    // 捕抓 timeout 的錯誤
    if (error_message.includes("Timeout")) {
      error_message = "由於連線問題檔案上傳逾時, 請重新整理頁面, 稍後再試一次！";
    }

    // 印出 error message
    const message = error_message;
    const source = 'ImportSMAQsep.vue line.483';
    const user = user_info.value.email;
    loggerV2.error(message, source, user);
  }

  // 更新 file_list 中 file 的 path
  else {
    file_list.forEach((file) => {
      file.path = uploading.find((res) => res.file === file.name).storage_path;
    });
  }

  // 隱藏 loading 視窗
  $q.loading.hide();
}

// 更新 SMA v4 檔案
watch(smav4FilesSelected, async (newVal, oldVal) => {

  // 取得新增的檔案
  const addedFiles = newVal.filter(newfile => !oldVal.find(oldfile => newfile.name === oldfile.name));

  // 如果新增的檔案存在, 則上傳
  if (addedFiles.length > 0) {

    // 顯示 loading 視窗
    $q.loading.show();

    // 上傳檔案
    await uploadFile(addedFiles);

    // 加入到 smav4Files
    addedFiles.forEach((file) => {
      smav4Files.value.push(DEFINED_SMAV4FILE(file.name, file.path));
    });

    // 如果沒有設定檔, 則新增一個設定檔
    if (configs.value.length === 0) {
      await saveConfig('', false);
    }

    // 更新設定檔
    if (currentDisplayedConfig.value) {
      await saveConfig(currentDisplayedConfig.value, false);
    }

    // 隱藏 loading 視窗
    $q.loading.hide();
  }

}, { deep: true });

// 更新列表中 SMA v4 檔案
watch(smav4Files, async (newVal, oldVal) => {
  if (oldVal.length > 0) {
    await saveConfig(currentDisplayedConfig.value);
  }
}, { deep: true });

// 刪除列表中 SMA v4 檔案
async function deleteSMAv4File(file) {
  smav4Files.value = smav4Files.value.filter((f) => f.file_name !== file.file_name);
  if (currentDisplayedConfig.value) {
    await saveConfig(currentDisplayedConfig.value, false);
  }
}

/* 開發模式參數設置 */
// (DEPRECATED) const peakSettingRef = ref(null);
const saveConfigBtn = ref(null);
const currentPeakCondition = ref(null);

// (DEPRECATED) 更新峰值選擇範圍
/*
function update_current_peak_condition(new_peak_condition) {
  currentPeakCondition.value = new_peak_condition;
}
*/

// 取得正式的 SC 名稱
const getFormalSCName = (name) => {
  switch (name) {
    case 'std1':
      return 'SC-C';
    case 'std2':
      return 'SC-N';
    case 'sample':
      return 'Sample';
    default:
      return name;
  }
}

// 驗證 SMA v4 輸入
const validateSMAv4Input = (file_list) => {

  // 1. 檢查是否有檔案輸入
  if (file_list.length === 0) {
    validateErrorMessage.value = "* 尚未上傳任何檔案";
    return false;
  }

  // 2. 檢查是否有選擇 SMN1-std1, SMN1-std2, SMN2-std1, SMN2-std2, 且數量都是 1
  for (const smn of ['smn1', 'smn2']) {
    for (const std of ['std1', 'std2']) {
      const file_count = file_list.filter(file => file.smnType === smn && file.expType === std).length;
      if (file_count !== 1) {
        validateErrorMessage.value = `* ${smn}-${std} 檔案數量不正確, 標準品數量應為 1.`;
        return false;
      }
    }
  }

  // 3. 如果沒有錯誤, 則回傳 true
  return true;
}

// 解析 SMA v4 檔案
const parseSMAv4Input = (file_list) => {
  let smav4InputFilesObj = {
    smn1_std1: null,
    smn1_std2: null,
    smn2_std1: null,
    smn2_std2: null,
    smn1_samples: [],
    smn2_samples: []
  };

  // 解析 SMA v4 檔案
  for (const file of file_list) {
    if (file.smnType === 'smn1' && file.expType === 'std1') {
      smav4InputFilesObj.smn1_std1 = file.path;
    }
    else if (file.smnType === 'smn1' && file.expType === 'std2') {
      smav4InputFilesObj.smn1_std2 = file.path;
    }
    else if (file.smnType === 'smn1' && file.expType === 'sample') {
      smav4InputFilesObj.smn1_samples.push(file.path);
    }
    else if (file.smnType === 'smn2' && file.expType === 'std1') {
      smav4InputFilesObj.smn2_std1 = file.path;
    }
    else if (file.smnType === 'smn2' && file.expType === 'std2') {
      smav4InputFilesObj.smn2_std2 = file.path;
    }
    else if (file.smnType === 'smn2' && file.expType === 'sample') {
      smav4InputFilesObj.smn2_samples.push(file.path);
    }
  }

  // 回傳解析後的 SMA v4 檔案
  return smav4InputFilesObj;
}

// 定義 SMA v4 的 result object
const SMAv4_RESULT = (
  STD_DATA,
  SAMPLE_DATA,
  COPY_NUMBER_RANGES,
  RESULT_LIST,
  PARAMETERS,
  INPUT_FILE_OBJ,
  USE_CONFIG_NAME
) => {

  // 目前沒有特殊處理, 直接回傳
  return {
    STD_DATA,
    SAMPLE_DATA,
    COPY_NUMBER_RANGES,
    RESULT_LIST,
    PARAMETERS,
    INPUT_FILE_OBJ,
    USE_CONFIG_NAME
  }
}

// 取得 control_ids
const getControlID = (smav4InputFilesObj) => {

  // 取得檔名並且移除附檔名
  const simplifyFilePath = (file_path) => {
    if (!file_path) return '';

    // 先取得檔案名稱（移除路徑）
    const fileName = file_path.split('/').pop();

    // 移除附檔名
    return fileName.replace(/\.[^.]+$/, '');
  }

  return [
    simplifyFilePath(smav4InputFilesObj.smn1_std1),
    simplifyFilePath(smav4InputFilesObj.smn1_std2),
    simplifyFilePath(smav4InputFilesObj.smn2_std1),
    simplifyFilePath(smav4InputFilesObj.smn2_std2),
  ]
}

const smnTypeInterpretation = (smn1, smn2) => {
  const type = String(smn1) + String(smn2);

  const isNormal = (typeArray) => [
    "20", "21", "22", "23", "24",
    "30", "31", "32", "33", "34",
    "41", "42", "43", "44"
  ].includes(typeArray);

  const isCarrier = (typeArray) => ["10", "11", "12", "13", "14"].includes(typeArray);
  const isAffected = (typeArray) => ["01", "02", "03", "04"].includes(typeArray);

  if (isNormal(type)) {
    return { value: "normal", label: "Normal" };
  } else if (isCarrier(type)) {
    return { value: "carrier", label: "SMA carrier" };
  } else if (isAffected(type)) {
    return { value: "affected", label: "SMA affected" };
  } else {
    return { value: "invalid", label: "Invalid" };
  }
};

/* 主程式 */
async function onSubmit() {

  // 先存設定
  saveConfigBtn.value.click();

  // *. 顯示 loading 視窗
  $q.loading.show({
    spinner: QSpinnerFacebook,
    spinnerColor: "deep-orange-6",
    spinnerSize: 100,
    message: "Analyzing...",
    messageColor: "white",
  });

  // 檔案輸入
  const FileCheckList = smav4Files.value;
  const validateFiles = validateSMAv4Input(FileCheckList);
  if (!validateFiles) {
    $q.loading.hide();
    return;
  }

  // 解析 SMA v4 檔案
  const smav4InputFilesObj = parseSMAv4Input(FileCheckList);

  // 取得 control_ids
  const control_id = getControlID(smav4InputFilesObj);

  // inputData
  const InputData = { file_path: smav4InputFilesObj };

  // 取得 settingProps
  const currentSettingProps = store.getters["analysis_setting/getSettingProps"];

  // 執行 submitWorkflow
  const analysisResult = await submitWorkflow('SMA', InputData, user_info.value, currentSettingProps);

  // 檢查有沒有出錯
  if (analysisResult.status == 'success'){
    dialog_error_message.value = "";

    // 將 result 中 Infinity 轉換成 null
    const resultStr = analysisResult.result.replace(/Infinity/g, 'null');
    const resultObj = JSON.parse(resultStr);

    // 製作 SMAv4_RESULT
    const SMAv4_Result = SMAv4_RESULT(
      resultObj.STD_DATA,
      resultObj.SAMPLE_DATA,
      resultObj.COPY_NUMBER_RANGES,
      resultObj.RESULT_LIST,
      resultObj.PARAMETERS,
      smav4InputFilesObj,
      currentDisplayedConfig.value
    );

    // 製作 EXPORT_RESULT
    const sample_list = Object.keys(SMAv4_Result.RESULT_LIST);
    const exportResult = sample_list.map((sample_name, index)=>{
      const smn1 = SMAv4_Result.RESULT_LIST[sample_name].smn1_copy_number;
      const smn2 = SMAv4_Result.RESULT_LIST[sample_name].smn2_copy_number;
      const smnAssessment = smnTypeInterpretation(smn1, smn2);
      return EXPORT_RESULT(
        index+1,
        sample_name,
        SMAv4_Result.RESULT_LIST[sample_name].typeStr,
        [SMAv4_Result.RESULT_LIST[sample_name].typeStr],
        smnAssessment.value,
        smnAssessment.label
      )
    })

    // 製作 ANALYSIS_RESULT
    const AnalysisResult = ANALYSIS_RESULT(
      "SMAv4",
      currentAnalysisID.value.analysis_uuid,
      resultObj.config,
      control_id,
      resultObj.qc_status,
      resultObj.errMsg,
      SMAv4_Result,
      exportResult
    );

    // 將結果存到 firestore
    update_userAnalysisData(user_info.value.uid, dbSMAv4ResultPath, AnalysisResult, currentAnalysisID.value.analysis_uuid);

    // 更新 currentDisplayAnalysisID
    store.commit("analysis_setting/updateCurrentDisplayAnalysisID", {
      analysis_name: "SMAv4",
      analysis_uuid: currentAnalysisID.value.analysis_uuid,
    });

    // 更新 currentAnalysisID
    const new_id = `analysis_${uuidv4()}`;
    store.commit('analysis_setting/updateCurrentAnalysisID', {
      analysis_name: 'SMAv4',
      analysis_uuid: new_id,
    });
    currentAnalysisID.value = store.getters['analysis_setting/getCurrentAnalysisID'];

    // 清除 store 的 subjectInfoTable 和 LabInfomation
    store.commit("export_page_setting/initExportPageSetting");

    // 隱藏 loading 視窗
    $q.loading.hide();

    // 跳轉到分析結果頁面
    setTimeout(()=>{
      router.push({path: '/page-preview'});
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

// 掛載時執行
onMounted(async () => {
  // 取得使用者身份
  const { login_status } = updateGetUserInfo();
  is_login.value = login_status.value.is_login;
  user_info.value = login_status.value.user_info;

  // 先嘗試取得當前的分析 ID, 如果沒有則建立新的分析 ID
  currentAnalysisID.value = store.getters['analysis_setting/getCurrentAnalysisID'];
  setAnalysisID(store, 'SMAv4');

  // 更新設定檔
  await updateConfigs();

  // 如果設定檔存在, 則顯示第一個設定檔
  if (configs.value.length > 0) {
    currentDisplayedConfig.value = configs.value[0].name;
  }
});

</script>
