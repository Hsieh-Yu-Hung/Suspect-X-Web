<template>
  <q-card bordered :style="{ 'min-height': '100%' }">

    <!-- 警告視窗 -->
    <WarningDialog
      ref="warning_dialog"
      :error_message="dialog_error_message"
    />

    <!-- 標題 -->
    <q-card-section>
      <div style="display: flex; flex-direction: row; gap: 1em;">
        <div style="width:50%;">
          <div class="text-h5 text-uppercase text-bold text-blue-grey-7">
            Import
          </div>
          <div class="text-subtitle1">
            Please upload the Sanger Sequencer result <b>*.ab1</b> file.
          </div>
        </div>
        <div style="width:50%;">
          <div style="height: 100%; display: flex; flex-direction: row; gap: 2em; align-items: center; justify-content: space-between;">
            <div style="display: flex; flex-direction: row; gap: 0.4em; align-items: center;">
              <q-icon name="mdi-history" size="1.5em" color="blue-grey-7" />
              <span class="text-h5 text-uppercase text-bold text-blue-grey-7">History</span>
            </div>
            <div style="width: 100%;">
              <q-select
                clearable
                label="You can load previous analysis settings here."
                filled dense v-model="selected_history"
                :options="history_options"
                style="width: 100%;"
              />
            </div>
          </div>
        </div>
      </div>
    </q-card-section>

    <!-- 輸入表單區 -->
    <q-card-section>

      <!-- 輸入表單區 -->
      <div style="display: flex; flex-direction: row; gap: 1em;">

        <!-- Sample 分組列表 + 開發設定版面 -->
        <div class="col" style="width: 70%; border: 1px dashed #e0e0e0; padding: 1em;">

          <!-- Sample 分組列表(上)/開發設定版面(下) -->
          <div>

            <!-- 上傳 Sanger Sequencer 結果 -->
            <div>

              <div style="display: flex; flex-direction: row; gap: 1em; align-items: center; justify-content: space-between;">
                <!-- 標題 -->
                <span class="text-bold text-h6 text-blue-grey-7">
                  Sample List
                </span>

                <!-- 隱藏一個 q-file 用來上傳 Sample 的檔案 -->
                <q-file
                  ref="uploaded_sampleList_file_input"
                  v-model="uploaded_sample_file"
                  label=""
                  multiple
                  style="display: none;"
                />

                <!-- 新增樣本 -->
                <q-btn
                  label="Add Sample"
                  color="blue-4"
                  text-color="white"
                  icon="mdi-plus"
                  @click="addSample"
                />
              </div>

              <div v-if="sampleList_row.length > 0" style="margin-block: 1em;">
                <q-table
                  :columns="sampleList_column"
                  :rows="sampleList_row"
                  row-key="index"
                  selection="single"
                  v-model:selected="selected_sample"
                  :rows-per-page-options="[1000]"
                >

                  <!-- Sample 名稱 -->
                  <template v-slot:body-cell-Sample_Name="props">
                    <q-td class="text-center">
                      <q-input
                        style="min-width: 15em;"
                        v-model="props.row.sample_name"
                        dense
                        outlined
                        class="text-center"
                      />
                    </q-td>
                  </template>

                  <!-- 顯示上傳的檔案 -->
                  <template v-slot:body-cell-Sequencing_Files="props">
                    <q-td class="text-center">
                      <div v-if="props.row.sequencing_files.length > 0" style="display: flex; flex-direction: column;">
                        <q-chip
                          v-for="file in props.row.sequencing_files"
                          :key="file.file_name"
                          :label="file.file_name"
                          color="grey-3"
                          text-color="deep-orange-6"
                          dense
                          removable
                          @remove="removeFile(file, props.row)"
                          icon="mdi-file-document-outline"
                          style="min-width: 16em; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"
                        />
                      </div>
                      <div v-else>
                        <span class="text-subtitle2 text-grey-6"> Please upload <b>2</b> files </span>
                      </div>
                    </q-td>
                  </template>

                  <!-- 功能按鈕 -->
                  <template v-slot:body-cell-Function_Buttons="props">
                    <q-td class="text-center" style="width: 10%;">

                      <!-- 按鈕群組 -->
                      <div style="display: flex; flex-direction: row; gap: 2em; justify-content: right;">

                        <!-- 上傳檔案 -->
                        <q-btn
                          label=""
                          color="grey-1"
                          text-color="green-4"
                          round
                          icon="note_add"
                          dense
                          @click="uploadSampleListFile(props.row.index)"
                        />

                        <!-- 刪除 -->
                        <q-btn
                          label=""
                          color="grey-1"
                          text-color="red-8"
                          round
                          icon="mdi-delete"
                          dense
                          @click="removeSample(props.row)"
                        />
                      </div>

                    </q-td>
                  </template>

                </q-table>
              </div>

              <div style="width: 100%; margin-block: 1em; text-align: center;" v-else>
                <span class="text-subtitle2 text-deep-orange-6"> -- Click <b>+ ADD SAMPLE</b> to add a new sample -- </span>
              </div>

            </div>

            <!-- 開發設定版面 -->
            <div style="margin-block: 2em; background-color: rgba(221, 232, 243, 0.2); border-radius: 10px; padding: 10px;">
              <!-- 開發設定標題 -->
              <div class="row" style="display: flex; flex-direction: row; justify-content: space-between; align-items: center;">
                <span class="text-bold text-h6 text-blue-grey-7">
                  Development Settings
                </span>
                <q-btn dense flat label="Load Testing" icon="mdi-download" text-color="indigo-7" @click="loadTestingSamples" />
              </div>

              <!-- 開發設定參數:Left-Trim, Right-Trim -->
              <div class="q-mt-md">
                <div class="row" style="display: flex; flex-direction: row; gap: 5em; align-items: center;">
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

          </div>

        </div>

        <!-- FileBucket -->
        <div class="col-1" style="width: 30%; border: 1px dashed #e0e0e0; padding: 1em;">
          <!-- 開發設定標題 -->
          <div class="row" style="display: flex; flex-direction: row; justify-content: space-between; align-items: center;">
            <span class="text-bold text-h6 text-blue-grey-7">File Bucket</span>
            <div style="display: flex; flex-direction: row; gap: 1em; align-items: center;">
              <q-btn dense label="" icon="mdi-reply-all" color="brown-13" @click="loadFileToSampleList()" />
              <q-btn dense label="" icon="mdi-upload" color="indigo-7" @click="seqencingResultFileInput.pickFiles()" />
            </div>
          </div>
          <div class="row q-mt-md" v-if="file_bucket_list.length > 0">
            <q-list dense bordered padding class="rounded-borders" style="width: 100%; max-height: 500px; overflow-y: auto;">
              <q-item v-for="file in file_bucket_list" :key="file.file_name">
                <div style="width: 100%; display: flex; flex-direction: row; justify-content: space-between; align-items: center;">
                  <div style="display: flex; flex-direction: row; gap: 1em; align-items: center;">
                    <q-checkbox v-model="selected_files" :val="file.file_name" />
                    <q-icon size="1.2em" color="grey-7" name="mdi-file-document-outline" />
                    <span style="max-width: 15em; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" class="text-subtitle2 text-blue-grey-7">{{ file.file_name }}</span>
                  </div>
                  <div style="display: flex; flex-direction: row; align-items: center;">
                    <q-btn size="xs" round dense label="" icon="mdi-close" color="red-7" @click="removeBucketFile(file)" />
                  </div>
                </div>
              </q-item>
            </q-list>
          </div>
          <div class="row q-mt-md" style="margin-top: 2em; display: flex; flex-direction: column; justify-content: center; align-items: center; width: 100%;" v-else>
            <span class="text-subtitle2 text-deep-orange-6"> -- Please upload some file. -- </span>
          </div>
          <q-file
            ref="seqencingResultFileInput"
            v-model="seqencingResultFile"
            label=""
            filled
            dense
            multiple
            style="display: none;"
          />
        </div>

      </div>

      <!-- 分析按鈕 -->
      <div class="row q-mt-lg justify-end">
        <q-btn label="Analyze" color="blue-grey-7" @click="onSubmit" />
      </div>

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
import { doc, getDoc, collection, getDocs } from 'firebase/firestore';
import { deleteFile, listAllFilesInFolder } from '@/firebase/firebaseStorage';
import { submitWorkflow } from '@/composables/submitWorkflow';
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';
import { CATEGORY_LIST, upload_files_to_storage } from '@/composables/storageManager';
import { setAnalysisID } from '@/composables/checkAnalysisStatus';
import { ANALYSIS_RESULT, EXPORT_RESULT, update_userAnalysisData, dataset_list, Database } from '@/firebase/firebaseDatabase';

