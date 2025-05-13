<template>
  <general-dataset-tmpl
    :dataset_class="props.dataset_class"
    :datasetList="DatasetList"
    @submit="onSubmit"
    @updateDatasetList="updateDatasetList"
    ref="generalDatasetTmpl"
  >
    <template #dataset-content="{ dataset }">
      <div v-if="dataset.instrument !== 'z480'" style="display: flex; flex-direction: column; align-items: flex-start; margin-top: 0.5em;">
        <div style="display: flex; flex-direction: row; align-items: center; gap: 0.5em;">
          <span class="text-subtitle2">Result File:</span>
          <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset.file?.split('/')?.pop()" />
        </div>
        <div v-if="props.dataset_class !== 'SMA'" style="display: flex; flex-direction: row; align-items: center; gap: 0.5em;">
          <span class="text-subtitle2">Control Well:</span>
          <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset.controlWell" />
        </div>
        <div v-if="props.dataset_class === 'SMA'" style="display: flex; flex-direction: row; align-items: center; gap: 0.5em;">
          <span class="text-subtitle2">SC1 Well:</span>
          <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset.SC1Well" />
        </div>
        <div v-if="props.dataset_class === 'SMA'" style="display: flex; flex-direction: row; align-items: center; gap: 0.5em;">
          <span class="text-subtitle2">SC2 Well:</span>
          <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset.SC2Well" />
        </div>
        <div style="display: flex; flex-direction: row; align-items: center; gap: 0.5em;">
          <span class="text-subtitle2">NTC Well:</span>
          <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset.NTCWell" />
        </div>
      </div>
      <div v-else style="display: flex; flex-direction: column; align-items: flex-start; margin-top: 0.5em;">
        <div style="display: flex; flex-direction: row; align-items: center; gap: 0.5em;">
          <span class="text-subtitle2">VIC File:</span>
          <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset?.VIC?.split('/')?.pop()" />
        </div>
        <div style="display: flex; flex-direction: row; align-items: center; gap: 0.5em;">
          <span class="text-subtitle2">FAM File:</span>
          <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset?.FAM?.split('/')?.pop()" />
        </div>
        <div v-if="props.dataset_class === 'SMA'" style="display: flex; flex-direction: row; align-items: center; gap: 0.5em;">
          <span class="text-subtitle2">CY5 File:</span>
          <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset?.CY5?.split('/')?.pop()" />
        </div>
        <div v-if="props.dataset_class !== 'SMA'" style="display: flex; flex-direction: row; align-items: center; gap: 0.5em;">
          <span class="text-subtitle2">Control Well:</span>
          <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset?.controlWell" />
        </div>
        <div v-if="props.dataset_class === 'SMA'" style="display: flex; flex-direction: row; align-items: center; gap: 0.5em;">
          <span class="text-subtitle2">SC1 Well:</span>
          <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset?.SC1Well" />
        </div>
        <div v-if="props.dataset_class === 'SMA'" style="display: flex; flex-direction: row; align-items: center; gap: 0.5em;">
          <span class="text-subtitle2">SC2 Well:</span>
          <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset?.SC2Well" />
        </div>
        <div style="display: flex; flex-direction: row; align-items: center; gap: 0.5em;">
          <span class="text-subtitle2">NTC Well:</span>
          <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset?.NTCWell" />
        </div>
      </div>
    </template>

    <template #add-content>
      <div v-if="selectedInstrument !== 'z480'" style="display: flex; flex-direction: row; gap: 1.5em; width: 100%;">
        <span class="text-subtitle2" style="white-space: nowrap; margin-top: 0.6em;">結果檔案:</span>
        <q-file
          v-model="resultFile"
          class="q-mb-md"
          dense
          filled
          style="width: 100%;"
          :rules="[val => !!val || '請上傳結果檔案']"
          use-chips
          color="deep-orange-8"
        />
      </div>
      <div v-else style="display: flex; flex-direction: column; width: 100%;">
        <div style="display: flex; flex-direction: row; gap: 0.5em; width: 100%;">
          <span class="text-subtitle2" style="white-space: nowrap; margin-top: 0.6em;">VIC 檔案:</span>
          <q-file
            v-model="Z480_Files.VIC"
            class="q-mb-md"
            dense
            filled
            style="width: 100%;"
            :rules="[val => !!val || '請上傳結果檔案']"
            use-chips
            color="deep-orange-8"
          />
        </div>
        <div style="display: flex; flex-direction: row; gap: 0.5em; width: 100%;">
          <span class="text-subtitle2" style="white-space: nowrap; margin-top: 0.6em;">FAM 檔案:</span>
          <q-file
            v-model="Z480_Files.FAM"
            class="q-mb-md"
            dense
            filled
            style="width: 100%;"
            :rules="[val => !!val || '請上傳結果檔案']"
            use-chips
            color="deep-orange-8"
          />
        </div>
        <div v-if="props.dataset_class === 'SMA'" style="display: flex; flex-direction: row; gap: 0.5em; width: 100%;">
          <span class="text-subtitle2" style="white-space: nowrap; margin-top: 0.6em;">CY5 檔案:</span>
          <q-file
            v-model="Z480_Files.CY5"
            class="q-mb-md"
            dense
            filled
            style="width: 100%;"
            :rules="[val => !!val || '請上傳結果檔案']"
            use-chips
            color="deep-orange-8"
          />
        </div>
      </div>
      <div v-if="props.dataset_class === 'SMA'" style="display: flex; flex-direction: row; gap: 0.5em; width: 100%;">
        <span class="text-subtitle2" style="white-space: nowrap; margin-top: 0.6em;">SC1 Well: </span>
        <q-select
          v-model="SC1Well.X"
          class="q-mb-md"
          :options="optionX"
          dense
          filled
          color="deep-orange-8"
          style="width: 100%;"
        />
        <q-select
          v-model="SC1Well.Y"
          class="q-mb-md"
          :options="optionY"
          dense
          filled
          style="width: 100%;"
        />
      </div>
      <div v-if="props.dataset_class === 'SMA'" style="display: flex; flex-direction: row; gap: 0.5em; width: 100%;">
        <span class="text-subtitle2" style="white-space: nowrap; margin-top: 0.6em;">SC2 Well: </span>
        <q-select
          v-model="SC2Well.X"
          class="q-mb-md"
          :options="optionX"
          dense
          filled
          color="deep-orange-8"
          style="width: 100%;"
        />
        <q-select
          v-model="SC2Well.Y"
          class="q-mb-md"
          :options="optionY"
          dense
          filled
          style="width: 100%;"
        />
      </div>
      <div v-if="props.dataset_class !== 'SMA'" style="display: flex; flex-direction: row; gap: 0.5em; width: 100%;">
        <span class="text-subtitle2" style="white-space: nowrap; margin-top: 0.6em;">Control Well: </span>
        <q-select
          v-model="controlWell.X"
          class="q-mb-md"
          :options="optionX"
          dense
          filled
          color="deep-orange-8"
          style="width: 100%;"
        />
        <q-select
          v-model="controlWell.Y"
          class="q-mb-md"
          :options="optionY"
          dense
          filled
          style="width: 100%;"
        />
      </div>
      <div v-if="selectedInstrument !== 'SMA'" style="display: flex; flex-direction: row; gap: 0.5em; width: 100%;">
        <span class="text-subtitle2" style="white-space: nowrap; margin-top: 0.6em;">NTC Well: </span>
        <q-select
          v-model="NTCWell.X"
          class="q-mb-md"
          :options="optionX"
          dense
          filled
          color="deep-orange-8"
          style="width: 100%;"
        />
        <q-select
          v-model="NTCWell.Y"
          class="q-mb-md"
          :options="optionY"
          dense
          filled
          style="width: 100%;"
        />
      </div>
    </template>
  </general-dataset-tmpl>
