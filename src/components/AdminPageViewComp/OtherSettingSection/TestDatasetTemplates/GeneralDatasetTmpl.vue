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
                <div style="display: flex; flex-direction: column; align-items: center; gap: 0.5em; width: 100%;">
                  <span v-if="!dataset.edit" class="text-subtitle1 text-bold text-blue-grey-8" style="white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">{{ dataset.name }}</span>
                  <q-input
                    v-else
                    dense
                    :model-value="dataset.name"
                    @update:model-value="val => dataset.name = val"
                    class="text-subtitle1 text-bold text-blue-grey-8"
                    autofocus
                  />
                  <div>
                    <q-chip color="indigo-3" dense class="text-subtitle2" :label="dataset.instrument" />
                    <q-chip color="blue-4" dense class="text-subtitle2" :label="dataset.reagent" />
                    <q-chip color="yellow-9" dense class="text-subtitle2" :label="dataset.group" />
                    <q-chip :color="dataset.qc === 'Passed' ? 'green-4' : 'red-4'" dense class="text-subtitle2" :label="dataset.qc" />
                  </div>
                </div>
                <div style="display: flex; flex-direction: row; align-items: center; gap: 0.5em;">
                  <q-btn flat :color="dataset.edit ? 'green-9' : 'primary'" :icon="dataset.edit ? 'check' : 'edit'" dense class="text-subtitle2" @click.prevent="editDataset(dataset)" />
                  <q-btn flat color="red-9" icon="delete" dense class="text-subtitle2" @click.prevent="deleteDataset(dataset)" />
                  <q-btn flat color="cyan-9" icon="info" dense class="text-subtitle2" @click.prevent="displayDataset(dataset)" />
                </div>
              </div>

              <!-- 根據不同 dataset_class 顯示不同資料集 -->
              <div style="display: flex; flex-direction: column; align-items: flex-start; margin-top: 0.5em; width: 100%; gap: 0.2em;">
                <span class="text-subtitle2" style="white-space: nowrap;">Result: {{ dataset.result }}</span>
                <span class="text-subtitle2" style="white-space: nowrap; margin-block: 0.5em;">Assessments: {{ dataset.assessments }}</span>
                <slot name="dataset-content" :dataset="dataset"></slot>
              </div>
            </div>
          </q-item-section>
        </q-item>
      </q-list>

    </div>

    <!-- 新增資料集 -->
    <div class="col q-mb-md" style="border: 1px solid #e0e0e0; border-radius: 10px; padding: 10px; background-color: rgba(221, 232, 243, 0.2);">
      <q-form @submit="onSubmit">
        <div style="display: flex; flex-direction: column; gap: 0.5em; align-items: flex-start; justify-content: space-between;">
          <div class="row" style="display: flex; flex-direction: row; gap: 0.5em;">
            <q-icon name="category" size="md" class="text-blue-grey-7" />
            <span class="text-h5 q-mb-md text-blue-grey-7 text-bold">新增資料集</span>
          </div>
          <div class="row q-pa-md" style="display: flex; flex-direction: column; gap: 1em; width: 100%;">
            <div style="display: flex; flex-direction: row; gap: 0.5em; width: 100%;">
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
              <q-btn-dropdown color="yellow-9" :label="selectedGroup.label">
                <q-list>
                  <q-item v-for="group in groupOptions" :key="group" clickable v-close-popup @click="selectedGroup = group">
                    <q-item-section>
                      {{ group.label.toUpperCase() }}
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-btn-dropdown>
              <q-btn-dropdown :color="selectedQC === 'Passed' ? 'green-4' : 'red-4'" :label="selectedQC">
                <q-list>
                  <q-item v-for="qc in qcOptions" :key="qc" clickable v-close-popup @click="selectedQC = qc">
                    <q-item-section>
                      {{ qc.toUpperCase() }}
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-btn-dropdown>
              <q-btn color="cyan-8" icon="add_box" dense class="text-subtitle2" label="" type="submit" />
            </div>
            <div style="display: flex; flex-direction: row; gap: 0.5em; justify-content: flex-end; width: 100%;">
              <span class="text-subtitle2" style="white-space: nowrap; margin-top: 0.6em; margin-right: 0.5em;">Result:</span>
              <q-input style="width: 100%;" v-model="resultText" dense class="text-subtitle2" :rules="[val => !!val || 'Please Enter Result String']" lazy-rules />
              <span class="text-subtitle2" style="white-space: nowrap; margin-top: 0.6em; margin-right: 0.5em;">Assessments:</span>
              <q-input style="width: 100%;" v-model="assessmentsText" dense class="text-subtitle2" :rules="[val => !!val || 'Please Enter Assessments String']" lazy-rules />
            </div>
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
          <!-- 根據不同 dataset_class 顯示不同資料集 -->
          <div style="display: flex; flex-direction: column; gap: 0.5em; width: 100%; align-items: center;">
            <slot name="add-content"></slot>
          </div>
        </div>
      </q-form>
    </div>
  </div>
</template>

