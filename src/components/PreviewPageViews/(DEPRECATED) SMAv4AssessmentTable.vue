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
        <q-th key="assessment" :props="props"><div class="table-header"><span>Assessment</span></div></q-th>
        <q-th key="showFig" :props="props"><div class="table-header"><span></span></div></q-th>
      </q-tr>
    </template>

    <!-- Assessment 欄位 -->
    <template v-slot:body-cell-assessment="cell">
      <q-td :props="cell">
        <q-chip
          :key="cell.value"
          :color="interpretationColor(cell.value)"
          :label="cell.value"
        />
      </q-td>
    </template>

    <!-- Show Fig 欄位 -->
    <template v-slot:body-cell-showFig="cell">
      <q-td :props="cell">
        <q-btn
          push
          :color="btnColor(cell.row.sample)"
          :text-color="btnTextColor(cell.row.sample)"
          round
          size="md"
          icon="mdi-chart-bell-curve-cumulative"
          @click="showFigure(cell.row.sample, cell.row.smn_number.split(':')[0], cell.row.smn_number.split(':')[1])"
          :disable="cell.row.assessment === 'Invalid' ? true : false"
        />
      </q-td>
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
  { name: 'assessment', required: true, label: 'Assessment', align: 'center', field: 'assessment', sortable: true },
  { name: 'showFig', required: true, label: 'Show Fig', align: 'center', field: 'showFig', sortable: false }
];

// 表格資料
const range_table_rows = ref([]);

// 顯示圖片
const figRows = ref([]);
const showFigureType = ref(null);
const showFigureWell = ref(null);

// Functions

// 解釋 SMN 類型
function smnTypeInterpretation(smn1, smn2) {
  let type = String(smn1) + String(smn2);

  // Defined interpretation
  function isNormal(typeArray) {
    return [
      "20",
      "21",
      "22",
      "23",
      "24",
      "30",
      "31",
      "32",
      "33",
      "34",
      "41",
      "42",
      "43",
      "44",
    ].includes(typeArray);
  }
  function isCarrier(typeArray) {
    return ["10", "11", "12", "13", "14"].includes(typeArray);
  }
  function isAffected(typeArray) {
    return ["01", "02", "03", "04"].includes(typeArray);
  }

  if (isNormal(type)) {
    // Defined "Noraml" by SMN1:SMN2 =
    // 2:0 or 2:1 or 2:2 or 2:3 or 2:4 or
    // 3:0 or 3:1 or 3:2 or 3:3 or 3:4 or
    // 4:1 or 4:2 or 4:3 or 4:4
    return {
      value: "normal",
      label: "Normal",
    };;
  } else if (isCarrier(type)) {
    // Defined "SMA carrier" by SMN1:SMN2 =
    // 1:0 or 1:1 or 1:2 or 1:3 or 1:4
    return {
      value: "carrier",
      label: "SMA carrier",
    };
  } else if (isAffected(type)) {
    return {
      value: "affected",
      label: "SMA affected",
    };
  } else {
    // Defined "Invalid" (nonsense value) by SMN1:SMN2 =
    // 0:0
    return {
      value: "invalid",
      label: "Invalid",
    };
  }
};

// 解釋 SMN 類型顏色
const interpretationColor = (value) => {
  if (value === "Normal") {
    return "green-13";
  } else if (value === "SMA carrier") {
    return "yellow-7";
  } else if (value.includes("SMA affected")) {
    return "deep-orange-5";
  } else {
    return "grey-4";
  }
};

// Show Fig 按鈕文字顏色
const btnTextColor = (well) => {
  if (showFigureWell.value === well) {
    return "white"
  } else {
    return "blue-grey-8"
  }
};

// Show Fig 按鈕顏色
const btnColor = (well) => {
  if (showFigureWell.value === well) {
    return "blue-grey-8"
  } else {
    return "white"
  }
};

// 取得圖片路徑
const imgPath = (type) => {
  if (popupLst.includes(type)) {
    popupShow.value = true;
  } else {
    popupShow.value = false;
  }
  if (normalLst.includes(type)) {
    isNormal.value = true;
  } else {
    isNormal.value = false;
  }
  return `diagram/${type.replace(":", "_")}-1.svg`;
};

// 顯示圖片
function showFigure (well, smn1, smn2) {
  if (showFigureWell.value === well) {
    showFigureWell.value = null;
    showFigureType.value = null;
    figRows.value = [];
  } else {
    showFigureWell.value = well;
    showFigureType.value = `${smn1}:${smn2}`;
    figRows.value = getFigRows(smn1, smn2);
  }
};

// 更新表格資料
function updateRangeTableRows() {

  // 得到 props 的資料
  const result_table_row = computed(() => props.result_table_row);

  // 取出 sample
  const sample_list = [...new Set(result_table_row.value.filter(row => row.type === 'sample').map(row => row.sample_name.split('-smn')[0]))];

  sample_list.forEach(sample => {
    const smn1_copy_number = result_table_row.value.filter(row => row.sample_name.split('-smn')[0] === sample && row.smn === 'smn1').map(row => row.num);
    const smn2_copy_number = result_table_row.value.filter(row => row.sample_name.split('-smn')[0] === sample && row.smn === 'smn2').map(row => row.num);
    const row = {
      sample: sample,
      smn: smn1_copy_number + ' : ' + smn2_copy_number,
      assessment: smnTypeInterpretation(smn1_copy_number, smn2_copy_number).label
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
