<template>
  <q-card bordered style="width: 100%;">
    <q-card-section>
      <div class="text-h5 text-uppercase text-bold text-blue-grey-7">
        Testing Table
      </div>
      <div class="q-pa-md">
        <q-table
          :rows="dataset_rows"
          :columns="dataset_columns"
          row-key="name"
          :rows-per-page-options="[1000]"
        >
        </q-table>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import getTestingData from '@/composables/useGetTestingData';

// props
const props = defineProps({
  current_product: {
    type: String,
    required: true,
  },
});

// 取得 Dataset Name
const dataset_name = computed(() => {
  switch (props.current_product) {
    case 'fx':
      return 'FXS';
    case 'hd':
      return 'HTD';
    case 'sma':
      return 'SMA';
    case 'thal-import-alpha':
      return 'THAL_ALPHA';
    case 'thal-import-beta':
      return 'THAL_BETA';
    case 'nudt15':
      return 'NUDT15';
    case 'apoe-import':
      return 'APOE';
    case 'mthfr-import':
      return 'MTHFR';
    default:
      return props.current_product;
  }
});

// 定義 dataset_rows
const dataset_rows = ref([
  {
    name: 'Dataset 1',
    group: 'Positive',
    config: 'instrument/reagent',
    result: 'result',
    qc: 'pass the criteria',
    assessment: 'assessment',
  },
]);

// 定義 dataset_columns
const dataset_columns = ref([
  {
    name: 'DatasetName',
    label: 'Dataset Name',
    field: 'name',
    align: 'center',
  },
  {
    name: 'Group',
    label: 'Group',
    field: 'group',
    align: 'center',
  },
  {
    name: 'Config',
    label: 'Configs',
    field: 'config',
    align: 'center',
  },
  {
    name: 'QC',
    label: 'QC',
    field: 'qc',
    align: 'center',
  },
  {
    name: 'Result',
    label: 'Result',
    field: 'result',
    align: 'center',
  },
  {
    name: 'Assessment',
    label: 'Assessment',
    field: 'assessment',
    align: 'center',
  },
  {
    name: 'Validation',
    label: '',
    field: 'validation',
    align: 'center',
  },
]);

// 測試資料集
const testing_data = ref([]);

// 定義 onMounted
onMounted(async () => {
  // 取得測試資料集
  testing_data.value = await getTestingData(dataset_name.value);
  console.log("testing_data", testing_data.value);
});
</script>