// 引入元件
import WarningDialog from '@/components/WarningDialog.vue';
import loggerV2 from '@/composables/loggerV2';

// 控制警告視窗
const dialog_error_message = ref("");
const warning_dialog = ref(null);

// 定義 ThalBeta 的 database 路徑
const dbThalBetaResultPath = "thalbeta_result";
const storageThalBetaPath = "thal_beta_import";
const databaseConfigPath = 'thalbeta_import_config';

// 定義 seqencingResultFileInput
const seqencingResultFileInput = ref(null);

// 定義 uploaded_sampleList_file_input
const uploaded_sampleList_file_input = ref(null);
const uploaded_sample_file = ref([]);
const addFileSampleIndex = ref(null);

// 導入 store, Quasar
const store = useStore();
const router = useRouter();
const $q = useQuasar();

// 使用者身份
const is_login = ref(false);
const user_info = ref(null);
const currentAnalysisID = ref(null);

// 表單資料 (檔案和參數)
const seqencingResultFile = ref([]);
const left_trim = ref(50);
const right_trim = ref(50);
const peak_ratio = ref(0.25);
const selected_sample = ref([]);

// 過去的分析
const selected_history = ref(null);
const history_options = ref([])

/* FileBucket */

// 定
const FileObj = (file_path) => {
  return {
    file_name: file_path.split('/').pop(),
    file_path: file_path
  }
}

