<template>
  <q-card class="card">
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
                <q-btn dense round icon="delete" color="red" @click="deletePermission(props.row)" />
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
import { PERMISSION, getPermissionDatabase, deletePermissionDatabase, addPermissionDatabase } from '@/firebase/firebaseDatabase';

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
    // 更新資料庫
    await addPermissionDatabase(PERMISSION(row.permission_name, row.permission_label, row.description));
  } else {
    row.editable = true;
  }
};

// 刪除權限
const deletePermission = async (permission) => {
  // 從 rows 中刪除該權限
  rows.value = rows.value.filter(row => row.permission_name !== permission.permission_name);
  // 更新資料庫
  await deletePermissionDatabase(permission.permission_name);
};

// 掛載
onMounted(() => {
  loadPermissionData();
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