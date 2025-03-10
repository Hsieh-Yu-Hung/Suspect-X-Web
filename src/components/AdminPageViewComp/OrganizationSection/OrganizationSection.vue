<template>
  <q-card class="card">

    <!-- Title -->
    <q-card-section >
      <div class="section">
        <span class="title">編輯 Organization 設定</span>
        <div class="flex flex-center" style="gap: 10px">
          <q-btn glossy icon="group_add" color="cyan-9" label="新增" @click="add_organization" />
        </div>
      </div>
    </q-card-section>

    <!-- 我是分隔線 -->
    <q-separator />

    <!-- Content -->
    <q-card-section>
      <q-list v-if="display_organization.length > 1">
        <OrganizationItem
          v-for="item in display_organization"
          :key="item.organization_id"
          :organization_info="item"
          :ref="item.organization_id"
          :software_version_list="software_versions"
          @update_firestore_organization="update_organization_Lists"
          @delete_organization="delete_organization"
        />
      </q-list>
      <div class="flex flex-center flex-row" v-else>
        <span class="subtitle"> ... 請點按鈕新增組織資料 ...</span>
      </div>
    </q-card-section>

  </q-card>
</template>

<script setup>
// 導入模組
import { ref, onMounted } from 'vue';
import { useQuasar } from 'quasar';

// 導入元件
import OrganizationItem from '@/components/AdminPageViewComp/OrganizationSection/OrganizationItem.vue';
import { ORGAN_DATA, dataset_list, deleteData, getOrganizationDatabase, addOrganizationDatabase } from '@/firebase';
import { load_software_version_for_dropdown, load_organization_from_firestore } from '@/firebase';

// 取得 Quasar
const $q = useQuasar();

// 顯示組織資料
const header = ORGAN_DATA('組織名稱', '軟體選用', '成員數量', '加入日期', null, false);
const display_organization = ref([header]);

// 軟體版本列表
const software_versions = ref(['請選擇']);

// 新增組織功能
const add_organization = () => {
  const new_name = '新增組織';
  const new_software_selection = '請選擇';
  const new_member_count = '0';
  const new_join_date = new Date().toLocaleDateString();
  const new_organization = ORGAN_DATA(new_name, new_software_selection, new_member_count, new_join_date);
  display_organization.value.push(new_organization);
};

// Emits
const emit = defineEmits(['organization_List_is_updated']);

// 刪除組織資料
async function delete_organization(organization_id_to_delete) {

  // 開啟loading
  $q.loading.show();

  // 取得新的 display_organization
  const new_display_organization = display_organization.value.filter(
    item => item.organization_id !== organization_id_to_delete || item.organization_id === 'default'
  );

  // 更新 display_organization
  display_organization.value = new_display_organization;

  // 更新 firestore
  await deleteData(dataset_list.organization_list, organization_id_to_delete)
  .then((Response) => {
    if(Response.status === 'success') {
      // 發送事件
      emit('organization_List_is_updated');
    }
    else {
      console.error(Response.message);
    }
  })
  .catch((error) => {
    console.error(error);
  })
  .finally(() => {
    // 關閉loading
    $q.loading.hide();
  });
}

// 更新 organization 和 firestore 組織資料
async function update_organization_Lists(new_organization) {

  // 開啟loading
  $q.loading.show();

  // 更新 display_organization
  display_organization.value = display_organization.value.map(organization =>
    organization.organization_id === new_organization.organization_id ? new_organization : organization
  );

  // 更新 firestore
  const organizations = await getOrganizationDatabase();
  const masked_organization_name = "組織名稱";
  display_organization.value.forEach(current_organization => {
    if (current_organization.organization_name !== masked_organization_name) {
      if (organizations.find(item => item.organization_id === current_organization.organization_id)) {
        if (current_organization.organization_id === new_organization.organization_id) {
          // 如果存在則更新
          addOrganizationDatabase(current_organization);
        }
      }
      else {
        // 如果不存在則加入
        addOrganizationDatabase(current_organization);
      }
    }
  });

  // 發送事件
  emit('organization_List_is_updated');

  // 關閉loading
  $q.loading.hide();
}

// 更新軟體版本列表
async function update_software_version_list() {
  // 從 firestore 載入軟體資料
  await load_software_version_for_dropdown(software_versions.value);
}

// onMounted
onMounted(async () => {

  // 開啟loading
  $q.loading.show();

  // 從 firestore 載入軟體資料
  await load_software_version_for_dropdown(software_versions.value);

  // 從 firestore 載入組織資料
  await load_organization_from_firestore(display_organization.value);

  // 關閉loading
  $q.loading.hide();

});

// Expose functions
defineExpose({
  update_software_version_list,
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
