<template>
  <q-table
    :rows="range_table_rows"
    :columns="range_table_columns"
    :rows-per-page-options="[0]"
    flat
    row-key="label"
    bordered
    dense
    style="height: 100%; width: 100%;"
  >
    <template v-slot:top>
      <div class="q-ma-md text-h6 text-bold text-grey-7">條件範圍</div>
      <q-space />
      <div class="q-ml-md row">
        <q-btn
          class="row q-ma-sm"
          color="purple"
          padding="xs"
          flat
          icon="restart_alt"
          label="Reset"
          @click="reset_table_value"/>
      </div>
    </template>
    <template v-slot:body="props">
      <q-tr :props="props">
        <q-td key="label" :props="props">{{ props.row.label }}</q-td>
        <q-td key="num" :props="props">{{ props.row.num }}</q-td>
        <q-td key="min" :props="props" style="width: 25%;">
          <q-input v-model.number="props.row.min" type="number" dense borderless filled step="0.01" input-style="text-align: center;" />
        </q-td>
        <q-td key="max" :props="props" style="width: 25%;">
          <q-input v-model.number="props.row.max" type="number" dense borderless filled step="0.01" input-style="text-align: center;" />
        </q-td>
      </q-tr>
    </template>
  </q-table>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import _ from 'lodash';

// 定義 props
const props = defineProps({
  range_table: {
    type: Object,
    default: null,
    required: true
  },
});

// 定義 emits
const emit = defineEmits(['update-range-table']);

// 定義表格的欄位
const range_table_columns = [
  { name: 'label', label: 'Label', field: 'label', align: 'center' },
  { name: 'num', label: 'Copy Number', field: 'num', align: 'center' },
  { name: 'min', label: 'Min', field: 'min', align: 'center' },
  { name: 'max', label: 'Max', field: 'max', align: 'center' }
];

// 初始化表格的行資料
const range_table_rows = ref([
  { label: 'smn1', num: '1', min: 0, max: 0 },
  { label: 'smn1', num: '2', min: 0, max: 0 },
  { label: 'smn1', num: '3', min: 0, max: 0 },
  { label: 'smn2', num: '1', min: 0, max: 0 },
  { label: 'smn2', num: '2', min: 0, max: 0 },
  { label: 'smn2', num: '3', min: 0, max: 0 }
]);

// 原始表格值
const original_range_table_rows = ref([]);

// 計算傳入的 range_table
const range_table = computed(() => props.range_table);

// 更新 range_table_rows
function update_range_table_rows(newRangeTable) {
  for (let smn in newRangeTable) {
    for (let std in newRangeTable[smn]) {
      const row = range_table_rows.value.find(row => row.label === smn && row.num === std);
      row.min = Number(newRangeTable[smn][std].min.toFixed(4)); // 設定最小值
      row.max = Number(newRangeTable[smn][std].max.toFixed(4)); // 設定最大值
    }
  }
}

// 比較新舊值的特定欄位是否不同
function grepValueCompare(newValue, previousValue, label, num, key) {
  const new_value = newValue.find(row => row.label === label && row.num === num);
  const previous_value = previousValue.find(row => row.label === label && row.num === num);
  return new_value[key] !== previous_value[key];
}

// 同步值的變化
function syncValue(newValue, previousValue, smn) {
  if (grepValueCompare(newValue, previousValue, smn, '2', 'min')) {
    const changed_value = newValue.find(row => row.label === smn && row.num === '2').min;
    range_table_rows.value.find(row => row.label === smn && row.num === '1').max = changed_value;
  }
  if (grepValueCompare(newValue, previousValue, smn, '1', 'max')) {
    const changed_value = newValue.find(row => row.label === smn && row.num === '1').max;
    range_table_rows.value.find(row => row.label === smn && row.num === '2').min = changed_value;
  }
  if (grepValueCompare(newValue, previousValue, smn, '3', 'min')) {
    const changed_value = newValue.find(row => row.label === smn && row.num === '3').min;
    range_table_rows.value.find(row => row.label === smn && row.num === '2').max = changed_value;
  }
  if (grepValueCompare(newValue, previousValue, smn, '2', 'max')) {
    const changed_value = newValue.find(row => row.label === smn && row.num === '2').max;
    range_table_rows.value.find(row => row.label === smn && row.num === '3').min = changed_value;
  }
}

// 重置表格值
function reset_table_value() {
  range_table_rows.value = JSON.parse(JSON.stringify(original_range_table_rows.value));
}

// 複製初始值
let previousValue = _.cloneDeep(range_table_rows.value);

// 初始化
function init_range_table_rows(){
  update_range_table_rows(range_table.value);
  original_range_table_rows.value = JSON.parse(JSON.stringify(range_table_rows.value));
}

// 監聽 range_table_rows 的變化
watch(range_table_rows, (newValue) => {
  syncValue(newValue, previousValue, 'smn1');
  syncValue(newValue, previousValue, 'smn2');
  previousValue = _.cloneDeep(newValue);
  emit('update-range-table');
}, { deep: true });

// 監聽 range_table 的變化
watch(range_table, (newValue) => {
  update_range_table_rows(newValue);
  original_range_table_rows.value = JSON.parse(JSON.stringify(range_table_rows.value));
}, { deep: true });

// 暴露給父組件的屬性和方法
defineExpose({
  range_table_rows,
  update_range_table_rows,
  init_range_table_rows
});
</script>