// FileBucket 選擇的檔案
const selected_files = ref([])

// FileBucket 列表
const file_bucket_list = ref([])

// FileBucket 移除檔案
const removeBucketFile = async (file) => {
  const response = await deleteFile(file.file_path);
  if (response.status === 'success') {
    await loadStorageFiles();
  }
}

// 載入 Storage 中的檔案
async function loadStorageFiles() {
  const storageFilePath = `${user_info.value.uid}/${storageThalBetaPath}/${currentAnalysisID.value.analysis_uuid}`;
  const files = await listAllFilesInFolder(storageFilePath);
  const file_obj = files.map(f => FileObj(f._location.path_));
  file_bucket_list.value = file_obj;
}

/* Sample List */

// Sample List 移除檔案
const removeFile = (file, row) => {
  row.sequencing_files = row.sequencing_files.filter(f => f.file_name !== file.file_name);
}

// 樣本列表的 column
const sampleList_column = [
  {
    name:'Index',
    label: 'No.',
    field: 'index',
    align: 'center'
  },
  {
    name: 'Sample_Name',
    label: 'Sample Name',
    field: 'sample_name',
    align: 'center'
  },
  {
    name: 'Sequencing_Files',
    label: 'Sequencing Files',
    field: 'sequencing_files',
    align: 'center'
  },
  {
    name: 'Function_Buttons',
    label: '',
    field: 'function_buttons',
    align: 'center'
  },
]

// 樣本列表
const sampleList_row = ref([])

// 定義 ThalBeta 的結果
const THAL_BETA_RESULT = (sample_name, input_file, parameters, resultTable) => {
  return {
    sample_name: sample_name,
    input_file: input_file,
    parameters: parameters,
    resultTable: resultTable
  }
}

