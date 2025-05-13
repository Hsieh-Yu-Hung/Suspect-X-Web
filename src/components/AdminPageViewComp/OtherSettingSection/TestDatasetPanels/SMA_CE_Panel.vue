<template>
  <GeneralDatasetTmpl
    dataset_class="SMA_CE"
    :datasetList="DatasetList"
    @submit="onSubmit"
    @reset="onReset"
    @updateDatasetList="updateDatasetList"
    ref="generalDatasetTmpl"
  >
    <template #dataset-content="slotProps">
      <div class="sample-item">
        <span class="text-subtitle2">SMN1 SC-C: </span>
        <q-chip color="grey-3" dense class="text-subtitle2" :label="slotProps.dataset.smn1_sc_c" />
      </div>
      <div class="sample-item">
        <span class="text-subtitle2">SMN1 SC-N: </span>
        <q-chip color="grey-3" dense class="text-subtitle2" :label="slotProps.dataset.smn1_sc_n" />
      </div>
      <div class="samples-container">
        <span class="text-subtitle2">SMN1 Samples: </span>
        <q-chip
          v-for="sample in slotProps.dataset.smn1_samples"
          :key="sample"
          color="grey-3"
          dense
          class="text-subtitle2"
          :label="sample.name"
        />
      </div>
      <div class="sample-item">
        <span class="text-subtitle2">SMN2 SC-C: </span>
        <q-chip color="grey-3" dense class="text-subtitle2" :label="slotProps.dataset.smn2_sc_c" />
      </div>
      <div class="sample-item">
        <span class="text-subtitle2">SMN2 SC-N: </span>
        <q-chip color="grey-3" dense class="text-subtitle2" :label="slotProps.dataset.smn2_sc_n" />
      </div>
      <div class="samples-container">
        <span class="text-subtitle2">SMN2 Samples: </span>
        <q-chip
          v-for="sample in slotProps.dataset.smn2_samples"
          :key="sample"
          color="grey-3"
          dense
          class="text-subtitle2"
          :label="sample.name"
        />
      </div>
    </template>

    <template #add-content>
      <div class="upload-controls">
        <q-btn
          dense
          color="deep-orange-6"
          icon="upload"
          label="上傳"
          @click="triggerFileUpload"
          class="upload-btn"
        />
        <div class="q-ml-md">
          <q-toggle
            :label="useGeneType"
            color="pink"
            false-value="SMN1"
            true-value="SMN2"
            v-model="useGeneType"
          />
        </div>
        <q-file
          ref="fileInput"
          v-model="datasetFiles"
          class="q-mb-md hidden-file-input"
          dense
          accept=".xlsx,.xls"
          multiple
          @update:model-value="handleFileUpload"
        />
      </div>
      <div
        v-for="(file, index) in uploadedFiles"
        :key="index"
        class="full-width q-pa-sm file-item"
      >
        <div class="row items-center q-gutter-md">
          <!-- 檔名 -->
          <div class="col-4 file-name">
            <span class="text-subtitle2">{{ file.name }}</span>
          </div>

          <!-- SMN1/SMN2 選項 -->
          <div class="col-2">
            <q-radio v-model="file.geneType" val="SMN1" label="SMN1" class="q-mr-md" />
            <q-radio v-model="file.geneType" val="SMN2" label="SMN2" />
          </div>

          <!-- 樣本類型選擇 -->
          <div class="col-3">
            <q-select
              v-model="file.sampleType"
              :options="sampleTypeOptions"
              dense
              outlined
              class="sample-type-select"
            />
          </div>

          <!-- 刪除按鈕 -->
          <div class="col-1">
            <q-btn
              flat
              round
              color="red-9"
              icon="delete"
              size="sm"
              @click="removeFile(index)"
            >
              <q-tooltip>刪除此檔案</q-tooltip>
            </q-btn>
          </div>
        </div>
      </div>
    </template>
  </GeneralDatasetTmpl>
</template>

<script setup>
// 導入模組
import { v4 as uuidv4 } from 'uuid'
import { ref, onMounted, computed } from 'vue'
import { useQuasar } from 'quasar'
import { uploadFileToStorage } from '@/firebase/firebaseStorage'
import { addTestingSample, dataset_list, Database } from '@/firebase/firebaseDatabase'
import { collection, getDocs, deleteDoc } from 'firebase/firestore'
import GeneralDatasetTmpl from '@/components/AdminPageViewComp/OtherSettingSection/TestDatasetTemplates/GeneralDatasetTmpl.vue'
import { createSmaCeDataset } from '@/types/dataset'

// 常數定義
const DATASET_CLASS = "SMA_CE"
const NOTIFICATION_TIMEOUT = 2000

// 樣本類型選項
const sampleTypeOptions = [
  { label: 'Sample', value: 'Sample' },
  { label: 'SC-C', value: 'SC-C' },
  { label: 'SC-N', value: 'SC-N' }
]

