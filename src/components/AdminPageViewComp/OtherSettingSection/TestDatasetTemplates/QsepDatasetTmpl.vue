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
                <div style="display: flex; flex-direction: row; align-items: center; gap: 0.5em;">
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
              <div style="display: flex; flex-direction: column; align-items: flex-start; margin-top: 0.5em;">
                <template v-if="TypeI_class.includes(props.dataset_class)">
                  <div style="display: flex; flex-direction: row; align-items: center; gap: 0.5em;">
                    <span class="text-subtitle2">Control File:</span>
                    <q-chip class="text-subtitle2" style="margin-right: 0.5em;">{{ dataset.controlFile.split('/').pop() }}</q-chip>
                  </div>
                  <div style="display: flex; flex-direction: row; align-items: flex-start; gap: 0.5em;">
                    <span class="text-subtitle2" style="white-space: nowrap; margin-top: 0.5em;">Sample Files:</span>
                    <div style="display: flex; flex-direction: column; align-items: flex-start; flex-wrap: wrap;">
                      <q-chip v-for="file in dataset.sampleFiles" :key="file" class="text-subtitle2" style="margin-right: 0.5em;">{{ file.split('/').pop() }}</q-chip>
                    </div>
                  </div>
                </template>
                <template v-else>
                  <div style="display: flex; flex-direction: row; align-items: flex-start; gap: 0.5em; margin-top: 1.5em;">
                    <span class="text-subtitle2" style="white-space: nowrap;">SC1 Files:</span>
                    <div style="display: flex; flex-direction: row; flex-wrap: wrap; gap: 0.5em;">
                      <q-chip v-for="file in dataset.sc1_files" :key="file" class="text-subtitle2">{{ file.split('/').pop() }}</q-chip>
                    </div>
                  </div>
                  <div style="display: flex; flex-direction: row; align-items: flex-start; gap: 0.5em; margin-top: 1.5em;">
                    <span class="text-subtitle2" style="white-space: nowrap;">SC2 Files:</span>
                    <div style="display: flex; flex-direction: row; flex-wrap: wrap; gap: 0.5em;">
                      <q-chip v-for="file in dataset.sc2_files" :key="file" class="text-subtitle2">{{ file.split('/').pop() }}</q-chip>
                    </div>
                  </div>
                  <div v-for="groupNum in getGroupNumbers(dataset.sample_files)" :key="groupNum" style="display: flex; flex-direction: row; align-items: flex-start; gap: 0.5em; margin-top: 1.5em;">
                    <span class="text-subtitle2" style="white-space: nowrap;">Sample Files 組 {{ groupNum }}:</span>
                    <div style="display: flex; flex-direction: row; flex-wrap: wrap; gap: 0.5em;">
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

          <!-- Type I 資料集 -->
          <div v-if="TypeI_class.includes(props.dataset_class)" style="width: 100%;">
            <div style="display: flex; flex-direction: row; gap: 0.5em; width: 100%; overflow: auto;">
              <span class="text-subtitle2" style="white-space: nowrap; margin-top: 0.6em;">Control File:</span>
              <q-file
                v-model="controlFile"
                class="q-mb-md"
                filled
                dense
                style="width: 100%;"
                use-chips
                :rules="[val => !!val || 'Control File 為必填']"
                lazy-rules
                color="deep-orange-6"
                stack-label
                accept=".xlsx,.xls"
              />
            </div>
            <div style="display: flex; flex-direction: row; align-items: flex-start; gap: 0.5em; width: 100%; overflow: auto;">
              <span class="text-subtitle2" style="white-space: nowrap; margin-top: 0.6em;">Sample Files:</span>
              <q-file
                v-model="sampleFiles"
                class="q-mb-md"
                filled
                dense
                style="width: 100%;"
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

          <!-- Type II 資料集 -->
          <div v-if="TypeII_class.includes(props.dataset_class)" style="width: 100%;">
            <div v-for="sc in ['SC1', 'SC2']" :key="sc" style="display: flex; flex-direction: row; gap: 0.5em; width: 100%; overflow: auto;">
              <span class="text-subtitle2" style="white-space: nowrap; margin-top: 0.6em;">{{ sc }} File:</span>
              <q-file
                v-model="SC_Files[sc]"
                class="q-mb-md"
                filled
                dense
                style="width: 100%;"
                use-chips
                multiple
                :rules="[val => !!val && val.length === 3 || '請上傳 3 個檔案']"
                lazy-rules
                color="deep-orange-6"
                stack-label
                accept=".xlsx,.xls"
              />
            </div>
            <div style="display: flex; flex-direction: column; gap: 1em; width: 100%;">
              <div v-for="(group, groupIndex) in TypeII_sampleFiles" :key="groupIndex" style="display: flex; flex-direction: row; align-items: flex-start; gap: 0.5em; width: 100%; overflow: auto;">
                <span class="text-subtitle2" style="white-space: nowrap; margin-top: 0.6em;">Sample Files 組 {{ groupIndex + 1 }}:</span>
                <q-file
                  v-model="TypeII_sampleFiles[groupIndex]"
                  class="q-mb-md"
                  filled
                  dense
                  style="width: 100%;"
                  multiple
                  use-chips
                  :rules="[val => val && val.length === 3 || '請上傳 3 個檔案']"
                  lazy-rules
                  color="deep-orange-6"
                  stack-label
                  accept=".xlsx,.xls"
                />
                <div style="display: flex; flex-direction: row; gap: 0.5em; align-items: center; justify-content: center; margin-top: 0.2em;">
                  <q-btn v-if="groupIndex === TypeII_sampleFiles.length - 1" color="primary" icon="add_box" dense class="text-subtitle2" label="" @click.prevent="addTypeII_sampleFile" />
                  <q-btn color="red-8" icon="delete" dense class="text-subtitle2" label="" @click.prevent="deleteTypeII_sampleFile(groupIndex)" />
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

