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
        <q-item v-for="dataset in DatasetList" :key="dataset.name">
          <q-item-section>
            <div style="display: flex; flex-direction: column; align-items: flex-start;" :class="{ 'collapsed': !dataset.isSelected, 'expanded': dataset.isSelected }">
              <div style="display: flex; flex-direction: row; align-items: center; gap: 0.5em; width: 100%; justify-content: space-between;">
                <div style="display: flex; flex-direction: row; align-items: center; gap: 0.5em; width: 100%;">
                  <span v-if="!dataset.edit" class="text-h6 text-bold text-blue-grey-8">{{ dataset.name }}</span>
                  <q-input
                    v-else
                    dense
                    :model-value="dataset.name"
                    @update:model-value="val => dataset.name = val"
                    class="text-h6 text-bold text-blue-grey-8"
                    autofocus
                  />
                  <q-chip color="indigo-3" dense class="text-subtitle2" :label="dataset.instrument" />
                  <q-chip color="blue-4" dense class="text-subtitle2" :label="dataset.reagent" />
                </div>
                <div style="display: flex; flex-direction: row; align-items: center; gap: 0.5em;">
                  <q-btn flat :color="dataset.edit ? 'green-9' : 'primary'" :icon="dataset.edit ? 'check' : 'edit'" dense class="text-subtitle2" @click.prevent="editDataset(dataset)" />
                  <q-btn flat color="red-9" icon="delete" dense class="text-subtitle2" @click.prevent="deleteDataset(dataset)" />
                  <q-btn flat color="cyan-9" icon="info" dense class="text-subtitle2" @click.prevent="displayDataset(dataset)" />
                </div>
              </div>
              <div style="display: flex; flex-direction: column; align-items: flex-start; margin-top: 0.5em; width: 100%; gap: 0.2em;">
                <div>
                  <span class="text-subtitle2">SMN1 SC-C: </span>
                  <q-chip color="grey-3" dense class="text-subtitle2" :label="dataset.smn1_sc_c" />
                </div>
                <div>
                  <span class="text-subtitle2">SMN1 SC-N: </span>
                  <q-chip color="grey-3" dense class="text-subtitle2" :label="dataset.smn1_sc_n" />
                </div>
                <div style="display: flex; flex-direction: column; align-items: flex-start; gap: 0.5em;">
                  <span class="text-subtitle2">SMN1 Samples: </span>
                  <q-chip v-for="sample in dataset.smn1_samples" :key="sample" color="grey-3" dense class="text-subtitle2" :label="sample.name" />
                </div>
                <div>
                  <span class="text-subtitle2">SMN2 SC-C: </span>
                  <q-chip color="grey-3" dense class="text-subtitle2" :label="dataset.smn2_sc_c" />
                </div>
                <div>
                  <span class="text-subtitle2">SMN2 SC-N: </span>
                  <q-chip color="grey-3" dense class="text-subtitle2" :label="dataset.smn2_sc_n" />
                </div>
                <div style="display: flex; flex-direction: column; align-items: flex-start; gap: 0.5em;">
                  <span class="text-subtitle2">SMN2 Samples: </span>
                  <q-chip v-for="sample in dataset.smn2_samples" :key="sample" color="grey-3" dense class="text-subtitle2" :label="sample.name" />
                </div>
              </div>
            </div>
          </q-item-section>
        </q-item>
      </q-list>

    </div>

    <!-- 新增資料集 -->
    <div class="col q-mb-md" style="border: 1px solid #e0e0e0; border-radius: 10px; padding: 10px; background-color: rgba(221, 232, 243, 0.2);">
      <q-form @reset="onReset" @submit="onSubmit">
        <div style="display: flex; flex-direction: row; gap: 0.5em; align-items: center; justify-content: space-between;">
          <div style="display: flex; flex-direction: row; gap: 0.5em;">
            <q-icon name="category" size="md" class="text-blue-grey-7" />
            <span class="text-h5 q-mb-md text-blue-grey-7 text-bold">新增資料集</span>
          </div>
          <div style="display: flex; flex-direction: row; gap: 0.5em;">
            <q-btn-dropdown color="indigo-3" :label="selectedInstrument">
              <q-list>
                <q-item v-for="instrument in getInstrumentOptions" :key="instrument" clickable v-close-popup @click="selectedInstrument = instrument">
                  <q-item-section>
                    {{ instrument.toUpperCase() }}
                  </q-item-section>
                </q-item>
              </q-list>
            </q-btn-dropdown>
            <q-btn-dropdown color="blue-4" :label="selectedReagent">
              <q-list>
                <q-item v-for="reagent in getReagentOptions" :key="reagent" clickable v-close-popup @click="selectedReagent = reagent">
                  <q-item-section>
                    {{ reagent.toUpperCase() }}
                  </q-item-section>
                </q-item>
              </q-list>
            </q-btn-dropdown>
            <q-btn color="cyan-8" icon="add_box" dense class="text-subtitle2" label="新增" type="submit" />
          </div>
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
            <q-btn style="height: 100%; width: 20%;" dense color="deep-orange-6" icon="upload" label="上傳" @click="triggerFileUpload" />
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
              class="q-mb-md"
              dense
              style="width: 100%; display: none;"
              accept=".xlsx,.xls"
              multiple
              @update:model-value="handleFileUpload"
            />
          </div>
          <div style="display: flex; flex-direction: column; gap: 0.5em; width: 100%; align-items: center;">
            <div v-for="(file, index) in uploadedFiles" :key="index" class="full-width q-pa-sm" style="border: 1px solid #e0e0e0; border-radius: 4px;">
              <div class="row items-center q-gutter-md">
                <!-- 檔名 -->
                <div class="col-4" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
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
                    style="width: 150px"
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
          </div>
        </div>
      </q-form>
    </div>
  </div>
