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
              <div style="display: flex; flex-direction: column; align-items: flex-start; margin-top: 0.5em; width: 100%;">
                <div v-for="sample in dataset.sample_files" :key="sample.name">
                  <span class="text-subtitle2">{{ sample.name }}</span>
                  <div style="display: flex; justify-content: flex-start; flex-direction: column; align-items: flex-start; gap: 0.5em; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                    <q-chip v-for="file in sample.files" :key="file.file_name" color="grey-3" dense class="text-subtitle2" :label="file.file_name" />
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
          </div>
          <div style="display: flex; flex-direction: column; gap: 0.5em; width: 100%; align-items: center;">
            <div v-for="(sample, index) in sampleList" :key="index" style="display: flex; flex-direction: row; gap: 0.5em; width: 100%; align-items: center;">
              <span class="text-subtitle2" style="white-space: nowrap;">Sample {{ index + 1 }}</span>
              <div style="display: flex; flex-direction: row; width: 100%; align-items: center;">
                <q-input :rules="[val => !!val || '請輸入樣本名稱']" lazy-rules dense filled v-model="sample.name" class="text-subtitle2 q-pa-md" style="width: 50%;" />
                <q-file
                  v-model="sample.files"
                  class="text-subtitle2 q-pa-md"
                  style="width: 100%;"
                  filled
                  dense
                  use-chips
                  multiple
                  :rules="[
                    val => (val && val.length === 2) || '請上傳 2 個結果檔案'
                  ]"
                  lazy-rules
                  label="Upload 2 Sanger *ab1 Files"
                  color="deep-orange-8"
                  accept=".ab1"
                  @update:model-value="val => sample.files = val"
                  @rejected="onRejected"
                />
                <div style="display: flex; flex-direction: row; gap: 0.5em;">
                  <q-btn flat round dense color="primary" icon="add_circle" @click="addSample(index)" />
                  <q-btn flat round dense color="negative" icon="remove_circle" @click="removeSample(index)" v-if="sampleList.length > 1" />
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
import { ref, onMounted, computed } from 'vue'
import { uploadFileToStorage, deleteFile, Storage } from '@/firebase/firebaseStorage'
import { addTestingSample, dataset_list, Database } from '@/firebase/firebaseDatabase'
import { collection, getDocs, doc, deleteDoc, updateDoc } from 'firebase/firestore'
import { v4 as uuidv4 } from 'uuid'
import { ref as storageRef, listAll, deleteObject } from 'firebase/storage'

// 選取的儀器, 試劑
const selectedInstrument = ref('qsep100')
const selectedReagent = ref('Beta-Thal_v1')

