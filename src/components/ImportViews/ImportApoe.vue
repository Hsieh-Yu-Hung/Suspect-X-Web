<template>
  <q-card bordered :style="{ 'min-height': '100%' }">

    <!-- 警告視窗 -->
    <WarningDialog
      ref="warning_dialog"
      :error_message="dialog_error_message"
    />

    <!-- 內容 -->
    <q-card-section>
      <div class="text-h5 text-uppercase text-bold text-blue-grey-7">
        Import
      </div>
      <div class="text-subtitle1">
        Please select the corresponding standard control and sample E2, E3, E4 result files.
      </div>
    </q-card-section>
    <q-card-section>
      <q-form class="q-gutter-sm" @submit="onSubmit">
        <q-file
          v-model="control1File"
          multiple
          append
          use-chips
          color="deep-orange-6"
          stack-label
          label="Standard control 1"
          :rules="[(val) => (val && val.length === 3) || `Please select standard control 1 E2, E3, E4 files`]"
          accept=".xlsx, .xls"
          lazy-rules
        >
          <template v-slot:before>
            <q-icon name="mdi-microsoft-excel" />
          </template>
        </q-file>
        <q-file
          v-model="control2File"
          multiple
          append
          use-chips
          color="deep-orange-6"
          stack-label
          label="Standard control 2"
          :rules="[(val) => (val && val.length === 3) || `Please select standard control 2 E2, E3, E4 files`]"
          accept=".xlsx, .xls"
          lazy-rules
        >
          <template v-slot:before>
            <q-icon name="mdi-microsoft-excel" />
          </template>
        </q-file>
        <div v-for="(sample, idx) in sampleFile" :key="idx">
          <q-file
            v-model="sampleFile[idx]"
            multiple
            append
            use-chips
            color="deep-orange-6"
            stack-label
            :label="'Testing sample ' + (idx + 1)"
            :rules="[(val) => (val && val.length === 3) || `Please select sample E2, E3, E4 files`]"
            accept=".xlsx, .xls"
            lazy-rules
          >
            <template v-slot:before>
              <q-icon name="mdi-microsoft-excel" />
            </template>
            <template v-slot:after>
              <q-btn round outline size="sm" color="primary" icon="library_add" class="q-mr-sm" @click="addSampleFileInput(idx)" />
              <q-btn round outline size="sm" color="red" icon="delete" :disable="sampleFile.length < 2" @click="removeSampleFileInput(idx)" />
            </template>
          </q-file>
        </div>
        <div class="row q-mt-lg justify-end">
          <q-btn label="Analyze" type="submit" color="blue-grey-7" />
        </div>
      </q-form>
    </q-card-section>
  </q-card>
</template>

<script setup>
// 導入模組
import { ref, watch, onMounted } from "vue";
import { useQuasar, QSpinnerFacebook } from 'quasar';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import { v4 as uuidv4 } from 'uuid';

// 元件
import WarningDialog from '@/components/WarningDialog.vue';

// 導入 composable
import { upload_files_to_storage } from '@/composables/storageManager';
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';
import { submitWorkflow } from '@/composables/submitWorkflow';
import { CATEGORY_LIST } from '@/composables/storageManager';
import { setAnalysisID } from '@/composables/checkAnalysisStatus';
import { ANALYSIS_RESULT, simplifyFilePath, EXPORT_RESULT, update_userAnalysisData } from '@/firebase/firebaseDatabase';
import loggerV2 from '@/composables/loggerV2';
import getTestingData from '@/composables/useGetTestingData';

// consts
const $q = useQuasar();
const store = useStore();
const router = useRouter();

// 控制警告視窗
const dialog_error_message = ref("");
const warning_dialog = ref(null);

// input 檔案
const control1File = ref(null);
const control2File = ref(null);
const sampleFile = ref(new Array(1).fill([]));

// 使用者身份
const is_login = ref(false);
const user_info = ref(null);

// 當前的分析 ID
const currentAnalysisID = ref(null);

// 保存上傳紀錄供檢查不同
const sampleUploaded = ref(null);

// APOE result 資料庫路徑
const dbAPOEResultPath = 'apoe_result';

/* functions */

