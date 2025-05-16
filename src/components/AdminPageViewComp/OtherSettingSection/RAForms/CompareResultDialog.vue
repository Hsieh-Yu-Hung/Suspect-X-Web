<template>
  <q-dialog v-model="isOpen" persistent>
    <q-card style="min-width: 1000px">
      <q-card-section class="row items-center">
        <div class="text-h6">結果比對</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>

      <q-card-section>
        <q-table
          :rows="combinedCompareData"
          :columns="compareColumns"
          row-key="id"
          :rows-per-page-options="[0]"
        >
          <template v-slot:body-cell-type="props">
            <q-td :props="props">
              <q-chip
                :color="props.row.type === 'Assessment' ? 'primary' : 'teal'"
                text-color="white"
                :icon="props.row.type === 'Assessment' ? 'assessment' : 'analytics'"
              >
                {{ props.row.type }}
              </q-chip>
            </q-td>
          </template>
          <template v-slot:body-cell-status="props">
            <q-td :props="props">
              <q-chip
                :color="props.row.status === 'match' ? 'positive' : 'negative'"
                text-color="white"
                :icon="props.row.status === 'match' ? 'check_circle' : 'error'"
              >
                {{ props.row.status === 'match' ? '符合' : '不符合' }}
              </q-chip>
            </q-td>
          </template>
        </q-table>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="關閉" color="primary" v-close-popup />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  },
  rowData: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['update:modelValue']);

// 控制對話框顯示
const isOpen = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
});

// 表格列定義
const compareColumns = [
  {
    name: 'type',
    label: '類型',
    field: 'type',
    align: 'center'
  },
  {
    name: 'sample_id',
    label: '樣本 ID',
    field: 'sample_id',
    align: 'center'
  },
  {
    name: 'answer',
    label: '預期結果',
    field: 'answer',
    align: 'center'
  },
  {
    name: 'testing',
    label: '測試結果',
    field: 'testing',
    align: 'center'
  },
  {
    name: 'status',
    label: '狀態',
    field: 'status',
    align: 'center'
  }
];

// 合併比對數據
const combinedCompareData = computed(() => {

  // 檢查數據結構
  if (!props.rowData) {
    console.error("No rowData");
    return [];
  }

  const assessmentData = [];
  if (props.rowData.assessment) {
    const answerSet = Array.isArray(props.rowData.assessment.anwser_set) ?
      props.rowData.assessment.anwser_set : [];
    const testingSet = Array.isArray(props.rowData.assessment.testing_set) ?
      props.rowData.assessment.testing_set : [];

    answerSet.forEach(answer => {
      const testing = testingSet.find(test => test.sample_id === answer.sample_id);
      assessmentData.push({
        id: `assessment-${answer.sample_id}`,
        type: 'Assessment',
        sample_id: answer.sample_id,
        answer: answer.context,
        testing: testing?.context || '未測試',
        status: testing?.context === answer.context ? 'match' : 'mismatch'
      });
    });
  }

  const resultData = [];
  if (props.rowData.result) {
    const answerSet = Array.isArray(props.rowData.result.anwser_set) ?
      props.rowData.result.anwser_set : [];
    const testingSet = Array.isArray(props.rowData.result.testing_set) ?
      props.rowData.result.testing_set : [];

    answerSet.forEach(answer => {
      const testing = testingSet.find(test => test.sample_id === answer.sample_id);
      resultData.push({
        id: `result-${answer.sample_id}`,
        type: 'Result',
        sample_id: answer.sample_id,
        answer: answer.context,
        testing: testing?.context || '未測試',
        status: testing?.context === answer.context ? 'match' : 'mismatch'
      });
    });
  }

  const combined = [...assessmentData, ...resultData];
  return combined;
});

</script>

<style scoped>
.q-table {
  background-color: white;
}
</style>
