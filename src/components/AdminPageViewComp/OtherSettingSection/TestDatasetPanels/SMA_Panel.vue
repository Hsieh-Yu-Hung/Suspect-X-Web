<template>
  <div>
    <QPCRDatasetTmpl ref="qpcrDatasetTmpl" :dataset_class="dataset_class" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import QPCRDatasetTmpl from '../TestDatasetTemplates/QPCRDatasetTmpl.vue';

// 引用 QsepDatasetTmpl
const qpcrDatasetTmpl = ref(null)

// 定義 dataset_class
const dataset_class = 'SMA'

</script>