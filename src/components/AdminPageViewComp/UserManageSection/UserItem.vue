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
          <q-btn glossy icon="gpp_maybe" color="red" label="確定" @click="delete_user" />
          <q-btn glossy icon="close" color="grey-9" label="取消" @click="warning_dialog = false" />
        </div>
      </q-card-section>
    </q-card>
  </q-dialog>

  <!-- 使用者資料管理 -->
  <q-item class="item">

    <!-- 使用者 Email -->
    <q-item-section class="col" style="min-width: 250px;">
      <q-item-label v-if="props.user_info.id === masked_user_id">{{ display_user_info.email }}</q-item-label>
      <q-field dense v-else standout="bg-teal text-white" stack-label>
        <template v-slot:control>
          <div class="self-center full-width no-outline" tabindex="0">{{ display_user_info.email }}</div>
        </template>
      </q-field>
    </q-item-section>

    <!-- 所屬組織 -->
    <q-item-section class="col" style="min-width: 150px;">
      <q-item-label v-if="props.user_info.id === masked_user_id">{{ display_user_info.organization }}</q-item-label>
      <DropDownList v-else
      name="organization_dropdown"
      ref="organization_dropdown"
      @update_selected_value="update_dropList_value"
      :list_data="props.organization_list"
      :selected_value="props.user_info.organization" />
    </q-item-section>

    <!-- 可執行動作 (個人權限) -->
    <q-item-section class="col" style="min-width: 150px;">
      <q-item-label v-if="props.user_info.id === masked_user_id">{{ display_user_info.actions }}</q-item-label>
      <div class="row flex-start flex" style="flex-direction: row;" v-else>

        <div v-if="display_user_info.actions.length > 0" class="col flex flex-center">
          <!-- 顯示權限標籤 -->
          <q-chip v-for="(action, index) in display_user_info.actions"
            :icon="action.action_active ? 'check' : 'close'"
            :color="action.action_active ? 'orange-9' : 'blue-grey-7'"
            removable
            text-color="white"
            :key="index"
            :label="action.action_label"
            class="cursor-pointer glossy"
            clickable
            @click="toggle_action_active(props.user_info.id, index)"
            @remove="remove_action(props.user_info.id, index)"
          />
        </div>
        <div v-else class="col flex flex-center">
          <span class="text-subtitle2"> -- 沒有權限 --</span>
        </div>

        <!-- 下拉式選單選擇權限 -->
        <div class="col-1">
          <q-btn-dropdown dropdown-icon="add" color="primary" glossy dense label="">
            <q-list>
              <q-item @click="add_action(props.user_info.id, permission)" clickable v-close-popup v-for="(permission, index) in permission_list" :key="index">
                <q-item-section>
                  <q-item-label>{{ permission.permission_label }}</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-btn-dropdown>
        </div>

      </div>
    </q-item-section>

    <!-- 帳號開通 -->
    <q-item-section class="col-1" style="width: 100px;">
      <q-item-label v-if="props.user_info.id === masked_user_id">{{ display_user_info.account_active }}</q-item-label>
      <div v-else class="flex flex-center" style="gap: 10px;">
        <q-btn-toggle
          v-model="account_active_btn_option"
          push
          rounded
          glossy
          dense
          @click="update_account_active"
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
    <q-item-section class="col-1" style="width: 150px;">
      <q-item-label v-if="props.user_info.id === masked_user_id">{{ display_user_info.role }}</q-item-label>
      <DropDownList v-else
        name="account_role_dropdown"
        ref="account_role_dropdown"
        :list_data="account_role_option.map(option => option.label)"
        :selected_value="current_account_role.label"
        @update_selected_value="update_dropList_value"
      />
    </q-item-section>

    <!-- 申請日期 -->
    <q-item-section class="col-1" style="width: 200px;">
      <q-item-label v-if="props.user_info.id === masked_user_id">{{ display_user_info.created_at }}</q-item-label>
      <q-item-label v-else>{{ props.user_info.created_at }}</q-item-label>
    </q-item-section>

    <!-- 編輯按鈕 -->
    <q-item-section class="col-1" style="width: 50px;">
      <div>
        <q-btn dense glossy icon="delete" color="red-9" @click="pop_up_warning_dialog"
          :style="props.user_info.id === masked_user_id ? 'display: none;' : ''" />
      </div>
    </q-item-section>

  </q-item>

