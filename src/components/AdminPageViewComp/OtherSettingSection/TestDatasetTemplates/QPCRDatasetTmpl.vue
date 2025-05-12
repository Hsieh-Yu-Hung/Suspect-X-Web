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
              <div v-if="dataset.instrument !== 'z480'" style="display: flex; flex-direction: column; align-items: flex-start; margin-top: 0.5em;">
                <div style="display: flex; flex-direction: row; align-items: center; gap: 0.5em;">
                  <span class="text-subtitle2">Result File:</span>
                  <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset.file.split('/').pop()" />
                </div>
                <div style="display: flex; flex-direction: row; align-items: center; gap: 0.5em;">
                  <span class="text-subtitle2">Control Well:</span>
                  <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset.controlWell" />
                </div>
                <div style="display: flex; flex-direction: row; align-items: center; gap: 0.5em;">
                  <span class="text-subtitle2">NTC Well:</span>
                  <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset.NTCWell" />
                </div>
              </div>
              <div v-else style="display: flex; flex-direction: column; align-items: flex-start; margin-top: 0.5em;">
                <div style="display: flex; flex-direction: row; align-items: center; gap: 0.5em;">
                  <span class="text-subtitle2">VIC File:</span>
                  <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset?.VIC?.split('/').pop()" />
                </div>
                <div style="display: flex; flex-direction: row; align-items: center; gap: 0.5em;">
                  <span class="text-subtitle2">FAM File:</span>
                  <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset?.FAM?.split('/').pop()" />
                </div>
                <div v-if="props.dataset_class === 'SMA'" style="display: flex; flex-direction: row; align-items: center; gap: 0.5em;">
                  <span class="text-subtitle2">CY5 File:</span>
                  <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset?.CY5?.split('/').pop()" />
                </div>
                <div style="display: flex; flex-direction: row; align-items: center; gap: 0.5em;">
                  <span class="text-subtitle2">Control Well:</span>
                  <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset?.controlWell" />
                </div>
                <div style="display: flex; flex-direction: row; align-items: center; gap: 0.5em;">
                  <span class="text-subtitle2">NTC Well:</span>
                  <q-chip color="grey-2" dense class="text-subtitle2" :label="dataset?.NTCWell" />
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
          <div style="display: flex; flex-direction: row; gap: 0.5em; width: 100%;">
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
          <div style="display: flex; flex-direction: row; gap: 0.5em; width: 100%;">
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
        </div>
      </q-form>
    </div>
  </div>
</template>

<script setup>
// 導入模組
import { ref, onMounted, computed, watch } from 'vue'
import { uploadFileToStorage, Storage } from '@/firebase/firebaseStorage'
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
const TypeI_class = ['MTHFR', 'NUDT15']
const TypeII_class = ['SMA']

// 定義一個 Dataset 的資料結構
const Dataset = (NAME, FILE, CONTRL_WELL, NTC_WELL, INSTRUMENT, REAGENT, VIC, FAM, CY5, STORAGE_PATH) => {
  return {
    name: NAME,
    file: FILE,
    controlWell: CONTRL_WELL,
    NTCWell: NTC_WELL,
    instrument: INSTRUMENT,
    reagent: REAGENT,
    edit: false,
    originalName: null,
    isSelected: false,
    VIC: VIC,
    FAM: FAM,
    CY5: CY5,
    storagePath: STORAGE_PATH
  }
}

// 定義選項
const optionX = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
const optionY = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']

// 定義結果檔案
const resultFile = ref(null)
const controlWell = ref({
  X: null,
  Y: null
})
const NTCWell = ref({
  X: null,
  Y: null
})
const Z480_Files = ref({
  VIC: null,
  FAM: null,
  CY5: null
})

// 選取的儀器, 試劑
const selectedInstrument = ref(null)
const selectedReagent = ref(null)

// 資料集列表
const DatasetList = ref([])

/* Table Data */
const datasetName = ref('')

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