</template>

<script setup>
// 導入模組
import { v4 as uuidv4 } from 'uuid'
import { ref, onMounted, computed } from 'vue'
import { useQuasar } from 'quasar'
import { uploadFileToStorage, deleteFile, Storage } from '@/firebase/firebaseStorage'
import { addTestingSample, dataset_list, Database } from '@/firebase/firebaseDatabase'
import { collection, getDocs, doc, deleteDoc, updateDoc } from 'firebase/firestore'
import { ref as storageRef, listAll, deleteObject } from 'firebase/storage'

// 使用 Quasar 的通知
const $q = useQuasar()

// 選取的儀器, 試劑
const selectedInstrument = ref('qsep100')
const selectedReagent = ref('SMA CE v1')

// 定義一個 Dataset 的資料結構
const Dataset = (NAME, SMN1_SC_C, SMN1_SC_N, SMN1_Samples, SMN2_SC_C, SMN2_SC_N, SMN2_Samples, INSTRUMENT, REAGENT) => {
  let datasetObj = {
    name: NAME,
    originalName: NAME,
    smn1_sc_c: SMN1_SC_C,
    smn1_sc_n: SMN1_SC_N,
    smn1_samples: SMN1_Samples,
    smn2_sc_c: SMN2_SC_C,
    smn2_sc_n: SMN2_SC_N,
    smn2_samples: SMN2_Samples,
    isSelected: false,
    edit: false,
    instrument: INSTRUMENT,
    reagent: REAGENT
  }
  return datasetObj
}

// 資料集列表
const DatasetList = ref([])

/* Table Data */
const datasetName = ref('')

// 樣本列表
const sampleList = ref([
  {
    name: '',
    files: null
  }
])

// 選取的基因型
const useGeneType = ref('SMN1')

// 新增的響應式變數
const fileInput = ref(null)
const uploadedFiles = ref([])
const datasetFiles = ref([])
const sampleTypeOptions = [
  { label: 'Sample', value: 'Sample' },
  { label: 'SC-C', value: 'SC-C' },
  { label: 'SC-N', value: 'SC-N' }
]

