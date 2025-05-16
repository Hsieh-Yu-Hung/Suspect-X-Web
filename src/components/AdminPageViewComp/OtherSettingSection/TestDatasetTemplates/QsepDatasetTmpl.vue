<template>
  <!-- 主要資料集模板組件 -->
  <GeneralDatasetTmpl
    :dataset_class="props.dataset_class"
    :datasetList="datasetList"
    @submit="onSubmit"
    @reset="onReset"
    @updateDatasetList="updateDatasetList"
    ref="generalDatasetTmpl"
  >
    <!-- =================== -->
    <!-- 資料集內容顯示區塊 -->
    <!-- =================== -->
    <template #dataset-content="{ dataset }">
      <!-- Type I 資料集顯示 -->
      <template v-if="typeIClass.includes(props.dataset_class)">
        <div class="dataset-info">
          <div class="file-upload-row">
            <span class="info-label text-subtitle2">Control File:</span>
            <q-chip class="text-subtitle2">{{ dataset.controlFile.split('/').pop() }}</q-chip>
          </div>
          <div class="file-upload-row">
            <span class="info-label text-subtitle2">Sample Files:</span>
            <div class="sample-files-list">
              <q-chip
                v-for="file in dataset.sampleFiles"
                :key="file"
                class="text-subtitle2"
              >
                {{ file.split('/').pop() }}
              </q-chip>
            </div>
          </div>
        </div>
      </template>

      <!-- Type II 資料集顯示 -->
      <template v-else>
        <div class="dataset-info">
          <!-- SC1 檔案 -->
          <div class="file-upload-row">
            <span class="info-label text-subtitle2">SC1 Files:</span>
            <div class="sample-files-list">
              <q-chip
                v-for="file in dataset.sc1_files"
                :key="file"
                class="text-subtitle2"
              >
                {{ file.split('/').pop() }}
              </q-chip>
            </div>
          </div>

          <!-- SC2 檔案 -->
          <div class="file-upload-row">
            <span class="info-label text-subtitle2">SC2 Files:</span>
            <div class="sample-files-list">
              <q-chip
                v-for="file in dataset.sc2_files"
                :key="file"
                class="text-subtitle2"
              >
                {{ file.split('/').pop() }}
              </q-chip>
            </div>
          </div>

          <!-- 樣本檔案組 -->
          <div
            v-for="groupNum in getGroupNumbers(dataset.sample_files)"
            :key="groupNum"
            class="sample-files-group"
          >
            <div class="file-upload-row">
              <span class="info-label text-subtitle2">Sample Files 組 {{ groupNum }}:</span>
              <div class="sample-files-list">
                <q-chip
                  v-for="file in dataset.sample_files.filter(f => f.group === groupNum)"
                  :key="file.path"
                  class="text-subtitle2"
                >
                  {{ file.path.split('/').pop() }}
                </q-chip>
              </div>
            </div>
          </div>
        </div>
      </template>
    </template>

    <!-- =================== -->
    <!-- 新增資料集表單區塊 -->
    <!-- =================== -->
    <template #add-content>
      <div class="file-upload-section">
        <!-- Type I 資料集表單 -->
        <div v-if="typeIClass.includes(props.dataset_class)" class="file-upload-section">
          <div class="file-upload-row">
            <span class="upload-label text-subtitle2">Control File:</span>
            <q-file
              v-model="controlFile"
              class="upload-field"
              filled
              dense
              use-chips
              :rules="[val => !!val || 'Control File 為必填']"
              lazy-rules
              color="deep-orange-6"
              stack-label
              accept=".xlsx,.xls"
            />
          </div>
          <div class="file-upload-row">
            <span class="upload-label text-subtitle2">Sample Files:</span>
            <q-file
              v-model="sampleFiles"
              class="upload-field"
              filled
              dense
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

        <!-- Type II 資料集表單 -->
        <div v-if="typeIIClass.includes(props.dataset_class)" class="file-upload-section">
          <!-- SC1 和 SC2 檔案上傳 -->
          <div
            v-for="sc in ['SC1', 'SC2']"
            :key="sc"
            class="file-upload-row"
          >
            <span class="upload-label text-subtitle2">{{ sc }} File:</span>
            <q-file
              v-model="scFiles[sc]"
              class="upload-field"
              filled
              dense
              use-chips
              multiple
              :rules="[val => !!val && val.length === 3 || '請上傳 3 個檔案']"
              lazy-rules
              color="deep-orange-6"
              stack-label
              accept=".xlsx,.xls"
            />
          </div>

          <!-- 樣本檔案組上傳 -->
          <div
            v-for="(group, groupIndex) in typeIISampleFiles"
            :key="groupIndex"
            class="file-upload-row"
          >
            <span class="upload-label text-subtitle2">Sample Files 組 {{ groupIndex + 1 }}:</span>
            <q-file
              v-model="typeIISampleFiles[groupIndex]"
              class="upload-field"
              filled
              dense
              multiple
              use-chips
              :rules="[val => val && val.length === 3 || '請上傳 3 個檔案']"
              lazy-rules
              color="deep-orange-6"
              stack-label
              accept=".xlsx,.xls"
            />
            <div class="flex row gap-sm items-center">
              <q-btn
                v-if="groupIndex === typeIISampleFiles.length - 1"
                color="primary"
                icon="add_box"
                dense
                class="text-subtitle2"
                @click.prevent="addTypeIISampleFile"
              />
              <q-btn
                color="red-8"
                icon="delete"
                dense
                class="text-subtitle2"
                @click.prevent="deleteTypeIISampleFile(groupIndex)"
              />
            </div>
          </div>
        </div>
      </div>
    </template>
  </GeneralDatasetTmpl>
