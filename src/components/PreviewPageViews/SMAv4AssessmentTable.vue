<template>
  <q-table
    :rows="range_table_rows"
    :columns="range_table_columns"
    :rows-per-page-options="[0]"
    flat
    row-key="label"
  >
    <!-- 表格標題-->
    <template v-slot:header="props">
      <q-tr>
        <q-th key="sample" :props="props"><div class="table-header"><span>Sample</span></div></q-th>
        <q-th key="smn" :props="props"><div class="table-header"><span>SMN1:SMN2</span></div></q-th>
        <q-th key="status" :props="props"><div class="table-header"><span>Status</span></div></q-th>
      </q-tr>
    </template>

  </q-table>
</template>

<script setup>
// 倒入模組
import { ref, computed } from 'vue';

// 定義 props
const props = defineProps({
  result_table_row: {
    type: Array,
    required: true
  }
});

// 表格欄位
const range_table_columns = [
  { name: 'sample', required: true, label: 'Sample', align: 'center', field: 'sample', sortable: true},
  { name: 'smn', required: true, label: 'SMN1:SMN2', align: 'center', field: 'smn', sortable: true },
  { name: 'status', required: true, label: 'Status', align: 'center', field: 'status', sortable: true }
];

// 表格資料
const range_table_rows = ref([]);

// Functions
function updateRangeTableRows() {

  // 得到 props 的資料
  const result_table_row = computed(() => props.result_table_row);

  // 取出 sample
  const sample_list = [...new Set(result_table_row.value.filter(row => row.type === 'sample').map(row => row.sample_name.split('-smn')[0]))];

  sample_list.forEach(sample => {
    const smn1_copy_number = result_table_row.value.filter(row => row.sample_name.includes(sample) && row.smn === 'smn1').map(row => row.num);
    const smn2_copy_number = result_table_row.value.filter(row => row.sample_name.includes(sample) && row.smn === 'smn2').map(row => row.num);
    const row = {
      sample: sample,
      smn: smn1_copy_number + ' : ' + smn2_copy_number,
      status: '尚未決定'
    }
    range_table_rows.value.push(row);
  });
}

// Expose
defineExpose({
  updateRangeTableRows,
});

</script>

<style scoped>
.table-header{
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 16px;
}
</style>
