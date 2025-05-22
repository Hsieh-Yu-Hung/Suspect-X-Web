<template>
  <!-- ========================= -->
  <!-- 主要資料集模板組件 -->
  <!-- ========================= -->
  <GeneralDatasetTmpl
    dataset_class="SMA_CE"
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
      <!-- SMN1 相關資訊 -->
      <div class="dataset-section">
        <div class="info-item">
          <span class="info-label">SMN1 SC-C: </span>
          <q-chip color="grey-3" dense class="info-value" :label="slotProps.dataset.smn1_sc_c" />
        </div>
        <div class="info-item">
          <span class="info-label">SMN1 SC-N: </span>
          <q-chip color="grey-3" dense class="info-value" :label="slotProps.dataset.smn1_sc_n" />
        </div>
        <div class="samples-section">
          <span class="info-label">SMN1 Samples: </span>
          <div class="samples-list">
            <q-chip
              v-for="sample in slotProps.dataset.smn1_samples"
              :key="sample"
              color="grey-3"
              dense
              class="info-value"
              :label="sample.name"
            />
          </div>
        </div>
      </div>

      <!-- SMN2 相關資訊 -->
      <div class="dataset-section">
        <div class="info-item">
          <span class="info-label">SMN2 SC-C: </span>
          <q-chip color="grey-3" dense class="info-value" :label="slotProps.dataset.smn2_sc_c" />
        </div>
        <div class="info-item">
          <span class="info-label">SMN2 SC-N: </span>
          <q-chip color="grey-3" dense class="info-value" :label="slotProps.dataset.smn2_sc_n" />
        </div>
        <div class="samples-section">
          <span class="info-label">SMN2 Samples: </span>
          <div class="samples-list">
            <q-chip
              v-for="sample in slotProps.dataset.smn2_samples"
              :key="sample"
              color="grey-3"
              dense
              class="info-value"
              :label="sample.name"
            />
          </div>
        </div>
      </div>
    </template>

    <!-- ========================= -->
    <!-- 新增資料集表單區塊 -->
    <!-- ========================= -->
    <template #add-content>
      <!-- 上傳控制區 -->
      <div class="upload-controls">
        <q-btn
          dense
          color="deep-orange-6"
          icon="upload"
          label="上傳"
          @click="triggerFileUpload"
          class="upload-btn"
        />
        <div class="gene-type-toggle">
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
          class="hidden-file-input"
          dense
          accept=".xlsx,.xls"
          multiple
          @update:model-value="handleFileUpload"
        />
      </div>

      <!-- 已上傳檔案列表 -->
      <div class="uploaded-files-list">
        <div
          v-for="(file, index) in uploadedFiles"
          :key="index"
          class="file-item"
        >
          <div class="file-item-content">
            <!-- 檔案名稱 -->
            <div class="file-name">
              <span class="text-subtitle2">{{ file.name }}</span>
            </div>

            <!-- 基因類型選擇 -->
            <div class="gene-type-selection">
              <q-radio color="green" v-model="file.geneType" val="SMN1" label="SMN1" class="gene-type-radio" />
              <q-radio color="pink" v-model="file.geneType" val="SMN2" label="SMN2" />
            </div>

            <!-- 樣本類型選擇 -->
            <div class="sample-type-selection">
              <q-select
                v-model="file.sampleType"
                :options="sampleTypeOptions"
                dense
                outlined
                class="sample-type-select"
              />
            </div>

            <!-- 操作按鈕 -->
            <div class="file-actions">
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
      </div>
    </template>
  </GeneralDatasetTmpl>
</template>

<script setup>
// ============================
// 導入相關模組
// ============================
import { v4 as uuidv4 } from 'uuid'
import { ref, onMounted, computed } from 'vue'
import { useQuasar } from 'quasar'
import { uploadFileToStorage } from '@/firebase/firebaseStorage'
import { addTestingSample, dataset_list, Database } from '@/firebase/firebaseDatabase'
import { collection, getDocs, deleteDoc } from 'firebase/firestore'
import GeneralDatasetTmpl from '@/components/AdminPageViewComp/OtherSettingSection/TestDatasetTemplates/GeneralDatasetTmpl.vue'
import { createSmaCeDataset } from '@/types/dataset'

// ============================
// 常數定義
// ============================
const DATASET_CLASS = "SMA_CE"
const NOTIFICATION_TIMEOUT = 2000

// 樣本類型選項
const sampleTypeOptions = [
  { label: 'Sample', value: 'Sample' },
  { label: 'SC-C', value: 'SC-C' },
  { label: 'SC-N', value: 'SC-N' }
]

// ============================
// 響應式狀態
// ============================
const $q = useQuasar()
const generalDatasetTmpl = ref(null)
const DatasetList = ref([])
const useGeneType = ref('SMN1')
const fileInput = ref(null)
const uploadedFiles = ref([])
const datasetFiles = ref([])

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
const showNotification = (type, message) => {
  $q.notify({
    type,
    message,
    position: 'top',
    timeout: NOTIFICATION_TIMEOUT
  })
}

