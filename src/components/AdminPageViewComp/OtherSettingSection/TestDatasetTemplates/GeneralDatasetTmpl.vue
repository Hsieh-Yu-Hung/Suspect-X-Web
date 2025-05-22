<template>

  <!-- ================ -->
  <!-- 彈出視窗區塊 -->
  <!-- ================ -->
  <div>
    <popup-form-tmpl ref="popupDialog" @confirm="(results) => handleConfirm(results, currentEditingDataset)" title="結果矩陣" />
    <popup-form-tmpl ref="viewDialog" title="檢視結果矩陣" :readonly="true" />
  </div>

  <div class="row">
    <!-- ================ -->
    <!-- 資料集列表區塊 -->
    <!-- ================ -->
    <div class="col dataset-list">
      <!-- 標題 -->
      <div class="header">
        <q-icon name="collections_bookmark" size="md" class="text-blue-grey-7" />
        <span class="text-h5 q-mb-md text-blue-grey-7 text-bold">現有集合</span>
      </div>

      <!-- 空狀態提示 -->
      <div class="empty-state" v-if="DatasetList.length === 0">
        <span class="text-subtitle2 text-blue-9"> -- 請新增一些測試資料集 -- </span>
      </div>

      <!-- 資料集列表內容 -->
      <q-list class="dataset-list-content" bordered separator v-else>
        <q-item v-for="dataset in DatasetList" :key="dataset.name">
          <q-item-section>
            <div class="dataset-item" :class="{ 'collapsed': !dataset.isSelected, 'expanded': dataset.isSelected }">

              <!-- 資料集標題與標籤 -->
              <div class="dataset-header">
                <div class="dataset-info">
                  <!-- 資料集名稱（可編輯/顯示模式） -->
                  <span v-if="!dataset.edit" class="dataset-name">{{ dataset.name }}</span>
                  <q-input
                    v-else
                    dense
                    :model-value="dataset.name"
                    @update:model-value="val => dataset.name = val"
                    class="dataset-name-input"
                    autofocus
                  />
                  <!-- 資料集標籤 -->
                  <div class="dataset-tags">
                    <q-chip color="indigo-3" dense class="text-subtitle2" :label="dataset.instrument" />
                    <q-chip color="blue-4" dense class="text-subtitle2" :label="dataset.reagent" />
                    <q-chip color="yellow-9" dense class="text-subtitle2" :label="dataset.group" clickable @click="toggleGroup(dataset)" />
                    <q-chip :color="dataset.qc === 'Passed' ? 'green-4' : 'red-4'" dense class="text-subtitle2" :label="dataset.qc" clickable @click="toggleQC(dataset)" />
                  </div>
                </div>
                <!-- 操作按鈕 -->
                <div class="dataset-actions">
                  <q-btn flat :color="dataset.edit ? 'green-9' : 'primary'" :icon="dataset.edit ? 'check' : 'edit'" dense class="text-subtitle2" @click.prevent="editDataset(dataset)" />
                  <q-btn flat color="red-9" icon="delete" dense class="text-subtitle2" @click.prevent="deleteDataset(dataset)" />
                  <q-btn flat color="cyan-9" icon="info" dense class="text-subtitle2" @click.prevent="displayDataset(dataset)" />
                </div>
              </div>

              <!-- 資料集設定區域 -->
              <div class="dataset-settings">
                <!-- 結果矩陣操作 -->
                <div class="matrix-actions">
                  <div class="matrix-buttons">
                    <span class="matrix-label">設定 Result & Assessment：</span>
                    <q-btn
                      color="primary"
                      icon="visibility"
                      dense
                      @click="viewDatasetMatrix(dataset)"
                      label="檢視結果"
                    />
                    <q-btn
                      color="primary"
                      icon="edit"
                      dense
                      @click="editDatasetMatrix(dataset)"
                      label="編輯結果"
                    />
                  </div>
                </div>
                <!-- 資料集特定內容 -->
                <slot name="dataset-content" :dataset="dataset"></slot>
              </div>
            </div>
          </q-item-section>
        </q-item>
      </q-list>
    </div>

    <!-- ================ -->
    <!-- 新增資料集區塊 -->
    <!-- ================ -->
    <div class="col add-dataset">
      <q-form @submit="onSubmit">
        <!-- 新增資料集表單 -->
        <div class="add-dataset-container">
          <!-- 標題 -->
          <div class="add-dataset-header">
            <q-icon name="category" size="md" class="text-blue-grey-7" />
            <span class="text-h5 q-mb-md text-blue-grey-7 text-bold">新增資料集</span>
          </div>

          <!-- 表單內容 -->
          <div class="add-dataset-content">
            <!-- 快速選擇按鈕組 -->
            <div class="button-group">
              <!-- 儀器選擇 -->
              <q-btn-dropdown class="instrument-btn" color="indigo-3" :label="selectedInstrument">
                <q-list>
                  <q-item v-for="instrument in getInstrumentOptions" :key="instrument" clickable v-close-popup @click="selectedInstrument = instrument">
                    <q-item-section>
                      {{ instrument.toUpperCase() }}
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-btn-dropdown>
              <!-- 試劑選擇 -->
              <q-btn-dropdown class="reagent-btn" color="blue-4" :label="selectedReagent">
                <q-list>
                  <q-item v-for="reagent in getReagentOptions" :key="reagent" clickable v-close-popup @click="selectedReagent = reagent">
                    <q-item-section>
                      {{ reagent.toUpperCase() }}
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-btn-dropdown>
              <!-- 群組選擇 -->
              <q-btn-dropdown class="group-btn" color="yellow-9" :label="selectedGroup.label">
                <q-list>
                  <q-item v-for="group in groupOptions" :key="group" clickable v-close-popup @click="selectedGroup = group">
                    <q-item-section>
                      {{ group.label.toUpperCase() }}
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-btn-dropdown>
              <!-- QC 狀態選擇 -->
              <q-btn-dropdown class="qc-btn" :color="selectedQC === 'Passed' ? 'green-4' : 'red-4'" :label="selectedQC">
                <q-list>
                  <q-item v-for="qc in qcOptions" :key="qc" clickable v-close-popup @click="selectedQC = qc">
                    <q-item-section>
                      {{ qc.toUpperCase() }}
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-btn-dropdown>
              <!-- 新增按鈕 -->
              <q-btn class="add-btn text-subtitle2" color="primary" icon="add_box" dense label="" type="submit" />
            </div>

            <!-- 結果矩陣設定 -->
            <div class="matrix-settings">
              <div class="matrix-header">
                <span class="matrix-title">設定 Result & Assessment：</span>
                <div class="matrix-actions">
                  <q-btn
                    color="primary"
                    icon="visibility"
                    dense
                    @click="viewMatrix"
                    label="檢視結果"
                  />
                  <q-btn
                    color="primary"
                    icon="edit"
                    dense
                    @click="openDialog"
                    label="編輯結果"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 資料集名稱與自訂內容 -->
        <div class="dataset-name-container">
          <!-- 資料集名稱輸入 -->
          <div class="dataset-name-input">
            <span class="text-subtitle2">資料集名稱:</span>
            <q-input
              v-model="datasetName"
              class="q-mb-md"
              style="width: 100%;"
              dense
              :rules="[val => !!val || '請輸入資料集名稱']"
              lazy-rules
            />
          </div>
          <!-- 資料集特定內容 -->
          <div class="dataset-content">
            <slot name="add-content"></slot>
          </div>
        </div>
      </q-form>
    </div>
  </div>
