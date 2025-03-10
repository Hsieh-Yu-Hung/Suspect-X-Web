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
          <q-btn glossy icon="gpp_maybe" color="red" label="確定" @click="delete_organization" />
          <q-btn glossy icon="close" color="grey-9" label="取消" @click="warning_dialog = false" />
        </div>
      </q-card-section>
    </q-card>
  </q-dialog>

  <!-- 組織設定 -->
  <q-item class="item">

    <!-- icon -->
    <q-item-section avatar class="col-1" style="width: 50px;">
      <q-icon name="home_work" color="brown-4" :style="organization_name === masked_organization_name ? { display: 'none' } : { display: 'block' }" />
    </q-item-section>

    <!-- 組織名稱 -->
    <q-item-section class="col">
      <q-item-label v-if="organization_name === masked_organization_name">{{ organization_name }}</q-item-label>
      <q-input style="min-width: 100px" color="lime-2" borderless :readonly="disable_edit" dense filled v-else v-model="organization_name" />
    </q-item-section>

    <!-- 軟體版本 -->
    <q-item-section class="col">
      <q-item-label v-if="organization_name === masked_organization_name">{{ software_selection }}</q-item-label>
      <DropDownList
        name="software_dropdown"
        style="min-width: 120px"
        v-else
        ref="software_dropdown_list"
        :disableEdit="disable_edit"
        :list_data="props.software_version_list"
        :selected_value="software_selection" />
    </q-item-section>

    <!-- 成員數量 -->
    <q-item-section class="col-1" style="width: 100px;">
      <q-item-label>{{ member_count }}</q-item-label>
    </q-item-section>

    <!-- 加入日期 -->
    <q-item-section class="col-1" style="width: 100px;">
      <q-item-label>{{ join_date }}</q-item-label>
    </q-item-section>

    <!-- 編輯按鈕 -->
    <q-item-section class="col-1" style="width: 100px;">
      <div class="flex flex-center" :style="organization_name === masked_organization_name ? { display: 'none' } : { display: 'block' }">
        <q-btn dense glossy :icon="disable_edit ? 'edit' : 'check'" :color="disable_edit ? 'primary' : 'green'" style="margin-inline: 5px" @click="edit_organization" />
        <q-btn dense glossy icon="delete" color="red-9" @click="pop_up_warning_dialog" />
      </div>
    </q-item-section>

  </q-item>
</template>

<script setup>

// 導入模組
import { ref } from 'vue';

// 導入元件
import DropDownList from '@/components/DropDownList.vue';
import { ORGAN_DATA } from '@/firebase';

// 接收 props
const props = defineProps({
  organization_info: {
    type: Object,
    required: true,
  },
  software_version_list: {
    type: Array,
    required: false,
  },
});

// constants
const masked_organization_name = "組織名稱";

// refs
const organization_name = ref(props.organization_info.organization_name);
const software_selection = ref(props.organization_info.software_selection);
const member_count = ref(props.organization_info.member_count);
const join_date = ref(props.organization_info.join_date);
const organization_id = props.organization_info.organization_id;

// 軟體版本下拉選單
const software_dropdown_list = ref(null);

// 是否可編輯組織名稱
const disable_edit = ref(!props.organization_info.editable);

// 警告視窗
const warning_dialog = ref(false);

// 發送事件
const emit = defineEmits(['delete_organization', 'update_firestore_organization']);

// 修改組織名稱
function edit_organization() {
  // 確認修改(從 disable_edit = false 改成 true 時)
  if (disable_edit.value === false) {
    // 更新組織資料
    const new_organization = ORGAN_DATA(
      organization_name.value,
      software_dropdown_list.value.display_selected_value,
      member_count.value,
      join_date.value,
      organization_id,
      false);

    // 更新 firestore
    emit('update_firestore_organization', new_organization);
  }
  disable_edit.value = !disable_edit.value;
}

// 開啟警告視窗
function pop_up_warning_dialog() {
  warning_dialog.value = true;
}

// 刪除組織
function delete_organization() {
  emit('delete_organization', organization_id);
  warning_dialog.value = false;
}

</script>

<style scoped>
.item {
  text-align: center;
  gap: 10px;
  justify-content: center;
}
</style>
