<template>
  <div class="row">

    <!-- 資料集列表 -->
    <div class="col q-mb-md" style="margin-right: 1em; border-radius: 10px; padding: 10px; border: 1px solid #e0e0e0;">

      <div style="display: flex; flex-direction: row; gap: 0.5em;">
        <q-icon name="collections_bookmark" size="md" class="text-blue-grey-7" />
        <span class="text-h5 q-mb-md text-blue-grey-7 text-bold">現有集合</span>
      </div>

      <!-- 如果沒有資料集，顯示提示訊息 -->
      <div style="display: flex; flex-direction: row; align-items: center; justify-content: center; height: 100%;" v-if="DatasetList.length === 0">
        <span class="text-subtitle2 text-blue-9"> -- 請新增一些測試資料集 -- </span>
      </div>

      <!-- 如果資料集列表不為空，顯示資料集列表 -->
      <q-list bordered separator v-else>
        <q-item clickable v-ripple v-for="dataset in DatasetList" :key="dataset.name" @click.prevent="displayDataset(dataset)">
          <q-item-section>
            <div style="display: flex; flex-direction: column; align-items: flex-start;" :class="{ 'collapsed': !dataset.isSelected, 'expanded': dataset.isSelected }">
              <div style="display: flex; flex-direction: row; align-items: center; gap: 0.5em; width: 100%; justify-content: space-between;">
                <span class="text-h6 text-bold text-blue-grey-8">{{ dataset.name }}</span>
                <div style="display: flex; flex-direction: row; align-items: center; gap: 0.5em;">
                  <q-btn flat color="primary" icon="edit" dense class="text-subtitle2" @click.prevent="editDataset(dataset)" />
                  <q-btn flat color="red-9" icon="delete" dense class="text-subtitle2" @click.prevent="deleteDataset(dataset)" />
                </div>
              </div>
              <div style="display: flex; flex-direction: column; align-items: flex-start; margin-top: 0.5em;">
                <div style="display: flex; flex-direction: row; align-items: center; gap: 0.5em;">
                  <span class="text-subtitle2">Control File:</span>
                  <q-chip class="text-subtitle2" style="margin-right: 0.5em;">{{ dataset.controlFile }}</q-chip>
                </div>
                <div style="display: flex; flex-direction: row; align-items: flex-start; gap: 0.5em;">
                  <span class="text-subtitle2" style="white-space: nowrap; margin-top: 0.5em;">Sample Files:</span>
                  <div style="display: flex; flex-direction: row; align-items: flex-start; flex-wrap: wrap;">
                    <q-chip v-for="file in dataset.sampleFiles" :key="file" class="text-subtitle2" style="margin-right: 0.5em;">{{ file }}</q-chip>
                  </div>
                </div>
              </div>
            </div>
          </q-item-section>
        </q-item>
      </q-list>

    </div>

    <!-- 新增資料集 -->
    <div class="col q-mb-md" style="border: 1px solid #e0e0e0; border-radius: 10px; padding: 10px; background-color: rgba(221, 232, 243, 0.2);">
      <q-form @submit="onSubmit" @reset="onReset">
        <div style="display: flex; flex-direction: row; gap: 0.5em; align-items: center; justify-content: space-between;">
          <div style="display: flex; flex-direction: row; gap: 0.5em;">
            <q-icon name="category" size="md" class="text-blue-grey-7" />
            <span class="text-h5 q-mb-md text-blue-grey-7 text-bold">新增資料集</span>
          </div>
          <q-btn color="cyan-8" icon="add_box" dense class="text-subtitle2" label="新增" type="submit" />
        </div>
        <div style="display: flex; flex-direction: column; align-items: center; width: 100%; margin-top: 1em;">
          <div style="display: flex; flex-direction: row; gap: 0.5em; width: 100%;">
            <span class="text-subtitle2" style="white-space: nowrap; margin-top: 0.6em;">資料集名稱:</span>
            <q-input
              v-model="datasetName"
              class="q-mb-md"
              dense
              style="width: 100%;"
              :rules="[val => !!val || '請輸入資料集名稱']"
              lazy-rules
            />
          </div>
          <div style="display: flex; flex-direction: row; gap: 0.5em; width: 100%; overflow: auto;">
            <span class="text-subtitle2" style="white-space: nowrap; margin-top: 0.6em;">Control File:</span>
            <q-file
              v-model="controlFile"
              class="q-mb-md"
              filled
              dense
              style="width: 100%;"
              use-chips
              :rules="[val => !!val || 'Control File 為必填']"
              lazy-rules
              color="deep-orange-6"
              stack-label
              accept=".xlsx,.xls"
            />
          </div>
          <div style="display: flex; flex-direction: row; align-items: flex-start; gap: 0.5em; width: 100%; overflow: auto;">
            <span class="text-subtitle2" style="white-space: nowrap; margin-top: 0.6em;">Sample Files:</span>
            <q-file
              v-model="sampleFiles"
              class="q-mb-md"
              filled
              dense
              style="width: 100%;"
              multiple
              use-chips
              :rules="[val => val && val.length > 0 || '請至少上傳一個 Sample File']"
              lazy-rules
              color="deep-orange-6"
              stack-label
              accept=".xlsx,.xls"
            />
          </div>
        </div>
      </q-form>
    </div>
  </div>