</template>

<script setup>
// ===============================
// 引入所需的模組和組件
// ===============================
import { ref, computed, onMounted, watch } from 'vue'
import { Storage } from '@/firebase/firebaseStorage'
import { dataset_list, Database } from '@/firebase/firebaseDatabase'
import { collection, getDocs, doc, deleteDoc, updateDoc } from 'firebase/firestore'
import { ref as storageRef, listAll, deleteObject } from 'firebase/storage'
import PopupFormTmpl from 'src/components/AdminPageViewComp/OtherSettingSection/RAForms/popupFormTmpl.vue'
import { useQuasar } from 'quasar'

// ===============================
// Props 定義
// ===============================
const props = defineProps({
  // 資料集類別
  dataset_class: {
    type: String,
    required: true
  },
  // 資料集列表
  datasetList: {
    type: Array,
    required: true
  }
})

// ===============================
// 響應式狀態
// ===============================
// 資料集列表計算屬性
const DatasetList = computed(() => {
  return props.datasetList ? props.datasetList : []
})

// 資料集名稱
const datasetName = ref('')

// 當前正在編輯的資料集
const currentEditingDataset = ref(null)

// 結果矩陣相關
const popupDialog = ref(null)
const viewDialog = ref(null)
const result_matrix = ref([])

// 選擇狀態
const selectedInstrument = ref('')
const selectedReagent = ref('')
const selectedGroup = ref({
  label: 'Positive',
  value: 'Positive'
})
const selectedQC = ref('Passed')

// ===============================
// 常量定義
// ===============================
// QC 選項
const qcOptions = ['Passed', 'Failed']

