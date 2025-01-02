<template>
  <q-layout view="hHh lpR lFr">

    <!-- Layout Header -->
    <q-header v-model="show_header" reveal elevated class="bg-indigo-2 text-white" height-hint="98">

      <!-- 標題列 -->
      <q-toolbar>

        <!-- 左邊選單按鈕 -->
        <q-btn flat round icon="menu" @click="toggleLeftDrawer" />

        <!-- 標題 -->
        <q-toolbar-title>
          <div style="width: fit-content; display: flex; flex-direction: row; align-items: center; cursor: pointer;" @click="to_index">
            <!-- logo -->
            <div class="logo" style="height: 35px; margin-inline: 10px;">
              <img src="/icon.png" style="height: 100%;">
            </div>
            <!-- 標題文字 -->
            <div style="height: 40px; margin-inline: 10px; display: flex; flex-direction: row; align-items: center;">
              <span style="font-size: 1.4em; font-weight: bold; color: black;">ACCUiNspection
                <span style="font-size: 0.4em; font-weight: bold; color: slategray; margin-inline: 5px;">WEB Service</span>
              </span>
            </div>
          </div>
        </q-toolbar-title>

        <!-- 右邊選單按鈕 -->
        <q-btn dense flat icon="group" label="Show Account" @click="toggleRightDrawer" color="black"/>
      </q-toolbar>

      <!-- 頁籤按鈕 -->
      <q-tabs align="right" class="text-blue-grey-8">
        <q-route-tab to="/page-import" label="Import" />
        <q-route-tab to="/page-analysis" label="Analysis" />
        <q-route-tab to="/page-export" label="Export" />
      </q-tabs>

    </q-header>

    <q-drawer v-model="leftDrawerOpen" side="left" overlay bordered>
      <!-- drawer content -->
    </q-drawer>

    <q-drawer v-model="rightDrawerOpen" side="right" overlay behavior="mobile" bordered>
      <!-- drawer content -->
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>

  </q-layout>
</template>

<script setup>

/* Import modules */
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router';

/* refs */
const router = useRouter();
const route = useRoute();
const leftDrawerOpen = ref(false)
const rightDrawerOpen = ref(false)
const show_header = ref(true);

/* functions */

// 開關左邊選單
const toggleLeftDrawer = () => {
  leftDrawerOpen.value = !leftDrawerOpen.value
}

// 開關右邊選單
const toggleRightDrawer = () => {
  rightDrawerOpen.value = !rightDrawerOpen.value
}

// 開關標題列
const closeHeader = () => {
  show_header.value = false;
}

// 開啟標題列
const openHeader = () => {
  show_header.value = true;
}

// 跳轉到首頁
const to_index = () => {
  router.push('/');
}

/* onMounted */
onMounted(() => {
  if (route.path === '/login') {
    closeHeader();
  } else {
    openHeader();
  }
});

/* watch */
watch(route, () => {
  if (route.path === '/login') {
    closeHeader();
  } else {
    openHeader();
  }
});

</script>
