<template>
  <!-- 警告視窗 -->
  <q-dialog v-model="show_warning_dialog" persistent>
    <q-card style="width: 1000px;">
      <q-card-section>
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 15px; width: 100%;">
          <div class="flex flex-row items-center justify-center gap-2" style="width: 100%;">
            <q-icon name="warning" color="red" size="lg" />
            <span class="text-h6">發生錯誤</span>
          </div>
          <div style="width: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 15px;">
            <p class="text-body1" style="word-break: break-word; width: 100%;">{{ props.error_message }}</p>
            <q-btn label="關閉" color="primary" @click="show_warning_dialog = false" />
          </div>
        </div>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup>

// 導入模組
import { ref } from 'vue';

// Props
const props = defineProps({
  error_message: {
    type: String,
    default: ""
  }
})

// 控制警告視窗
const show_warning_dialog = ref(false);

// 開啟警告視窗
function open_warning_dialog() {
  show_warning_dialog.value = true;
}

// Expose
defineExpose({
  open_warning_dialog
})

</script>