// 更新 user database 的資料
function updateDatabaseSampleList(new_sample_list) {
  const data = {sample_list: new_sample_list};
  const setConfigName = currentAnalysisID.value.analysis_uuid;
  update_userAnalysisData(user_info.value.uid, databaseConfigPath, data, setConfigName);
}

// 從 database 讀取樣本列表
async function loadDatabaseSampleList() {
  // 讀取 user database 的資料
  const search_path = `${dataset_list.user_analysis}/${user_info.value.uid}/${databaseConfigPath}`;
  const collectionRef = collection(Database, search_path);

  // 取得所有文件
  const querySnapshot = await getDocs(collectionRef);
  const analysis_list = [];

  querySnapshot.forEach((doc) => {
    analysis_list.push({
      label: doc.id,
      value: doc.id
    });
  });

  // 讀取 user database 的資料
  const data = await getDoc(doc(collection(Database, search_path), currentAnalysisID.value.analysis_uuid)).then((snapshot) => {
    return snapshot.data();
  }).catch((error) => {
    console.error(` Get analysis result failed, ID: ${currentAnalysisID.value.analysis_uuid}, Error: ${error}`);
  });

  // 如果 data 存在, 則設定 sampleList_row
  if (data) {
    sampleList_row.value = data.sample_list;
  }
  else {
    sampleList_row.value = [];
  }
}

// 上傳 Sample 的檔案
async function uploadSampleListFile(index) {
  addFileSampleIndex.value = index;
  uploaded_sampleList_file_input.value.pickFiles();
}

// Functions

// 將 Bucket 中的檔案載入到樣本列表
function loadFileToSampleList() {
  if (selected_files.value.length === 0){
    $q.notify({
      message: 'Please select 2 files from bucket',
      color: 'deep-orange-6',
      position: 'top',
      progress: true,
      timeout: 500
    });
    return;
  }
  if (selected_sample.value.length === 0){
    $q.notify({
      message: 'Please select A sample',
      color: 'deep-orange-6',
      position: 'top',
      progress: true,
      timeout: 500
    });
    return;
  }

  const selectedFiles = file_bucket_list.value.filter(f => selected_files.value.includes(f.file_name));
  const selectedIndex = selected_sample.value[0].index;
  sampleList_row.value.find(r => r.index === selectedIndex).sequencing_files = selectedFiles;

  // 清除 selected_files
  selected_files.value = [];
}

// 新增樣本
function addSample() {
  sampleList_row.value.push({
    index: sampleList_row.value.length + 1,
    sample_name: 'New Sample',
    sequencing_files: []
  });
}

// 刪除樣本
function removeSample(row) {
  sampleList_row.value = sampleList_row.value.filter(r => r.index !== row.index);
  // 剩下的 sample 重新編號
  sampleList_row.value.forEach((r, index) => {
    r.index = index + 1;
  });
}

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

// 驗證每一個 Sample 都要有 2 個檔案, 且 Sample 命名正確
function validateSampleList(sampleList) {
  // 初始化 Error message
  dialog_error_message.value = "";

  if (sampleList.length === 0) {
    dialog_error_message.value = "請至少新增一個樣本！";
    return false;
  }

  // 檢查是否有空的樣本名稱
  const emptySamples = sampleList
    .filter(sample => !sample.sample_name || sample.sample_name.trim() === '')
    .map(sample => `No. ${sample.index}`);

  const hasEmptySampleName = emptySamples.length > 0;

  // 加入 Error message
  if (hasEmptySampleName) {
    dialog_error_message.value += `以下樣本名稱不得為空：${emptySamples.join(', ')}！\n`;
  }

  // 檢查每一個 Sample 是否有 2 個檔案
  const invalidFileSamples = sampleList
    .filter(sample => sample.sequencing_files.length !== 2)
    .map(sample => sample.sample_name || `Sample #${sample.index}`);

  const hasInvalidFileCount = invalidFileSamples.length > 0;

  // 加入 Error message
  if (hasInvalidFileCount) {
    dialog_error_message.value += `以下樣本必須要有 2 個檔案：${invalidFileSamples.join(', ')}！\n`;
  }

  // 檢查是否有重複的 sample_name
  const sampleNameSet = new Set();
  const duplicateSamples = new Set();

  sampleList.forEach(sample => {
    if (sample.sample_name && sampleNameSet.has(sample.sample_name)) {
      duplicateSamples.add(sample.sample_name);
    }
    if (sample.sample_name) {
      sampleNameSet.add(sample.sample_name);
    }
  });

  const hasDuplicateSampleName = duplicateSamples.size > 0;

  // 加入 Error message
  if (hasDuplicateSampleName) {
    dialog_error_message.value += `以下樣本名稱重複：${Array.from(duplicateSamples).join(', ')}！`;
  }

  return !(hasEmptySampleName || hasInvalidFileCount || hasDuplicateSampleName);
}