// 使用 Quasar 的通知
const $q = useQuasar()
const generalDatasetTmpl = ref(null)

// 資料集資料相關響應式變數
const DatasetList = ref([])
const useGeneType = ref('SMN1')
const fileInput = ref(null)
const uploadedFiles = ref([])
const datasetFiles = ref([])

// 從子組件獲取值的計算屬性
const datasetName = computed(() => generalDatasetTmpl.value?.datasetName)
const selectedInstrument = computed(() => generalDatasetTmpl.value?.selectedInstrument)
const selectedReagent = computed(() => generalDatasetTmpl.value?.selectedReagent)
const selectedGroup = computed(() => generalDatasetTmpl.value?.selectedGroup)
const selectedQC = computed(() => generalDatasetTmpl.value?.selectedQC)
const resultText = computed(() => generalDatasetTmpl.value?.resultText)
const assessmentsText = computed(() => generalDatasetTmpl.value?.assessmentsText)

// 顯示通知的輔助函數
const showNotification = (type, message) => {
  $q.notify({
    type,
    message,
    position: 'top',
    timeout: NOTIFICATION_TIMEOUT
  })
}

// 驗證表單的輔助函數
const validateForm = () => {
  // 檢查資料集名稱和上傳的檔案
  if (!datasetName.value) {
    showNotification('negative', '請填寫資料集名稱')
    return false
  }

  if (uploadedFiles.value.length === 0) {
    showNotification('negative', '請上傳至少一個檔案')
    return false
  }

  // 檢查 Result 和 Assessments
  if (!resultText.value) {
    showNotification('negative', '請填寫 Result 欄位')
    return false
  }

  if (!assessmentsText.value) {
    showNotification('negative', '請填寫 Assessments 欄位')
    return false
  }

  return true
}

// 上傳檔案到 Storage
const uploadFilesToStorage = async (storagePath) => {
  try {
    const uploadPromises = uploadedFiles.value.map(async (file) => {
      const filePath = `${storagePath}/${file.name}`
      await uploadFileToStorage(file.file, filePath, 'test')
      return {
        file_name: file.name,
        file_path: `testing_data/${filePath}`
      }
    })
    return await Promise.all(uploadPromises)
  } catch (error) {
    console.error('上傳檔案失敗:', error)
    showNotification('negative', '上傳檔案失敗: ' + error.message)
    throw error
  }
}

// 獲取分組檔案
const getGroupedFiles = (storagePath) => {
  return {
    smn1_sc_c: uploadedFiles.value.filter(file =>
      file.geneType === 'SMN1' && file.sampleType.value === 'SC-C'
    ).map(file => ({
      name: file.name,
      path: `testing_data/${storagePath}/${file.name}`,
      expType: "std1",
      smnType: "smn1"
    }))[0]?.name || '',

    smn1_sc_n: uploadedFiles.value.filter(file =>
      file.geneType === 'SMN1' && file.sampleType.value === 'SC-N'
    ).map(file => ({
      name: file.name,
      path: `testing_data/${storagePath}/${file.name}`,
      expType: "std2",
      smnType: "smn1"
    }))[0]?.name || '',

    smn1_samples: uploadedFiles.value.filter(file =>
      file.geneType === 'SMN1' && file.sampleType.value === 'Sample'
    ).map(file => ({
      name: file.name,
      path: `testing_data/${storagePath}/${file.name}`,
      expType: "sample",
      smnType: "smn1"
    })),

    smn2_sc_c: uploadedFiles.value.filter(file =>
      file.geneType === 'SMN2' && file.sampleType.value === 'SC-C'
    ).map(file => ({
      name: file.name,
      path: `testing_data/${storagePath}/${file.name}`,
      expType: "std1",
      smnType: "smn2"
    }))[0]?.name || '',

    smn2_sc_n: uploadedFiles.value.filter(file =>
      file.geneType === 'SMN2' && file.sampleType.value === 'SC-N'
    ).map(file => ({
      name: file.name,
      path: `testing_data/${storagePath}/${file.name}`,
      expType: "std2",
      smnType: "smn2"
    }))[0]?.name || '',

    smn2_samples: uploadedFiles.value.filter(file =>
      file.geneType === 'SMN2' && file.sampleType.value === 'Sample'
    ).map(file => ({
      name: file.name,
      path: `testing_data/${storagePath}/${file.name}`,
      expType: "sample",
      smnType: "smn2"
    }))
  }
}

// 檢查資料集是否存在並獲取 UID
const getDatasetUid = async (name) => {
  try {
    let datasetUid = ''
    const searchPath = `${dataset_list.testing_data}`
    const collectionRef = collection(Database, searchPath)
    const querySnapshot = await getDocs(collectionRef)

    for (const document of querySnapshot.docs) {
      const docData = document.data()
      if (docData.dataset_name === name && docData.dataset_class === DATASET_CLASS) {
        datasetUid = document.id
        await deleteDoc(document.ref)
        break
      }
    }

    return datasetUid || uuidv4()
  } catch (error) {
    console.error('檢查資料集時出錯:', error)
    showNotification('negative', '檢查資料集失敗: ' + error.message)
    throw error
  }
}