// 定義一個 Dataset 的資料結構
const Dataset = (NAME, SAMPLE_FILES, INSTRUMENT, REAGENT, STORAGE_PATH) => {
  let datasetObj = {
    name: NAME,
    originalName: NAME,
    sample_files: SAMPLE_FILES,
    isSelected: false,
    edit: false,
    instrument: INSTRUMENT,
    reagent: REAGENT,
    storagePath: STORAGE_PATH
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

// 顯示資料集
const displayDataset = (dataset) => {
  dataset.isSelected = !dataset.isSelected
}

// 編輯資料集
const editDataset = async (dataset) => {
  if (dataset.edit) {
    dataset.edit = false
    // 更新資料庫中 dataset_class = "BETA-THAL" && dataset_name = dataset.name 的資料
    const search_path = `${dataset_list.testing_data}`;
    const collectionRef = collection(Database, search_path);
    const querySnapshot = await getDocs(collectionRef);

    querySnapshot.forEach(async (document) => {
      const doc_data = document.data();
      if (doc_data.dataset_class === "BETA-THAL" && doc_data.dataset_name === dataset.originalName) {
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
    const folderPath = `testing_data/${dataset.storagePath}`;
    const folderRef = storageRef(Storage, folderPath);

    // 定義遞迴刪除函數
    const recursiveDelete = async (ref) => {
      const result = await listAll(ref);

      // 刪除當前資料夾中的所有檔案
      const fileDeletePromises = result.items.map(item => deleteObject(item));

      // 遞迴處理所有子資料夾
      const folderDeletePromises = result.prefixes.map(async (prefix) => {
        await recursiveDelete(prefix);
      });

      // 等待所有刪除操作完成
      await Promise.all([...fileDeletePromises, ...folderDeletePromises]);
    };

    // 執行遞迴刪除
    await recursiveDelete(folderRef);

    // 取得 database 中所有分析
    const search_path = `${dataset_list.testing_data}`;
    const collectionRef = collection(Database, search_path);

    // 取得所有文件
    const querySnapshot = await getDocs(collectionRef);
    querySnapshot.forEach(async (document) => {
      const doc_data = document.data();
      if (doc_data.dataset_class === "BETA-THAL" && doc_data.dataset_name === dataset.name) {
        await deleteDoc(document.ref);
      }
    })

    // 更新顯示
    await updateDatasetList();

  } catch (error) {
    console.error('刪除資料集時發生錯誤：', error);
  }
}

// 新增樣本
const addSample = (index) => {
  sampleList.value.splice(index + 1, 0, {
    name: '',
    files: null
  })
}

// 移除樣本
const removeSample = (index) => {
  if (sampleList.value.length > 1) {
    sampleList.value.splice(index, 1)
  }
}

// 修改提交表單函數
const onSubmit = async () => {
  // 檢查所有必填欄位
  if (!datasetName.value || sampleList.value.length === 0) {
    return
  }

  // 檢查每個樣本是否都有名稱和兩個檔案
  const isValid = sampleList.value.every(sample =>
    sample.name && sample.files && sample.files.length === 2
  )

  if (!isValid) {
    return
  }

  // Storage Path, 隨機產生一組 uuid
  const storage_path = uuidv4()

  // 上傳所有樣本的檔案
  const uploadPromises = sampleList.value.map(async (sample) => {
    const filePromises = sample.files.map(async (file) => {
      const file_storage_path = `${storage_path}/${sample.name}/${file.name}`
      await uploadFileToStorage(file, file_storage_path, 'test')
      return {
        file_name: file.name,
        file_path: `testing_data/${file_storage_path}`
      }
    })
    return {
      name: sample.name,
      files: await Promise.all(filePromises)
    }
  })

  const uploadedSamples = await Promise.all(uploadPromises)

  // 將資料集設定存到 firestore
  const dataset_data = {
    dataset_class: "BETA-THAL",
    dataset_name: datasetName.value,
    instrument: selectedInstrument.value,
    reagent: selectedReagent.value,
    sample_files: uploadedSamples,
    storagePath: storage_path
  }

  // 檢查是否已存在相同名稱的資料集
  let dataset_uid = ''
  const search_path = `${dataset_list.testing_data}`
  const collectionRef = collection(Database, search_path)
  const querySnapshot = await getDocs(collectionRef)
  querySnapshot.forEach(async (document) => {
    const doc_data = document.data()
    if (doc_data.dataset_name === datasetName.value && doc_data.dataset_class === "BETA-THAL") {
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
  onReset()

  // 更新集合顯示
  await updateDatasetList()
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
    if (doc_data.dataset_class && doc_data.dataset_class === "BETA-THAL") {
      DatasetList.value.push(Dataset(
        doc_data.dataset_name,
        doc_data.sample_files,
        doc_data.instrument,
        doc_data.reagent,
        doc_data.storagePath
      ))
    }
  })
}

// 取得儀器選項
const getInstrumentOptions = ref(['qsep100'])

// 取得試劑
const getReagentOptions = ref([selectedReagent.value])

// 掛載元件
onMounted(async () => {
  await updateDatasetList()
  selectedInstrument.value = getInstrumentOptions.value[0]
  selectedReagent.value = getReagentOptions.value[0]
})

// 處理檔案被拒絕的情況
const onRejected = () => {
  $q.notify({
    type: 'negative',
    message: '只能上傳 .ab1 檔案',
    position: 'top',
    timeout: 2000
  })
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