// Props
const props = defineProps({
  dataset_class: {
    type: String,
    required: true
  }
})

// 定義資料集類型
const TypeI_class = ['FXS', 'HTD']
const TypeII_class = ['APOE']

// 選取的儀器, 試劑
const selectedInstrument = ref(null)
const selectedReagent = ref(null)

// 定義一個 Dataset 的資料結構
const Dataset = (NAME, CONTROL_FILE, SAMPLE_FILES, INSTRUMENT, REAGENT, STORAGE_PATH) => {
  let datasetObj = {
    name: NAME,
    originalName: NAME,
    isSelected: false,
    edit: false,
    instrument: INSTRUMENT,
    reagent: REAGENT,
    storagePath: STORAGE_PATH
  }

  if (TypeI_class.includes(props.dataset_class)) {
    // Type I 資料集的處理
    datasetObj = {
      ...datasetObj,
      controlFile: CONTROL_FILE,
      sampleFiles: SAMPLE_FILES
    }
  } else {
    // Type II 資料集的處理
    datasetObj = {
      ...datasetObj,
      sc1_files: CONTROL_FILE,  // 在 Type II 中，CONTROL_FILE 存放 sc1_files
      sc2_files: SAMPLE_FILES.sc2_files,  // SAMPLE_FILES 包含 sc2_files 和 sample_files
      sample_files: SAMPLE_FILES.sample_files
    }
  }

  return datasetObj
}

// 資料集列表
const DatasetList = ref([])

/* Table Data */
const datasetName = ref('')

// Type I 資料集
const controlFile = ref(null)
const sampleFiles = ref([])

// Type II 資料集
const SC_Files = ref({
  SC1: null,
  SC2: null
})
const TypeII_sampleFiles = ref([[]])

// 顯示資料集
const displayDataset = (dataset) => {
  dataset.isSelected = !dataset.isSelected
}