</template>

<script setup>
// ==========================================
// 導入相關模組
// ==========================================
import { ref, onMounted, computed } from 'vue'
import { uploadFileToStorage } from '@/firebase/firebaseStorage'
import { addTestingSample, dataset_list, Database } from '@/firebase/firebaseDatabase'
import { collection, getDocs, doc, deleteDoc } from 'firebase/firestore'
import { v4 as uuidv4 } from 'uuid'
import { createQSEPDataset } from '@/types/dataset'
import GeneralDatasetTmpl from './GeneralDatasetTmpl.vue'
import { useQuasar } from 'quasar'
// ==========================================
// Props 定義
// ==========================================
const props = defineProps({
  dataset_class: {
    type: String,
    required: true
  }
})

// ==========================================
// 常數定義
// ==========================================
const typeIClass = ['FXS', 'HTD']
const typeIIClass = ['APOE']

// ==========================================
// 響應式狀態
// ==========================================
// 子組件引用
const generalDatasetTmpl = ref(null)

// 資料集列表
const datasetList = ref([])

// Type I 資料集狀態
const controlFile = ref(null)
const sampleFiles = ref([])

// Type II 資料集狀態
const scFiles = ref({
  SC1: null,
  SC2: null
})
const typeIISampleFiles = ref([[]])

// useQuasar
const $q = useQuasar()

// ==========================================
// 計算屬性
// ==========================================
const datasetName = computed(() => generalDatasetTmpl.value?.datasetName)
const selectedInstrument = computed(() => generalDatasetTmpl.value?.selectedInstrument)
const selectedReagent = computed(() => generalDatasetTmpl.value?.selectedReagent)
const selectedGroup = computed(() => generalDatasetTmpl.value?.selectedGroup)
const selectedQC = computed(() => generalDatasetTmpl.value?.selectedQC)
const result_matrix = computed(() => generalDatasetTmpl.value?.result_matrix)

// ==========================================
// Type II 資料集方法
// ==========================================
// 新增樣本檔案組
const addTypeIISampleFile = () => {
  typeIISampleFiles.value.push([])
}

// 刪除樣本檔案組
const deleteTypeIISampleFile = (index) => {
  if (typeIISampleFiles.value.length > 1) {
    typeIISampleFiles.value.splice(index, 1)
  } else {
    typeIISampleFiles.value[0] = []
  }
}

// ==========================================
// 表單提交處理
// ==========================================
// 主要提交處理
const onSubmit = async () => {
  if (typeIClass.includes(props.dataset_class)) {
    await onSubmitTypeI()
  } else if (typeIIClass.includes(props.dataset_class)) {
    await onSubmitTypeII()
  }
}