<script setup>
// 導入模組
import { ref, computed, onMounted, watch } from 'vue'
import { Storage } from '@/firebase/firebaseStorage'
import { dataset_list, Database } from '@/firebase/firebaseDatabase'
import { collection, getDocs, doc, deleteDoc, updateDoc } from 'firebase/firestore'
import { ref as storageRef, listAll, deleteObject } from 'firebase/storage'

// Props
const props = defineProps({
  dataset_class: {
    type: String,
    required: true
  },
  datasetList: {
    type: Array,
    required: true
  }
})

// 資料集列表
const DatasetList = computed(() => {
  return props.datasetList ? props.datasetList : []
})
const datasetName = ref('')

// Emits
const emit = defineEmits(['submit', 'reset', 'updateDatasetList'])

const selectedInstrument = ref('')
const selectedReagent = ref('')

const getInstrumentOptions = computed(() => {
  switch (props.dataset_class) {
    case 'SMA_CE':
      return ['qsep100']
    case 'BETA-THAL':
      return ['qsep100']
    case 'MTHFR':
      return ['qs3', 'qtower', 'z480']
    case 'NUDT15':
      return ['qs3', 'z480']
    case 'SMA':
      return ['qs3', 'qtower', 'z480']
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

const getReagentOptions = computed(() => {
  switch (props.dataset_class) {
    case 'SMA_CE':
      return ['SMA CE v1']
    case 'BETA-THAL':
      return ['Beta-Thal v1']
    case 'MTHFR':
      if (selectedInstrument.value === 'z480') {
        return ['MTHFR_v3']
      } else {
        return ['MTHFR_v1', 'MTHFR_v2']
      }
    case 'NUDT15':
      if (selectedInstrument.value === 'z480') {
        return ['NUDT15_v2']
      } else {
        return ['NUDT15_v1']
      }
    case 'SMA':
      if (selectedInstrument.value === 'z480') {
        return ['SMA_v3']
      }
      else if (selectedInstrument.value === 'qtower') {
        return ['SMA_v1']
      }
      else {
        return ['SMA_v1', 'SMA_v2']
      }
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

const selectedGroup = ref({
  label: 'Positive',
  value: 'Positive'
})
const groupOptions = [
  {
    label: 'Positive',
    value: 'Positive'
  },
  {
    label: 'Negative',
    value: 'Negative'
  },
  {
    label: 'Invalid(S)',
    value: 'Invalid(S)'
  },
  {
    label: 'Invalid(QC)',
    value: 'Invalid(QC)'
  }
]

const selectedQC = ref('Passed');
const qcOptions = ['Passed', 'Failed'];

// 資料集預期結果
const resultText = ref('')
const assessmentsText = ref('')

// 顯示資料集
const displayDataset = (dataset) => {
  dataset.isSelected = !dataset.isSelected
}

// 編輯資料集
const editDataset = async (dataset) => {
  if (dataset.edit) {
    dataset.edit = false
    // 更新資料庫中 dataset_class = "SMA_CE" && name = dataset.name 的資料
    const search_path = `${dataset_list.testing_data}`;
    const collectionRef = collection(Database, search_path);
    const querySnapshot = await getDocs(collectionRef);

    querySnapshot.forEach(async (document) => {
      const doc_data = document.data();
      if (doc_data.dataset_class === props.dataset_class && doc_data.name === dataset.originalName) {
        const docRef = doc(Database, search_path, document.id);
        await updateDoc(docRef, {
          name: dataset.name
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
      if (doc_data.dataset_class === props.dataset_class && doc_data.name === dataset.name) {
        await deleteDoc(document.ref);
      }
    })

    // 更新顯示
    emit('updateDatasetList')

  } catch (error) {
    console.error('刪除資料集時發生錯誤：', error);
  }
}

// 修改提交表單函數
const onSubmit = async () => {
  emit('submit')
  emit('updateDatasetList')
}

// Expose
defineExpose({
  datasetName,
  selectedInstrument,
  selectedReagent,
  selectedGroup,
  selectedQC,
  resultText,
  assessmentsText
})

// 監控儀器變更，自動更新試劑選項
watch(selectedInstrument, () => {
  switch (props.dataset_class) {
    case 'MTHFR':
      selectedReagent.value = selectedInstrument.value === 'z480' ? 'MTHFR_v3' : 'MTHFR_v1'
      break
    case 'NUDT15':
      selectedReagent.value = selectedInstrument.value === 'z480' ? 'NUDT15_v2' : 'NUDT15_v1'
      break
    case 'SMA':
      selectedReagent.value = selectedInstrument.value === 'z480' ? 'SMA_v3' : 'SMA_v1'
      break
  }
})

// 掛載
onMounted(async () => {
  selectedInstrument.value = getInstrumentOptions.value[0]
  selectedReagent.value = getReagentOptions.value[0]
})

</script>

<style scoped>
.collapsed {
  height: 4.5em;
  overflow: hidden;
}
.expanded {
  height: auto;
  overflow: auto;
}
</style>