</template>

<script setup>
// 導入模組
import { ref, onMounted } from 'vue'
import { uploadFileToStorage } from '@/firebase/firebaseStorage'

// 定義一個 Dataset 的資料結構
const Dataset = (NAME, CONTROL_FILE, SAMPLE_FILES) => {
  return {
    name: NAME,
    controlFile: CONTROL_FILE,
    sampleFiles: SAMPLE_FILES,
    isSelected: false
  }
}

// 資料集列表
const DatasetList = ref([])

/* Table Data */
const datasetName = ref('FXS測試資料')
const controlFile = ref(null)
const sampleFiles = ref([])

// 顯示資料集
const displayDataset = (dataset) => {
  dataset.isSelected = !dataset.isSelected
}

// 編輯資料集
const editDataset = (dataset) => {
  console.log(dataset)
}

// 刪除資料集
const deleteDataset = (dataset) => {
  console.log(dataset)
}
// 提交表單
const onSubmit = async () => {
  // 檢查所有必填欄位
  if (!datasetName.value || !controlFile.value || !sampleFiles.value || sampleFiles.value.length === 0) {
    return
  }

  // 上傳 Control File
  const control_file_storage_path = `${datasetName.value}/${controlFile.value.name}`
  const controlFileUploadResult = await uploadFileToStorage(controlFile.value, control_file_storage_path, 'test')
  console.log("Control File Upload Result:", controlFileUploadResult)

  // 上傳 Sample Files
  sampleFiles.value.forEach(async (file) => {
    const sample_file_storage_path = `${datasetName.value}/${file.name}`
    const sampleFilesUploadResult = await uploadFileToStorage(file, sample_file_storage_path, 'test')
    console.log("Sample Files Upload Result:", sampleFilesUploadResult)
  })

  // 重置表單
  onReset()
}

// 重置表單
const onReset = () => {
  datasetName.value = ''
  controlFile.value = null
  sampleFiles.value = []
}

// 掛載元件
onMounted(() => {
  // 初始化資料集列表
  DatasetList.value.push(Dataset('TEST-Set1', 'FXS_control.txt', ['FXS_sample1.txt', 'FXS_sample2.txt', 'FXS_sample3.txt']))
  DatasetList.value.push(Dataset('TEST-Set2', 'FXS_control.txt', ['FXS_sample4.txt', 'FXS_sample5.txt', 'FXS_sample6.txt']))
})

</script>

<style scoped>
.collapsed {
  height: 3em;
  overflow: hidden;
}
.expanded {
  height: auto;
  overflow: auto;
}
</style>