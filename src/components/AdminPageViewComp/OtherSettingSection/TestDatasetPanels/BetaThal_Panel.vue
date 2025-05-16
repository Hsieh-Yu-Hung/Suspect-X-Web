<template>
  <!-- ========================= -->
  <!-- 主要資料集模板組件 -->
  <!-- ========================= -->
  <GeneralDatasetTmpl
    dataset_class="BETA-THAL"
    :datasetList="DatasetList"
    @submit="onSubmit"
    @reset="onReset"
    @updateDatasetList="updateDatasetList"
    ref="generalDatasetTmpl"
  >
    <!-- ========================= -->
    <!-- 資料集內容顯示區塊 -->
    <!-- ========================= -->
    <template #dataset-content="slotProps">
      <div class="dataset-container w100">
        <div class="dataset-content">
          <span class="dataset-name">Left-Trim:</span>
          <span class="dataset-value">{{ slotProps.dataset.leftTrim }}</span>
        </div>
        <div class="dataset-content">
          <span class="dataset-name">Right-Trim:</span>
          <span class="dataset-value">{{ slotProps.dataset.rightTrim }}</span>
        </div>
        <div class="dataset-content">
          <span class="dataset-name">Peak-Ratio:</span>
          <span class="dataset-value">{{ slotProps.dataset.peakRatio }}</span>
        </div>
      </div>
      <div class="dataset-container w100">
        <!-- 樣本檔案列表 -->
        <div
          v-for="sample in slotProps.dataset.sample_files"
          :key="sample.name"
          class="dataset-item w100"
        >
          <span class="dataset-name">{{ sample.name }}</span>
          <div class="file-list">
            <q-chip
              v-for="file in sample.files"
              :key="file.file_name"
              color="grey-3"
              dense
              class="file-chip"
              :label="file.file_name"
            />
          </div>
        </div>
      </div>
    </template>

    <!-- ========================= -->
    <!-- 新增資料集表單區塊 -->
    <!-- ========================= -->
    <template #add-content>
      <div class="form-container">
        <!-- 參數設置 -->
        <div class="form-content w100">
          <div class="form-item w100">
            <div class="form-content">
              <span class="form-label">Left-Trim:</span>
              <q-input
                dense
                v-model="leftTrim"
                type="number"
                class="name-input"
              />
            </div>
            <div class="form-content">
              <span class="form-label">Right-Trim:</span>
              <q-input
                dense
              v-model="rightTrim"
              type="number"
                class="name-input"
              />
            </div>
            <div class="form-content">
              <span class="form-label">Peak-Ratio:</span>
              <q-input
                dense
              v-model="peakRatio"
              type="number"
                class="name-input"
              />
            </div>
          </div>
        </div>
        <!-- 樣本列表 -->
        <div
          v-for="(sample, index) in sampleList"
          :key="index"
          class="form-item"
        >
          <!-- 樣本標題 -->
          <span class="form-label">Sample {{ index + 1 }}</span>

          <!-- 樣本內容區域 -->
          <div class="form-content">
            <!-- 樣本名稱輸入 -->
            <q-input
              v-model="sample.name"
              :rules="sampleNameRules"
              lazy-rules
              dense
              filled
              class="name-input"
            />

            <!-- 檔案上傳區域 -->
            <q-file
              v-model="sample.files"
              class="file-input"
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

            <!-- 操作按鈕區域, 由於流程關係至提供一次一組, 先關閉新增功能 -->
            <div class="action-buttons" v-if="false">
              <q-btn
                flat
                round
                dense
                color="primary"
                icon="add_circle"
                @click="addSample(index)"
              >
                <q-tooltip>新增樣本</q-tooltip>
              </q-btn>
              <q-btn
                v-if="sampleList.length > 1"
                flat
                round
                dense
                color="negative"
                icon="remove_circle"
                @click="removeSample(index)"
              >
                <q-tooltip>刪除樣本</q-tooltip>
              </q-btn>
            </div>
          </div>
        </div>
      </div>
    </template>
  </GeneralDatasetTmpl>
</template>

<script setup>
// ============================
// 導入相關模組
// ============================
import { ref, onMounted, computed } from 'vue'
import { useQuasar } from 'quasar'
import { uploadFileToStorage } from '@/firebase/firebaseStorage'
import { addTestingSample, dataset_list, Database } from '@/firebase/firebaseDatabase'
import { collection, getDocs, deleteDoc } from 'firebase/firestore'
import { v4 as uuidv4 } from 'uuid'
import GeneralDatasetTmpl from '@/components/AdminPageViewComp/OtherSettingSection/TestDatasetTemplates/GeneralDatasetTmpl.vue'
import { createBetaThalDataset } from '@/types/dataset.js'

// ============================
// 常數定義
// ============================
const DATASET_CLASS = "BETA-THAL"
const DEFAULT_GROUP = { label: 'Positive', value: 'Positive' }
const DEFAULT_QC = 'Passed'
const NOTIFICATION_TIMEOUT = 2000

// ============================
// 表單驗證規則
// ============================
const sampleNameRules = [val => !!val || '請輸入樣本名稱']
const sampleFileRules = [val => (val && val.length === 2) || '請上傳 2 個結果檔案']

// ============================
// 響應式狀態
// ============================
const $q = useQuasar()
const generalDatasetTmpl = ref(null)
const DatasetList = ref([])
const sampleList = ref([{ name: '', files: null }])
const leftTrim = ref(50)
const rightTrim = ref(50)
const peakRatio = ref(0.25)