// 定義 APOE result
const APOE_RESULT = (control1List, control2List, sampleObjList, resultObj) => {
  return {
    control1List: control1List,
    control2List: control2List,
    sampleObjList: sampleObjList,
    assessmentResult: resultObj
  }
}

// 評估結果
const assessment = (value) => {
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

// 送出表單
async function onSubmit() {
  // *. 顯示 loading 視窗
  $q.loading.show({
    spinner: QSpinnerFacebook,
    spinnerColor: "deep-orange-6",
    spinnerSize: 100,
    message: "Analyzing...",
    messageColor: "white",
  });

  // 設定輸入
  const parsedSampleNameList = sampleFile.value.map((fileList) => { return filenameParser(fileList[0].name); });
  const id_labeled_sample_name_list = sampleFile.value.map((fileList) => {
    return {
      sampleId: parsedSampleNameList.find((sample) => fileList[0].name.includes(sample.sampleId)).sampleId,
      filePathList: fileList.map((file)=>file.path)
    }
  });
  const ApoeInputData = {
    control1PathList: control1File.value.map((file) => {return file.path}),
    control2PathList: control2File.value.map((file) => {return file.path}),
    samplePathList: id_labeled_sample_name_list
  }

  // 取得 control1 和 control2 的 ID
  const control1IDs = ApoeInputData.control1PathList.map((path) => {return simplifyFilePath(path)});
  const control2IDs = ApoeInputData.control2PathList.map((path) => {return simplifyFilePath(path)});
  const controlIDs = [...control1IDs, ...control2IDs];

  // 取得 settingProps
  const currentSettingProps = store.getters["analysis_setting/getSettingProps"];

  // 執行 submitWorkflow
  const analysisResult = await submitWorkflow('APOE', ApoeInputData, user_info.value, currentSettingProps);

  // 檢查有沒有出錯
  if (analysisResult.status == 'success'){
    dialog_error_message.value = "";

    // 將 result 轉換成 Object
    const resultObj = JSON.parse(analysisResult.result);

    // APOE result
    const APOE_Result = APOE_RESULT(
      resultObj.control1,
      resultObj.control2,
      resultObj.samples,
      resultObj.result
    );

    // Export Result
    const sample_ids = Object.keys(resultObj.result);
    const exportResult = sample_ids.map((sample_id, index) => {
      const resultList = resultObj.result[sample_id].rfu_status.map((rfu) => {return rfu.peak_group})
      const sortedResultList = resultList.sort((a, b) => {return a.localeCompare(b)});
      return EXPORT_RESULT(
        index+1,
        sample_id,
        sortedResultList.join(""),
        [sortedResultList.join("/")],
        resultObj.result[sample_id].assessment,
        assessment(resultObj.result[sample_id].assessment)
      );
    });

    // 製作 ANALYSIS_RESULT
    const AnalysisResult = ANALYSIS_RESULT(
      currentAnalysisID.value.analysis_name,
      currentAnalysisID.value.analysis_uuid,
      resultObj.config,
      controlIDs,
      resultObj.qc_status,
      resultObj.errMsg,
      APOE_Result,
      exportResult
    );

    // 將結果存到 firestore
    update_userAnalysisData(user_info.value.uid, dbAPOEResultPath, AnalysisResult, currentAnalysisID.value.analysis_uuid);

    // 更新 currentDisplayAnalysisID
    store.commit("analysis_setting/updateCurrentDisplayAnalysisID", {
      analysis_name: "APOE",
      analysis_uuid: currentAnalysisID.value.analysis_uuid,
    });

    // 更新 currentAnalysisID
    const new_id = `analysis_${uuidv4()}`;
    store.commit('analysis_setting/updateCurrentAnalysisID', {
      analysis_name: "APOE",
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

// Get type information from filename
function filenameParser(filename) {
  let name = filename.split(".").slice(0, -1).join(".");

  let parts =  name.split("_");
  let well = parts.slice(-2, -1).shift().split("").slice(-3).join("");
  let sampleId = parts.slice(0, -2).join("_");
  let rawSampleId = parts.slice(1).join("_");

  return {
    sampleId: sampleId,
    rawSampleId: rawSampleId,
    well: well,
  }
}

// 選擇檔案後立即上傳
async function uploadFile(file_list, analysisID, subDir) {

  // 顯示 loading 視窗
  $q.loading.show();

  // 存到當前使用者
  const user_uid = user_info.value.uid;

  // 存到 Apoe data 資料夾
  const category = CATEGORY_LIST.apoe_import;

  // 上傳檔案
  const uploading = await Promise.all(file_list.map(async (file) => {
    return await upload_files_to_storage(
      file, user_uid, category, analysisID, subDir
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

    // 設定 dialog_error_message, 跳出警告視窗
    dialog_error_message.value = error_message;
    warning_dialog.value.open_warning_dialog();

    // 印出 error message
    const message = error_message;
    const source = 'ImportApoe.vue line.277';
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

// 處理 sample file upload
async function handleSampleFileUpload(newVal) {
  // 初始化 file_to_upload
  let file_to_upload = null;

  // 如果 sampleUploaded 是 null, 則將 newVal 複製到 sampleUploaded
  if (sampleUploaded.value == null) {
    sampleUploaded.value = JSON.parse(JSON.stringify(newVal));
    file_to_upload = newVal;
  }

  // 如果 sampleUploaded 不是 null, 則比較 newVal 和 sampleUploaded 是否相同
  else {
    if (JSON.parse(JSON.stringify(newVal)) !== sampleUploaded.value) {

      // 找出新增的檔案
      const added_fileList = newVal.filter((fileList) => {
        return !sampleUploaded.value.some((sampleFileList) => {
          return JSON.stringify(fileList) === JSON.stringify(sampleFileList);
        });
      });

      // 更新 file_to_upload
      file_to_upload = added_fileList;
    }
  }

  // 上傳檔案
  if (file_to_upload != null) {
    await Promise.all(file_to_upload.map(async (file_list) => {
      if (file_list.length > 0) {
        const sampleLayer = filenameParser(file_list[0].name).sampleId;
        await uploadFile(file_list, currentAnalysisID.value.analysis_uuid, `samples/${sampleLayer}`);
      }
    }))
    .catch((error) => {
      const message = error;
      const source = 'ImportApoe.vue line.342';
      const user = user_info.value.email;
      loggerV2.error(message, source, user);
    });
  }

  // 更新 sampleUploaded
  sampleUploaded.value = JSON.parse(JSON.stringify(newVal));
}

// 新增 sample file input
function addSampleFileInput(idx) {
  sampleFile.value.splice(idx + 1, 0, []);
}

// 移除 sample file input
function removeSampleFileInput(idx) {
  sampleFile.value.splice(idx, 1);
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
  const testing_data = await getTestingData("APOE");
  const selected_dataset = testing_data.find((item) => item.name === dataset_name);

  // 更新 control1File 和 control2File
  control1File.value = selected_dataset.sc1_files.map((file) => {return makeFile(file)});
  control2File.value = selected_dataset.sc2_files.map((file) => {return makeFile(file)});

  // 更新 sampleFile
  const groupList = new Set(selected_dataset.sample_files.map(sample => sample.group));
  sampleFile.value = [];
  groupList.forEach((group) => {
    sampleFile.value.push(selected_dataset.sample_files.filter((sample) => sample.group === group).map((sample) => {return makeFile(sample.path)}));
  });

  // submit
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
  setAnalysisID(store, 'APOE');
});

// 監聽 Control1File 的變化上傳檔案
watch(control1File, async (newVal, oldVal) => {
  // 比較 newVal 和 oldVal 是否相同, 找出新增的檔案
  const added_file = oldVal ? newVal.filter((file) => !oldVal.includes(file)) : newVal;
  // 上傳新增的檔案
  await uploadFile(added_file, currentAnalysisID.value.analysis_uuid, "control1");
});

// 監聽 Control2File 的變化上傳檔案
watch(control2File, async (newVal, oldVal) => {
  // 比較 newVal 和 oldVal 是否相同, 找出新增的檔案
  const added_file = oldVal ? newVal.filter((file) => !oldVal.includes(file)) : newVal;
  // 上傳新增的檔案
  await uploadFile(added_file, currentAnalysisID.value.analysis_uuid, "control2");
});

// 監聽 SampleFile 的變化上傳檔案
watch(sampleFile, async (newVal) => {
  await handleSampleFileUpload(newVal);
}, {deep: true});

</script>
