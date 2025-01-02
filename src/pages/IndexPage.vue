<template>
  <q-page class="flex flex-center">
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: pointer;" @click="login">
      <!-- Logo -->
      <img
        alt="ACCUiNspection logo"
        src="/logo.png"
        height="40px"
      >
      <!-- Login button -->
      <div style="width: 100%; display: flex; flex-direction: row; align-items: center; justify-content: space-evenly; margin-top: 1.5em;">
        <q-icon class="login-hint" name="east" />
        <span class="login-hint">Click to login</span>
        <q-icon class="login-hint" name="west" />
      </div>
    </div>
  </q-page>
</template>

<script setup>
defineOptions({
  name: 'IndexPage'
});

/* functions */

// Login function
const login = () => {
  console.log('Login');
}

</script>

<style scoped>
.login-hint {
  font-size: 14px;
  color: silver;
}
</style>
