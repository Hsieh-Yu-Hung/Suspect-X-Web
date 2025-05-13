<template>
  <GeneralDatasetTmpl
    :dataset_class="props.dataset_class"
    :datasetList="datasetList"
    @submit="onSubmit"
    @reset="onReset"
    @updateDatasetList="updateDatasetList"
    ref="generalDatasetTmpl"
  >
    <!-- 資料集內容插槽 -->
    <template #dataset-content="{ dataset }">
      <template v-if="typeIClass.includes(props.dataset_class)">
        <div class="flex row items-center gap-sm">
          <span class="text-subtitle2">Control File:</span>
          <q-chip class="text-subtitle2 q-mr-sm">{{ dataset.controlFile.split('/').pop() }}</q-chip>
        </div>
        <div class="flex row items-start gap-sm">
          <span class="text-subtitle2" style="white-space: nowrap; margin-top: 0.5em;">Sample Files:</span>
          <div class="flex column items-start flex-wrap">
            <q-chip
              v-for="file in dataset.sampleFiles"
              :key="file"
              class="text-subtitle2 q-mr-sm"
            >
              {{ file.split('/').pop() }}
            </q-chip>
          </div>
        </div>
      </template>
      <template v-else>
        <div class="flex row items-start gap-sm q-mt-md">
          <span class="text-subtitle2" style="white-space: nowrap;">SC1 Files:</span>
          <div class="flex row flex-wrap gap-sm">
            <q-chip
              v-for="file in dataset.sc1_files"
              :key="file"
              class="text-subtitle2"
            >
              {{ file.split('/').pop() }}
            </q-chip>
          </div>
        </div>
        <div class="flex row items-start gap-sm q-mt-md">
          <span class="text-subtitle2" style="white-space: nowrap;">SC2 Files:</span>
          <div class="flex row flex-wrap gap-sm">
            <q-chip
              v-for="file in dataset.sc2_files"
              :key="file"
              class="text-subtitle2"
            >
              {{ file.split('/').pop() }}
            </q-chip>
          </div>
        </div>
        <div
          v-for="groupNum in getGroupNumbers(dataset.sample_files)"
          :key="groupNum"
          class="flex row items-start gap-sm q-mt-md"
        >
          <span class="text-subtitle2" style="white-space: nowrap;">Sample Files 組 {{ groupNum }}:</span>
          <div class="flex row flex-wrap gap-sm">
            <q-chip
              v-for="file in dataset.sample_files.filter(f => f.group === groupNum)"
              :key="file.path"
              class="text-subtitle2"
            >
              {{ file.path.split('/').pop() }}
            </q-chip>
          </div>
        </div>
      </template>
    </template>

    <!-- 新增資料集內容插槽 -->
    <template #add-content>
      <div style="width: 100%;">
        <!-- Type I 資料集 -->
        <div v-if="typeIClass.includes(props.dataset_class)" style="width: 100%;">
          <div class="flex row gap-sm overflow-auto">
            <span class="text-subtitle2" style="white-space: nowrap; margin-top: 0.6em;">Control File:</span>
            <q-file
              v-model="controlFile"
              class="q-mb-md w-100"
              filled
              dense
              use-chips
              :rules="[val => !!val || 'Control File 為必填']"
              lazy-rules
              color="deep-orange-6"
              stack-label
              accept=".xlsx,.xls"
              style="width: 100%;"
            />
          </div>
          <div class="flex row items-start gap-sm overflow-auto">
            <span class="text-subtitle2" style="white-space: nowrap; margin-top: 0.6em;">Sample Files:</span>
            <q-file
              v-model="sampleFiles"
              class="q-mb-md w-100"
              filled
              dense
              multiple
              use-chips
              :rules="[val => val && val.length > 0 || '請至少上傳一個 Sample File']"
              lazy-rules
              color="deep-orange-6"
              stack-label
              accept=".xlsx,.xls"
              style="width: 100%;"
            />
          </div>
        </div>

        <!-- Type II 資料集 -->
        <div v-if="typeIIClass.includes(props.dataset_class)" style="width: 100%;">
          <div
            v-for="sc in ['SC1', 'SC2']"
            :key="sc"
            class="flex row gap-sm w-100 overflow-auto"
            style="gap: 1.5em;"
          >
            <span class="text-subtitle2" style="white-space: nowrap; margin-top: 0.6em;">{{ sc }} File:</span>
            <q-file
              v-model="scFiles[sc]"
              class="q-mb-md w-100"
              filled
              dense
              use-chips
              multiple
              :rules="[val => !!val && val.length === 3 || '請上傳 3 個檔案']"
              lazy-rules
              color="deep-orange-6"
              stack-label
              accept=".xlsx,.xls"
              style="width: 85%;"
            />
          </div>
          <div style="gap: 1.5em;">
            <div
              v-for="(group, groupIndex) in typeIISampleFiles"
              :key="groupIndex"
              class="flex row items-start overflow-auto"
              style="gap: 1.5em;"
            >
              <span class="text-subtitle2" style="white-space: nowrap; margin-top: 0.75em;">Sample Files 組 {{ groupIndex + 1 }}:</span>
              <q-file
                v-model="typeIISampleFiles[groupIndex]"
                class="q-mb-md w-100"
                filled
                dense
                multiple
                use-chips
                :rules="[val => val && val.length === 3 || '請上傳 3 個檔案']"
                lazy-rules
                color="deep-orange-6"
                stack-label
                accept=".xlsx,.xls"
                style="width: 60%;"
              />
              <div class="flex row gap-sm items-center justify-center q-mt-xs" style="gap: 0.5em;">
                <q-btn
                  v-if="groupIndex === typeIISampleFiles.length - 1"
                  color="primary"
                  icon="add_box"
                  dense
                  class="text-subtitle2"
                  label=""
                  @click.prevent="addTypeIISampleFile"
                />
                <q-btn
                  color="red-8"
                  icon="delete"
                  dense
                  class="text-subtitle2"
                  label=""
                  @click.prevent="deleteTypeIISampleFile(groupIndex)"
                />
              </div>
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
import { uploadFileToStorage } from '@/firebase/firebaseStorage'
import { addTestingSample, dataset_list, Database } from '@/firebase/firebaseDatabase'
import { collection, getDocs, doc, deleteDoc } from 'firebase/firestore'
import { v4 as uuidv4 } from 'uuid'
import { createQSEPDataset } from '@/types/dataset'
import GeneralDatasetTmpl from './GeneralDatasetTmpl.vue'

