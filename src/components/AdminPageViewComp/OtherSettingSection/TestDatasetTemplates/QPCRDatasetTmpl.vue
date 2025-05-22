<template>
  <!-- ================ -->
  <!-- 主要資料集模板 -->
  <!-- ================ -->
  <general-dataset-tmpl
    :dataset_class="props.dataset_class"
    :datasetList="DatasetList"
    @submit="onSubmit"
    @updateDatasetList="updateDatasetList"
    ref="generalDatasetTmpl"
  >
    <!-- ================ -->
    <!-- 資料集內容區塊 -->
    <!-- ================ -->
    <template #dataset-content="{ dataset }">
      <!-- 非 Z480 儀器的資料顯示 -->
      <div v-if="dataset.instrument !== 'z480'" class="dataset-info">
        <div class="info-row">
          <span class="info-label">Result File:</span>
          <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset.file?.split('/')?.pop()" />
        </div>
        <!-- SMA 特定欄位 -->
        <template v-if="props.dataset_class === 'SMA'">
          <div class="info-row">
            <span class="info-label">SC1 Well:</span>
            <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset.SC1Well" />
          </div>
          <div class="info-row">
            <span class="info-label">SC2 Well:</span>
            <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset.SC2Well" />
          </div>
        </template>
        <!-- 非 SMA 的控制井 -->
        <div v-else class="info-row">
          <span class="info-label">Control Well:</span>
          <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset.controlWell" />
        </div>
        <div class="info-row">
          <span class="info-label">NTC Well:</span>
          <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset.NTCWell" />
        </div>
      </div>

      <!-- Z480 儀器的資料顯示 -->
      <div v-else class="dataset-info">
        <div class="info-row">
          <span class="info-label">VIC File:</span>
          <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset?.VIC?.split('/')?.pop()" />
        </div>
        <div class="info-row">
          <span class="info-label">FAM File:</span>
          <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset?.FAM?.split('/')?.pop()" />
        </div>
        <!-- SMA 特定欄位 -->
        <template v-if="props.dataset_class === 'SMA'">
          <div class="info-row">
            <span class="info-label">CY5 File:</span>
            <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset?.CY5?.split('/')?.pop()" />
          </div>
          <div class="info-row">
            <span class="info-label">SC1 Well:</span>
            <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset?.SC1Well" />
          </div>
          <div class="info-row">
            <span class="info-label">SC2 Well:</span>
            <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset?.SC2Well" />
          </div>
        </template>
        <!-- 非 SMA 的控制井 -->
        <div v-else class="info-row">
          <span class="info-label">Control Well:</span>
          <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset?.controlWell" />
        </div>
        <div class="info-row">
          <span class="info-label">NTC Well:</span>
          <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset?.NTCWell" />
        </div>
      </div>
    </template>

    <!-- ================ -->
    <!-- 新增內容區塊 -->
    <!-- ================ -->
    <template #add-content>
      <!-- 檔案上傳區域 -->
      <div v-if="selectedInstrument !== 'z480'" class="file-upload-row">
        <span class="upload-label">結果檔案:</span>
        <q-file
          v-model="resultFile"
          class="q-mb-md upload-field"
          dense
          filled
          :rules="[val => !!val || '請上傳結果檔案']"
          use-chips
          color="deep-orange-8"
        />
      </div>

      <!-- Z480 特定檔案上傳 -->
      <div v-else class="z480-upload-section">
        <div class="file-upload-row">
          <span class="upload-label">VIC 檔案:</span>
          <q-file
            v-model="Z480_Files.VIC"
            class="q-mb-md upload-field"
            dense
            filled
            :rules="[val => !!val || '請上傳結果檔案']"
            use-chips
            color="deep-orange-8"
          />
        </div>
        <div class="file-upload-row">
          <span class="upload-label">FAM 檔案:</span>
          <q-file
            v-model="Z480_Files.FAM"
            class="q-mb-md upload-field"
            dense
            filled
            :rules="[val => !!val || '請上傳結果檔案']"
            use-chips
            color="deep-orange-8"
          />
        </div>
        <!-- SMA 特定檔案 -->
        <div v-if="props.dataset_class === 'SMA'" class="file-upload-row">
          <span class="upload-label">CY5 檔案:</span>
          <q-file
            v-model="Z480_Files.CY5"
            class="q-mb-md upload-field"
            dense
            filled
            :rules="[val => !!val || '請上傳結果檔案']"
            use-chips
            color="deep-orange-8"
          />
        </div>
      </div>

      <!-- Well 選擇區域 -->
      <!-- SMA Well 選擇 -->
      <template v-if="props.dataset_class === 'SMA'">
        <div class="well-selection-row">
          <span class="well-label">SC1 Well: </span>
          <div class="well-selects">
            <q-select
              v-model="SC1Well.X"
              class="q-mb-md select-field"
              :options="optionX"
              dense
              filled
              color="deep-orange-8"
            />
            <q-select
              v-model="SC1Well.Y"
              class="q-mb-md select-field"
              :options="optionY"
              dense
              filled
            />
          </div>
        </div>
        <div class="well-selection-row">
          <span class="well-label">SC2 Well: </span>
          <div class="well-selects">
            <q-select
              v-model="SC2Well.X"
              class="q-mb-md select-field"
              :options="optionX"
              dense
              filled
              color="deep-orange-8"
            />
            <q-select
              v-model="SC2Well.Y"
              class="q-mb-md select-field"
              :options="optionY"
              dense
              filled
            />
          </div>
        </div>
      </template>

      <!-- 非 SMA Control Well 選擇 -->
      <div v-if="props.dataset_class !== 'SMA'" class="well-selection-row">
        <span class="well-label">Control Well: </span>
        <div class="well-selects">
          <q-select
            v-model="controlWell.X"
            class="q-mb-md select-field"
            :options="optionX"
            dense
            filled
            color="deep-orange-8"
          />
          <q-select
            v-model="controlWell.Y"
            class="q-mb-md select-field"
            :options="optionY"
            dense
            filled
          />
        </div>
      </div>

      <!-- NTC Well 選擇 -->
      <div v-if="selectedInstrument !== 'SMA'" class="well-selection-row">
        <span class="well-label">NTC Well: </span>
        <div class="well-selects">
          <q-select
            v-model="NTCWell.X"
            class="q-mb-md select-field"
            :options="optionX"
            dense
            filled
            color="deep-orange-8"
          />
          <q-select
            v-model="NTCWell.Y"
            class="q-mb-md select-field"
            :options="optionY"
            dense
            filled
          />
        </div>
      </div>
    </template>
  </general-dataset-tmpl>
