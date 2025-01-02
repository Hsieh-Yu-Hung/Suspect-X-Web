<template>
  <q-layout view="hHh lpR lFr">

    <!-- Layout Header -->
    <q-header reveal elevated class="bg-indigo-2 text-white" height-hint="98">

      <!-- 標題列 -->
      <q-toolbar>

        <!-- 左邊選單按鈕 -->
        <q-btn flat round icon="menu" @click="toggleLeftDrawer" />

        <!-- 標題 -->
        <q-toolbar-title>
          <div style="display: flex; flex-direction: row; align-items: center;">
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
import { ref } from 'vue'

const leftDrawerOpen = ref(false)
const rightDrawerOpen = ref(false)

const toggleLeftDrawer = () => {
  leftDrawerOpen.value = !leftDrawerOpen.value
}

const toggleRightDrawer = () => {
  rightDrawerOpen.value = !rightDrawerOpen.value
}

</script>
