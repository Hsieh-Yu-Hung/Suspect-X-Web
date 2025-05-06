<template>
  <div>

    <!-- 標題 -->
    <div class="flex items-center" style="gap: 1em;">
      <q-icon name="edit_square" size="24px" class="text-blue-grey-8" />
      <span class="text-h6 text-bold text-blue-grey-8">管理測試資料集</span>
    </div>

    <!-- 選單 -->
    <div style="border: 1px solid #e0e0e0; border-radius: 10px; padding: 10px; margin-top: 1em;">
      <q-splitter
        v-model="splitterModel"
        style="height: 100%"
      >

        <!-- 頁籤 -->
        <template v-slot:before>
          <q-tabs
            v-model="tab"
            vertical
            class="text-blue-grey-8"
          >
            <q-tab name="fxs" label="FXS" />
            <q-tab name="htd" label="HTD" />
            <q-tab name="mthfr" label="MTHFR" />
            <q-tab name="sma" label="SMA" />
            <q-tab name="apoe" label="APOE" />
            <q-tab name="nudt15" label="NUDT15" />
            <q-tab name="alpha_thal" label="ALPAH-THAL" />
            <q-tab name="beta_thal" label="BETA-THAL" />
          </q-tabs>
        </template>

        <!-- 內容 -->
        <template v-slot:after>
          <q-tab-panels
            v-model="tab"
            animated
            swipeable
            vertical
            transition-prev="jump-up"
            transition-next="jump-up"
          >
            <!-- FXS -->
            <q-tab-panel name="fxs">
              <FXS_Panel />
            </q-tab-panel>

          </q-tab-panels>
        </template>

      </q-splitter>
    </div>

  </div>
</template>

<script setup>
// 導入模組
import { ref } from 'vue'

// 導入元件
import FXS_Panel from '@/components/AdminPageViewComp/OtherSettingSection/TestDatasetPanels/FXS_Panel.vue'

// 測試資料集
const tab = ref('fxs')
const splitterModel = ref(10)


</script>

<style scoped>
.card {
  width: 100%;
  overflow: auto;
  height: 100%;
}
.section {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.title {
  font-size: 1.2em;
  font-weight: bold;
}
.subtitle {
  font-size: 1em;
  font-weight: normal;
  font-style: italic;
}
</style>