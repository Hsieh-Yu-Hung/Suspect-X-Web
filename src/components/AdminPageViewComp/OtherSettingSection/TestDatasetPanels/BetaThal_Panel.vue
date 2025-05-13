<template>
  <GeneralDatasetTmpl
    dataset_class="BETA-THAL"
    :datasetList="DatasetList"
    @submit="onSubmit"
    @reset="onReset"
    @updateDatasetList="updateDatasetList"
    ref="generalDatasetTmpl"
  >
    <template #dataset-content="slotProps">
      <div class="sample-container">
        <div v-for="sample in slotProps.dataset.sample_files" :key="sample.name">
          <span class="text-subtitle2">{{ sample.name }}</span>
          <div class="file-list">
            <q-chip
              v-for="file in sample.files"
              :key="file.file_name"
              color="grey-3"
              dense
              class="text-subtitle2"
              :label="file.file_name"
            />
          </div>
        </div>
      </div>
    </template>

    <template #add-content>
      <div class="sample-list-container">
        <div
          v-for="(sample, index) in sampleList"
          :key="index"
          class="sample-item"
        >
          <span class="text-subtitle2 sample-label">Sample {{ index + 1 }}</span>
          <div class="sample-content">
            <q-input
              v-model="sample.name"
              :rules="sampleNameRules"
              lazy-rules
              dense
              filled
              class="text-subtitle2 q-pa-md sample-name-input"
            />
            <q-file
              v-model="sample.files"
              class="text-subtitle2 q-pa-md sample-file-input"
              filled
              dense
              use-chips
              multiple
              :rules="sampleFileRules"
              lazy-rules
              label="Upload 2 Sanger *ab1 Files"
              color="deep-orange-8"
              accept=".ab1"
              @update:model-value="val => sample.files = val"
              @rejected="onRejected"
            />
            <div class="sample-actions">
              <q-btn flat round dense color="primary" icon="add_circle" @click="addSample(index)" />
              <q-btn
                v-if="sampleList.length > 1"
                flat
                round
                dense
                color="negative"
                icon="remove_circle"
                @click="removeSample(index)"
              />
            </div>
          </div>
        </div>
      </div>
    </template>
  </GeneralDatasetTmpl>
</template>

<script setup>
// 導入模組
import { ref, onMounted, computed } from 'vue'
import { useQuasar } from 'quasar'
import { uploadFileToStorage } from '@/firebase/firebaseStorage'
import { addTestingSample, dataset_list, Database } from '@/firebase/firebaseDatabase'
import { collection, getDocs, deleteDoc } from 'firebase/firestore'
import { v4 as uuidv4 } from 'uuid'
import GeneralDatasetTmpl from '@/components/AdminPageViewComp/OtherSettingSection/TestDatasetTemplates/GeneralDatasetTmpl.vue'
import { createBetaThalDataset } from '@/types/dataset.js'

// 常數定義
const DATASET_CLASS = "BETA-THAL"
const DEFAULT_GROUP = { label: 'Positive', value: 'Positive' }
const DEFAULT_QC = 'Passed'
const NOTIFICATION_TIMEOUT = 2000

// 表單驗證規則
const sampleNameRules = [val => !!val || '請輸入樣本名稱']
const sampleFileRules = [val => (val && val.length === 2) || '請上傳 2 個結果檔案']

// 使用 Quasar 的通知
const $q = useQuasar()
const generalDatasetTmpl = ref(null)

// 表單數據和計算屬性
const DatasetList = ref([])
const sampleList = ref([{ name: '', files: null }])

// 從子組件獲取值的計算屬性
const datasetName = computed(() => generalDatasetTmpl.value?.datasetName)
const selectedInstrument = computed(() => generalDatasetTmpl.value?.selectedInstrument)
const selectedReagent = computed(() => generalDatasetTmpl.value?.selectedReagent)
const selectedGroup = computed(() => generalDatasetTmpl.value?.selectedGroup)
const selectedQC = computed(() => generalDatasetTmpl.value?.selectedQC)
const resultText = computed(() => generalDatasetTmpl.value?.resultText)
const assessmentsText = computed(() => generalDatasetTmpl.value?.assessmentsText)

// 樣本操作函數
const addSample = (index) => {
  sampleList.value.splice(index + 1, 0, { name: '', files: null })
}