// 顯示資料集
const displayDataset = (dataset) => {
  dataset.isSelected = !dataset.isSelected
}

// 編輯資料集
const editDataset = async (dataset) => {
  if (dataset.edit) {
    dataset.edit = false
    // 更新資料庫中 dataset_class = "SMA_CE" && dataset_name = dataset.name 的資料
    const search_path = `${dataset_list.testing_data}`;
    const collectionRef = collection(Database, search_path);
    const querySnapshot = await getDocs(collectionRef);

    querySnapshot.forEach(async (document) => {
      const doc_data = document.data();
      if (doc_data.dataset_class === "SMA_CE" && doc_data.dataset_name === dataset.originalName) {
        const docRef = doc(Database, search_path, document.id);
        await updateDoc(docRef, {
          dataset_name: dataset.name
        });
        dataset.originalName = dataset.name;  // 更新成功後更新原始名稱
      }
    });
  } else {
    dataset.originalName = dataset.name;  // 開始編輯時保存原始名稱
    dataset.edit = true;
  }
}

// 刪除資料集
const deleteDataset = async (dataset) => {
  try {
    // 刪除 storage 中的檔案
    const folderPath = `testing_data/${dataset.name}`;
    const folderRef = storageRef(Storage, folderPath);

    // 列出資料夾中的所有檔案
    const result = await listAll(folderRef);

    // 刪除所有檔案
    const deletePromises = result.items.map(item => deleteObject(item));
    await Promise.all(deletePromises);

    // 遞迴處理所有子資料夾
    const subFolderPromises = result.prefixes.map(async (prefix) => {
      const subResult = await listAll(prefix);
      const subDeletePromises = subResult.items.map(item => deleteObject(item));
      return Promise.all(subDeletePromises);
    });

    await Promise.all(subFolderPromises);

    // 取得 database 中所有分析
    const search_path = `${dataset_list.testing_data}`;
    const collectionRef = collection(Database, search_path);

    // 取得所有文件
    const querySnapshot = await getDocs(collectionRef);
    querySnapshot.forEach(async (document) => {
      const doc_data = document.data();
      if (doc_data.dataset_class === "SMA_CE" && doc_data.dataset_name === dataset.name) {
        await deleteDoc(document.ref);
      }
    })

    // 更新顯示
    await updateDatasetList();

  } catch (error) {
    console.error('刪除資料集時發生錯誤：', error);
  }
}

