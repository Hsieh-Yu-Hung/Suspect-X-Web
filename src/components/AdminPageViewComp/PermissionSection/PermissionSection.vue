<template>
  <q-card class="card">

    <!-- 身份管理區域 -->
    <q-card-section style="display: flex; flex-direction: column; gap: 10px;">

      <!-- 標題 -->
      <div class="section">
        <span class="title">身份管理</span>
        <q-btn style="padding: 0.4em;" dense icon="add" label="新增角色" color="green-4" @click="addRole" />
      </div>

      <!-- 身份管理表格 -->
      <div v-if="rows.length > 0" class="q-pa-md">
        <q-table
          :rows="role_rows"
          :columns="role_columns"
          row-key="id"
          class="text-center"
          :rows-per-page-options="[1000]"
        >

          <!-- 角色名稱 -->
          <template v-slot:body-cell-role_name="props">
            <q-td style="width: 15%;">
              <q-input
                v-model="props.row.role_name"
                dense
                filled
                label="輸入角色名稱"
                color="green-8"
                :disable="!props.row.editable"
              />
            </q-td>
          </template>

          <!-- 角色標籤 -->
          <template v-slot:body-cell-role_label="props">
            <q-td style="width: 15%;">
              <q-input
                v-model="props.row.role_label"
                dense
                filled
                label="輸入角色標籤"
                color="green-8"
                :disable="!props.row.editable"
              />
            </q-td>
          </template>

          <!-- 角色權限 -->
          <template v-slot:body-cell-role_permission="props">
            <q-td style="width: 20%;">

              <div class="row flex-start flex" style="flex-direction: row;">
                <div v-if="props.row.role_permission.length > 0" class="col flex flex-center">
                  <!-- 顯示權限標籤 -->
                  <q-chip v-for="(action, index) in props.row.role_permission"
                    icon="book"
                    color="indigo-9"
                    removable
                    text-color="white"
                    :key="index"
                    :label="action.action_label"
                    class="glossy"
                    @remove="remove_action(props.row.id, index)"
                  />
                </div>
                <div v-else class="col flex flex-center">
                  <span class="text-subtitle2"> -- 沒有權限 --</span>
                </div>

                <!-- 下拉式選單選擇權限 -->
                <div class="col-1">
                  <q-btn-dropdown :disable="props.row.editable" dropdown-icon="add" :color="!props.row.editable ? 'primary' : 'grey-4'" glossy dense label="">
                    <q-list>
                      <q-item @click="add_action(props.row.id, permission, index)" clickable v-close-popup v-for="(permission, index) in permission_list" :key="index">
                        <q-item-section>
                          <q-item-label>{{ permission.permission_label }}</q-item-label>
                        </q-item-section>
                      </q-item>
                    </q-list>
                  </q-btn-dropdown>
                </div>

              </div>
            </q-td>
          </template>

          <!-- 角色描述 -->
          <template v-slot:body-cell-role_description="props">
            <q-td style="width: 40%;">
              <q-input
                v-model="props.row.role_description"
                dense
                filled
                label="輸入角色描述"
                color="green-8"
                :disable="!props.row.editable"
              />
            </q-td>
          </template>

          <!-- 功能按鈕 -->
          <template v-slot:body-cell-role_function_btns="props">
            <q-td>
              <div style="display: flex; justify-content: center; align-items: center; gap: 10px;">
                <q-btn
                  dense
                  round
                  :color="props.row.editable ? 'green-4' : 'primary'"
                  :icon="props.row.editable ? 'check' : 'edit'"
                  @click="editRole(props.row)" />
                <q-btn
                  dense
                  round
                  icon="delete"
                  color="red"
                  @click="deleteRole(props.row)" />
              </div>
            </q-td>
          </template>

          <!-- 可編輯 -->
          <template v-slot:body-cell-role_editable="props">
            <q-td>
              <div>{{ props.row.editable ? '' : '' }}</div>
            </q-td>
          </template>

        </q-table>
      </div>

    </q-card-section>

    <!-- 權限動作區域 -->
    <q-card-section style="display: flex; flex-direction: column; gap: 10px;">

      <!-- 標題 -->
      <div class="section">
        <span class="title">權限管理</span>
        <q-btn style="padding: 0.4em;" dense icon="add" label="新增權限" color="green-4" @click="addPermission" />
      </div>

      <!-- 權限管理表格 -->
      <div v-if="rows.length > 0" class="q-pa-md">
        <q-table
          :rows="rows"
          :columns="columns"
          row-key="id"
          class="text-center"
          :rows-per-page-options="[1000]"
        >

          <!-- 權限名稱 -->
          <template v-slot:body-cell-action_name="props">
            <q-td style="width: 20%;">
              <q-input
                v-model="props.row.permission_name"
                dense
                filled
                label="輸入權限名稱"
                color="green-8"
                :disable="!props.row.editable"
              />
            </q-td>
          </template>

          <!-- 權限標示 -->
          <template v-slot:body-cell-action_label="props">
            <q-td style="width: 20%;">
              <q-input
                v-model="props.row.permission_label"
                dense
                filled
                label="輸入權限標示"
                color="green-8"
                :disable="!props.row.editable"
              />
            </q-td>
          </template>

          <!-- 權限描述 -->
          <template v-slot:body-cell-action_description="props">
            <q-td style="width: 60%;">
              <q-input
                v-model="props.row.description"
                filled
                clearable
                autogrow
                dense
                color="green-8"
                label="輸入權限描述"
                :disable="!props.row.editable"
              />
            </q-td>
          </template>

          <!-- 功能按鈕 -->
          <template v-slot:body-cell-function_btns="props">
            <q-td>
              <div style="display: flex; justify-content: center; align-items: center; gap: 10px;">
                <q-btn
                  dense
                  round
                  :color="props.row.editable ? 'green-4' : 'primary'"
                  :icon="props.row.editable ? 'check' : 'edit'"
                  @click="editPermission(props.row)" />
                <q-btn
                  dense
                  round
                  icon="delete"
                  color="red"
                  @click="deletePermission(props.row)" />
              </div>
            </q-td>
          </template>

          <!-- 可編輯 -->
          <template v-slot:body-cell-editable="props">
            <q-td>
              <div>{{ props.row.editable ? '' : '' }}</div>
            </q-td>
          </template>

        </q-table>
      </div>
      <div v-else class="q-pa-md flex flex-center">
        <span class="subtitle"> -- 尚未設定任何權限 -- </span>
      </div>

    </q-card-section>

  </q-card>