// 提交表單
const onSubmit = async () => {

  // 不通過驗證則不執行
  if (!validateSampleList(sampleList_row.value)) {
    warning_dialog.value.open_warning_dialog();
    return;
  }

  // 取得 settingProps
  const currentSettingProps = store.getters["analysis_setting/getSettingProps"];

  // 儲存所有分析結果的陣列
  const allbetaThalResults = [];
  const allbetaThalExportResults = [];
  let tmp_resultObj = null;
  try {

    // 使用 for 迴圈處理所有樣本
    for (const [index, sampleInput] of sampleList_row.value.entries()) {

      // 顯示 loading 視窗
      $q.loading.show({
        spinner: QSpinnerFacebook,
        spinnerColor: "deep-orange-6",
        spinnerSize: 100,
        message: `正在分析樣本 ${index + 1}/${sampleList_row.value.length}`,
        messageColor: "white",
      });

      // 準備輸入資料
      const beta_thal_input_data = {
        sample_name: sampleInput.sample_name,
        file_path: sampleInput.sequencing_files,
        left_trim: left_trim.value,
        right_trim: right_trim.value,
        peak_ratio: peak_ratio.value
      };

      // 執行分析
      const analysisResult = await submitWorkflow('THAL_BETA', beta_thal_input_data, user_info.value, currentSettingProps);

      if (analysisResult.status === 'success') {

        // 將 result 轉換成 Object
        const resultObj = JSON.parse(analysisResult.result);
        tmp_resultObj = resultObj;

        // 製作 THAL_BETA_RESULT
        const THAL_BETA_Result = THAL_BETA_RESULT(
          resultObj.sample_name,
          resultObj.input_file.join(','),
          resultObj.parameters,
          resultObj.result
        );

        // 製作 EXPORT_RESULT
        const exportResult = EXPORT_RESULT(index + 1, resultObj.sample_name, "", "", "", "");

        // 將結果加入陣列
        allbetaThalResults.push(THAL_BETA_Result);
        allbetaThalExportResults.push(exportResult);
      }
      else if (analysisResult.status == 'error') {
        throw new Error(`Sample name: ${sampleInput.sample_name} 分析失敗, Error: ${analysisResult.message}`);
      }
    }
  }
  catch (error) {
    // 發生錯誤時的處理
    console.error('Analysis error:', error);
    dialog_error_message.value = error.message;
    warning_dialog.value.open_warning_dialog();
    $q.loading.hide();
  }

  // 製作 ANALYSIS_RESULT
  const AnalysisResult = ANALYSIS_RESULT(
    currentAnalysisID.value.analysis_name,
    currentAnalysisID.value.analysis_uuid,
    tmp_resultObj.config,
    ["N/A"],
    tmp_resultObj.qc_status,
    tmp_resultObj.errMsg,
    allbetaThalResults,
    allbetaThalExportResults
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

// 載入 history 的資料
async function loadHistoryData() {
  // 取得 database 中所有分析
  const search_path = `${dataset_list.user_analysis}/${user_info.value.uid}/${databaseConfigPath}`;
  const collectionRef = collection(Database, search_path);

  // 取得所有文件
  const querySnapshot = await getDocs(collectionRef);
  const analysis_list = [];

  querySnapshot.forEach((doc) => {
    analysis_list.push({
      label: doc.id,
      value: doc.id
    });
  });

  // 更新 history options
  analysis_list.forEach((analysis) => {
    // 如果不在 history_options 中, 則加入
    if (!history_options.value.some(h => h.value === analysis.value)) {
      history_options.value.push({label: analysis.label, value: analysis.value});
    }
  });

  // 如果不在 history_options 中, 則加入
  analysis_list.forEach((analysis) => {
    if (!history_options.value.some(h => h.value === analysis.value)) {
      history_options.value.push({label: analysis.label, value: analysis.value});
    }
  });
}

// 載入測試 Sample
async function loadTestingSamples() {

  // 取得 database 中所有分析
  const search_path = `${dataset_list.testing_data}`;
  const collectionRef = collection(Database, search_path);

  // 取得所有文件
  const querySnapshot = await getDocs(collectionRef);

  // 載入測試樣本
  const testing_sample_list = querySnapshot.docs[0].data();
  sampleList_row.value = testing_sample_list.sample_list;
}

// 掛載時
onMounted(async () => {
  // 取得使用者身份
  const { login_status } = updateGetUserInfo();
  is_login.value = login_status.value.is_login;
  user_info.value = login_status.value.user_info;

  // 先嘗試取得當前的分析 ID, 如果沒有則建立新的分析 ID
  currentAnalysisID.value = store.getters['analysis_setting/getCurrentAnalysisID'];
  setAnalysisID(store, 'THAL_BETA');

  // 載入 history 的資料
  history_options.value = [{label: currentAnalysisID.value.analysis_uuid, value: currentAnalysisID.value.analysis_uuid}];
  selected_history.value = currentAnalysisID.value.analysis_uuid;
  await loadHistoryData();

  // 讀取當前使用者的 firebase storage 中的檔案
  await loadStorageFiles();

  // 讀取 database 的樣本列表
  await loadDatabaseSampleList();
});

// 監聽 controlSampleFile
watch(seqencingResultFile, async(newVal) => {
  await uploadFile(newVal);
  await loadStorageFiles();
});

// 監聽 selected_files, 如果超過 2 個, 則只保留前 2 個
watch(selected_files, (newVal) => {
  if (newVal.length > 2) {
    selected_files.value = selected_files.value.slice(0, 2);
  }
});

// 監聽 sampleList_row
watch(sampleList_row, async (newVal) => {
  updateDatabaseSampleList(newVal);
}, { deep: true });

// 監聽 uploaded_sample_file
watch(uploaded_sample_file, async (newVal) => {
  // 不允許數量不是 2 個檔案
  if (newVal.length !== 2) {
    $q.notify({
      message: 'Please upload Exactly 2 files for each sample!',
      color: 'deep-orange-6',
      position: 'top',
      progress: true,
      timeout: 500
    });
    return;
  }
  // 上傳檔案
  else {
    await uploadFile(newVal);
    const file_objs = newVal.map(file => FileObj(file.path));
    sampleList_row.value.find(r => r.index === addFileSampleIndex.value).sequencing_files = file_objs;
    await loadStorageFiles();
  }
});

// 監聽 selected_history
watch(selected_history, async (newVal) => {

  // 如果沒有選擇, 則返回
  if (!newVal) {
    return;
  }

  // 設定 currentAnalysisID
  currentAnalysisID.value = {
    analysis_name: "THAL_BETA",
    analysis_uuid: typeof newVal === 'string' ? newVal : newVal.value
  }

  // 讀取當前使用者的 firebase storage 中的檔案
  await loadStorageFiles();

  // 讀取 database 的樣本列表
  await loadDatabaseSampleList();
});
</script>