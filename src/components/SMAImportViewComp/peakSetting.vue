<template>
  <!-- SMN1/2 Peak Definition -->
  <q-expansion-item label="Peak Range + RFU Threshold" icon="category" class="bg-grey-1" header-style="font-size: 18px; font-weight: bold; background-color: #f5f5f5;" style="padding-bottom: 10px;">
    <div class="row q-ml-md" style="margin-block: 10px; display: flex; flex-direction: row; align-items: center; justify-content: space-between;">
      <span class="text-h6 text-blue-grey-5">SMN1 Peak Definition</span>
      <div>
        <q-btn icon="rule" color="green-7" glossy label="Apply" style="margin-right: 20px;" @click="applySettings" />
        <q-btn icon="history" color="brown-5" glossy label="Reset" style="margin-right: 20px;" @click="resetSettings" />
      </div>
    </div>
    <div class="row q-ml-md" style="display: flex; flex-direction: row; align-items: center; justify-content: space-between; margin-block: 20px; margin-inline: 20px; border-bottom: 1px solid #e0e0e0;" v-for="peak in ['internalControlPeak', 'targetPeak']" :key="peak">
      <!-- 理論值 -->
      <div class="row setting-block">
        <span class="text-subtitle2" style="font-size: 18px;" v-if="peak == 'internalControlPeak'">IC Peak</span>
        <span class="text-subtitle2" style="font-size: 18px;" v-else-if="peak == 'targetPeak'">TG Peak</span>
        <span class="text-subtitle2" style="margin-left: 15px; font-size: 18px;">理論值</span>
        <q-input v-model="currentSettings.smn1[peak].Peak_size" type="number" filled style="max-width: 80px; margin-left: 10px; font-size: 18px;" dense />
        <span class="text-subtitle2" style="margin-left: 15px; font-size: 18px;">bp</span>
      </div>
      <!-- 區間 -->
      <div class="row setting-block">
        <span class="text-subtitle2" style="margin-left: 15px; font-size: 18px;">區間</span>
        <div class="row" style="display: flex; flex-direction: column; align-items: center; margin-inline: 10px;">
          <div class="row" style="display: flex; flex-direction: row; align-items: center;">
            <q-icon name="add" style="font-size: 18px; margin-left: 5px;" />
            <q-input v-model="currentSettings.smn1[peak].Positive_range" type="number" filled style="max-width: 70px; margin-left: 10px; margin-block: 10px; font-size: 18px;" dense />
            <span class="text-subtitle2" style="margin-left: 15px; font-size: 18px;">%</span>
          </div>
          <div class="row" style="display: flex; flex-direction: row; align-items: center; margin-left: 5px;">
            <q-icon name="remove" style="font-size: 16px;" />
            <q-input v-model="currentSettings.smn1[peak].Negative_range" type="number" filled style="max-width: 70px; margin-left: 10px; margin-block: 10px; font-size: 18px;" dense />
            <span class="text-subtitle2" style="margin-left: 15px; font-size: 18px;">%</span>
          </div>
        </div>
      </div>
      <!-- 計算後範圍 -->
      <div class="row setting-block">
        <div class="row" style="display: flex; flex-direction: column; align-items: center; margin-inline: 10px;">
          <div class="row" style="display: flex; flex-direction: row; align-items: center;">
            <span class="text-subtitle2" style="margin-left: 15px; font-size: 18px;">Max</span>
            <q-input v-model="currentSettings.smn1[peak].peak_select_range.max" type="number" filled style="max-width: 80px; margin-left: 10px; margin-block: 10px; font-size: 18px;" dense readonly/>
            <span class="text-subtitle2" style="margin-left: 15px; font-size: 18px;">bp</span>
          </div>
          <div class="row" style="display: flex; flex-direction: row; align-items: center; margin-left: 4px;">
            <span class="text-subtitle2" style="margin-left: 15px; font-size: 18px;">Min</span>
            <q-input v-model="currentSettings.smn1[peak].peak_select_range.min" type="number" filled style="max-width: 80px; margin-left: 10px; margin-block: 10px; font-size: 18px;" dense readonly/>
            <span class="text-subtitle2" style="margin-left: 15px; font-size: 18px;">bp</span>
          </div>
        </div>
      </div>
      <!-- RFU Threshold -->
      <div class="row setting-block">
        <span class="text-subtitle2" style="margin-left: 15px; font-size: 18px;">RFU Threshold</span>
        <q-input v-model="currentSettings.smn1[peak].RFU_threshold" type="number" filled style="max-width: 80px; margin-left: 10px; font-size: 18px;" dense step="0.1" />
      </div>
      <!-- 條件範圍 -->
      <div class="row setting-block">
        <span class="text-subtitle2" style="margin-left: 15px; font-size: 18px;">範圍內至少要有</span>
        <q-input v-model="currentSettings.smn1[peak].Min_peak_count" type="number" filled style="max-width: 60px; margin-left: 10px; font-size: 18px;" dense />
        <span class="text-subtitle2" style="margin-left: 15px; font-size: 18px;">個 Peak </span>
      </div>
    </div>
    <div class="row q-ml-md" style="margin-block: 10px;">
      <span class="text-h6 text-blue-grey-5">SMN2 Peak Definition</span>
    </div>
    <div class="row q-ml-md" style="display: flex; flex-direction: row; align-items: center; justify-content: space-between; margin-block: 20px; margin-inline: 20px; border-bottom: 1px solid #e0e0e0;">
      <!-- 理論值 -->
      <div class="row setting-block">
        <span class="text-subtitle2" style="font-size: 18px;">理論值</span>
        <div class="row" style="display: flex; flex-direction: column; align-items: center; margin-inline: 10px;">
          <div class="row" style="display: flex; flex-direction: row; align-items: center;">
            <span class="text-subtitle2" style="margin-left: 15px; font-size: 18px;">TG Peak</span>
            <q-input v-model="currentSettings.smn2.peak_condition.target_size" type="number" filled style="max-width: 80px; margin-left: 10px; margin-block: 10px; font-size: 18px;" dense />
            <span class="text-subtitle2" style="margin-left: 15px; font-size: 18px;">bp</span>
          </div>
          <div class="row" style="display: flex; flex-direction: row; align-items: center;">
            <span class="text-subtitle2" style="margin-left: 15px; font-size: 18px;">IC Peak</span>
            <q-input v-model="currentSettings.smn2.peak_condition.internal_ctrl_size" type="number" filled style="max-width: 80px; margin-left: 10px; margin-block: 10px; font-size: 18px;" dense />
            <span class="text-subtitle2" style="margin-left: 15px; font-size: 18px;">bp</span>
          </div>
        </div>
      </div>
      <!-- 區間 -->
      <div class="row setting-block">
        <span class="text-subtitle2" style="margin-left: 15px; font-size: 18px;">區間</span>
        <div class="row" style="display: flex; flex-direction: column; align-items: center; margin-inline: 10px;">
          <div class="row" style="display: flex; flex-direction: row; align-items: center;">
            <q-icon name="add" style="font-size: 18px; margin-left: 5px;" />
            <q-input v-model="currentSettings.smn2.peak_condition.Positive_range" type="number" filled style="max-width: 70px; margin-left: 10px; margin-block: 10px; font-size: 18px;" dense />
            <span class="text-subtitle2" style="margin-left: 15px; font-size: 18px;">%</span>
          </div>
          <div class="row" style="display: flex; flex-direction: row; align-items: center; margin-left: 5px;">
            <q-icon name="remove" style="font-size: 16px;" />
            <q-input v-model="currentSettings.smn2.peak_condition.Negative_range" type="number" filled style="max-width: 70px; margin-left: 10px; margin-block: 10px; font-size: 18px;" dense />
            <span class="text-subtitle2" style="margin-left: 15px; font-size: 18px;">%</span>
          </div>
        </div>
      </div>
      <!-- 計算後範圍 -->
      <div class="row setting-block">
        <div class="row" style="display: flex; flex-direction: column; align-items: center; margin-inline: 10px;">
          <div class="row" style="display: flex; flex-direction: row; align-items: center;">
            <span class="text-subtitle2" style="margin-left: 15px; font-size: 18px;">Max</span>
            <q-input v-model="currentSettings.smn2.peak_condition.peak_select_range.max" type="number" filled style="max-width: 80px; margin-left: 10px; margin-block: 10px; font-size: 18px;" dense readonly/>
            <span class="text-subtitle2" style="margin-left: 15px; font-size: 18px;">bp</span>
          </div>
          <div class="row" style="display: flex; flex-direction: row; align-items: center; margin-left: 4px;">
            <span class="text-subtitle2" style="margin-left: 15px; font-size: 18px;">Min</span>
            <q-input v-model="currentSettings.smn2.peak_condition.peak_select_range.min" type="number" filled style="max-width: 80px; margin-left: 10px; margin-block: 10px; font-size: 18px;" dense readonly/>
            <span class="text-subtitle2" style="margin-left: 15px; font-size: 18px;">bp</span>
          </div>
        </div>
      </div>
      <!-- RFU Threshold -->
      <div class="row setting-block">
        <span class="text-subtitle2" style="margin-left: 15px; font-size: 18px;">RFU Threshold</span>
        <q-input v-model="currentSettings.smn2.peak_condition.RFU_threshold" type="number" filled style="max-width: 80px; margin-left: 10px; font-size: 18px;" dense step="0.1" />
      </div>
      <!-- 條件範圍 -->
      <div class="row setting-block">
        <span class="text-subtitle2" style="margin-left: 15px; font-size: 18px;">範圍內至少要有</span>
        <q-input v-model="currentSettings.smn2.peak_condition.Min_peak_count" type="number" filled style="max-width: 60px; margin-left: 10px; font-size: 18px;" dense />
        <span class="text-subtitle2" style="margin-left: 15px; font-size: 18px;">個 Peak </span>
      </div>
    </div>
  </q-expansion-item>
