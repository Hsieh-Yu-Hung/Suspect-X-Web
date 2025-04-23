<template>
  <q-card class="card">

    <!-- Title -->
    <q-card-section >
      <div class="section">
        <span class="text-h5 text-bold text-blue-grey-8">其他控制項</span>
      </div>
    </q-card-section>

    <!-- 1. 管理測試資料集 -->
    <q-card-section>
      <ManageTestDataset />
    </q-card-section>

  </q-card>
</template>

<script setup>
// 導入元件
import ManageTestDataset from './ManageTestDataset.vue'
</script>

<style scoped>
.card {
  width: 100%;
  overflow: auto;
  height: 100%;
}
.section {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.title {
  font-size: 1.2em;
  font-weight: bold;
}
.subtitle {
  font-size: 1em;
  font-weight: normal;
  font-style: italic;
}
</style>