// Props
const props = defineProps({
  dataset_class: {
    type: String,
    required: true
  }
})

// 從子組件獲取值的計算屬性
const generalDatasetTmpl = ref(null)
const datasetName = computed(() => generalDatasetTmpl.value?.datasetName)
const selectedInstrument = computed(() => generalDatasetTmpl.value?.selectedInstrument)
const selectedReagent = computed(() => generalDatasetTmpl.value?.selectedReagent)
const selectedGroup = computed(() => generalDatasetTmpl.value?.selectedGroup)
const selectedQC = computed(() => generalDatasetTmpl.value?.selectedQC)
const resultText = computed(() => generalDatasetTmpl.value?.resultText)
const assessmentsText = computed(() => generalDatasetTmpl.value?.assessmentsText)

// 定義資料集類型
const typeIClass = ['FXS', 'HTD']
const typeIIClass = ['APOE']

// 資料集列表
const datasetList = ref([])

// Type I 資料集
const controlFile = ref(null)
const sampleFiles = ref([])

// Type II 資料集
const scFiles = ref({
  SC1: null,
  SC2: null
})
const typeIISampleFiles = ref([[]])

// 新增 Type II 樣本檔案
const addTypeIISampleFile = () => {
  typeIISampleFiles.value.push([])
}

// 刪除 Type II 樣本檔案
const deleteTypeIISampleFile = (index) => {
  if (typeIISampleFiles.value.length > 1) {
    typeIISampleFiles.value.splice(index, 1)
  } else {
    typeIISampleFiles.value[0] = []
  }
}

// 提交表單
const onSubmit = async () => {
  if (typeIClass.includes(props.dataset_class)) {
    await onSubmitTypeI()
  } else if (typeIIClass.includes(props.dataset_class)) {
    await onSubmitTypeII()
  }
}

// 提交表單 - Type I
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
  const qsepDataset = createQSEPDataset(
    datasetName.value,
    `testing_data/${controlFileStoragePath}`,
    sampleFilePaths,
    null,
    null,
    null,
    selectedInstrument.value,
    selectedReagent.value,
    storagePath,
    props.dataset_class,
    resultText.value,
    assessmentsText.value,
    selectedGroup.value?.value,
    selectedQC.value
  )

  // 將 qsepDataset 轉換為平面物件
  const datasetData = qsepDataset.toPlainObject()

  // 檢查資料庫中是否有相同名稱的資料集
  await saveDataset(datasetData)
}

// 提交表單 - Type II
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
  const qsepDataset = createQSEPDataset(
    datasetName.value,
    null,
    null,
    sc1FilePaths,
    sc2FilePaths,
    sampleFilesPaths,
    selectedInstrument.value,
    selectedReagent.value,
    storagePath,
    props.dataset_class,
    resultText.value,
    assessmentsText.value,
    selectedGroup.value?.value,
    selectedQC.value
  )

  // 將 qsepDataset 轉換為平面物件
  const datasetData = qsepDataset.toPlainObject()

  // 儲存資料集
  await saveDataset(datasetData)
}

// 儲存資料集到資料庫
const saveDataset = async (datasetData) => {
  // 檢查是否已存在相同名稱的資料集
  let datasetUid = ''
  const searchPath = `${dataset_list.testing_data}`
  const collectionRef = collection(Database, searchPath)
  const querySnapshot = await getDocs(collectionRef)

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

  await addTestingSample(datasetData, datasetUid)

  // 重置表單
  onReset()

  // 更新集合顯示
  await updateDatasetList()
}

// 重置表單
const onReset = () => {
  controlFile.value = null
  sampleFiles.value = []
  typeIISampleFiles.value = [[]]
  scFiles.value = {
    SC1: null,
    SC2: null
  }

  // 重置子組件的表單
  if (generalDatasetTmpl.value) {
    generalDatasetTmpl.value.datasetName = ''
    generalDatasetTmpl.value.resultText = ''
    generalDatasetTmpl.value.assessmentsText = ''
  }
}

// 更新集合顯示
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
        dataset = createQSEPDataset(
          docData.dataset_name,
          docData.controlFile,
          docData.sampleFiles,
          null,
          null,
          null,
          docData.instrument,
          docData.reagent,
          docData.storagePath,
          docData.dataset_class,
          docData.result,
          docData.assessments,
          docData.group,
          docData.qc
        )
      } else {
        dataset = createQSEPDataset(
          docData.dataset_name,
          null,
          null,
          docData.sc1_files,
          docData.sc2_files,
          docData.sample_files,
          docData.instrument,
          docData.reagent,
          docData.storagePath,
          docData.dataset_class,
          docData.result,
          docData.assessments,
          docData.group,
          docData.qc
        )
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

// 掛載元件
onMounted(async () => {
  await updateDatasetList()
})
</script>