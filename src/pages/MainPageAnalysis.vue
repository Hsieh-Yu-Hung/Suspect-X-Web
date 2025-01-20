<template>
  <q-page>
    <div class="row justify-between q-mt-lg q-mx-xl">
      <div class="col">
        <AnalysisSettings></AnalysisSettings>
      </div>
    </div>
  </q-page>
</template>

<script setup>
/* Import modules */
import { onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';

// 導入模組 composable
import { useValidateAccountStatus } from '@/composables/accessStoreUserInfo.js';

// 導入元件
import AnalysisSettings from '@/components/AnalysisSettings.vue';

// 取得 Quasar 和 Router 和 store
const $q = useQuasar();
const router = useRouter();
const store = useStore();

// 掛載時
onMounted(() => {
  // 檢查帳號狀態, 若未開通則跳轉到 not-active
  // useValidateAccountStatus($q, router, store);
});

</script>
