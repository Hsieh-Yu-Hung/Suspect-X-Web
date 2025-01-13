<template>
  <q-page class="flex flex-center">

    <!-- Login form -->
    <transition name="fade" v-if="current_form === 'login'">
      <LoginForm v-if="display_page_content" ref="login_form" @switch_to_register="switch_to_register" />
    </transition>

    <!-- Register form -->
    <transition name="fade" v-if="current_form === 'register'">
      <RegisterForm v-if="display_page_content" ref="register_form" @switch_to_login="switch_to_login" />
    </transition>

  </q-page>
</template>

<script setup>

/* Define options */
defineOptions({
  name: 'LoginPage'
});

/* Import modules */
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

/* Import components */
import LoginForm from 'components/LoginForm.vue';
import RegisterForm from 'components/RegisterForm.vue';

/* refs */
const router = useRouter();
const login_form = ref(null);
const register_form = ref(null);
const display_page_content = ref(false);
const current_form = ref('login');

/* functions */

// 顯示頁面
function show_page(delay = 200) {
  setTimeout(() => {
    display_page_content.value = true;
  }, delay);
}

// 切換表單 -- 登入
function switch_to_login() {
  current_form.value = 'login';
}

// 切換表單 -- 註冊
function switch_to_register() {
  current_form.value = 'register';
}

/* onMounted */
onMounted(() => {
  show_page();
});

</script>

<style scoped>
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