// 修改提交表單函數
const onSubmit = async () => {

  // 檢查所有必填欄位
  if (!datasetName.value || uploadedFiles.value.length === 0) {
    return
  }

  // 開啟 loading
  $q.loading.show()

  // Storage Path, 隨機產生一組 uuid
  const storage_path = uuidv4()

  // 上傳所有樣本的檔案
  const uploadPromises = uploadedFiles.value.map(async (file) => {
    const file_storage_path = `${storage_path}/${file.name}`
    await uploadFileToStorage(file.file, file_storage_path, 'test')
    return {
        file_name: file.name,
        file_path: `testing_data/${file_storage_path}`
      }
    })

  // 將資料集設定存到 firestore
  const dataset_data = {
    dataset_class: "SMA_CE",
    dataset_name: datasetName.value,
    instrument: selectedInstrument.value,
    reagent: selectedReagent.value,
    SMN1_SC_C: uploadedFiles.value.filter(file => file.geneType === 'SMN1' && file.sampleType.value === 'SC-C').map(file => ({
      name: file.name,
      path: `testing_data/${storage_path}/${file.name}`,
      expType: "std1",
      smnType: "smn1"
    })),
    SMN1_SC_N: uploadedFiles.value.filter(file => file.geneType === 'SMN1' && file.sampleType.value === 'SC-N').map(file => ({
      name: file.name,
      path: `testing_data/${storage_path}/${file.name}`,
      expType: "std2",
      smnType: "smn1"
    })),
    SMN1_Samples: uploadedFiles.value.filter(file => file.geneType === 'SMN1' && file.sampleType === 'Sample').map(file => ({
      name: file.name,
      path: `testing_data/${storage_path}/${file.name}`,
      expType: "sample",
      smnType: "smn1"
    })),
    SMN2_SC_C: uploadedFiles.value.filter(file => file.geneType === 'SMN2' && file.sampleType.value === 'SC-C').map(file => ({
      name: file.name,
      path: `testing_data/${storage_path}/${file.name}`,
      expType: "std1",
      smnType: "smn2"
    })),
    SMN2_SC_N: uploadedFiles.value.filter(file => file.geneType === 'SMN2' && file.sampleType.value === 'SC-N').map(file => ({
      name: file.name,
      path: `testing_data/${storage_path}/${file.name}`,
      expType: "std2",
      smnType: "smn2"
    })),
    SMN2_Samples: uploadedFiles.value.filter(file => file.geneType === 'SMN2' && file.sampleType === 'Sample').map(file => ({
      name: file.name,
      path: `testing_data/${storage_path}/${file.name}`,
      expType: "sample",
      smnType: "smn2"
    }))
  }

  // 檢查是否已存在相同名稱的資料集
  let dataset_uid = ''
  const search_path = `${dataset_list.testing_data}`
  const collectionRef = collection(Database, search_path)
  const querySnapshot = await getDocs(collectionRef)
  querySnapshot.forEach(async (document) => {
    const doc_data = document.data()
    if (doc_data.dataset_name === datasetName.value && doc_data.dataset_class === "SMA_CE") {
      dataset_uid = document.id
      await deleteDoc(document.ref)
    }
  })

  // 如果沒有，則新增資料集
  if (dataset_uid === '') {
    dataset_uid = uuidv4()
  }

  await addTestingSample(dataset_data, dataset_uid)

  // 重置表單
  // onReset()

  // 更新集合顯示
  await updateDatasetList()

  // 關閉 loading
  $q.loading.hide()
}

// 修改重置表單函數
const onReset = () => {
  datasetName.value = ''
  sampleList.value = [{
    name: '',
    files: null
  }]
}

// 更新集合顯示
async function updateDatasetList() {
  // 取得 database 中所有分析
  const search_path = `${dataset_list.testing_data}`;
  const collectionRef = collection(Database, search_path);

  // 取得所有文件
  const querySnapshot = await getDocs(collectionRef);

  // 清空集合
  DatasetList.value = []

  // 載入測試樣本
  querySnapshot.forEach(async (document) => {
    const doc_data = document.data();
    if (doc_data.dataset_class && doc_data.dataset_class === "SMA_CE") {
      DatasetList.value.push(Dataset(
        doc_data.dataset_name,
        doc_data.SMN1_SC_C[0].name,
        doc_data.SMN1_SC_N[0].name,
        doc_data.SMN1_Samples,
        doc_data.SMN2_SC_C[0].name,
        doc_data.SMN2_SC_N[0].name,
        doc_data.SMN2_Samples,
        doc_data.instrument,
        doc_data.reagent
      ))
    }
  })
}

// 取得儀器選項
const getInstrumentOptions = ref(['qsep100'])

// 取得試劑
const getReagentOptions = ref([selectedReagent.value])

// 觸發檔案上傳
const triggerFileUpload = () => {
  fileInput.value.pickFiles()
}

// 處理檔案上傳
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
        geneType: useGeneType.value, // 預設值
        sampleType: 'Sample' // 預設值
      })
    }
  })
}

// 掛載元件
onMounted(async () => {
  await updateDatasetList()
  selectedInstrument.value = getInstrumentOptions.value[0]
  selectedReagent.value = getReagentOptions.value[0]
})

// 在 script setup 部分添加 removeFile 函數
const removeFile = (index) => {
  uploadedFiles.value.splice(index, 1)
}

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