const removeSample = (index) => {
  if (sampleList.value.length > 1) {
    sampleList.value.splice(index, 1)
  }
}

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
  // 檢查子組件 ref 是否存在
  if (!generalDatasetTmpl.value) {
    showNotification('negative', '表單初始化錯誤')
    return false
  }

  const name = datasetName.value
  const result = resultText.value
  const assessments = assessmentsText.value

  // 檢查資料集名稱和樣本
  if (!name || sampleList.value.length === 0) {
    showNotification('negative', '請填寫資料集名稱並添加至少一個樣本')
    return false
  }

  // 檢查 Result 和 Assessments
  if (!assessments || !result) {
    showNotification('negative', '請填寫 Result 和 Assessments 欄位')
    return false
  }

  // 檢查每個樣本
  const isValid = sampleList.value.every(sample =>
    sample.name && sample.files && sample.files.length === 2
  )

  if (!isValid) {
    showNotification('negative', '請確保每個樣本都有名稱和兩個檔案')
    return false
  }

  return true
}

// 上傳樣本檔案
const uploadSampleFiles = async (storagePath) => {
  try {
    const uploadPromises = sampleList.value.map(async (sample) => {
      const filePromises = sample.files.map(async (file) => {
        const filePath = `${storagePath}/${sample.name}/${file.name}`
        await uploadFileToStorage(file, filePath, 'test')
        return {
          file_name: file.name,
          file_path: `testing_data/${filePath}`
        }
      })
      return {
        name: sample.name,
        files: await Promise.all(filePromises)
      }
    })

    return await Promise.all(uploadPromises)
  } catch (error) {
    console.error('上傳樣本檔案失敗:', error)
    showNotification('negative', '上傳檔案失敗: ' + error.message)
    throw error
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
      if (docData.name === name && docData.dataset_class === DATASET_CLASS) {
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
    // 獲取表單數據
    const name = datasetName.value
    const result = resultText.value
    const assessments = assessmentsText.value

    // 生成隨機儲存路徑
    const storagePath = uuidv4()

    // 上傳檔案
    const uploadedSamples = await uploadSampleFiles(storagePath)

    // 創建資料集
    const datasetData = createBetaThalDataset(
      name,
      uploadedSamples,
      selectedInstrument.value,
      selectedReagent.value,
      selectedGroup.value.value,
      selectedQC.value,
      result,
      assessments,
      storagePath
    )

    // 檢查是否已存在相同名稱的資料集
    const datasetUid = await getDatasetUid(name)

    // 轉換為純 JavaScript 物件並保存
    const plainObject = datasetData.toPlainObject()
    await addTestingSample(plainObject, datasetUid)

    // 顯示成功通知
    showNotification('positive', '資料集創建成功')

    // 重置表單並更新列表
    onReset()
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
  // 重置樣本列表
  sampleList.value = [{ name: '', files: null }]

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
        DatasetList.value.push(createBetaThalDataset(
          docData.name,
          docData.sample_files,
          docData.instrument,
          docData.reagent,
          docData.group || DEFAULT_GROUP,
          docData.qc || DEFAULT_QC,
          docData.result || '',
          docData.assessments || '',
          docData.storagePath
        ))
      }
    })
  } catch (error) {
    console.error('更新資料集列表失敗:', error)
    showNotification('negative', '更新資料集列表失敗: ' + error.message)
  }
}

// 處理檔案被拒絕的情況
const onRejected = () => {
  showNotification('negative', '只能上傳 .ab1 檔案')
}

// 掛載元件
onMounted(async () => {
  await updateDatasetList()
})
</script>

<style scoped>
.sample-container {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-top: 0.5em;
  width: 100%;
}

.file-list {
  display: flex;
  justify-content: flex-start;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5em;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sample-list-container {
  display: flex;
  flex-direction: column;
  gap: 0.5em;
  width: 100%;
  align-items: center;
}

.sample-item {
  display: flex;
  flex-direction: row;
  gap: 0.5em;
  width: 100%;
  align-items: center;
}

.sample-label {
  white-space: nowrap;
}

.sample-content {
  display: flex;
  flex-direction: row;
  width: 100%;
  align-items: center;
}

.sample-name-input {
  width: 50%;
}

.sample-file-input {
  width: 100%;
}

.sample-actions {
  display: flex;
  flex-direction: row;
  gap: 0.5em;
}
</style>
