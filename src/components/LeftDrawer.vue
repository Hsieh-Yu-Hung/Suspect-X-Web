<template>
  <div class="drawer-content">
    <q-btn glossy label="Debug" @click="debug_test">
      <q-icon name="bug_report" />
    </q-btn>
  </div>
</template>

<script setup>

import { getData, dataset_list } from '@/firebase';

/* functions */

// Debug test
async function debug_test() {
  console.log('debug_test');
}

</script>

<style scoped>
.drawer-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
}
</style>