</template>

<script setup>
// ===============================
// 引入所需的模組和組件
// ===============================
import { ref, computed, onMounted, watch } from 'vue'
import { uploadFileToStorage } from '@/firebase/firebaseStorage'
import { addTestingSample, dataset_list, Database } from '@/firebase/firebaseDatabase'
import { collection, getDocs, deleteDoc } from 'firebase/firestore'
import { v4 as uuidv4 } from 'uuid'
import GeneralDatasetTmpl from './GeneralDatasetTmpl.vue'
import { createQPCRDataset } from '@/types/dataset'
import { useQuasar } from 'quasar'

// ===============================
// Props 定義
// ===============================
const props = defineProps({
  dataset_class: {
    type: String,
    required: true
  }
})

// ===============================
// 常量定義
// ===============================
// Well 位置選項
const optionX = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
const optionY = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']

// ===============================
// 響應式狀態
// ===============================
// 表單欄位
const resultFile = ref(null)
const controlWell = ref({ X: null, Y: null })
const SC1Well = ref({ X: null, Y: null })
const SC2Well = ref({ X: null, Y: null })
const NTCWell = ref({ X: null, Y: null })
const Z480_Files = ref({ VIC: null, FAM: null, CY5: null })

// 資料集列表
const DatasetList = ref([])

// 子組件引用
const generalDatasetTmpl = ref(null)

// ===============================
// 計算屬性
// ===============================
// 從子組件獲取值
const datasetName = computed(() => generalDatasetTmpl.value?.datasetName)
const selectedInstrument = computed(() => generalDatasetTmpl.value?.selectedInstrument)
const selectedReagent = computed(() => generalDatasetTmpl.value?.selectedReagent)
const selectedGroup = computed(() => generalDatasetTmpl.value?.selectedGroup)
const selectedQC = computed(() => generalDatasetTmpl.value?.selectedQC)
const result_matrix = computed(() => generalDatasetTmpl.value?.result_matrix)

