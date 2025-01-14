<template>
  <div class="drawer-content">
    <q-btn glossy label="Debug" @click="debug_test">
      <q-icon name="bug_report" />
    </q-btn>
  </div>
</template>

<script setup>

/* functions */
import { on_request_example } from '@/firebase';

// Debug test
async function debug_test() {
  console.log('debug_test');
  const res = await on_request_example().then((response) => {
    return response.data;
  });
  console.log("response:", res);
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