// Type I 資料集提交
const onSubmitTypeI = async () => {
  // 檢查所有必填欄位
  if (!datasetName.value || !controlFile.value || !sampleFiles.value || sampleFiles.value.length === 0) {
    return
  }

  // Storage Path, 隨機產生一組 uuid
  const storagePath = uuidv4()

  // 上傳 Control File
  const controlFileStoragePath = `${storagePath}/${controlFile.value.name}`
  await uploadFileToStorage(controlFile.value, controlFileStoragePath, 'test')

  // 上傳 Sample Files
  const sampleFilePaths = []
  for (const file of sampleFiles.value) {
    const sampleFileStoragePath = `${storagePath}/${file.name}`
    await uploadFileToStorage(file, sampleFileStoragePath, 'test')
    sampleFilePaths.push(`testing_data/${sampleFileStoragePath}`)
  }

  // 創建 QSEPDataset 實例並轉換為平面物件
  const qsepDataset = createQSEPDataset({
    name: datasetName.value,
    controlFile: `testing_data/${controlFileStoragePath}`,
    sampleFiles: sampleFilePaths,
    sc1_files: null,
    sc2_files: null,
    sample_files: null,
    instrument: selectedInstrument.value,
    reagent: selectedReagent.value,
    storagePath: storagePath,
    dataset_class: props.dataset_class,
    group: selectedGroup.value?.value,
    qc: selectedQC.value,
    result_matrix: result_matrix.value
  })

  // 將 qsepDataset 轉換為平面物件
  const datasetData = qsepDataset.toPlainObject()

  // 檢查資料庫中是否有相同名稱的資料集
  await saveDataset(datasetData)
}

// Type II 資料集提交
const onSubmitTypeII = async () => {
  // 檢查所有必填欄位
  if (!datasetName.value || !scFiles.value.SC1 || !scFiles.value.SC2) {
    return
  }

  // 檢查每組 Sample Files 是否都有3個檔案
  const isValidSampleFiles = typeIISampleFiles.value.every(group => group && group.length === 3)
  if (!isValidSampleFiles) {
    return
  }

  // Storage Path, 隨機產生一組 uuid
  const storagePath = uuidv4()

  // 上傳 SC1 Files
  const sc1FilePaths = await Promise.all(scFiles.value.SC1.map(async (file) => {
    const fileStoragePath = `${storagePath}/SC1/${file.name}`
    await uploadFileToStorage(file, fileStoragePath, 'test')
    return `testing_data/${fileStoragePath}`
  }))

  // 上傳 SC2 Files
  const sc2FilePaths = await Promise.all(scFiles.value.SC2.map(async (file) => {
    const fileStoragePath = `${storagePath}/SC2/${file.name}`
    await uploadFileToStorage(file, fileStoragePath, 'test')
    return `testing_data/${fileStoragePath}`
  }))

  // 上傳所有組的 Sample Files
  const sampleFilesPaths = []
  for (let groupIndex = 0; groupIndex < typeIISampleFiles.value.length; groupIndex++) {
    const group = typeIISampleFiles.value[groupIndex]
    for (const file of group) {
      const fileStoragePath = `${storagePath}/samples/group${groupIndex + 1}/${file.name}`
      await uploadFileToStorage(file, fileStoragePath, 'test')
      sampleFilesPaths.push({
        group: groupIndex + 1,
        path: `testing_data/${fileStoragePath}`
      })
    }
  }

  // 創建 QSEPDataset 實例並轉換為平面物件
  const qsepDataset = createQSEPDataset({
    name: datasetName.value,
    controlFile: null,
    sampleFiles: null,
    sc1_files: sc1FilePaths,
    sc2_files: sc2FilePaths,
    sample_files: sampleFilesPaths,
    instrument: selectedInstrument.value,
    reagent: selectedReagent.value,
    storagePath: storagePath,
    dataset_class: props.dataset_class,
    group: selectedGroup.value?.value,
    qc: selectedQC.value,
    result_matrix: result_matrix.value
  })

  // 將 qsepDataset 轉換為平面物件
  const datasetData = qsepDataset.toPlainObject()

  // 檢查資料庫中是否有相同名稱的資料集
  await saveDataset(datasetData)
}

// ==========================================
// 資料集管理方法
// ==========================================
// 顯示通知訊息
const showNotification = (type, message) => {
  $q.notify({
    type,
    message,
    position: 'top',
    timeout: NOTIFICATION_TIMEOUT
  })
}

