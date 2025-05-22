<template>
  <div>
    <QsepDatasetTmpl ref="qsepDatasetTmpl" :dataset_class="dataset_class" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import QsepDatasetTmpl from '../TestDatasetTemplates/QsepDatasetTmpl.vue';

// 引用 QsepDatasetTmpl
const qsepDatasetTmpl = ref(null)

// 定義 dataset_class
const dataset_class = 'FXS'

</script>