// 群組選項
const groupOptions = [
  { label: 'Positive', value: 'Positive' },
  { label: 'Negative', value: 'Negative' },
  { label: 'Invalid(S)', value: 'Invalid(S)' },
  { label: 'Invalid(QC)', value: 'Invalid(QC)' }
]

// ===============================
// Emits 定義
// ===============================
const emit = defineEmits(['submit', 'reset', 'updateDatasetList'])

// ===============================
// 計算屬性
// ===============================
// 獲取儀器選項
const getInstrumentOptions = computed(() => {
  switch (props.dataset_class) {
    case 'SMA_CE':
      return ['qsep100']
    case 'BETA-THAL':
      return ['qsep100']
    case 'MTHFR':
      return ['qs3', 'tower', 'z480']
    case 'NUDT15':
      return ['qs3', 'z480']
    case 'SMA':
      return ['qs3', 'tower', 'z480']
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

// 獲取試劑選項
const getReagentOptions = computed(() => {
  switch (props.dataset_class) {
    case 'SMA_CE':
      return ['SMA CE v1']
    case 'BETA-THAL':
      return ['B-Thal v1']
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
      else if (selectedInstrument.value === 'tower') {
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

// ===============================
// 工具函數
// ===============================
// 初始化 Quasar 通知
const $q = useQuasar()

// 顯示通知的輔助函數
const showNotification = (type, message) => {
  $q.notify({
    type,
    message,
    position: 'top',
    timeout: 2000
  })
}

// ===============================
// 資料集操作方法
// ===============================
// 顯示資料集詳情
const displayDataset = (dataset) => {
  dataset.isSelected = !dataset.isSelected
}

// 編輯資料集
const editDataset = async (dataset) => {
  try {
    if (dataset.edit) {
      dataset.edit = false
      // 更新資料庫中的資料
      const search_path = `${dataset_list.testing_data}`
      const collectionRef = collection(Database, search_path)
      const querySnapshot = await getDocs(collectionRef)

      for (const document of querySnapshot.docs) {
        const doc_data = document.data()
        if (doc_data.dataset_class === props.dataset_class && doc_data.name === dataset.originalName) {
          const docRef = doc(Database, search_path, document.id)
          await updateDoc(docRef, {
            name: dataset.name
          })
          dataset.originalName = dataset.name  // 更新成功後更新原始名稱
          showNotification('positive', '資料集名稱更新成功')
          break
        }
      }
    } else {
      dataset.originalName = dataset.name  // 開始編輯時保存原始名稱
      dataset.edit = true
    }
  } catch (error) {
    console.error('編輯資料集時發生錯誤：', error)
    showNotification('negative', '編輯資料集時發生錯誤')
  }
}

// 刪除資料集
const deleteDataset = async (dataset) => {
  try {
    // 刪除 storage 中的檔案
    const folderPath = `testing_data/${dataset.storagePath}`
    const folderRef = storageRef(Storage, folderPath)

    // 定義遞迴刪除函數
    const recursiveDelete = async (ref) => {
      const result = await listAll(ref)
      const fileDeletePromises = result.items.map(item => deleteObject(item))
      const folderDeletePromises = result.prefixes.map(prefix => recursiveDelete(prefix))
      await Promise.all([...fileDeletePromises, ...folderDeletePromises])
    }

    // 執行遞迴刪除
    await recursiveDelete(folderRef)

    // 取得 database 中所有分析
    const search_path = `${dataset_list.testing_data}`
    const collectionRef = collection(Database, search_path)
    const querySnapshot = await getDocs(collectionRef)

    for (const document of querySnapshot.docs) {
      const doc_data = document.data()
      if (doc_data.dataset_class === props.dataset_class && doc_data.name === dataset.name) {
        await deleteDoc(document.ref)
        break
      }
    }

    // 更新顯示
    emit('updateDatasetList')
    showNotification('positive', '資料集刪除成功')

  } catch (error) {
    console.error('刪除資料集時發生錯誤：', error)
    showNotification('negative', '刪除資料集時發生錯誤')
  }
}

// ===============================
// 表單處理方法
// ===============================
// 提交表單
const onSubmit = async () => {
  try {
    // 基本驗證
    if (!datasetName.value) {
      showNotification('negative', '請輸入資料集名稱')
      return
    }

    // 驗證 result_matrix
    if (!result_matrix.value || !Array.isArray(result_matrix.value)) {
      showNotification('negative', '格式錯誤')
      return
    }

    // 檢查每個 result_matrix 項目
    const isValidResultMatrix = result_matrix.value.every(item =>
      item.sample_id && item.assessment
    )

    if (!isValidResultMatrix) {
      showNotification('negative', '請確保每個結果資訊都已填寫完整')
      return
    }

    // 發出提交事件
    emit('submit', {
      result_matrix: result_matrix.value
    })

    // 更新顯示
    emit('updateDatasetList')
  } catch (error) {
    console.error('提交表單時發生錯誤：', error)
    showNotification('negative', '提交表單時發生錯誤')
  }
}

// ===============================
// 結果矩陣操作方法
// ===============================
// 開啟編輯對話框
const openDialog = () => {
  try {
    popupDialog.value.open(result_matrix.value)
  } catch (error) {
    console.error('開啟編輯視窗時發生錯誤：', error)
    showNotification('negative', '開啟編輯視窗時發生錯誤')
  }
}

// 檢視結果矩陣
const viewMatrix = () => {
  try {
    if (!result_matrix.value || result_matrix.value.length === 0) {
      showNotification('warning', '目前沒有結果資訊可供檢視')
      return
    }
    viewDialog.value.open(result_matrix.value)
  } catch (error) {
    console.error('開啟檢視視窗時發生錯誤：', error)
    showNotification('negative', '開啟檢視視窗時發生錯誤')
  }
}

// 檢視資料集矩陣
const viewDatasetMatrix = (dataset) => {
  try {
    if (!dataset.result_matrix || dataset.result_matrix.length === 0) {
      showNotification('warning', '目前沒有結果資訊可供檢視')
      return
    }
    viewDialog.value.open(dataset.result_matrix)
  } catch (error) {
    console.error('開啟檢視視窗時發生錯誤：', error)
    showNotification('negative', '開啟檢視視窗時發生錯誤')
  }
}

// 編輯資料集矩陣
const editDatasetMatrix = (dataset) => {
  try {
    // 設置當前正在編輯的資料集
    currentEditingDataset.value = dataset

    // 如果資料集沒有結果矩陣,初始化一個空的
    if (!dataset.result_matrix) {
      dataset.result_matrix = [{
        sample_id: '',
        result: '',
        assessment: ''
      }]
    }

    // 開啟編輯視窗
    popupDialog.value.open(dataset.result_matrix)
  } catch (error) {
    console.error('編輯結果資訊時發生錯誤：', error)
    showNotification('negative', '編輯結果資訊時發生錯誤')
    // 重置當前編輯的資料集
    currentEditingDataset.value = null
  }
}

// 處理確認事件
const handleConfirm = async (results, dataset) => {
  try {
    // 驗證結果
    if (!Array.isArray(results)) {
      showNotification('negative', '結果資訊格式錯誤')
      return
    }

    // 驗證每個結果項目
    const isValid = results.every(item =>
      item.sample_id && item.assessment
    )

    if (!isValid) {
      showNotification('negative', '請確保每個結果資訊都已填寫完整')
      return
    }

    // 如果是編輯現有資料集
    if (dataset) {
      try {
        // 更新資料集的結果矩陣
        dataset.result_matrix = results

        // 更新資料庫
        const search_path = `${dataset_list.testing_data}`
        const collectionRef = collection(Database, search_path)
        const querySnapshot = await getDocs(collectionRef)

        let updated = false
        for (const document of querySnapshot.docs) {
          const doc_data = document.data()
          if (doc_data.dataset_class === props.dataset_class && doc_data.name === dataset.name) {
            const docRef = doc(Database, search_path, document.id)
            await updateDoc(docRef, {
              result_matrix: results
            })
            showNotification('positive', '結果資訊更新成功')
            updated = true

            // 重置當前編輯的資料集
            currentEditingDataset.value = null
            break
          }
        }

        if (!updated) {
          showNotification('negative', '找不到要更新的資料集')
        }
      } catch (error) {
        showNotification('negative', '更新資料集時發生錯誤')
      }
    }
    // 如果是新增資料集
    else {
      try {
        result_matrix.value = results
        showNotification('positive', '結果資訊更新成功')
      } catch (error) {
        showNotification('negative', '新增結果資訊時發生錯誤')
      }
    }
  } catch (error) {
    showNotification('negative', '處理結果資訊時發生錯誤')
  }
}

// 切換 QC 狀態
const toggleQC = async (dataset) => {
  try {
    // 找到當前 QC 在選項中的索引
    const currentIndex = qcOptions.indexOf(dataset.qc)
    // 計算下一個選項的索引（循環）
    const nextIndex = (currentIndex + 1) % qcOptions.length
    // 更新 QC 值
    dataset.qc = qcOptions[nextIndex]

    // 更新資料庫
    const search_path = `${dataset_list.testing_data}`
    const collectionRef = collection(Database, search_path)
    const querySnapshot = await getDocs(collectionRef)

    for (const document of querySnapshot.docs) {
      const doc_data = document.data()
      if (doc_data.dataset_class === props.dataset_class && doc_data.name === dataset.name) {
        const docRef = doc(Database, search_path, document.id)
        await updateDoc(docRef, {
          qc: dataset.qc
        })
        showNotification('positive', 'QC 狀態更新成功')
        break
      }
    }
  } catch (error) {
    console.error('更新 QC 狀態時發生錯誤：', error)
    showNotification('negative', '更新 QC 狀態時發生錯誤')
  }
}

// 切換群組
const toggleGroup = async (dataset) => {
  try {
    // 找到當前群組在選項中的索引
    const currentIndex = groupOptions.findIndex(option => option.value === dataset.group)
    // 計算下一個選項的索引（循環）
    const nextIndex = (currentIndex + 1) % groupOptions.length
    // 更新群組值
    dataset.group = groupOptions[nextIndex].value

    // 更新資料庫
    const search_path = `${dataset_list.testing_data}`
    const collectionRef = collection(Database, search_path)
    const querySnapshot = await getDocs(collectionRef)

    for (const document of querySnapshot.docs) {
      const doc_data = document.data()
      if (doc_data.dataset_class === props.dataset_class && doc_data.name === dataset.name) {
        const docRef = doc(Database, search_path, document.id)
        await updateDoc(docRef, {
          group: dataset.group
        })
        showNotification('positive', '群組更新成功')
        break
      }
    }
  } catch (error) {
    console.error('更新群組時發生錯誤：', error)
    showNotification('negative', '更新群組時發生錯誤')
  }
}

// ===============================
// 生命週期鉤子
// ===============================
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

// 組件掛載時的初始化
onMounted(async () => {
  selectedInstrument.value = getInstrumentOptions.value[0]
  selectedReagent.value = getReagentOptions.value[0]
})

// ===============================
// 導出組件接口
// ===============================
defineExpose({
  datasetName,
  selectedInstrument,
  selectedReagent,
  selectedGroup,
  selectedQC,
  result_matrix,
  viewMatrix
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

.dataset-list {
  margin-right: 1em;
  border-radius: 10px;
  padding: 10px;
  border: 1px solid #e0e0e0;
}

.header {
  display: flex;
  flex-direction: row;
  gap: 0.5em;
}

.empty-state {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.dataset-list-content {
  overflow-x: auto;
}

.dataset-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.dataset-header {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 0.5em;
  width: 100%;
  justify-content: space-between;
}

.dataset-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5em;
  width: 100%;
}

.dataset-name {
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.dataset-name-input {
  width: 100%;
}

.dataset-actions {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 0.5em;
}

.dataset-settings {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-top: 0.5em;
  width: 100%;
  gap: 0.2em;
}

.matrix-actions {
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  width: 100%;
}

.matrix-buttons {
  display: flex;
  flex-direction: row;
  gap: 0.5em;
  align-items: center;
}

.matrix-label {
  white-space: nowrap;
  font-weight: bold;
  margin-block: 1.5em;
}

.add-dataset {
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  padding: 10px;
  background-color: rgba(221, 232, 243, 0.2);
}

.add-dataset-container {
  display: flex;
  flex-direction: column;
  gap: 0.5em;
  align-items: flex-start;
  justify-content: space-between;
}

.add-dataset-header {
  display: flex;
  flex-direction: row;
  gap: 0.5em;
}

.add-dataset-content {
  display: flex;
  flex-direction: column;
  gap: 1em;
  width: 100%;
  padding: 1em;
}

.button-group {
  width: 100%;
}

.button-group > * {
  margin-inline: 0.2em;
}

.dataset-name-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  margin-top: 1em;
}

.dataset-name-input {
  display: flex;
  flex-direction: row;
  gap: 0.5em;
  width: 100%;
}

.dataset-name-input span {
  white-space: nowrap;
  margin-top: 0.6em;
}

.dataset-content {
  display: flex;
  flex-direction: column;
  gap: 0.5em;
  width: 100%;
  align-items: center;
}

.matrix-settings {
  display: flex;
  flex-direction: column;
  gap: 0.5em;
  justify-content: flex-start;
  width: 100%;
  align-content: center;
}

.matrix-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.matrix-title {
  white-space: nowrap;
  font-weight: bold;
  margin-right: 0.5em;
  align-self: center;
}

.matrix-actions {
  display: flex;
  flex-direction: row;
  gap: 0.5em;
}
</style>
