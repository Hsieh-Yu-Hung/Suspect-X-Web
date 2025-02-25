<template>
  <q-card class="card">

    <!-- Title -->
    <q-card-section >
      <div class="section">
        <span class="title">其他控制項</span>
      </div>
    </q-card-section>

    <!-- 1. 尚未實作 -->
    <q-card-section>

    </q-card-section>

  </q-card>
</template>

<script setup>
// 導入模組
import { useQuasar } from 'quasar';
import { uploadLogs } from '@/firebase/firebaseFunction.js';

// 取得 Quasar
const $q = useQuasar();

// 上傳日誌
const callUploadLogs = async () => {
  $q.loading.show();
  const response = await uploadLogs().then(res => {
    return res.data;
  });
  if (response.status === "success") {
    $q.notify({
      message: response.message,
      progress: true,
      color: 'green',
      icon: 'check',
      position: 'top',
      timeout: 1000
    });
  }
  else {
    $q.notify({
      message: response.message,
      color: 'red',
      icon: 'warning',
      position: 'top',
      timeout: 3000
    });
  }
  $q.loading.hide();
}

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