// ===============================
// 工具函數
// ===============================
// 初始化 Quasar 通知
const $q = useQuasar()

// 顯示通知
const showNotification = (type, message) => {
  $q.notify({
    type,
    message,
    position: 'top',
    timeout: 2000
  })
}

// ===============================
// 表單處理方法
// ===============================
// 提交表單
const onSubmit = async () => {
  try {
    // 檢查所有必填欄位
    const isZ480 = selectedInstrument.value === 'z480'
    const isSMA = props.dataset_class === 'SMA'

    // 基本必填項目
    let requiredFields = [datasetName.value]
    let errorMessage = '請檢查所有必填欄位'

    // 根據儀器和測試類型檢查必填項目
    if (isZ480) {
      if (isSMA) {
        requiredFields.push(
          Z480_Files.value.VIC,
          Z480_Files.value.FAM,
          Z480_Files.value.CY5,
          NTCWell.value.X,
          NTCWell.value.Y,
          SC1Well.value.X,
          SC1Well.value.Y,
          SC2Well.value.X,
          SC2Well.value.Y
        )
      } else {
        requiredFields.push(
          Z480_Files.value.VIC,
          Z480_Files.value.FAM,
          NTCWell.value.X,
          NTCWell.value.Y,
          controlWell.value.X,
          controlWell.value.Y
        )
      }
    } else {
      if (isSMA) {
        requiredFields.push(
          resultFile.value,
          NTCWell.value.X,
          NTCWell.value.Y,
          SC1Well.value.X,
          SC1Well.value.Y,
          SC2Well.value.X,
          SC2Well.value.Y
        )
      } else {
        requiredFields.push(
          resultFile.value,
          controlWell.value.X,
          controlWell.value.Y,
          NTCWell.value.X,
          NTCWell.value.Y
        )
      }
    }

    // 檢查是否有任何項目未填
    if (requiredFields.some(field => !field)) {
      showNotification('negative', errorMessage)
      return false
    }

    // Storage Path, 隨機產生一組 uuid
    const storagePath = uuidv4()

    // 上傳檔案並獲取路徑
    let fileData = {}
    if (isZ480) {
      if (Z480_Files.value.VIC) {
        const vicPath = `${storagePath}/VIC/${Z480_Files.value.VIC.name}`
        await uploadFileToStorage(Z480_Files.value.VIC, vicPath, 'test')
        fileData.VIC = `testing_data/${vicPath}`
      }
      if (Z480_Files.value.FAM) {
        const famPath = `${storagePath}/FAM/${Z480_Files.value.FAM.name}`
        await uploadFileToStorage(Z480_Files.value.FAM, famPath, 'test')
        fileData.FAM = `testing_data/${famPath}`
      }
      if (isSMA && Z480_Files.value.CY5) {
        const cy5Path = `${storagePath}/CY5/${Z480_Files.value.CY5.name}`
        await uploadFileToStorage(Z480_Files.value.CY5, cy5Path, 'test')
        fileData.CY5 = `testing_data/${cy5Path}`
      }
    } else if (resultFile.value) {
      const filePath = `${storagePath}/${resultFile.value.name}`
      await uploadFileToStorage(resultFile.value, filePath, 'test')
      fileData.file = `testing_data/${filePath}`
    }

    // 創建 QPCRDataset 實例
    const qpcrDataset = createQPCRDataset(
      datasetName.value,
      fileData.file || null,
      isSMA ? null : `${controlWell.value.X}${controlWell.value.Y}`,
      `${NTCWell.value.X}${NTCWell.value.Y}`,
      isSMA ? `${SC1Well.value.X}${SC1Well.value.Y}` : null,
      isSMA ? `${SC2Well.value.X}${SC2Well.value.Y}` : null,
      selectedInstrument.value,
      selectedReagent.value,
      fileData.VIC || null,
      fileData.FAM || null,
      fileData.CY5 || null,
      storagePath,
      selectedGroup.value?.value,
      selectedQC.value,
      props.dataset_class,
      result_matrix.value
    )

    // 將 qpcrDataset 轉換為平面物件
    const datasetData = qpcrDataset.toPlainObject()

    // 檢查資料庫中是否有相同名稱的資料集
    let datasetUid = ''
    const searchPath = `${dataset_list.testing_data}`
    const collectionRef = collection(Database, searchPath)
    const querySnapshot = await getDocs(collectionRef)

    for (const document of querySnapshot.docs) {
      const docData = document.data()
      if (docData.name === datasetName.value && docData.dataset_class === props.dataset_class) {
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

    // 新增資料集到資料庫
    await addTestingSample(datasetData, datasetUid)

    // 重置表單
    onReset()

    // 更新集合顯示
    await updateDatasetList()

    showNotification('positive', '資料集新增成功')
    return true
  } catch (error) {
    console.error('提交表單時發生錯誤：', error)
    showNotification('negative', '提交表單時發生錯誤')
    return false
  }
}

// 重置表單
const onReset = () => {
  resultFile.value = null
  controlWell.value = { X: null, Y: null }
  SC1Well.value = { X: null, Y: null }
  SC2Well.value = { X: null, Y: null }
  NTCWell.value = { X: null, Y: null }
  Z480_Files.value = { VIC: null, FAM: null, CY5: null }

  // 如果子組件可用，重置子組件的表單
  if (generalDatasetTmpl.value) {
    generalDatasetTmpl.value.datasetName = ''
    generalDatasetTmpl.value.result_matrix = []
  }
}

// 更新集合顯示
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
      if (docData.dataset_class && docData.dataset_class === props.dataset_class) {
        const dataset = createQPCRDataset(
          docData.name,
          docData.resultFile,
          docData.controlWell,
          docData.NTCWell,
          docData.SC1Well,
          docData.SC2Well,
          docData.instrument,
          docData.reagent,
          docData.VIC,
          docData.FAM,
          docData.CY5,
          docData.storagePath,
          docData.group,
          docData.qc,
          docData.dataset_class,
          docData.result_matrix
        )
        DatasetList.value.push(dataset)
      }
    }
  } catch (error) {
    console.error('更新資料集列表時發生錯誤:', error)
    showNotification('negative', '更新資料集列表時發生錯誤')
  }
}

