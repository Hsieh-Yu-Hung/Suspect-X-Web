<template>
  <q-page class="flex flex-center">
    <div class="container">

      <div class="block" style="height: 50px; margin-bottom: 20px;">
        <img src="/logo.png" alt="logo">
      </div>

      <div style="display: flex; flex-direction: row; justify-content: center; align-items: center; gap: 10px;">
        <q-icon name="check_circle" color="green" size="sm"/>
        <span class="text-h5">
          帳號已成功註冊！
        </span>
      </div>

      <div style="display: flex; flex-direction: row; justify-content: center; align-items: center; gap: 10px;">
        <q-icon name="warning" color="deep-orange" size="sm"/>
        <span class="text-h5">
          但是尚未開通，請聯絡管理員！
        </span>
      </div>

    </div>
  </q-page>
</template>

<style scoped>
.container{
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100%;
  gap: 40px;
}
</style>
