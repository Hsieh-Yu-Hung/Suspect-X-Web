<template>

  <!-- 軟體版本設定 -->
  <q-card class="card">

    <!-- Header -->
    <q-card-section>
      <div class="section">
        <span class="title">編輯軟體版本設定</span>
        <div class="flex flex-center" style="gap: 10px">
          <q-btn glossy icon="webhook" color="deep-orange-9" label="新增" @click="add_software_version" />
        </div>
      </div>
    </q-card-section>

    <!-- 我是分隔線 -->
    <q-separator />

    <!-- Content -->
    <q-card-section>
      <q-list v-if="display_software_version.length > 1">
        <SoftwareItem v-for="item in display_software_version"
        :key="item.list_id"
        :software_info="item"
        @update_firestore_software="update_software_Lists"
        @delete_software="delete_software" />
      </q-list>
      <div class="flex flex-center flex-row" v-else>
        <span class="subtitle"> ... 請點按鈕新增軟體版本資料 ...</span>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup>
// 導入模組
import { ref, onMounted } from 'vue';

// 導入元件
import SoftwareItem from '@/components/SoftwareSection/SoftwareItem.vue';
import { deleteData, dataset_list } from '@/firebase';
import { SOFTWARE_DATA, addSoftwareVersionDatabase, getSoftwareVersionDatabase } from '@/firebase';
import { load_software_version_from_firestore } from '@/firebase';
import logger from '@/utility/logger';

// 顯示軟體資料
const header = SOFTWARE_DATA('軟體名稱', '軟體版本', '軟體備注', false);
const display_software_version = ref([header]);

// 發送事件
const emit = defineEmits(['software_List_is_updated']);

/* functions */

// 新增軟體
function add_software_version() {
  const new_software = SOFTWARE_DATA("NEW", "v1.0.0", "...輸入自定義軟體名稱和版本號...");
  display_software_version.value.push(new_software);
}

// 刪除軟體資料
async function delete_software(software_id_to_delete) {

  // 取得新的 display_software_version
  const new_display_software = display_software_version.value.filter(
    item => item.list_id !== software_id_to_delete
  );

  // 更新 display_software_version
  display_software_version.value = new_display_software;

  // 更新 firestore
  await deleteData(dataset_list.software_version_list, software_id_to_delete)
  .then((Response) => {
    if(Response.status === 'success') {
      logger.info(`${Response.message} ID: ${software_id_to_delete}`);
    }
    else {
      logger.error(`${Response.message} ID: ${software_id_to_delete}`);
    }
    // 發送事件
    emit('software_List_is_updated');
  })
  .catch((error) => {
    logger.error(`${error} ID: ${software_id_to_delete}`);
  });
}

// 更新 display_software_version 和 firestore 軟體資料
async function update_software_Lists(new_software) {

  // 更新display_software_version
  display_software_version.value = display_software_version.value.map(software =>
    software.list_id === new_software.list_id ? new_software : software
  );

  // 更新 firestore
  const softwares = await getSoftwareVersionDatabase();
  const masked_software_name = "軟體名稱";
  display_software_version.value.forEach(current_software => {
    if (current_software.software_name !== masked_software_name) {
      if (softwares.find(item => item.list_id === current_software.list_id)) {
        if (current_software.list_id === new_software.list_id) {
          // 如果存在則更新
          addSoftwareVersionDatabase(current_software);
          logger.info(`
          Update software version to firestore
          id: ${current_software.list_id}
          new_name: ${current_software.software_name}
          new_version: ${current_software.software_version}
          new_note: ${current_software.software_note}`);
        }
      }
      else {
        // 如果不存在則加入
        addSoftwareVersionDatabase(current_software);
        logger.info(`
        Add new software version to firestore
        name: ${current_software.software_name}
        version: ${current_software.software_version}
        note: ${current_software.software_note}`);
      }
    }
  });

  // 發送事件
  emit('software_List_is_updated');
}

// onMounted
onMounted(async () => {
  // 載入軟體資料
  await load_software_version_from_firestore(display_software_version.value);
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