// 編輯資料集
const editDataset = async (dataset) => {
  if (dataset.edit) {
    dataset.edit = false
    // 更新資料庫中 dataset_class = props.dataset_class && dataset_name = dataset.name 的資料
    const search_path = `${dataset_list.testing_data}`;
    const collectionRef = collection(Database, search_path);
    const querySnapshot = await getDocs(collectionRef);

    querySnapshot.forEach(async (document) => {
      const doc_data = document.data();
      if (doc_data.dataset_class === props.dataset_class && doc_data.dataset_name === dataset.originalName) {
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
      if (doc_data.dataset_class === props.dataset_class && doc_data.dataset_name === dataset.name) {
        await deleteDoc(document.ref);
      }
    })

    // 更新顯示
    await updateDatasetList();

  } catch (error) {
    console.error('刪除資料集時發生錯誤：', error);
  }
}

// 新增 Type II 樣本檔案
const addTypeII_sampleFile = () => {
  TypeII_sampleFiles.value.push([])
}

// 刪除 Type II 樣本檔案
const deleteTypeII_sampleFile = (index) => {
  if (TypeII_sampleFiles.value.length > 1) {
    TypeII_sampleFiles.value.splice(index, 1)
  } else {
    TypeII_sampleFiles.value[0] = []
  }
}

// 提交表單
const onSubmit = async () => {
  if (TypeI_class.includes(props.dataset_class)) {
    onSubmitI()
  } else if (TypeII_class.includes(props.dataset_class)) {
    onSubmitII()
  }
}

// 提交表單
const onSubmitI = async () => {
  // 檢查所有必填欄位
  if (!datasetName.value || !controlFile.value || !sampleFiles.value || sampleFiles.value.length === 0) {
    return
  }

  // Storage Path, 隨機產生一組 uuid
  const storage_path = uuidv4()

  // 上傳 Control File
  const control_file_storage_path = `${storage_path}/${controlFile.value.name}`
  uploadFileToStorage(controlFile.value, control_file_storage_path, 'test')

  // 上傳 Sample Files
  sampleFiles.value.forEach(async (file) => {
    const sample_file_storage_path = `${storage_path}/${file.name}`
    await uploadFileToStorage(file, sample_file_storage_path, 'test')
  })

  // 將資料集設定存到 firestore
  const dataset_data = {
    dataset_class: props.dataset_class,
    dataset_name: datasetName.value,
    instrument: selectedInstrument.value,
    reagent: selectedReagent.value,
    storagePath: storage_path,
    controlFile: `testing_data/${control_file_storage_path}`,
    sampleFiles: sampleFiles.value.map(file => `testing_data/${storage_path}/${file.name}`)
  }

  // 先檢查資料庫是否有 datasetName 和 dataset_class === props.dataset_class 的資料
  let dataset_uid = ''
  const search_path = `${dataset_list.testing_data}`;
  const collectionRef = collection(Database, search_path);
  const querySnapshot = await getDocs(collectionRef);
  querySnapshot.forEach(async (document) => {
    const doc_data = document.data();
    if (doc_data.dataset_name === datasetName.value && doc_data.dataset_class === props.dataset_class) {
      // 如果有的話，刪除資料集, 取得 id
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

// 提交表單
const onSubmitII = async () => {
  // 檢查所有必填欄位
  if (!datasetName.value || !SC_Files.value.SC1 || !SC_Files.value.SC2) {
    return
  }

  // 檢查每組 Sample Files 是否都有3個檔案
  const isValidSampleFiles = TypeII_sampleFiles.value.every(group => group && group.length === 3)
  if (!isValidSampleFiles) {
    return
  }

  // Storage Path, 隨機產生一組 uuid
  const storage_path = uuidv4()

  // 上傳 SC1 Files
  const sc1_file_paths = await Promise.all(SC_Files.value.SC1.map(async (file) => {
    const file_storage_path = `${storage_path}/SC1/${file.name}`
    await uploadFileToStorage(file, file_storage_path, 'test')
    return `testing_data/${file_storage_path}`
  }))

  // 上傳 SC2 Files
  const sc2_file_paths = await Promise.all(SC_Files.value.SC2.map(async (file) => {
    const file_storage_path = `${storage_path}/SC2/${file.name}`
    await uploadFileToStorage(file, file_storage_path, 'test')
    return `testing_data/${file_storage_path}`
  }))

  // 上傳所有組的 Sample Files
  const sample_files_paths = []
  for (let groupIndex = 0; groupIndex < TypeII_sampleFiles.value.length; groupIndex++) {
    const group = TypeII_sampleFiles.value[groupIndex]
    for (const file of group) {
      const file_storage_path = `${storage_path}/samples/group${groupIndex + 1}/${file.name}`
      await uploadFileToStorage(file, file_storage_path, 'test')
      sample_files_paths.push({
        group: groupIndex + 1,
        path: `testing_data/${file_storage_path}`
      })
    }
  }

  // 將資料集設定存到 firestore
  const dataset_data = {
    dataset_class: props.dataset_class,
    dataset_name: datasetName.value,
    instrument: selectedInstrument.value,
    reagent: selectedReagent.value,
    sc1_files: sc1_file_paths,
    sc2_files: sc2_file_paths,
    sample_files: sample_files_paths,
    storagePath: storage_path
  }

  // 檢查是否已存在相同名稱的資料集
  let dataset_uid = ''
  const search_path = `${dataset_list.testing_data}`
  const collectionRef = collection(Database, search_path)
  const querySnapshot = await getDocs(collectionRef)
  querySnapshot.forEach(async (document) => {
    const doc_data = document.data()
    if (doc_data.dataset_name === datasetName.value && doc_data.dataset_class === props.dataset_class) {
      // 如果有的話，刪除資料集, 取得 id
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

// 重置表單
const onReset = () => {
  datasetName.value = ''
  controlFile.value = null
  sampleFiles.value = []
  TypeII_sampleFiles.value = [[]]
  SC_Files.value = {
    SC1: null,
    SC2: null
  }
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
    if (doc_data.dataset_class && doc_data.dataset_class === props.dataset_class) {
      if (TypeI_class.includes(props.dataset_class)) {
        DatasetList.value.push(Dataset(doc_data.dataset_name, doc_data.controlFile, doc_data.sampleFiles, doc_data.instrument, doc_data.reagent, doc_data.storagePath))
      } else {
        DatasetList.value.push(Dataset(
          doc_data.dataset_name,
          doc_data.sc1_files,
          {
            sc2_files: doc_data.sc2_files,
            sample_files: doc_data.sample_files
          },
          doc_data.instrument,
          doc_data.reagent,
          doc_data.storagePath
        ))
      }
    }
  })
}

// 取得儀器選項
const getInstrumentOptions = computed(() => {
  switch (props.dataset_class) {
    case 'FXS':
      return ['qsep100']
    case 'HTD':
      return ['qsep100']
    case 'APOE':
      return ['qsep100']
    default:
      return []
  }
})

// 取得試劑
const getReagentOptions = computed(() => {
  switch (props.dataset_class) {
    case 'FXS':
      return ['FXS_v1', 'FXS_v2']
    case 'HTD':
      return ['HTD_v1']
    case 'APOE':
      return ['APOE_v1']
    default:
      return []
  }
})

// 掛載元件
onMounted(async () => {
  await updateDatasetList()
  selectedInstrument.value = getInstrumentOptions.value[0]
  selectedReagent.value = getReagentOptions.value[0]
})

// 在 script setup 部分添加以下函數
const getGroupNumbers = (sample_files) => {
  if (!sample_files) return []
  return [...new Set(sample_files.map(file => file.group))].sort((a, b) => a - b)
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