</template>

<script setup>

// 導入模組
import { ref, onMounted, computed } from 'vue';
import { getUsers_from_firestore, update_userData, ACTION, getPermissionDatabase } from '@/firebase/firebaseDatabase';

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
  account_role_option_list: {
    type: Array,
    required: true,
  },
});

// Emit
const emit = defineEmits(['update_user_info', 'delete_user']);

// constants
const masked_user_id = "header_id";

// refs
const display_user_info = computed(() => props.user_info);
const organization_dropdown = ref(null);
const account_role_dropdown = ref(null);

// 警告視窗
const warning_dialog = ref(false);

// 帳號開通按鈕
const account_active_btn_option = ref(display_user_info.value.account_active ? 'active' : 'inactive');

// 帳號身份選單
const account_role_option = ref(props.account_role_option_list);

// 當前選擇的帳號身份
const current_account_role = ref(account_role_option.value.find(option => option.role === props.user_info.role));

// 權限清單
const permission_list = ref([]);

/* functions */

// 更新帳號開通
function update_account_active() {
  const emit_data = {
    id: display_user_info.value.id,
    account_active: account_active_btn_option.value === 'active' ? true : false,
    check_account_active: true
  };
  emit('update_user_info', emit_data);
}

// 更新組織
function update_organization(data) {
  const emit_data = {
    id: display_user_info.value.id,
    organization: data.new_value,
  };
  emit('update_user_info', emit_data);
}

// 更新帳號身份
function update_account_role(data) {
  const emit_data = {
    id: display_user_info.value.id,
    role: account_role_option.value.find(option => option.label === data.new_value).role,
  };
  emit('update_user_info', emit_data);
}

// 警告視窗
function pop_up_warning_dialog() {
  warning_dialog.value = true;
}

// 確定刪除
function delete_user() {
  emit('delete_user', display_user_info.value.id);
  warning_dialog.value = false;
}

// 接收下拉選單更新
function update_dropList_value(toEmit) {
  if(toEmit.name === "organization_dropdown"){
    update_organization(toEmit);
  }
  if(toEmit.name === "account_role_dropdown"){
    update_account_role(toEmit);
  }
}

// 新增使用者權限動作
async function add_action(user_id, selected_permission) {
  const new_action = ACTION(selected_permission.permission_name, selected_permission.permission_label);
  const is_dup = display_user_info.value.actions.some(action => action.action_name === new_action.action_name);
  if(is_dup) {
    return;
  }
  const emit_data = {
    id: user_id,
    actions: [...display_user_info.value.actions, new_action],
  };
  emit('update_user_info', emit_data);
}

// 移除使用者權限動作
function remove_action(user_id, index) {
  const user_new_action_list = display_user_info.value.actions.filter((action, i) => i !== index);
  const emit_data = {
    id: user_id,
    actions: user_new_action_list,
  };
  emit('update_user_info', emit_data);
}

// 切換使用者權限動作啟用狀態
function toggle_action_active(user_id, index) {
  const emit_data = {
    id: user_id,
    actions: display_user_info.value.actions.map((action, i) => {
      if(i === index) {
        return { ...action, action_active: !action.action_active };
      }
      return action;
    }),
  };
  emit('update_user_info', emit_data);
}

// 掛載
onMounted(async () => {
  permission_list.value = await getPermissionDatabase();
});

</script>

<style scoped>
.item {
  text-align: center;
  gap: 10px;
  justify-content: flex-start;
  align-items: flex-start;
}
</style>