// 儲存資料集
const saveDataset = async (datasetData) => {
  // 檢查是否已存在相同名稱的資料集
  let datasetUid = ''
  const searchPath = `${dataset_list.testing_data}`
  const collectionRef = collection(Database, searchPath)
  const querySnapshot = await getDocs(collectionRef)

  // 檢查 result_matrix
  if (!result_matrix.value || !Array.isArray(result_matrix.value)) {
    showNotification('negative', '格式錯誤')
    return
  }

  // 檢查每個 result_matrix 項目
  const isValidResultMatrix = result_matrix.value.every(item =>
    item.sample_id && item.result && item.assessment
  )

  if (!isValidResultMatrix) {
    showNotification('negative', '請確保每個結果資訊都已填寫完整')
    return
  }

  for (const document of querySnapshot.docs) {
    const docData = document.data()
    if (docData.dataset_name === datasetName.value && docData.dataset_class === props.dataset_class) {
      // 如果有的話，刪除資料集, 取得 id
      datasetUid = document.id
      await deleteDoc(document.ref)
      break
    }
  }

  // 如果沒有，則新增資料集
  if (datasetUid === '') {
    datasetUid = uuidv4()
  }

  // 將 result_matrix 添加到 dataset_data
  const finalDatasetData = {
    ...datasetData,
    result_matrix: result_matrix.value
  }

  await addTestingSample(finalDatasetData, datasetUid)

  // 重置表單
  onReset()

  // 更新集合顯示
  await updateDatasetList()
}

// 重置表單
const onReset = () => {
  // 重置 Type I 資料集
  controlFile.value = null
  sampleFiles.value = []

  // 重置 Type II 資料集
  scFiles.value = {
    SC1: null,
    SC2: null
  }
  typeIISampleFiles.value = [[]]

  // 重置子組件
  if (generalDatasetTmpl.value) {
    generalDatasetTmpl.value.datasetName = ''
    generalDatasetTmpl.value.result_matrix = []
  }
}

// 更新資料集列表
const updateDatasetList = async () => {
  // 取得 database 中所有分析
  const searchPath = `${dataset_list.testing_data}`
  const collectionRef = collection(Database, searchPath)

  // 取得所有文件
  const querySnapshot = await getDocs(collectionRef)

  // 清空集合
  datasetList.value = []

  // 載入測試樣本
  for (const document of querySnapshot.docs) {
    const docData = document.data()
    if (docData.dataset_class && docData.dataset_class === props.dataset_class) {
      let dataset

      if (typeIClass.includes(props.dataset_class)) {
        dataset = createQSEPDataset({
          name: docData.dataset_name,
          controlFile: docData.controlFile,
          sampleFiles: docData.sampleFiles,
          sc1_files: null,
          sc2_files: null,
          sample_files: null,
          instrument: docData.instrument,
          reagent: docData.reagent,
          storagePath: docData.storagePath,
          dataset_class: docData.dataset_class,
          group: docData.group,
          qc: docData.qc,
          result_matrix: docData.result_matrix
        })
      } else {
        dataset = createQSEPDataset({
          name: docData.dataset_name,
          controlFile: null,
          sampleFiles: null,
          sc1_files: docData.sc1_files,
          sc2_files: docData.sc2_files,
          sample_files: docData.sample_files,
          instrument: docData.instrument,
          reagent: docData.reagent,
          storagePath: docData.storagePath,
          dataset_class: docData.dataset_class,
          group: docData.group,
          qc: docData.qc,
          result_matrix: docData.result_matrix
        })
      }

      datasetList.value.push(dataset)
    }
  }
}

// 取得資料集組號
const getGroupNumbers = (sampleFiles) => {
  if (!sampleFiles) return []
  return [...new Set(sampleFiles.map(file => file.group))].sort((a, b) => a - b)
}

// ==========================================
// 生命週期鉤子
// ==========================================
onMounted(async () => {
  await updateDatasetList()
})
</script>

<style scoped>
/* ================ */
/* 共用樣式 */
/* ================ */
.flex {
  display: flex;
}

.row {
  flex-direction: row;
}

.column {
  flex-direction: column;
}

.gap-sm {
  gap: 0.5em;
}

/* ================ */
/* 文字樣式 */
/* ================ */
.text-subtitle2 {
  font-size: 0.9em;
  font-weight: 500;
}

/* ================ */
/* 資料集顯示區塊 */
/* ================ */
.dataset-info {
  display: flex;
  flex-direction: column;
  gap: 0.5em;
  margin-top: 1em;
}

.info-label {
  white-space: nowrap;
}

/* ================ */
/* 檔案上傳區塊 */
/* ================ */
.file-upload-section {
  width: 100%;
  margin-bottom: 1em;
}

.file-upload-row {
  display: flex;
  align-items: center;
  gap: 1em;
  width: 100%;
}

.upload-label {
  white-space: nowrap;
  min-width: 100px;
}

.upload-field {
  flex: 1;
}

/* ================ */
/* 樣本檔案區塊 */
/* ================ */
.sample-files-section {
  margin-top: 1em;
}

.sample-files-group {
  margin-bottom: 1em;
}

.sample-files-label {
  white-space: nowrap;
  margin-right: 1em;
}

.sample-files-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5em;
}
</style>
