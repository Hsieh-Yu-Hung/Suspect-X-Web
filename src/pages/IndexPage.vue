<template>
  <q-page class="flex flex-center">
    <transition name="fade">
      <div v-if="display_page_content" style="display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: pointer;" @click="to_login">
        <!-- Logo -->
        <img
          alt="ACCUiNspection logo"
          src="/logo.png"
          height="40px"
        >
        <!-- Login button -->
        <div style="width: 100%; display: flex; flex-direction: row; align-items: center; justify-content: space-evenly; margin-top: 1.5em;">
          <q-icon class="login-hint" name="east" />
          <span class="login-hint">Click to Start</span>
          <q-icon class="login-hint" name="west" />
        </div>
      </div>
    </transition>
  </q-page>
</template>

<script setup>

/* Import modules */
import { ref } from 'vue';
import { useRouter } from 'vue-router';

/* refs */

// Router
const router = useRouter();

// State to control visibility
const display_page_content = ref(true);

defineOptions({
  name: 'IndexPage'
});

/* functions */

// Login function
const to_login = () => {
  // 關閉當前 page 顯示
  display_page_content.value = false;

  // 延遲 100ms 後跳轉到 login page
  setTimeout(() => {
    router.push('/login');
  }, 200);
}

</script>

<style scoped>
.login-hint {
  font-size: 14px;
  color: silver;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.fade-enter-to, .fade-leave-from {
  opacity: 1;
}
</style>
