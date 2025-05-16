<template>
  <!-- ===================== -->
  <!-- 彈出式對話框主容器 -->
  <!-- ===================== -->
  <q-dialog ref="dialogRef" @hide="onDialogHide">
    <q-card class="dialog-card">
      <!-- 對話框標題區塊 -->
      <q-card-section class="dialog-header">
        <div class="dialog-title">{{ title }}</div>
        <q-space />
        <q-btn class="close-btn" icon="close" flat round dense v-close-popup />
      </q-card-section>

      <!-- 對話框內容區塊 -->
      <q-card-section class="dialog-content">
        <!-- 結果列表 -->
        <q-list class="result-list">
          <q-item v-for="(item, index) in items" :key="index" class="result-item">
            <q-item-section>
              <div class="input-row">
                <!-- Sample ID 輸入框 -->
                <q-input
                  v-model="item.sample_id"
                  label="Sample ID"
                  dense
                  outlined
                  :readonly="readonly"
                  class="input-field"
                />
                <!-- Result 輸入框 -->
                <q-input
                  v-model="item.result"
                  label="Result"
                  dense
                  outlined
                  :readonly="readonly"
                  class="input-field"
                />
                <!-- Assessment 輸入框 -->
                <q-input
                  v-model="item.assessment"
                  label="Assessment"
                  dense
                  outlined
                  :readonly="readonly"
                  class="input-field"
                />
                <!-- 刪除按鈕 -->
                <div v-if="!readonly" class="delete-btn-container">
                  <q-btn
                    flat
                    round
                    dense
                    color="negative"
                    icon="delete"
                    @click="removeItem(index)"
                  />
                </div>
              </div>
            </q-item-section>
          </q-item>
        </q-list>

        <!-- 新增結果按鈕 -->
        <div v-if="!readonly" class="add-btn-container">
          <q-btn
            color="primary"
            icon="add"
            label="新增結果"
            dense
            @click="addItem"
          />
        </div>
      </q-card-section>

      <!-- 對話框底部按鈕區塊 -->
      <q-card-actions class="dialog-actions">
        <q-btn
          v-if="!readonly"
          color="primary"
          label="確認"
          @click="onOKClick"
        />
        <q-btn
          color="primary"
          flat
          label="關閉"
          v-close-popup
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
// =====================
// 導入相關模組
// =====================
import { ref } from 'vue'
import { useDialogPluginComponent } from 'quasar'

// =====================
// Props 定義
// =====================
const props = defineProps({
  title: {
    type: String,
    default: '結果矩陣'
  },
  readonly: {
    type: Boolean,
    default: false
  }
})

// =====================
// Emits 定義
// =====================
const emit = defineEmits([
  'confirm',
  'ok',
  'hide'
])

// =====================
// 對話框相關設定
// =====================
const { dialogRef, onDialogHide } = useDialogPluginComponent()

// =====================
// 響應式狀態
// =====================
const items = ref([]) // 儲存結果項目的陣列

// =====================
// 方法定義
// =====================
// 新增結果項目
const addItem = () => {
  items.value.push({
    sample_id: '',
    result: '',
    assessment: ''
  })
}

// 移除結果項目
const removeItem = (index) => {
  items.value.splice(index, 1)
}

// 確認按鈕點擊處理
const onOKClick = () => {
  emit('confirm', items.value) // 發送確認事件並傳遞資料
  dialogRef.value.hide() // 關閉對話框
}

// 開啟對話框
const open = (data = []) => {
  items.value = JSON.parse(JSON.stringify(data)) // 深拷貝傳入的資料
  dialogRef.value.show()
}

// =====================
// 導出方法
// =====================
defineExpose({
  open
})
</script>

<style scoped>
/* ===================== */
/* 對話框樣式 */
/* ===================== */
.dialog-card {
  min-width: 60em;
}

.dialog-header {
  display: flex;
  align-items: center;
  padding-bottom: 0;
}

.dialog-title {
  font-size: 1.25rem;
  font-weight: 500;
}

.dialog-content {
  padding-top: 0;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
}

/* ===================== */
/* 結果列表樣式 */
/* ===================== */
.result-list {
  margin-top: 1rem;
}

.result-item {
  padding: 1rem;
  margin-bottom: 0.5rem;
}

/* ===================== */
/* 輸入區域樣式 */
/* ===================== */
.input-row {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.input-field {
  flex: 1;
}

.delete-btn-container {
  display: flex;
  align-items: center;
}

/* ===================== */
/* 按鈕區域樣式 */
/* ===================== */
.add-btn-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 1rem;
}
</style>