</template>

<script setup>
// 導入模組
import { ref, computed, onMounted, watch } from 'vue'
import { uploadFileToStorage } from '@/firebase/firebaseStorage'
import { addTestingSample, dataset_list, Database } from '@/firebase/firebaseDatabase'
import { collection, getDocs, deleteDoc } from 'firebase/firestore'
import { v4 as uuidv4 } from 'uuid'
import GeneralDatasetTmpl from './GeneralDatasetTmpl.vue'
import { createQPCRDataset } from '@/types/dataset'

// Props
const props = defineProps({
  dataset_class: {
    type: String,
    required: true
  }
})

// 定義選項
const optionX = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
const optionY = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']

// 定義表單欄位
const resultFile = ref(null)
const controlWell = ref({ X: null, Y: null })
const SC1Well = ref({ X: null, Y: null })
const SC2Well = ref({ X: null, Y: null })
const NTCWell = ref({ X: null, Y: null })
const Z480_Files = ref({ VIC: null, FAM: null, CY5: null })

// 從子組件獲取值的計算屬性
const generalDatasetTmpl = ref(null)
const datasetName = computed(() => generalDatasetTmpl.value?.datasetName)
const selectedInstrument = computed(() => generalDatasetTmpl.value?.selectedInstrument)
const selectedReagent = computed(() => generalDatasetTmpl.value?.selectedReagent)
const selectedGroup = computed(() => generalDatasetTmpl.value?.selectedGroup)
const selectedQC = computed(() => generalDatasetTmpl.value?.selectedQC)
const resultText = computed(() => generalDatasetTmpl.value?.resultText)
const assessmentsText = computed(() => generalDatasetTmpl.value?.assessmentsText)


// 資料集列表
const DatasetList = ref([])