</template>

<script>
import { ref, watch } from 'vue';
import { useStore } from 'vuex';
import _ from 'lodash';

// 預設設定
const defaultSettings = {
  smn1:{
    internalControlPeak: {
      Peak_size: 241,
      Positive_range: 10,
      Negative_range: 10,
      RFU_threshold: 1,
      Min_peak_count: 1,
      peak_select_range: {max: 0, min: 0},
    },
    targetPeak: {
      Peak_size: 123,
      Positive_range: 10,
      Negative_range: 10,
      RFU_threshold: 1,
      Min_peak_count: 1,
      peak_select_range: {max: 0, min: 0},
    }
  },
  smn2: {
    peak_condition: {
      internal_ctrl_size: 340,
      target_size: 306,
      Positive_range: 10,
      Negative_range: 10,
      RFU_threshold: 1,
      Min_peak_count: 2,
      peak_select_range: {max: 0, min: 0},
    }
  }
}

// 複製設定
const settingBackup = JSON.parse(JSON.stringify(defaultSettings));

// 目前設定
const currentSettings = ref(defaultSettings);

// Functions
function update_PeakSelectRange(value,factors) {
  const range = {
    max: Math.round(parseInt(value) + parseInt(value) * factors.max),
    min: Math.round(parseInt(value) - parseInt(value) * factors.min),
  }
  return range;
}

