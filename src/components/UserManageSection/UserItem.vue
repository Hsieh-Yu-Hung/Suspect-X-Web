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
          <q-btn glossy icon="gpp_maybe" color="red" label="確定" @click="warning_dialog = false" />
          <q-btn glossy icon="close" color="grey-9" label="取消" @click="warning_dialog = false" />
        </div>
      </q-card-section>
    </q-card>
  </q-dialog>

  <!-- 使用者資料管理 -->
  <q-item class="item">

    <!-- 使用者 Email -->
    <q-item-section class="col-3">
      <q-item-label v-if="props.user_info.id === masked_user_id">{{ display_user_info.email }}</q-item-label>
      <q-field dense v-else standout="bg-teal text-white" stack-label>
        <template v-slot:control>
          <div class="self-center full-width no-outline" tabindex="0">{{ display_user_info.email }}</div>
        </template>
      </q-field>
    </q-item-section>

    <!-- 所屬組織 -->
    <q-item-section class="col-2">
      <q-item-label v-if="props.user_info.id === masked_user_id">{{ display_user_info.organization }}</q-item-label>
      <DropDownList v-else :list_data="props.organization_list" />
    </q-item-section>

    <!-- 帳號開通 -->
    <q-item-section class="col">
      <q-item-label v-if="props.user_info.id === masked_user_id">{{ display_user_info.account_active }}</q-item-label>
      <div v-else class="flex flex-center" style="gap: 10px;">
        <q-btn-toggle
          v-model="account_active_btn_option"
          push
          rounded
          glossy
          dense
          :toggle-color="account_active_btn_option === 'active' ? 'green' : 'red-7'"
          color="grey-9"
          :options="[
            {value: 'active', slot: 'active'},
            {value: 'inactive', slot: 'inactive'}
          ]"
        >
          <template v-slot:active>
            <div class="row items-center no-wrap">
              <q-icon right name="verified_user" />
            </div>
          </template>

          <template v-slot:inactive>
            <div class="row items-center no-wrap">
              <q-icon right name="block" />
            </div>
          </template>

        </q-btn-toggle>
      </div>
    </q-item-section>

    <!-- 帳號身份 -->
    <q-item-section class="col-2">
      <q-item-label v-if="props.user_info.id === masked_user_id">{{ display_user_info.role }}</q-item-label>
      <DropDownList v-else
        :list_data="account_role_option.map(option => option.label)"
        :selected_value="current_account_role.label"
      />
    </q-item-section>

    <!-- 申請日期 -->
    <q-item-section class="col">
      <q-item-label v-if="props.user_info.id === masked_user_id">{{ display_user_info.created_at }}</q-item-label>
      <q-item-label v-else>{{ props.user_info.created_at }}</q-item-label>
    </q-item-section>

    <!-- 編輯按鈕 -->
    <q-item-section class="col-1">
      <div>
        <q-btn dense glossy icon="delete" color="red-9" @click="pop_up_warning_dialog"
          :style="props.user_info.id === masked_user_id ? 'display: none;' : ''" />
      </div>
    </q-item-section>

  </q-item>

</template>

<script setup>

// 導入模組
import { ref } from 'vue';

// 導入元件
import DropDownList from '@/components/DropDownList.vue';

// props
const props = defineProps({
  user_info: {
    type: Object,
    required: true,
  },
  organization_list: {
    type: Array,
    required: true,
  },
});

// constants
const masked_user_id = "header_id";

// refs
const display_user_info = ref(props.user_info);

// 警告視窗
const warning_dialog = ref(false);

// 帳號開通按鈕
const account_active_btn_option = ref('inactive');

// 帳號身份選單
const account_role_option = ref([
  {role: 'user', label: '使用者'},
  {role: 'admin', label: '管理員'},
  {role: 'supervisor', label: '單位主管'},
]);

// 當前選擇的帳號身份
const current_account_role = ref(account_role_option.value.find(option => option.role === props.user_info.role));

/* functions */

// 刪除使用者資料
function pop_up_warning_dialog() {
  warning_dialog.value = true;
}

</script>

<style scoped>
.item {
  text-align: center;
  gap: 10px;
  justify-content: center;
}
</style>