// 提交表單
const onSubmit = async () => {
  // 檢查所有必填欄位
  if (selectedInstrument.value === 'z480'){
    if (props.dataset_class === 'SMA'){
      if (!datasetName.value || !Z480_Files.value.VIC || !Z480_Files.value.FAM || !Z480_Files.value.CY5 || !controlWell.value.X || !controlWell.value.Y || !NTCWell.value.X || !NTCWell.value.Y) {
        console.log('請檢查所有必填欄位Z480')
        return
      }
    }
    else{
      if (!datasetName.value || !Z480_Files.value.VIC || !Z480_Files.value.FAM || !controlWell.value.X || !controlWell.value.Y || !NTCWell.value.X || !NTCWell.value.Y) {
        console.log('請檢查所有必填欄位Z480')
        return
      }
    }
  }
  else{
    if (!datasetName.value || !resultFile.value || !controlWell.value.X || !controlWell.value.Y || !NTCWell.value.X || !NTCWell.value.Y) {
      console.log('請檢查所有必填欄位Other')
      return
    }
  }

  // Storage Path, 隨機產生一組 uuid
  const storage_path = uuidv4()

  // Z480
  if (selectedInstrument.value === 'z480') {
    const VIC_storage_path = `${storage_path}/${Z480_Files.value.VIC.name}`
    const FAM_storage_path = `${storage_path}/${Z480_Files.value.FAM.name}`
    const CY5_storage_path = `${storage_path}/${Z480_Files.value.CY5?.name}`
    await uploadFileToStorage(Z480_Files.value.VIC, VIC_storage_path, 'test')
    await uploadFileToStorage(Z480_Files.value.FAM, FAM_storage_path, 'test')
    if (props.dataset_class === 'SMA'){
      await uploadFileToStorage(Z480_Files.value.CY5, CY5_storage_path, 'test')
    }
  }
  else{
    // 上傳結果檔案
    const result_file_storage_path = `${storage_path}/${resultFile.value.name}`
    await uploadFileToStorage(resultFile.value, result_file_storage_path, 'test')
  }

  // 將資料集設定存到 firestore
  const dataset_data = {
    dataset_class: props.dataset_class,
    dataset_name: datasetName.value,
    resultFile: selectedInstrument.value === 'z480' ? null : `testing_data/${storage_path}/${resultFile.value.name}`,
    VIC: selectedInstrument.value === 'z480' ? `testing_data/${storage_path}/${Z480_Files.value.VIC.name}` : null,
    FAM: selectedInstrument.value === 'z480' ? `testing_data/${storage_path}/${Z480_Files.value.FAM.name}` : null,
    CY5: selectedInstrument.value === 'z480' ? `testing_data/${storage_path}/${Z480_Files.value.CY5?.name}` : null,
    controlWell: `${controlWell.value.X}${controlWell.value.Y}`,
    NTCWell: `${NTCWell.value.X}${NTCWell.value.Y}`,
    instrument: selectedInstrument.value,
    reagent: selectedReagent.value,
    storagePath: storage_path
  }

  // 先檢查資料庫是否有 datasetName 和 dataset_class === props.dataset_class 的資料
  let dataset_uid = ''
  const search_path = `${dataset_list.testing_data}`;
  const collectionRef = collection(Database, search_path);
  const querySnapshot = await getDocs(collectionRef);
  querySnapshot.forEach(async (document) => {
    const doc_data = document.data();
    if (doc_data.dataset_name === datasetName.value && doc_data.dataset_class === props.dataset_class) {
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
  resultFile.value = null
  controlWell.value = {
    X: null,
    Y: null
  }
  NTCWell.value = {
    X: null,
    Y: null
  }
  Z480_Files.value = {
    VIC: null,
    FAM: null,
    CY5: null
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
      DatasetList.value.push(Dataset(doc_data.dataset_name, doc_data.resultFile, doc_data.controlWell, doc_data.NTCWell, doc_data.instrument, doc_data.reagent, doc_data.VIC, doc_data.FAM, doc_data.CY5, doc_data.storagePath))
    }
  })
}

// 取得儀器選項
const getInstrumentOptions = computed(() => {
  switch (props.dataset_class) {
    case 'MTHFR':
      return ['qs3', 'qtower', 'z480']
    case 'NUDT15':
      return ['qs3', 'z480']
    case 'SMA':
      return ['qs3', 'qtower', 'z480']
    default:
      return []
  }
})

// 取得試劑
const getReagentOptions = computed(() => {
  switch (props.dataset_class) {
    case 'MTHFR':
      if (selectedInstrument.value === 'z480') {
        return ['MTHFR_v3']
      }
      else {
        return ['MTHFR_v1', 'MTHFR_v2']
      }
    case 'NUDT15':
      if (selectedInstrument.value === 'z480') {
        return ['NUDT15_v2']
      }
      else {
        return ['NUDT15_v1']
      }
    case 'SMA':
      if (selectedInstrument.value === 'z480') {
        return ['SMA_v3']
      }
      else {
        return ['SMA_v1', 'SMA_v2']
      }
    default:
      return []
  }
})

// 掛載元件
onMounted(async () => {
  await updateDatasetList()

  // 設定預設儀器.試劑
  selectedInstrument.value = getInstrumentOptions.value[0]
  selectedReagent.value = getReagentOptions.value[0]
})

// 監控
watch(selectedInstrument, () => {
  switch (props.dataset_class) {
    case 'MTHFR':
      if (selectedInstrument.value === 'z480') {
        selectedReagent.value = 'MTHFR_v3'
      }
      else {
        selectedReagent.value = 'MTHFR_v1'
      }
      break
    case 'NUDT15':
      if (selectedInstrument.value === 'z480') {
        selectedReagent.value = 'NUDT15_v2'
      }
      else {
        selectedReagent.value = 'NUDT15_v1'
      }
      break
    case 'SMA':
      if (selectedInstrument.value === 'z480') {
        selectedReagent.value = 'SMA_v3'
      }
      else {
        selectedReagent.value = 'SMA_v1'
      }
      break
    default:
      break
  }
})

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