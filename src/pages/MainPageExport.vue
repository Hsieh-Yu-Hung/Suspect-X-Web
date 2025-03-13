<template>
  <q-page>
    <div class="row justify-between q-mt-lg q-mx-xl">
      <div class="col">
        <ReportPreview />
      </div>
    </div>
    <div class="row justify-between q-mt-lg q-mx-xl q-pb-lg">
      <div class="col">
        <ReportExport />
      </div>
    </div>
  </q-page>
</template>

<script setup>
// 導入模組
import { onMounted, computed } from 'vue';
import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';

// 導入模組 composable
import { useValidateAccountStatus } from '@/composables/accessStoreUserInfo.js';

// 元件
import ReportPreview from '@/components/ExportPageViews/ReportPreview.vue';
import ReportExport from '@/components/ExportPageViews/ReportExport.vue';


// 取得 Quasar 和 Router 和 store
const $q = useQuasar();
const router = useRouter();
const store = useStore();

// 掛載時
onMounted(() => {
  // 檢查帳號狀態, 若未開通則跳轉到 not-active
  useValidateAccountStatus($q, router, store);
});

const settingProps = computed(() => {
  return store.state.data.settingProps;
});

const qualityControlProps = computed(() => {
  return store.state.data.qualityControlProps;
});
</script>