</template>

<script setup>
// 導入模組
import { ref, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { PERMISSION, getPermissionDatabase, deletePermissionDatabase,
         addPermissionDatabase, ROLE, getRoleDatabase, deleteRoleDatabase,
         addRoleDatabase, USER_INFO, update_userData, getUsers_from_firestore,
         updateRoleDatabase, ACTION } from '@/firebase/firebaseDatabase';

// 定義 Quasar
const $q = useQuasar();

// 定義變數
const rows = ref([]);
const columns = [
  {
    name: 'action_name',
    label: '權限名稱(id)',
    field: 'action_name',
    align: 'center',
    headerClasses: 'text-bold text-blue-grey-7'
  },
  {
    name: 'action_label',
    label: '權限標示',
    field: 'action_label',
    align: 'center',
    headerClasses: 'text-bold text-blue-grey-7'
  },
  {
    name: 'action_description',
    label: '權限描述',
    field: 'action_description',
    align: 'center',
    headerClasses: 'text-bold text-blue-grey-7'
  },
  {
    name: 'function_btns',
    label: '',
    field: 'function_btns',
    align: 'center',
    headerClasses: 'text-bold text-blue-grey-7'
  },
  {
    name: 'editable',
    label: '',
    field: 'editable'
  }
];

const role_rows = ref([]);
const role_columns = [
  {
    name: 'role_name',
    label: '角色名稱(id)',
    field: 'role_name',
    align: 'center',
    headerClasses: 'text-bold text-blue-grey-7'
  },
  {
    name: 'role_label',
    label: '角色標籤',
    field: 'role_label',
    align: 'center',
    headerClasses: 'text-bold text-blue-grey-7'
  },
  {
    name: 'role_permission',
    label: '角色權限',
    field: 'role_permission',
    align: 'center',
    headerClasses: 'text-bold text-blue-grey-7'
  },
  {
    name: 'role_description',
    label: '角色描述',
    field: 'role_description',
    align: 'center',
    headerClasses: 'text-bold text-blue-grey-7'
  },
  {
    name: 'role_function_btns',
    label: '',
    field: 'role_function_btns',
    align: 'center',
    headerClasses: 'text-bold text-blue-grey-7'
  },
  {
    name: 'role_editable',
    label: '',
    field: 'role_editable',
  }
];

// 儲存正在被編輯的權限名稱
const editingPermission = ref(null);

// 儲存正在被編輯的角色名稱
const editingRole = ref(null);

// 從 firestore 取得權限資料
const permission_list = ref([]);

// 新增權限
const addPermission = () => {
  rows.value.push(PERMISSION('', '', ''));
  rows.value[rows.value.length - 1].editable = true;
};

// 從 firestore 取得權限資料
const loadPermissionData = async () => {
  const permissions = await getPermissionDatabase();
  rows.value = permissions;
};

// 編輯權限
const editPermission = async (row) => {
  if (row.permission_name === '') {
    $q.notify({
      message: '權限名稱不能為空!',
      color: 'red',
      position: 'top',
      progress: true,
      timeout: 500
    });
    return;
  }
  if (row.editable) {
    row.editable = false;
    if (editingPermission.value) {
      // 先刪除舊的權限資料
      await deletePermissionDatabase(editingPermission.value);
      editingPermission.value = null;
    }
    // 更新資料庫
    await addPermissionDatabase(PERMISSION(row.permission_name, row.permission_label, row.description));
  } else {
    editingPermission.value = row.permission_name;
    row.editable = true;
  }

  // 更新權限列表
  await update_permission_list();
};

// 刪除權限
const deletePermission = async (permission) => {
  // 從 rows 中刪除該權限
  rows.value = rows.value.filter(row => row.permission_name !== permission.permission_name);
  // 更新資料庫
  await deletePermissionDatabase(permission.permission_name);
  // 更新權限列表
  await update_permission_list();
};

// 從 firestore 取得角色資料
const loadRoleData = async () => {
  const roles = await getRoleDatabase();
  role_rows.value = roles;
};

// 新增角色
const addRole = () => {
  role_rows.value.push(ROLE('', '', ''));
  role_rows.value[role_rows.value.length - 1].editable = true;
};

// 編輯角色
const editRole = async (row) => {
  if (row.role_name === '') {
    $q.notify({
      message: '角色名稱不能為空!',
      color: 'red',
      position: 'top',
      progress: true,
      timeout: 500
    });
    return;
  }
  if (row.editable) {
    // 取得 database 資料
    const db_role = await getRoleDatabase();
    const db_role_data = db_role.find(r => r.id === row.id);
    row.editable = false;
    if (editingRole.value) {
      // 先刪除舊的角色資料
      await deleteRoleDatabase(editingRole.value);
      editingRole.value = null;
    }
    // 更新資料庫
    await addRoleDatabase(ROLE(row.role_name, row.role_label, row.role_description, db_role_data? db_role_data.role_permission : []));
    // 重新整理頁面
    setTimeout(() => {
      window.location.reload();
    }, 100);
  }
  else {
    editingRole.value = row.role_name;
    row.editable = true;
  }
};

// 刪除角色
const deleteRole = async (role) => {
  // 從 rows 中刪除該角色
  role_rows.value = role_rows.value.filter(row => row.role_name !== role.role_name);
  // 更新資料庫
  await deleteRoleDatabase(role.role_name);
};

// 移除權限
const remove_action = async (row, index) => {
  // 先取得 firestore 資料
  const db_role = await getRoleDatabase();
  let edit_role = db_role.find(r => r.id === row);
  edit_role.role_permission.splice(index, 1);
  // 更新資料庫
  await updateRoleDatabase(edit_role);
  // 重新載入角色資料
  await loadRoleData();
};

// 新增權限
const add_action = async (row, permission, index) => {
  if (!row) { return; }
  // 先取得 firestore 資料
  const db_role = await getRoleDatabase();
  let edit_role = db_role.find(r => r.id === row);
  // 先檢查是否已經有該權限
  const has_permission = edit_role.role_permission.some(p => p.action_name === permission.permission_name);
  if (has_permission) { return; }
  edit_role.role_permission.push(ACTION(permission.permission_name, permission.permission_label));
  // 更新資料庫
  await updateRoleDatabase(edit_role);
  // 重新載入角色資料
  await loadRoleData();
};

// 更新權限列表
const update_permission_list = async () => {
  const permissions = await getPermissionDatabase();
  permission_list.value = permissions;
};

// 掛載
onMounted(async () => {
  loadPermissionData();
  loadRoleData();
  await update_permission_list();
});

</script>

<style scoped>
.card {
  width: 100%;
  overflow: auto;
  height: 100%;
}
.section {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.title {
  font-size: 1.2em;
  font-weight: bold;
}
.subtitle {
  font-size: 1em;
  font-weight: normal;
  font-style: italic;
}
</style>