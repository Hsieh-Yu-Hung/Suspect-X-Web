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
          <template v-slot:body-cell-config="props">
            <q-td :props="props">
              <div class="row q-gutter-sm justify-center" style="display: flex; flex-direction: column; justify-content: center; align-items: center;">
                <q-chip color="primary" text-color="white" icon="biotech" v-if="props.row.config.instrument">
                  {{ props.row.config.instrument }}
                </q-chip>
                <q-chip color="teal" text-color="white" icon="science" v-if="props.row.config.reagent">
                  {{ props.row.config.reagent }}
                </q-chip>
              </div>
            </q-td>
          </template>
          <template v-slot:body-cell-validation="props">
            <q-td :props="props">
              <div class="row q-gutter-sm justify-center" style="display: flex; flex-direction: column; justify-content: center; align-items: center;">
                <q-chip
                  :color="props.row.validation === 'ok' ? 'positive' : props.row.validation === 'error' ? 'negative' : 'grey'"
                  text-color="white"
                  :icon="props.row.validation === 'ok' ? 'check_circle' : props.row.validation === 'error' ? 'error' : 'help'">
                  {{ props.row.validation === 'ok' ? 'OK' : props.row.validation === 'error' ? 'Error' : 'Not Set' }}
                </q-chip>
              </div>
            </q-td>
          </template>
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
const dataset_rows = computed(() => {
  return testing_data.value.map((item) => {
    return {
      name: item.name,
      group: item.group,
      config: {
        instrument: item.instrument || '未指定',
        reagent: item.reagent || '未指定',
      },
      qc: item.qc,
      result: item.result,
      assessment: item.assessments,
      validation: 'not-set',
    };
  });
});

// 定義 dataset_columns
const dataset_columns = ref([
  {
    name: 'name',
    label: 'Dataset Name',
    field: 'name',
    align: 'center',
  },
  {
    name: 'group',
    label: 'Group',
    field: 'group',
    align: 'center',
  },
  {
    name: 'config',
    label: 'Configs',
    field: 'config',
    align: 'center',
    format: val => `${val.instrument} / ${val.reagent}`
  },
  {
    name: 'qc',
    label: 'QC',
    field: 'qc',
    align: 'center',
  },
  {
    name: 'result',
    label: 'Result',
    field: 'result',
    align: 'center',
  },
  {
    name: 'assessment',
    label: 'Assessment',
    field: 'assessment',
    align: 'center',
  },
  {
    name: 'validation',
    label: 'Validation',
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