// ============================
// 表單驗證與提交
// ============================
const validateForm = () => {
  try {
    // 檢查資料集名稱和上傳的檔案
    if (!datasetName.value) {
      showNotification('negative', '請填寫資料集名稱')
      return false
    }

    if (uploadedFiles.value.length === 0) {
      showNotification('negative', '請上傳至少一個檔案')
      return false
    }

    // 檢查 result_matrix
    if (!result_matrix.value || !Array.isArray(result_matrix.value)) {
      showNotification('negative', '請填寫結果矩陣')
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

    return true
  } catch (error) {
    console.error('驗證表單時出錯:', error)
    showNotification('negative', '驗證表單時出錯')
    return false
  }
}

const onSubmit = async () => {
  try {
    // 驗證表單
    if (!validateForm()) {
      return
    }

    // 開啟 loading
    $q.loading.show()

    // Storage Path, 隨機產生一組 uuid
    const storagePath = uuidv4()

    // 分類檔案
    const smn1_files = {
      sc_c: uploadedFiles.value.find(f => f.geneType === 'SMN1' && f.sampleType.value === 'SC-C'),
      sc_n: uploadedFiles.value.find(f => f.geneType === 'SMN1' && f.sampleType.value === 'SC-N'),
      samples: uploadedFiles.value.filter(f => f.geneType === 'SMN1' && f.sampleType.value === 'Sample')
    }

    const smn2_files = {
      sc_c: uploadedFiles.value.find(f => f.geneType === 'SMN2' && f.sampleType.value === 'SC-C'),
      sc_n: uploadedFiles.value.find(f => f.geneType === 'SMN2' && f.sampleType.value === 'SC-N'),
      samples: uploadedFiles.value.filter(f => f.geneType === 'SMN2' && f.sampleType.value === 'Sample')
    }

    // 上傳檔案到 Storage
    const uploadFile = async (file) => {
      if (!file) return null
      const filePath = `${storagePath}/${file.name}`
      await uploadFileToStorage(file.file, filePath, 'test')
      return file.name
    }

    const uploadSamples = async (samples) => {
      return await Promise.all(samples.map(async (sample) => {
        const path = `${storagePath}/${sample.name}`
        await uploadFileToStorage(sample.file, path, 'test')
        return {
          name: sample.name,
          path: `testing_data/${path}`,
          expType: 'sample',
          smnType: sample.geneType.toLowerCase()
        }
      }))
    }

    // 執行檔案上傳
    const [smn1_sc_c, smn1_sc_n, smn2_sc_c, smn2_sc_n] = await Promise.all([
      uploadFile(smn1_files.sc_c),
      uploadFile(smn1_files.sc_n),
      uploadFile(smn2_files.sc_c),
      uploadFile(smn2_files.sc_n)
    ])

    const [smn1_samples, smn2_samples] = await Promise.all([
      uploadSamples(smn1_files.samples),
      uploadSamples(smn2_files.samples)
    ])

    // 創建 SmaCeDataset 實例
    const smaCeDataset = createSmaCeDataset(
      datasetName.value,
      smn1_sc_c,
      smn1_sc_n,
      smn1_samples,
      smn2_sc_c,
      smn2_sc_n,
      smn2_samples,
      selectedInstrument.value,
      selectedReagent.value,
      selectedGroup.value?.value,
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
      if (docData.name === datasetName.value && docData.dataset_class === DATASET_CLASS) {
        datasetUid = document.id
        await deleteDoc(document.ref)
        break
      }
    }

    // 如果沒有，則新增資料集
    if (datasetUid === '') {
      datasetUid = uuidv4()
    }

    // 將 SmaCeDataset 轉換為平面物件
    const datasetData = smaCeDataset.toPlainObject()

    // 新增資料集到資料庫
    await addTestingSample(datasetData, datasetUid)

    // 重置表單
    onReset()

    // 更新集合顯示
    await updateDatasetList()

    // 顯示成功訊息
    showNotification('positive', '資料集新增成功')

  } catch (error) {
    console.error('新增資料集時發生錯誤:', error)
    showNotification('negative', '新增資料集時發生錯誤')
  } finally {
    // 關閉 loading
    $q.loading.hide()
  }
}

// ============================
// 檔案處理相關方法
// ============================
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

// ============================
// 資料集管理方法
// ============================
const onReset = () => {
  uploadedFiles.value = []
  datasetFiles.value = null

  // 如果子組件可用，重置子組件的表單
  if (generalDatasetTmpl.value) {
    generalDatasetTmpl.value.datasetName = ''
    generalDatasetTmpl.value.result_matrix = []
  }
}

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
        const dataset = createSmaCeDataset(
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

/* ========================= */
/* 資料集顯示區塊 */
/* ========================= */
.dataset-section {
  margin-bottom: 1.5rem;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
}

.info-label {
  font-size: 0.9rem;
  font-weight: 500;
  margin-right: 0.5rem;
}

.info-value {
  font-size: 0.9rem;
}

.samples-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.samples-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

/* ========================= */
/* 上傳控制區域 */
/* ========================= */
.upload-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  padding: 0.5rem;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.upload-btn {
  min-width: 100px;
}

.gene-type-toggle {
  margin-left: auto;
}

.hidden-file-input {
  display: none;
}

/* ========================= */
/* 檔案列表區域 */
/* ========================= */
.uploaded-files-list {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.file-item {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 0.75rem;
  background-color: #ffffff;
}

.file-item-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.file-name {
  flex: 5;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.gene-type-selection {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.gene-type-radio {
  margin-right: 0.5rem;
}

.sample-type-selection {
  flex: 1;
}

.sample-type-select {
  width: 6rem;
}

.file-actions {
  flex: 1;
  display: flex;
  justify-content: center;
}
</style>