// 提交表單
const onSubmit = async () => {
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
    console.log(errorMessage)
    return
  }

  // Storage Path, 隨機產生一組 uuid
  const storage_path = uuidv4()

  try {
    // 上傳檔案到 Storage
    if (isZ480) {
      const VIC_storage_path = `${storage_path}/${Z480_Files.value.VIC.name}`
      const FAM_storage_path = `${storage_path}/${Z480_Files.value.FAM.name}`
      await uploadFileToStorage(Z480_Files.value.VIC, VIC_storage_path, 'test')
      await uploadFileToStorage(Z480_Files.value.FAM, FAM_storage_path, 'test')

      if (isSMA && Z480_Files.value.CY5) {
        const CY5_storage_path = `${storage_path}/${Z480_Files.value.CY5.name}`
        await uploadFileToStorage(Z480_Files.value.CY5, CY5_storage_path, 'test')
      }
    } else if (resultFile.value) {
      // 上傳結果檔案
      const result_file_storage_path = `${storage_path}/${resultFile.value.name}`
      await uploadFileToStorage(resultFile.value, result_file_storage_path, 'test')
    }

    // 創建QPCRDataset類實例
    const qpcrDataset = createQPCRDataset(
      datasetName.value,
      isZ480 ? null : `testing_data/${storage_path}/${resultFile.value.name}`,
      `${controlWell.value.X}${controlWell.value.Y}`,
      `${NTCWell.value.X}${NTCWell.value.Y}`,
      `${SC1Well.value.X}${SC1Well.value.Y}`,
      `${SC2Well.value.X}${SC2Well.value.Y}`,
      selectedInstrument.value,
      selectedReagent.value,
      isZ480 ? `testing_data/${storage_path}/${Z480_Files.value.VIC.name}` : null,
      isZ480 ? `testing_data/${storage_path}/${Z480_Files.value.FAM.name}` : null,
      isZ480 && isSMA && Z480_Files.value.CY5 ? `testing_data/${storage_path}/${Z480_Files.value.CY5.name}` : null,
      storage_path,
      resultText.value,
      assessmentsText.value,
      selectedGroup.value.value,
      selectedQC.value,
      props.dataset_class
    );

    // 將QPCRDataset轉換為平面物件
    const dataset_data = {
      ...qpcrDataset.toPlainObject()
    };

    // 先檢查資料庫是否有相同名稱和分類的資料集
    let dataset_uid = ''
    const search_path = `${dataset_list.testing_data}`
    const collectionRef = collection(Database, search_path)
    const querySnapshot = await getDocs(collectionRef)

    querySnapshot.forEach(async (document) => {
      const doc_data = document.data()
      if (doc_data.name === datasetName.value && doc_data.dataset_class === props.dataset_class) {
        dataset_uid = document.id
        await deleteDoc(document.ref)
      }
    })

    // 如果沒有找到既有資料集，產生新的 UUID
    if (dataset_uid === '') {
      dataset_uid = uuidv4()
    }

    // 新增資料集到資料庫
    await addTestingSample(dataset_data, dataset_uid)

    // 重置表單
    onReset()

    // 更新集合顯示
    await updateDatasetList()
  } catch (error) {
    console.error('新增資料集時發生錯誤:', error)
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
    generalDatasetTmpl.value.resultText = ''
    generalDatasetTmpl.value.assessmentsText = ''
  }
}

// 更新集合顯示
async function updateDatasetList() {
  try {
    // 取得 database 中所有分析
    const search_path = `${dataset_list.testing_data}`
    const collectionRef = collection(Database, search_path)
    const querySnapshot = await getDocs(collectionRef)

    // 清空集合
    DatasetList.value = []

    // 載入測試樣本
    querySnapshot.forEach((document) => {
      const doc_data = document.data()
      if (doc_data.dataset_class && doc_data.dataset_class === props.dataset_class) {
        const dataset = createQPCRDataset(
          doc_data.name,
          doc_data.resultFile,
          doc_data.controlWell,
          doc_data.NTCWell,
          doc_data.SC1Well,
          doc_data.SC2Well,
          doc_data.instrument,
          doc_data.reagent,
          doc_data.VIC,
          doc_data.FAM,
          doc_data.CY5,
          doc_data.storagePath,
          doc_data.result,
          doc_data.assessments,
          doc_data.group,
          doc_data.qc,
          doc_data.dataset_class
        );
        DatasetList.value.push(dataset);
      }
    })
  } catch (error) {
    console.error('更新資料集列表時發生錯誤:', error)
  }
}

// 監控儀器變更，自動更新試劑選項
watch(selectedInstrument, () => {
  // 獲取正確的試劑值
  let newReagentValue;

  switch (props.dataset_class) {
    case 'MTHFR':
      newReagentValue = selectedInstrument.value === 'z480' ? 'MTHFR_v3' : 'MTHFR_v1';
      break;
    case 'NUDT15':
      newReagentValue = selectedInstrument.value === 'z480' ? 'NUDT15_v2' : 'NUDT15_v1';
      break;
    case 'SMA':
      newReagentValue = selectedInstrument.value === 'z480' ? 'SMA_v3' : 'SMA_v1';
      break;
    default:
      return;
  }

  // 通知父組件更新reagent值
  if (generalDatasetTmpl.value && generalDatasetTmpl.value.selectedReagent !== newReagentValue) {
    generalDatasetTmpl.value.selectedReagent = newReagentValue;
  }
})

// 掛載元件
onMounted(async () => {
  await updateDatasetList()
})
</script>