// 表單提交
const onSubmit = async () => {
  // 驗證表單
  if (!validateForm()) return

  // 開啟 loading
  $q.loading.show()

  try {
    // 生成隨機儲存路徑
    const storagePath = uuidv4()

    // 上傳檔案
    await uploadFilesToStorage(storagePath)

    console.log(uploadedFiles.value)

    // 獲取分組後的檔案
    const groupedFiles = getGroupedFiles(storagePath)

    // 創建資料集
    const datasetData = createSmaCeDataset(
      datasetName.value,
      groupedFiles.smn1_sc_c,
      groupedFiles.smn1_sc_n,
      groupedFiles.smn1_samples,
      groupedFiles.smn2_sc_c,
      groupedFiles.smn2_sc_n,
      groupedFiles.smn2_samples,
      selectedInstrument.value,
      selectedReagent.value,
      selectedGroup.value.value,
      selectedQC.value,
      resultText.value,
      assessmentsText.value,
      storagePath
    )

    // 檢查是否已存在相同名稱的資料集
    const datasetUid = await getDatasetUid(datasetName.value)

    // 轉換為純 JavaScript 物件並保存
    const plainObject = datasetData.toPlainObject()
    await addTestingSample(plainObject, datasetUid)

    // 顯示成功通知
    showNotification('positive', '資料集創建成功')

    // 重置表單並更新列表
    // onReset()
    await updateDatasetList()
  } catch (error) {
    console.error('提交表單時出錯:', error)
    showNotification('negative', '創建資料集失敗: ' + error.message)
  } finally {
    // 關閉 loading
    $q.loading.hide()
  }
}

// 重置表單
const onReset = () => {
  uploadedFiles.value = []
  datasetFiles.value = null

  // 如果子組件可用，重置子組件的表單
  if (generalDatasetTmpl.value) {
    generalDatasetTmpl.value.datasetName = ''
    generalDatasetTmpl.value.resultText = ''
    generalDatasetTmpl.value.assessmentsText = ''
  }
}

// 更新資料集列表
const updateDatasetList = async () => {
  try {
    // 取得 database 中所有分析
    const searchPath = `${dataset_list.testing_data}`
    const collectionRef = collection(Database, searchPath)
    const querySnapshot = await getDocs(collectionRef)

    // 清空集合
    DatasetList.value = []

    // 載入測試樣本
    querySnapshot.forEach(document => {
      const docData = document.data()
      if (docData.dataset_class === DATASET_CLASS) {
        DatasetList.value.push(createSmaCeDataset(
          docData.name,
          docData.SMN1_SC_C[0]?.name || '',
          docData.SMN1_SC_N[0]?.name || '',
          docData.SMN1_Samples || [],
          docData.SMN2_SC_C[0]?.name || '',
          docData.SMN2_SC_N[0]?.name || '',
          docData.SMN2_Samples || [],
          docData.instrument,
          docData.reagent,
          docData.group,
          docData.qc,
          docData.result,
          docData.assessments,
          docData.storagePath
        ))
      }
    })
  } catch (error) {
    console.error('更新資料集列表失敗:', error)
    showNotification('negative', '更新資料集列表失敗: ' + error.message)
  }
}

// 檔案操作相關函數
const triggerFileUpload = () => {
  fileInput.value.pickFiles()
}

const handleFileUpload = (files) => {
  if (!files) return

  Array.from(files).forEach(file => {
    // 檢查是否已存在相同檔名
    const isDuplicate = uploadedFiles.value.some(existingFile => existingFile.name === file.name)

    // 如果沒有重複，則加入新檔案
    if (!isDuplicate) {
      uploadedFiles.value.push({
        name: file.name,
        file: file,
        geneType: useGeneType.value,
        sampleType: { label: 'Sample', value: 'Sample' }
      })
    } else {
      showNotification('warning', `檔案 ${file.name} 已存在，略過此檔案`)
    }
  })
}

const removeFile = (index) => {
  uploadedFiles.value.splice(index, 1)
}

// 掛載元件
onMounted(async () => {
  await updateDatasetList()
})
</script>

<style scoped>
.sample-item {
  margin-bottom: 8px;
}

.samples-container {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5em;
  margin-bottom: 8px;
}

.upload-controls {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  align-items: center;
  width: 100%;
  gap: 0.5em;
  margin-bottom: 16px;
}

.upload-btn {
  height: 100%;
}

.hidden-file-input {
  width: 100%;
  display: none;
}

.file-item {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  margin-bottom: 8px;
}

.file-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sample-type-select {
  width: 150px;
}

.collapsed {
  height: 3em;
  overflow: hidden;
}

.expanded {
  height: auto;
  overflow: auto;
}
</style>
