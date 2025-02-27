<template>
  <q-card>

    <!-- Header -->
    <q-card-section>
      <div class="row justify-between" style="display: flex; flex-direction: row; align-items: center; justify-content: space-between;">
        <span class="text-h5 text-uppercase text-bold text-blue-grey-7">Parameters Setting</span>
        <div class="q-pa-md" style="display: flex; flex-direction: row; align-items: center; justify-content: space-between;">
          <div class="q-gutter-sm" style="margin-right: 20px; display: flex; flex-direction: row; align-items: center; justify-content: space-between;">
            <span class="text-subtitle2" style="font-size: 18px;">Re-analyse with: </span>
            <q-checkbox size="md" v-model="re_analyse_selection" val="new_peak" label="New Peak definition" color="teal" />
            <q-checkbox size="md" v-model="re_analyse_selection" val="new_std" label="New Standard Curve" color="orange" />
          </div>
          <q-btn icon="update" color="primary" label="Re-analyse" @click="reAnalysis" />
        </div>
      </div>
    </q-card-section>

    <!-- Content -->
    <q-card-section>
      <peakSetting ref="peakSettingRef" @update_PeakSelectRange="update_PeakSelectRange"></peakSetting>
    </q-card-section>
  </q-card>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { useStore } from 'vuex';
import peakSetting from '@/components/SMAImportViewComp/peakSetting.vue';

// 定義 emits
const emit = defineEmits(['reAnalysis']);

// 取得 store
const store = useStore();

// 重新分析選項
const re_analyse_selection = ref(['new_std']);

// 取得 peakSettingRef
const peakSettingRef = ref(null);

// 重新分析
function reAnalysis() {
  emit('reAnalysis');
}

// 將 re_analyse_selection 存到 store
function saveReAnalyseSelection() {
  const copy_of_re_analyse_selection = JSON.parse(JSON.stringify(re_analyse_selection.value));
  store.commit("analysis_setting/saveReAnalyseSelection", copy_of_re_analyse_selection);
}

// 更新 Peak 選擇範圍
function update_PeakSelectRange() {
  if (!re_analyse_selection.value.includes('new_peak')) {
    re_analyse_selection.value.push('new_peak');
  }
}

function updatePeakSettings(newPeakSettings){
  peakSettingRef.value.update_current_settings(newPeakSettings);
}

// Expose
defineExpose({
  updatePeakSettings
});

// 掛載時
onMounted(() => {
  // 初始化時將 re_analyse_selection 存到 store
  saveReAnalyseSelection();
});

// 監聽 re_analyse_selection 的變化
watch(re_analyse_selection, saveReAnalyseSelection, { deep: true });
</script>
