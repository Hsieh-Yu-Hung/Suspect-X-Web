<template>

  <!-- 警告視窗 -->
  <q-dialog v-model="warning_dialog" persistent>
    <q-card>
      <q-card-section>
        <div class="flex flex-center" style="gap: 10px; margin-block: 20px">
          <q-icon name="warning" color="red" size="lg" />
          <span class="text-h6 text-deep-orange-8">Warning</span>
        </div>
        <div class="flex flex-center" style="margin-block: 20px">
          <span class="text-subtitle1">此動作會刪除資料庫中的紀錄且無法復原！</span>
        </div>
        <div class="flex flex-center" style="gap: 20px; margin-block: 20px">
          <q-btn glossy icon="gpp_maybe" color="red" label="確定" @click="delete_software" />
          <q-btn glossy icon="close" color="grey-9" label="取消" @click="warning_dialog = false" />
        </div>
      </q-card-section>
    </q-card>
  </q-dialog>

  <!-- 軟體版本設定 -->
  <q-item class="item">

    <!-- icon -->
    <q-item-section class="col-1" avatar>
      <q-icon color="indigo-6" name="api" :style="software_name === masked_software_name ? { display: 'none' } : { display: 'block' }" />
    </q-item-section>

    <!-- 軟體名稱 -->
    <q-item-section class="col">
      <q-item-label v-if="software_name === masked_software_name">{{ software_name }}</q-item-label>
      <q-input color="lime-2" :readonly="disable_edit" dense v-else v-model="software_name" />
    </q-item-section>

    <!-- 軟體版本號 -->
    <q-item-section class="col">
      <q-item-label v-if="software_name === masked_software_name">{{ software_version }}</q-item-label>
      <q-input color="lime-2" :readonly="disable_edit" dense v-else v-model="software_version" />
    </q-item-section>

    <!-- 軟體備注 -->
    <q-item-section class="col-4">
      <q-item-label v-if="software_name === masked_software_name">{{ software_note }}</q-item-label>
      <q-input color="lime-2" :readonly="disable_edit" filled borderless dense v-else v-model="software_note" />
    </q-item-section>

    <!-- 編輯按鈕 -->
    <q-item-section class="col">
      <div :style="software_name === masked_software_name ? { display: 'none' } : { display: 'block' }">
        <q-btn dense glossy :icon="disable_edit ? 'edit' : 'check'" :color="disable_edit ? 'primary' : 'green'" style="margin-inline: 5px" @click="edit_software" />
        <q-btn dense glossy icon="delete" color="red-9" @click="pop_up_warning_dialog" />
      </div>
    </q-item-section>

  </q-item>

</template>

<script setup>

// 導入模組
import { ref } from 'vue';

// 導入元件
import { SOFTWARE_DATA } from '@/firebase';

// 接收 props
const props = defineProps({
  software_info: {
    type: Object,
    required: true,
  },
});

// constants
const masked_software_name = "軟體名稱";

// refs
const software_name = ref(props.software_info.software_name);
const software_version = ref(props.software_info.software_version);
const software_note = ref(props.software_info.software_note);
const list_id = props.software_info.list_id;

// 警告視窗
const warning_dialog = ref(false);

// 是否可編輯
const disable_edit = ref(!props.software_info.editable);

// 發送事件
const emit = defineEmits(['delete_software', 'update_firestore_software']);

// 修改軟體名稱
function edit_software() {
  // 確認修改(從 disable_edit = false 改成 true 時)
  if (disable_edit.value === false) {
    // 更新軟體資料
    const new_software = SOFTWARE_DATA(
      software_name.value,
      software_version.value,
      software_note.value,
      list_id,
      false);

    // 更新 firestore
    emit('update_firestore_software', new_software);
  }
  disable_edit.value = !disable_edit.value;
}

// 跳出警告視窗
function pop_up_warning_dialog() {
  warning_dialog.value = true;
}

// 刪除軟體
function delete_software() {
  warning_dialog.value = false;
  emit('delete_software', list_id);
}

</script>

<style scoped>
.item {
  text-align: center;
  gap: 10px;
  justify-content: center;
}
</style>