// ===============================
// 監聽器
// ===============================
// 監控儀器變更，自動更新試劑選項
watch(selectedInstrument, () => {
  // 獲取正確的試劑值
  let newReagentValue
  switch (props.dataset_class) {
    case 'MTHFR':
      newReagentValue = selectedInstrument.value === 'z480' ? 'MTHFR_v3' : 'MTHFR_v1'
      break
    case 'NUDT15':
      newReagentValue = selectedInstrument.value === 'z480' ? 'NUDT15_v2' : 'NUDT15_v1'
      break
    case 'SMA':
      newReagentValue = selectedInstrument.value === 'z480' ? 'SMA_v3' : 'SMA_v1'
      break
    default:
      return
  }

  // 通知父組件更新reagent值
  if (generalDatasetTmpl.value && generalDatasetTmpl.value.selectedReagent !== newReagentValue) {
    generalDatasetTmpl.value.selectedReagent = newReagentValue
  }
})

// ===============================
// 生命週期鉤子
// ===============================
onMounted(async () => {
  await updateDatasetList()
})
</script>

<style scoped>
/* 資料集資訊顯示 */
.dataset-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-top: 0.5em;
}

.info-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 0.5em;
}

.info-label {
  font-size: 0.9em;
  font-weight: 500;
}

/* 檔案上傳區域 */
.file-upload-row {
  display: flex;
  flex-direction: row;
  gap: 1.5em;
  width: 100%;
}

.upload-label {
  font-size: 0.9em;
  white-space: nowrap;
  margin-top: 0.6em;
}

.upload-field {
  width: 100%;
}

/* Z480 特定上傳區域 */
.z480-upload-section {
  display: flex;
  flex-direction: column;
  width: 100%;
}

/* Well 選擇區域 */
.well-selection-row {
  display: flex;
  flex-direction: row;
  gap: 0.5em;
  width: 100%;
}

.well-label {
  font-size: 0.9em;
  white-space: nowrap;
  margin-top: 0.6em;
}

.well-selects {
  display: flex;
  flex-direction: row;
  gap: 0.5em;
  width: 100%;
}

.select-field {
  width: 100%;
}
</style>
