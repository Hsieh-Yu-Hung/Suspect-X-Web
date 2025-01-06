<template>
  <q-select style="width: 100%;" :label="props.label" v-model="selected_value" :options="options">
    <template v-slot:prepend>
      <q-icon :name="props.icon" />
    </template>
  </q-select>
</template>

<script setup>
/* Import */
import { ref, onMounted } from 'vue';
import { useStore } from 'vuex';

/* Props */
const props = defineProps({
  label: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  data_key: {
    type: String,
    required: true
  }
});

/* Store */
const store = useStore();
const options = ref([]);
const selected_value = ref('');

/* function */
function update_organization_list() {
  // 觸發組織列表的載入
  store.dispatch('organization_list/load_organization_list');

  // 取得組織列表
  const organization_list = store.getters['organization_list/getOrganizationList'];

  // 設定下拉選單的選項
  options.value = organization_list;
}

/* onMounted */
onMounted(() => {
  if (props.data_key === 'organization') {
    // 載入組織列表
    update_organization_list();
  }
});

</script>