// ============================
// 計算屬性
// ============================
const datasetName = computed(() => generalDatasetTmpl.value?.datasetName)
const selectedInstrument = computed(() => generalDatasetTmpl.value?.selectedInstrument)
const selectedReagent = computed(() => generalDatasetTmpl.value?.selectedReagent)
const selectedGroup = computed(() => generalDatasetTmpl.value?.selectedGroup)
const selectedQC = computed(() => generalDatasetTmpl.value?.selectedQC)
const result_matrix = computed(() => generalDatasetTmpl.value?.result_matrix)

// ============================
// 工具函數
// ============================
// 顯示通知訊息
const showNotification = (type, message) => {
  $q.notify({
    type,
    message,
    position: 'top',
    timeout: NOTIFICATION_TIMEOUT
  })
}

// ============================
// 樣本操作方法
// ============================
// 新增樣本
const addSample = (index) => {
  sampleList.value.splice(index + 1, 0, { name: '', files: null })
}

// 移除樣本
const removeSample = (index) => {
  if (sampleList.value.length > 1) {
    sampleList.value.splice(index, 1)
  }
}

// 處理檔案被拒絕
const onRejected = () => {
  showNotification('negative', '只能上傳 .ab1 檔案')
}

// ============================
// 表單驗證與提交
// ============================
// 驗證表單的輔助函數
const validateForm = () => {
  // 檢查子組件 ref 是否存在
  if (!generalDatasetTmpl.value) {
    showNotification('negative', '表單初始化錯誤')
    return false
  }

  const name = datasetName.value

  // 檢查資料集名稱和樣本
  if (!name || sampleList.value.length === 0) {
    showNotification('negative', '請填寫資料集名稱並添加至少一個樣本')
    return false
  }

  // 檢查 result_matrix
  if (!result_matrix.value || !Array.isArray(result_matrix.value)) {
    showNotification('negative', '請填寫評估結果')
    return false
  }

  // 檢查每個 result_matrix 項目
  const isValidResultMatrix = result_matrix.value.every(item =>
    item.sample_id && item.result && item.assessment
  )

  if (!isValidResultMatrix) {
    showNotification('negative', '請確保每個結果資訊都已填寫完整')
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

// ============================
// 檔案上傳處理
// ============================
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

// ============================
// 資料集管理方法
// ============================
// 表單提交
const onSubmit = async () => {
  // 驗證表單
  if (!validateForm()) return

  // 開啟 loading
  $q.loading.show()

  try {
    // 獲取表單數據
    const name = datasetName.value

    // 生成隨機儲存路徑
    const storagePath = uuidv4()

    // 上傳檔案
    const uploadedSamples = await uploadSampleFiles(storagePath)

    // 創建資料集
    const betaThalDataset = createBetaThalDataset(
      name,
      uploadedSamples,
      leftTrim.value,
      rightTrim.value,
      peakRatio.value,
      selectedInstrument.value,
      selectedReagent.value,
      selectedGroup.value.value,
      selectedQC.value,
      storagePath,
      result_matrix.value
    )

    // 檢查資料庫中是否有相同名稱的資料集
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

    // 如果沒有，則新增資料集
    if (datasetUid === '') {
      datasetUid = uuidv4()
    }

    // 轉換為純 JavaScript 物件並保存
    const datasetData = betaThalDataset.toPlainObject()
    await addTestingSample(datasetData, datasetUid)

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
    generalDatasetTmpl.value.result_matrix = []
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
    for (const document of querySnapshot.docs) {
      const docData = document.data()
      if (docData.dataset_class === DATASET_CLASS) {
        const dataset = createBetaThalDataset(
          docData.name,
          docData.sample_files,
          docData.leftTrim,
          docData.rightTrim,
          docData.peakRatio,
          docData.instrument,
          docData.reagent,
          docData.group || DEFAULT_GROUP.value,
          docData.qc || DEFAULT_QC,
          docData.storagePath,
          docData.result_matrix
        )
        DatasetList.value.push(dataset)
      }
    }
  } catch (error) {
    console.error('更新資料集列表失敗:', error)
    showNotification('negative', '更新資料集列表失敗: ' + error.message)
  }
}

// ============================
// 生命週期鉤子
// ============================
onMounted(async () => {
  await updateDatasetList()
})
</script>

<style scoped>
/* ========================= */
/* 共用樣式 */
/* ========================= */
.text-subtitle2 {
  font-size: 0.9rem;
  font-weight: 500;
}
.w100 {
  width: 100%;
}
/* ========================= */
/* 資料集顯示區塊 */
/* ========================= */
.dataset-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  padding: 0.5rem;
}

.dataset-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.5rem;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

.dataset-name {
  font-size: 0.9rem;
  font-weight: 500;
  color: #424242;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding-left: 1rem;
}

.file-chip {
  font-size: 0.85rem;
}

/* ========================= */
/* 表單區塊樣式 */
/* ========================= */
.form-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  padding: 0.5rem;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background-color: #fafafa;
}

.form-label {
  font-size: 1rem;
  font-weight: 500;
  color: #616161;
}

.form-content {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

/* ========================= */
/* 輸入欄位樣式 */
/* ========================= */
.name-input {
  flex: 1;
  min-width: 200px;
}

.file-input {
  flex: 2;
  min-width: 300px;
}

/* ========================= */
/* 按鈕區域樣式 */
/* ========================= */
.action-buttons {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}
</style>