export default {
  setup(props, {emit}) {

    // 取得 store
    const $store = useStore();

    // 更新 SMN1 的 Peak 選擇範圍
    function update_SMN1_PeakSelectRange() {
      const smn1_IC_Peak_size = currentSettings.value.smn1.internalControlPeak.Peak_size;
      const smn1_IC_factors = {min: currentSettings.value.smn1.internalControlPeak.Negative_range * 0.01, max: currentSettings.value.smn1.internalControlPeak.Positive_range * 0.01};
      const newRange = update_PeakSelectRange(smn1_IC_Peak_size, smn1_IC_factors);
      const smn1_Tg_Peak_size = currentSettings.value.smn1.targetPeak.Peak_size;
      const smn1_Tg_factors = {min: currentSettings.value.smn1.targetPeak.Negative_range * 0.01, max: currentSettings.value.smn1.targetPeak.Positive_range * 0.01};
      const newTgRange = update_PeakSelectRange(smn1_Tg_Peak_size, smn1_Tg_factors);
      currentSettings.value.smn1.internalControlPeak.peak_select_range = newRange;
      currentSettings.value.smn1.targetPeak.peak_select_range = newTgRange;
      saveCurrentPeakSettings();
      emit('update_PeakSelectRange', currentSettings.value);
    }

    // 更新 SMN2 的 Peak 選擇範圍
    function update_SMN2_PeakSelectRange() {
      const smn2_IC_Peak_size = currentSettings.value.smn2.peak_condition.internal_ctrl_size;
      const smn2_TG_Peak_size = currentSettings.value.smn2.peak_condition.target_size;
      const smn2_factors = {min: currentSettings.value.smn2.peak_condition.Negative_range * 0.01, max: currentSettings.value.smn2.peak_condition.Positive_range * 0.01};
      const range_max = smn2_TG_Peak_size > smn2_IC_Peak_size ?
        Math.round(parseInt(smn2_TG_Peak_size) + parseInt(smn2_TG_Peak_size) * smn2_factors.max) :
        Math.round(parseInt(smn2_IC_Peak_size) + parseInt(smn2_IC_Peak_size) * smn2_factors.max);
      const range_min = smn2_TG_Peak_size < smn2_IC_Peak_size ?
        Math.round(parseInt(smn2_TG_Peak_size) - parseInt(smn2_TG_Peak_size) * smn2_factors.min) :
        Math.round(parseInt(smn2_IC_Peak_size) - parseInt(smn2_IC_Peak_size) * smn2_factors.min);
      const smn2_range = {max: range_max, min: range_min};
      currentSettings.value.smn2.peak_condition.peak_select_range = smn2_range;
      saveCurrentPeakSettings();
      emit('update_PeakSelectRange', currentSettings.value);
    }

    // 重置設定
    function resetSettings() {
      currentSettings.value.smn1.internalControlPeak.Peak_size = settingBackup.smn1.internalControlPeak.Peak_size;
      currentSettings.value.smn1.internalControlPeak.Positive_range = settingBackup.smn1.internalControlPeak.Positive_range;
      currentSettings.value.smn1.internalControlPeak.Negative_range = settingBackup.smn1.internalControlPeak.Negative_range;
      currentSettings.value.smn1.internalControlPeak.RFU_threshold = settingBackup.smn1.internalControlPeak.RFU_threshold;
      currentSettings.value.smn1.internalControlPeak.Min_peak_count = settingBackup.smn1.internalControlPeak.Min_peak_count;
      currentSettings.value.smn1.targetPeak.Peak_size = settingBackup.smn1.targetPeak.Peak_size;
      currentSettings.value.smn1.targetPeak.Positive_range = settingBackup.smn1.targetPeak.Positive_range;
      currentSettings.value.smn1.targetPeak.Negative_range = settingBackup.smn1.targetPeak.Negative_range;
      currentSettings.value.smn1.targetPeak.RFU_threshold = settingBackup.smn1.targetPeak.RFU_threshold;
      currentSettings.value.smn1.targetPeak.Min_peak_count = settingBackup.smn1.targetPeak.Min_peak_count;
      currentSettings.value.smn2.peak_condition.internal_ctrl_size = settingBackup.smn2.peak_condition.internal_ctrl_size;
      currentSettings.value.smn2.peak_condition.target_size = settingBackup.smn2.peak_condition.target_size;
      currentSettings.value.smn2.peak_condition.Positive_range = settingBackup.smn2.peak_condition.Positive_range;
      currentSettings.value.smn2.peak_condition.Negative_range = settingBackup.smn2.peak_condition.Negative_range;
      currentSettings.value.smn2.peak_condition.RFU_threshold = settingBackup.smn2.peak_condition.RFU_threshold;
      currentSettings.value.smn2.peak_condition.Min_peak_count = settingBackup.smn2.peak_condition.Min_peak_count;
      update_SMN1_PeakSelectRange();
      update_SMN2_PeakSelectRange();
    }

    // 應用設定
    function applySettings() {
      emit('apply_PeakSelectRange');
    }

    // 更新 current settings
    function update_current_settings(newSettings) {
      currentSettings.value.smn1.internalControlPeak.Peak_size = newSettings.smn1.internalControlPeak.Peak_size;
      currentSettings.value.smn1.internalControlPeak.Positive_range = newSettings.smn1.internalControlPeak.Positive_range;
      currentSettings.value.smn1.internalControlPeak.Negative_range = newSettings.smn1.internalControlPeak.Negative_range;
      currentSettings.value.smn1.internalControlPeak.RFU_threshold = newSettings.smn1.internalControlPeak.RFU_threshold;
      currentSettings.value.smn1.internalControlPeak.Min_peak_count = newSettings.smn1.internalControlPeak.Min_peak_count;
      currentSettings.value.smn1.targetPeak.Peak_size = newSettings.smn1.targetPeak.Peak_size;
      currentSettings.value.smn1.targetPeak.Positive_range = newSettings.smn1.targetPeak.Positive_range;
      currentSettings.value.smn1.targetPeak.Negative_range = newSettings.smn1.targetPeak.Negative_range;
      currentSettings.value.smn1.targetPeak.RFU_threshold = newSettings.smn1.targetPeak.RFU_threshold;
      currentSettings.value.smn1.targetPeak.Min_peak_count = newSettings.smn1.targetPeak.Min_peak_count;
      currentSettings.value.smn2.peak_condition.internal_ctrl_size = newSettings.smn2.peak_condition.internal_ctrl_size;
      currentSettings.value.smn2.peak_condition.target_size = newSettings.smn2.peak_condition.target_size;
      currentSettings.value.smn2.peak_condition.Positive_range = newSettings.smn2.peak_condition.Positive_range;
      currentSettings.value.smn2.peak_condition.Negative_range = newSettings.smn2.peak_condition.Negative_range;
      currentSettings.value.smn2.peak_condition.RFU_threshold = newSettings.smn2.peak_condition.RFU_threshold;
      currentSettings.value.smn2.peak_condition.Min_peak_count = newSettings.smn2.peak_condition.Min_peak_count;
      update_SMN1_PeakSelectRange();
      update_SMN2_PeakSelectRange();
    }

    // 將 current settings 存到 store
    function saveCurrentPeakSettings() {
      const copy_of_currentSettings = JSON.parse(JSON.stringify(currentSettings.value));
      $store.commit("SMAv4_analysis_data/saveSMAv4ReanalysePeakSettings", copy_of_currentSettings);
    }

    // 更新 SMN1 的 Peak 選擇範圍
    update_SMN1_PeakSelectRange();

    // 更新 SMN2 的 Peak 選擇範圍
    update_SMN2_PeakSelectRange();


    // 複製初始值
    let previousValue_smn1 = _.cloneDeep(currentSettings.value.smn1);
    let previousValue_smn2 = _.cloneDeep(currentSettings.value.smn2);

    // 監聽 currentSettings 的變化
    watch(currentSettings.value.smn1, (newVal) => {
      if (JSON.stringify(newVal) !== JSON.stringify(previousValue_smn1)) {
        update_SMN1_PeakSelectRange();
        previousValue_smn1 = _.cloneDeep(newVal);
      }
    }, { deep: true });
    watch(currentSettings.value.smn2, (newVal) => {
      if (JSON.stringify(newVal) !== JSON.stringify(previousValue_smn2)) {
        update_SMN2_PeakSelectRange();
        previousValue_smn2 = _.cloneDeep(newVal);
      }
    }, { deep: true });

    return {
      currentSettings,
      settingBackup,
      resetSettings,
      applySettings,
      saveCurrentPeakSettings,
      update_SMN1_PeakSelectRange,
      update_SMN2_PeakSelectRange,
      update_current_settings,
    };

  },
};
</script>

<style scoped>
.setting-block {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-inline: 5px;
}
</style>
