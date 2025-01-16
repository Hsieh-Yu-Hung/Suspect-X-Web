<template>
  <q-page class="flex flex-center">

    <!-- 組織/軟體資料管理 -->
    <div class="section-container">
      <OrganizationSection ref="organization_section" />
      <SoftwareSection ref="software_section" @software_List_is_updated="update_software_List" />
    </div>

    <!-- 使用者資料管理 -->
    <div class="section-container" style="width: 52vw;">
      <UserManageSection ref="user_manage_section" />
    </div>

  </q-page>
</template>

<script setup>

// 導入模組
import { ref } from 'vue';

// 導入元件
import OrganizationSection from '@/components/OrganizationSection/OrganizationSection.vue';
import SoftwareSection from '@/components/SoftwareSection/SoftwareSection.vue';
import UserManageSection from '@/components/UserManageSection/UserManageSection.vue';

// refs
const organization_section = ref(null);
const software_section = ref(null);
const user_manage_section = ref(null);

// 更新軟體列表
const update_software_List = () => {
  // 重新載入組織列表的軟體版本選單
  organization_section.value.update_software_version_list();
}

</script>

<style scoped>
.section-container {
  width: 40vw;
  min-width: 650px;
  display: flex;
  height: 90vh;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  gap: 10px;
  margin-block: auto;
  margin-inline: 10px;
  padding-block: 20px;
}
</style>
