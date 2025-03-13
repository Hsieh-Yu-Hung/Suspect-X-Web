<template>
  <q-card bordered style="width: 100%;" :style="{ display: showResult ? 'block' : 'none' }">
    <q-card-section>

      <!-- 標題 -->
      <div class="text-h5 text-uppercase text-bold text-blue-grey-7">
        Parameters Settings
      </div>

      <!-- SMA 設定是一個表單 -->
      <div style="padding-top: 1.5em;">
        <q-form class="q-gutter-sm col" @reset="reset" @submit="reAnalysis">

          <!-- 設定有效 CT 值範圍 -->
          <div class="row q-gutter-x-lg">

            <!-- 設定有效 CT 值範圍下限 -->
            <div class="q-gutter-x-md flex items-center">
              <span class="text-grey-7 text-subtitle1 text-bold">有效 CT 值範圍：</span>
              <q-input
                v-model.number="ValidCTRange.min"
                type="number"
                color="deep-orange-6"
                dense
                filled
                class="col-4"
                input-class="text-center"
                style="margin-left: 6px; width: 200px;"
                :min="0"
              >
              </q-input>
            </div>

            <!-- 設定有效 CT 值範圍分隔符號 -->
            <div class="flex items-center" style="margin-inline: 58px;">
              <span class="text-grey-7 text-body1 text-bold">到</span>
            </div>

            <!-- 設定有效 CT 值範圍上限 -->
            <div class="q-gutter-x-md flex items-center">
              <q-input
                v-model.number="ValidCTRange.max"
                type="number"
                color="deep-orange-6"
                dense
                filled
                class="col-3"
                input-class="text-center"
                style="margin-left: 14px; width: 200px;"
                :min="ValidCTRange.min"
              />
            </div>

          </div>

          <!-- 設定 Z480 校正值 -->
          <div class="row flex items-center q-gutter-x-lg">

            <!-- 設定 SMN1 校正值 -->
            <div class="q-gutter-x-md flex items-center">
              <span class="text-grey-7 text-subtitle1 text-bold">SMN1 校正值：</span>
              <q-input
                v-model.number="Z480_CT_CORRECTION.smn1"
                mask="#.##"
                fill-mask="0"
                reverse-fill-mask
                color="deep-orange-6"
                dense
                filled
                class="col-4"
                input-class="text-center"
                style="margin-left: 17px; width: 200px;"
              >
              </q-input>
            </div>

            <!-- 設定 SMN2 校正值 -->
            <div class="q-gutter-x-md flex items-center">
              <span class="text-grey-7 text-subtitle1 text-bold">SMN2 校正值：</span>
              <q-input
                v-model.number="Z480_CT_CORRECTION.smn2"
                mask="#.##"
                fill-mask="0"
                reverse-fill-mask
                color="deep-orange-6"
                dense
                filled
                class="col-4 q-ml-xl q-mr-lg"
                input-class="text-center"
                style="margin-left: 17px; width: 200px;"
              >
              </q-input>
            </div>

          </div>

          <!-- 允收範圍標題 -->
          <div class="q-gutter-x-sm row">
            <span class="text-grey-7 text-subtitle1 text-bold">允收範圍：</span>
          </div>

          <!-- 允收範圍 SMN1/SMN2 -->
          <div class="row q-pl-xl q-pr-xl">

            <!-- 允收範圍 SMN1 -->
            <div class="col" style="margin-bottom: 2.5em;">
              <div class="text-teal-7 text-subtitle2 text-bold">
                SMN1
              </div>
              <div class="text-grey-7 text-caption">
                SC1: RNP CT <b>{{ SC_CT_VALUE.SC1.rnp }}</b> - SMN1 CT <b>{{ SC_CT_VALUE.SC1.smn1 }}</b> = <b>{{ deltaCT.sc1.smn1 }}</b>
              </div>
              <div class="text-grey-7 text-caption">
                SC2: RNP CT <b>{{ SC_CT_VALUE.SC2.rnp }}</b> - SMN1 CT <b>{{ SC_CT_VALUE.SC2.smn1 }}</b> = <b>{{ deltaCT.sc2.smn1 }}</b>
              </div>
              <q-range
                v-model="ACCEPTANCE_RANGE.smn1"
                :min="0"
                :max="200"
                label-always
                color="teal-7"
                drag-range
                marker-labels
                switch-label-side
                :left-label-value="ACCEPTANCE_RANGE.smn1.min/100"
                :right-label-value="ACCEPTANCE_RANGE.smn1.max/100"
              >
                <template v-slot:marker-label-group="{ markerList }">
                  <div v-for="val in markerList" :key="val">
                    <div
                      v-if="val.index === SMN1_SMN2_DIFFERENCE.smn1"
                      :class="markerList[val.index].classes"
                      :style="markerList[val.index].style"
                    >
                      <q-icon class="text-deep-orange-8 full-width" name="arrow_drop_up" size="md" />
                      <div class="text-grey-7 text-caption" style="white-space: nowrap;">
                        <b>Diff: abs(</b> <b>{{ deltaCT.sc1.smn1 }}</b> - <b>{{ deltaCT.sc2.smn1 }}</b> <b>)</b> = <b>{{ Math.abs(deltaCT.sc1.smn1 - deltaCT.sc2.smn1).toFixed(2) }}</b>
                      </div>
                    </div>
                  </div>
                </template>
              </q-range>
            </div>

            <!-- 允收範圍 SMN2 -->
            <div class="col q-pl-xl" style="margin-bottom: 2.5em;">
              <div class="text-lime-10 text-subtitle2 text-bold">
                SMN2
              </div><div class="text-grey-7 text-caption">
                SC1: RNP CT <b>{{ SC_CT_VALUE.SC1.rnp }}</b> - SMN2 CT <b>{{ SC_CT_VALUE.SC1.smn2 }}</b> = <b>{{ deltaCT.sc1.smn2 }}</b>
              </div>
              <div class="text-grey-7 text-caption">
                SC2: RNP CT <b>{{ SC_CT_VALUE.SC2.rnp }}</b> - SMN2 CT <b>{{ SC_CT_VALUE.SC2.smn2 }}</b> = <b>{{ deltaCT.sc2.smn2 }}</b>
              </div>
              <q-range
                v-model="ACCEPTANCE_RANGE.smn2"
                :min="0"
                :max="200"
                label-always
                color="lime-9"
                drag-range
                marker-labels
                switch-label-side
                :left-label-value="ACCEPTANCE_RANGE.smn2.min/100"
                :right-label-value="ACCEPTANCE_RANGE.smn2.max/100"
              >
                <template v-slot:marker-label-group="{ markerList }">
                  <div v-for="val in markerList" :key="val">
                    <div
                      v-if="val.index === SMN1_SMN2_DIFFERENCE.smn2"
                      :class="markerList[val.index].classes"
                      :style="markerList[val.index].style"
                    >
                      <q-icon class="text-deep-orange-8 full-width" name="arrow_drop_up" size="md" />
                      <div class="text-grey-7 text-caption" style="white-space: nowrap;">
                        <b>Diff: abs(</b> <b>{{ deltaCT.sc1.smn2 }}</b> - <b>{{ deltaCT.sc2.smn2 }}</b> <b>)</b> = <b>{{ Math.abs(deltaCT.sc1.smn2 - deltaCT.sc2.smn2).toFixed(2) }}</b>
                      </div>
                    </div>
                  </div>
                </template>
              </q-range>
            </div>

          </div>

          <!-- 判定範圍標題 SMN1 -->
          <div class="q-gutter-x-sm row">
            <span class="text-grey-7 text-subtitle1 text-bold">SMN1 判定範圍 (RNP-SMN1)：</span>
          </div>

          <!-- 判定範圍 SMN1 -->
          <div class="row" style="margin-block: 1.2em;">

            <!-- 間距比例輸入 -->
            <q-input
              type="number"
              color="deep-orange-6"
              dense
              outlined
              stack-label
              class="q-ml-xl col-1"
              input-class="text-center"
              suffix="%"
              label="間距比例："
              style="width: 125px;"
              v-model="INTERVAL_RATIO.smn1"
            ></q-input>

            <!-- 判定儀器選擇-QS3 -->
            <q-radio
              v-model="smn1_analyzer_version"
              class="text-overline text-blue-7"
              color="blue-7"
              checked-icon="task_alt"
              :val="ANALYZER_VERSION.QS3"
              label="Analyzer QS3"
              unchecked-icon="panorama_fish_eye"
            />

            <!-- 判定儀器選擇-QS3L -->
            <q-radio
              v-model="smn1_analyzer_version"
              class="text-overline text-blue-10"
              color="blue-10"
              checked-icon="task_alt"
              :val="ANALYZER_VERSION.QS3L"
              label="Analyzer QS3L"
              unchecked-icon="panorama_fish_eye"
            />

            <!-- 判定儀器選擇-Z480 -->
            <q-radio
              v-model="smn1_analyzer_version"
              class="text-overline text-green-8"
              color="green-8"
              checked-icon="task_alt"
              :val="ANALYZER_VERSION.Z480"
              label="Analyzer Z480"
              unchecked-icon="panorama_fish_eye"
            />

            <!-- 判定儀器選擇-Custom -->
            <q-radio
              v-model="smn1_analyzer_version"
              class="text-overline text-purple-6"
              color="purple-6"
              checked-icon="task_alt"
              :val="ANALYZER_VERSION.CUSTOM"
              label="Custom"
              unchecked-icon="panorama_fish_eye"
            />
          </div>

          <!-- 判定範圍 SMN1 滑桿 -->
          <div class="row q-pl-xl q-pr-xl">
            <CustomSlider
              :pointData="SMN1_RANGE_SLIDER_Data"
              :labelColor="smn1_slider_label_color"
              ref="smn1_slider"
              name="SMN1_SLIDER"
            />
          </div>

          <!-- 判定範圍標題 SMN2 -->
          <div class="q-gutter-x-sm row">
            <span class="text-grey-7 text-subtitle1 text-bold">SMN2 判定範圍 (RNP-SMN2)：</span>
          </div>

          <!-- 判定範圍 SMN2 -->
          <div class="row" style="margin-block: 1.2em;">

            <!-- 間距比例輸入 -->
            <q-input
              v-model="INTERVAL_RATIO.smn2"
              type="number"
              color="deep-orange-6"
              dense
              outlined
              stack-label
              class="q-ml-xl col-1"
              input-class="text-center"
              suffix="%"
              label="間距比例："
              style="width: 125px;"
            ></q-input>

            <!-- 判定儀器選擇-QS3 -->
            <q-radio
              v-model="smn2_analyzer_version"
              class="text-overline text-blue-7"
              color="blue-7"
              checked-icon="task_alt"
              :val="ANALYZER_VERSION.QS3"
              label="Analyzer QS3"
              unchecked-icon="panorama_fish_eye"
            />

            <!-- 判定儀器選擇-QS3L -->
            <q-radio
              v-model="smn2_analyzer_version"
              class="text-overline text-blue-10"
              color="blue-10"
              checked-icon="task_alt"
              :val="ANALYZER_VERSION.QS3L"
              label="Analyzer QS3L"
              unchecked-icon="panorama_fish_eye"
            />

            <!-- 判定儀器選擇-Z480 -->
            <q-radio
              v-model="smn2_analyzer_version"
              class="text-overline text-green-8"
              color="green-8"
              checked-icon="task_alt"
              :val="ANALYZER_VERSION.Z480"
              label="Analyzer Z480"
              unchecked-icon="panorama_fish_eye"
            />

            <!-- 判定儀器選擇-Custom -->
            <q-radio
              v-model="smn2_analyzer_version"
              class="text-overline text-purple-6"
              color="purple-6"
              checked-icon="task_alt"
              :val="ANALYZER_VERSION.CUSTOM"
              label="Custom"
              unchecked-icon="panorama_fish_eye"
            />
          </div>

          <!-- 判定範圍 SMN2 滑桿 -->
          <div class="row q-pl-xl q-pr-xl">
            <CustomSlider
              :pointData="SMN2_RANGE_SLIDER_Data"
              :labelColor="smn2_slider_label_color"
              ref="smn2_slider"
              name="SMN2_SLIDER"
            />
          </div>

          <!-- 重置和重新分析按鈕 -->
          <div class="row q-mt-lg justify-end">
            <q-btn label="Reset" icon="refresh" type="reset" flat color="blue-grey-7" />
            <q-btn label="Re-Analysis" type="submit" class="q-ml-lg" color="blue-grey-7" />
          </div>

        </q-form>
      </div>

    </q-card-section>
  </q-card>
</template>

<script setup>
// 導入模組
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import { useQuasar, QSpinnerFacebook } from 'quasar';
import { v4 as uuidv4 } from 'uuid';

// 導入元件
import CustomSlider from '@/components/CustomSlider.vue';

// 導入模組 composable
import { submitWorkflow } from '@/composables/submitWorkflow';
import { setAnalysisID } from '@/composables/checkAnalysisStatus';
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo.js';
import { ANALYSIS_RESULT, EXPORT_RESULT, update_userAnalysisData, simplifyFilePath } from '@/firebase/firebaseDatabase';
import { getCurrentDisplayAnalysisID, getCurrentAnalysisResult } from '@/composables/checkAnalysisStatus.js';

// 使用者身份
const { login_status } = updateGetUserInfo();

// 取得 store, quasar, router
const store = useStore();
const $q = useQuasar();
const router = useRouter();

// 使用者身份
const is_login = ref(false);
const user_info = ref(null);

// 保存當前分析結果
const showResult = ref(true);
const currentAnalysisResult = ref(null);
const currentSettingProps = ref(null);
const currentDisplayAnalysis = ref({
  analysis_uuid: '',
  analysis_name: '',
});

/* 定義常數 */

// 分析版本 (QS3, QS3L, Z480, Custom)
const ANALYZER_VERSION = {
  QS3: 'QS3',
  QS3L: 'QS3L',
  Z480: 'Z480',
  CUSTOM: 'Custom',
};

// 預設有效 CT 值範圍
const DEFAULT_VALID_CT_RANGE = { min: 0, max: 30 };

// 有效 CT 值範圍
const ValidCTRange = ref(DEFAULT_VALID_CT_RANGE);

/* 定義變數 */

// 間距比例
const INTERVAL_RATIO = ref({ smn1: 0, smn2: 0 });
let INTERVAL_RATIO_Backup = JSON.parse(JSON.stringify(INTERVAL_RATIO.value));

// 選用分析版本
const smn1_analyzer_version = ref(ANALYZER_VERSION.QS3);
const smn2_analyzer_version = ref(ANALYZER_VERSION.QS3);

// Z480 CT 校正值
const Z480_CT_CORRECTION = { smn1: 0, smn2: 0 };

// SC 的 CT 值
const SC_CT_VALUE = ref({
  SC1: { rnp: 0, smn1: 0, smn2: 0 },
  SC2: { rnp: 0, smn1: 0, smn2: 0 },
});

// 計算 SC 的 delta CT 值
const deltaCT = computed(() => {
  const sc1 = {
    smn1: Math.abs(SC_CT_VALUE.value.SC1.rnp - SC_CT_VALUE.value.SC1.smn1).toFixed(2),
    smn2: Math.abs(SC_CT_VALUE.value.SC1.rnp - SC_CT_VALUE.value.SC1.smn2).toFixed(2),
  };
  const sc2 = {
    smn1: Math.abs(SC_CT_VALUE.value.SC2.rnp - SC_CT_VALUE.value.SC2.smn1).toFixed(2),
    smn2: Math.abs(SC_CT_VALUE.value.SC2.rnp - SC_CT_VALUE.value.SC2.smn2).toFixed(2),
  };
  return { sc1: sc1, sc2: sc2 };
});

// 計算允收範圍
const ACCEPTANCE_RANGE = ref({
  smn1: { min: 0, max: 0 },
  smn2: { min: 0, max: 0 },
});

// Standard control SMN1/SMN2 的差值
const SMN1_SMN2_DIFFERENCE = { smn1: 0, smn2: 0 };

const DEFAULT_RANGE_SLIDER_DATA = [
  {
    point: 0,
    knob: false,
    label: '0N',
  },
  {
    point: 1,
    knob: true,
    label: '1N',
  },
  {
    point: 2,
    knob: true,
    label: '2N',
  },
  {
    point: 3,
    knob: true,
    label: '3N',
  },
  {
    point: 4,
    knob: false,
    label: '4N',
  },
];

// SMN1 判定範圍滑桿
const SMN1_RANGE_SLIDER_Data = ref(DEFAULT_RANGE_SLIDER_DATA);

// SMN2 判定範圍滑桿
const SMN2_RANGE_SLIDER_Data = ref(DEFAULT_RANGE_SLIDER_DATA);

// 取得 SMN1 判定範圍滑桿資料
const used_SMN1_SLIDER_DATA = computed(() => {
  if (currentAnalysisResult.value) {
    switch (smn1_analyzer_version.value) {
      case ANALYZER_VERSION.QS3:
        if (!currentAnalysisResult.value.resultObj.V1.SMA_parameters) {
          return [];
        }
        return getRangeData(currentAnalysisResult.value.resultObj.V1.SMA_parameters.Threshold_Range.smn1);
      case ANALYZER_VERSION.QS3L:
        let qs3l_data = getRangeData(currentAnalysisResult.value.resultObj.V1.SMA_parameters.Threshold_Range.smn1);
        qs3l_data.forEach(item => {
          const value = currentAnalysisResult.value.resultObj.V1.SMA_parameters.Threshold_Range.smn1_restricted[item.label.toLowerCase()];
          item.var_value = value ? value.toFixed(2) : null;
        });
        return qs3l_data;
      case ANALYZER_VERSION.Z480:
        let z480_data = getRangeData(currentAnalysisResult.value.resultObj.V1.SMA_parameters.Threshold_Range.smn1);
        z480_data.forEach(item => {
          const value = currentAnalysisResult.value.resultObj.V1.SMA_parameters.Threshold_Range.smn1_restricted[item.label.toLowerCase()];
          item.var_value = value ? value.toFixed(2) : null;
        });
        return z480_data;
      case ANALYZER_VERSION.CUSTOM:
        if (!currentAnalysisResult.value.resultObj.V1.SMA_parameters) {
          return [];
        }
        return getRangeData(currentAnalysisResult.value.resultObj.V1.SMA_parameters.Threshold_Range.smn1);
      default:
        return [];
    }
  }
  return [];
});

// 取得 SMN2 判定範圍滑桿資料
const used_SMN2_SLIDER_DATA = computed(() => {
  if (currentAnalysisResult.value) {
    switch (smn2_analyzer_version.value) {
      case ANALYZER_VERSION.QS3:
        return getRangeData(currentAnalysisResult.value.resultObj.V1.SMA_parameters.Threshold_Range.smn2);
      case ANALYZER_VERSION.QS3L:
        if (!currentAnalysisResult.value.resultObj.V1.SMA_parameters) {
          return [];
        }
        let qs3l_data = getRangeData(currentAnalysisResult.value.resultObj.V1.SMA_parameters.Threshold_Range.smn2);
        qs3l_data.forEach(item => {
          const value = currentAnalysisResult.value.resultObj.V1.SMA_parameters.Threshold_Range.smn2_restricted[item.label.toLowerCase()];
          item.var_value = value ? value.toFixed(2) : null;
        });
        return qs3l_data;
      case ANALYZER_VERSION.Z480:
        let z480_data = getRangeData(currentAnalysisResult.value.resultObj.V1.SMA_parameters.Threshold_Range.smn2);
        z480_data.forEach(item => {
          const value = currentAnalysisResult.value.resultObj.V1.SMA_parameters.Threshold_Range.smn2_restricted[item.label.toLowerCase()];
          item.var_value = value ? value.toFixed(2) : null;
        });
        return z480_data;
      case ANALYZER_VERSION.CUSTOM:
        return getRangeData(currentAnalysisResult.value.resultObj.V1.SMA_parameters.Threshold_Range.smn2);
      default:
        return [];
    }
  }
  return [];
});

// 滑桿實體
const smn1_slider = ref(null);
const smn2_slider = ref(null);

// 滑桿標籤顏色
const smn1_slider_label_color = computed(() => getAnalyzerVersionLabelColor(smn1_analyzer_version.value));
const smn2_slider_label_color = computed(() => getAnalyzerVersionLabelColor(smn2_analyzer_version.value));

// 取得當前滑桿資料
const current_SMN1_Slider_data = computed(() => {
  if (smn1_slider.value) {
    return smn1_slider.value.getDisplayPointData();
  }
  return [];
});

const current_SMN2_Slider_data = computed(() => {
  if (smn2_slider.value) {
    return smn2_slider.value.getDisplayPointData();
  }
  return [];
});

// Database Path
const dbSMAResultPath = "sma_result";

// 當前的分析 ID
const currentAnalysisID = ref(null);

// 控制 Slider 是否更新
let flag = false;

/* Functions */

// 取得判定範圍滑桿資料
const getRangeData = (selected_range) => {
  return [
    {
      point: 0,
      var_value: 0,
      knob: false,
      label: '0N',
    },
    {
      point: selected_range['1n'].toFixed(2),
      var_value: selected_range['1n'].toFixed(2),
      knob: true,
      label: '1N',
    },
    {
      point: selected_range['2n'].toFixed(2),
      var_value: selected_range['2n'].toFixed(2),
      knob: true,
      label: '2N',
    },
    {
      point: selected_range['3n'].toFixed(2),
      var_value: selected_range['3n'].toFixed(2),
      knob: true,
      label: '3N',
    },
    {
      point: selected_range['4n'] ? selected_range['4n'].toFixed(2) : null,
      var_value: selected_range['4n'] ? selected_range['4n'].toFixed(2) : null,
      knob: false,
      label: '4N',
    },
  ];
};

// 取得 ANALYZER_VERSION 標籤顏色
function getAnalyzerVersionLabelColor(analyzerVersion) {
  switch (analyzerVersion) {
    case ANALYZER_VERSION.QS3:
      return 'rgba(10, 150, 255, 1)';
    case ANALYZER_VERSION.QS3L:
      return 'rgba(30, 75, 195, 1)';
    case ANALYZER_VERSION.Z480:
      return 'rgba(80, 175, 105, 1)';
    case ANALYZER_VERSION.CUSTOM:
      return 'rgba(165, 50, 225, 1)';
    default:
      return 'rgba(0, 0, 0, 1)';
  }
}

// 重置表單
function reset() {

  const getSMNVersion = store.getters["SMA_analysis_data/displaySMNVersion"];
  smn1_analyzer_version.value = getSMNVersion.smn1;
  smn2_analyzer_version.value = getSMNVersion.smn2;

  const getDistanceRatio = store.getters["SMA_analysis_data/distanceRatio"];
  INTERVAL_RATIO.value.smn1 = getDistanceRatio.smn1;
  INTERVAL_RATIO.value.smn2 = getDistanceRatio.smn2;

  flag = true;
  INTERVAL_RATIO_Backup = JSON.parse(JSON.stringify(INTERVAL_RATIO.value));
}

// 定義 SMA_RESULT
const SMA_RESULT = (analyzerVersion,SC1_Data, SC2_Data, NTC_Data, sampleDataList, SMA_parameters, resultList, inputObject) => {
  return {
    analyzerVersion,
    SC1_Data,
    SC2_Data,
    NTC_Data,
    sampleDataList,
    SMA_parameters,
    resultList,
    inputObject,
  }
}

// 重新分析
async function reAnalysis() {

  $q.loading.show({
    spinner: QSpinnerFacebook,
    spinnerColor: "deep-orange-6",
    spinnerSize: 100,
    message: "Analyzing...",
    messageColor: "white",
  });

  // 取得 Slider 的資料
  const smn1_slider_data = smn1_slider.value.getDisplayPointData();
  const smn2_slider_data = smn2_slider.value.getDisplayPointData();
  const SMN_Select_Range = {
    smn1: {
      "1n": parseFloat(smn1_slider_data.find(item => item.label === '1N').value),
      "2n": parseFloat(smn1_slider_data.find(item => item.label === '2N').value),
      "3n": parseFloat(smn1_slider_data.find(item => item.label === '3N').value),
    },
    smn2: {
      "1n": parseFloat(smn2_slider_data.find(item => item.label === '1N').value),
      "2n": parseFloat(smn2_slider_data.find(item => item.label === '2N').value),
      "3n": parseFloat(smn2_slider_data.find(item => item.label === '3N').value),
    },
  }

  // 搜集 parameters
  const parameters = {
    CT_Threshold_Range: {
      MIN: ValidCTRange.value.min,
      MAX: ValidCTRange.value.max,
    },
    SMN1_SC1_SC2_DIFF_Range: {
      MIN: ACCEPTANCE_RANGE.value.smn1.min / 100,
      MAX: ACCEPTANCE_RANGE.value.smn1.max / 100,
    },
    SMN2_SC1_SC2_DIFF_Range: {
      MIN: ACCEPTANCE_RANGE.value.smn2.min / 100,
      MAX: ACCEPTANCE_RANGE.value.smn2.max / 100,
    },
    Z480_SMN1_FACTOR: Z480_CT_CORRECTION.smn1,
    Z480_SMN2_FACTOR: Z480_CT_CORRECTION.smn2,
    SMN_Select_Range: SMN_Select_Range,
  }

  // 取得 inputData
  let InputData = currentAnalysisResult.value.resultObj.V1.inputObject
  InputData.parameters = parameters

  // 取得 settingProps
  const currentSettingProps = store.getters["analysis_setting/getSettingProps"];

  // 執行 submitWorkflow
  const analysisResult = await submitWorkflow('SMA', InputData, login_status.value.user_info, currentSettingProps);

  // 檢查有沒有出錯
  if (analysisResult.status == 'success'){

    // 將 result 轉換成 Object
    const resultV1Obj = JSON.parse(analysisResult.result['v1']);
    const resultV2Obj = JSON.parse(analysisResult.result['v2']);
    const resultV3Obj = JSON.parse(analysisResult.result['v3']);

    const SMA_ResultV1 = SMA_RESULT(
      'v1',
      resultV1Obj.SC1Data,
      resultV1Obj.SC2Data,
      resultV1Obj.NTCData,
      resultV1Obj.sampleDataList,
      resultV1Obj.SMAparameters,
      resultV1Obj.resultList,
      InputData,
    )

    const SMA_ResultV2 = SMA_RESULT(
      'v2',
      resultV2Obj.SC1Data,
      resultV2Obj.SC2Data,
      resultV2Obj.NTCData,
      resultV2Obj.sampleDataList,
      resultV2Obj.SMAparameters,
      resultV2Obj.resultList,
      InputData,
    )

    const SMA_ResultV3 = SMA_RESULT(
      'v3',
      resultV3Obj.SC1Data,
      resultV3Obj.SC2Data,
      resultV3Obj.NTCData,
      resultV3Obj.sampleDataList,
      resultV3Obj.SMAparameters,
      resultV3Obj.resultList,
      InputData,
    )

    // 製作 EXPORT_RESULT
    const current_instrument = currentSettingProps.instrument;
    const current_reagent = currentSettingProps.reagent;
    const used_SMA_Result = current_instrument == 'z480' ? SMA_ResultV3 :
                            current_instrument == 'qs3' && current_reagent == 'accuinSma2' ? SMA_ResultV2 :
                            SMA_ResultV1;
    const sample_list = used_SMA_Result.resultList.map(result=>result.sample_name);
    const exportResult = sample_list.map((sample_name, index)=>{
      return EXPORT_RESULT(
        index+1,
        sample_name,
        '',
        [],
        'not-set',
        'not-set'
      )
    })

    // 製作 ANALYSIS_RESULT
    const AnalysisResult = ANALYSIS_RESULT(
        "SMA",
        currentAnalysisID.value.analysis_uuid,
        {
          V1: resultV1Obj.config,
          V2: resultV2Obj.config,
          V3: resultV3Obj.config,
        },
        {
          V1: [simplifyFilePath(InputData.file_path)],
          V2: [simplifyFilePath(InputData.file_path)],
          V3: [simplifyFilePath(InputData.file_path)],
        },
        {
          V1: resultV1Obj.qc_status,
          V2: resultV2Obj.qc_status,
          V3: resultV3Obj.qc_status,
        },
        {
          V1: resultV1Obj.errMsg,
          V2: resultV2Obj.errMsg,
          V3: resultV3Obj.errMsg,
        },
        {
          V1: SMA_ResultV1,
          V2: SMA_ResultV2,
          V3: SMA_ResultV3,
        },
        exportResult
      );

    // 將結果存到 firestore
    update_userAnalysisData(user_info.value.uid, dbSMAResultPath, AnalysisResult, currentAnalysisID.value.analysis_uuid);

    // 更新 displaySMNVersion
    updateDisplaySMNVersion(smn1_analyzer_version.value, smn2_analyzer_version.value);

    // 更新 currentDisplayAnalysisID
    store.commit("analysis_setting/updateCurrentDisplayAnalysisID", {
      analysis_name: "SMA",
      analysis_uuid: currentAnalysisID.value.analysis_uuid,
    });

    // 更新 currentAnalysisID
    const new_id = `analysis_${uuidv4()}`;
    store.commit('analysis_setting/updateCurrentAnalysisID', {
      analysis_name: 'SMA',
      analysis_uuid: new_id,
    });
    currentAnalysisID.value = store.getters['analysis_setting/getCurrentAnalysisID'];

    // 跳轉到分析結果頁面
    setTimeout(()=>{
      // 隱藏 loading 視窗
      $q.loading.hide();

      // 重新整理頁面
      router.go(0);
    }, 1500);
  }
  else if (analysisResult.status == 'error'){
    console.error("Analysis Error: ", analysisResult.message)

    // 通知
    $q.notify({
      progress: true,
      message: "分析流程出了一點問題...",
      icon: 'mdi-alert-circle',
      color: 'deep-orange-6',
      position: 'top'
    });

    // 隱藏 loading 視窗
    $q.loading.hide();
  }
}

// 更新 displaySMNVersion
function updateDisplaySMNVersion(smn1_analyzer_version, smn2_analyzer_version) {
  let smn1_display_version = '';
  let smn2_display_version = '';
  let smn1_distance_ratio = 0;
  let smn2_distance_ratio = 0;
  switch (smn1_analyzer_version) {
    case ANALYZER_VERSION.QS3:
      smn1_display_version = 'QS3';
      smn1_distance_ratio = 0;
      break;
    case ANALYZER_VERSION.QS3L:
      smn1_display_version = 'QS3L';
      smn1_distance_ratio = 50;
      break;
    case ANALYZER_VERSION.Z480:
      smn1_display_version = 'Z480';
      smn1_distance_ratio = 50;
      break;
    case ANALYZER_VERSION.CUSTOM:
      smn1_display_version = 'Custom';
      smn1_distance_ratio = 0;
      break;
    default:
      smn1_display_version = 'Custom';
      smn1_distance_ratio = 0;
      break;
  }
  switch (smn2_analyzer_version) {
    case ANALYZER_VERSION.QS3:
      smn2_display_version = 'QS3';
      smn2_distance_ratio = 0;
      break;
    case ANALYZER_VERSION.QS3L:
      smn2_display_version = 'QS3L';
      smn2_distance_ratio = 50;
      break;
    case ANALYZER_VERSION.Z480:
      smn2_display_version = 'Z480';
      smn2_distance_ratio = 50;
      break;
    case ANALYZER_VERSION.CUSTOM:
      smn2_display_version = 'Custom';
      smn2_distance_ratio = 0;
      break;
    default:
      smn2_display_version = 'Custom';
      smn2_distance_ratio = 0;
      break;
  }

  store.commit("SMA_analysis_data/updateDisplaySMNVersion", {
    smn1: smn1_display_version,
    smn2: smn2_display_version,
  });
  store.commit("SMA_analysis_data/updateDistanceRatio", {
    smn1: smn1_distance_ratio,
    smn2: smn2_distance_ratio,
  });
}

// 更新滑桿資料
function updateSliderData(newVal, slider, data) {

  // 如果選用自訂分析版本, 則不進行更新
  if (newVal === ANALYZER_VERSION.CUSTOM) {
    if (slider.value.name === 'SMN1_SLIDER') {
      flag = true;
    }
    else if (slider.value.name === 'SMN2_SLIDER') {
      flag = true;
    }
  }

  // 如果是 Z480 分析版本, 則不進行更新
  else if (newVal === ANALYZER_VERSION.Z480) {
    // 更新滑桿資料
    let inputPointData = data;
    const N3_point = inputPointData.find(item => item.label === '3N').point;
    const N2_point = inputPointData.find(item => item.label === '2N').point;
    const diff = N3_point - N2_point;
    inputPointData.find(item => item.label === '4N').point = parseFloat(diff) + parseFloat(N3_point);
    inputPointData.find(item => item.label === '4N').label = '';
    slider.value.updatePointData(inputPointData);
    if (slider.value.name === 'SMN1_SLIDER') {
      INTERVAL_RATIO.value.smn1 = 50;
      flag = true;
    }
    else if (slider.value.name === 'SMN2_SLIDER') {
      INTERVAL_RATIO.value.smn2 = 50;
      flag = true;
    }
  }

  else if (newVal === ANALYZER_VERSION.QS3) {
    // 更新滑桿資料
    slider.value.updatePointData(data);
    if (slider.value.name === 'SMN1_SLIDER') {
      INTERVAL_RATIO.value.smn1 = 0;
      flag = true;
    }
    else if (slider.value.name === 'SMN2_SLIDER') {
      INTERVAL_RATIO.value.smn2 = 0;
      flag = true;
    }
  }

  // 如果是 QS3 或 QS3L 分析版本, 則更新滑桿資料
  else if (newVal === ANALYZER_VERSION.QS3L) {
    // 更新滑桿資料
    slider.value.updatePointData(data);
    if (slider.value.name === 'SMN1_SLIDER') {
      INTERVAL_RATIO.value.smn1 = 50;
      flag = true;
    }
    else if (slider.value.name === 'SMN2_SLIDER') {
      INTERVAL_RATIO.value.smn2 = 50;
      flag = true;
    }
  }
}

// 更新 Parameters
function updateSMA_Parameters() {
  const resultObj = currentAnalysisResult.value.resultObj.V1;
  // 更新 Z480 的 CT 校正值
  Z480_CT_CORRECTION.smn1 = resultObj.SMA_parameters.z480_Factors.Z480_SMN1_FACTOR;
  Z480_CT_CORRECTION.smn2 = resultObj.SMA_parameters.z480_Factors.Z480_SMN2_FACTOR;
  // 更新 CT Limit Range
  ValidCTRange.value.min = resultObj.SMA_parameters.CT_Limit_Range.MIN;
  ValidCTRange.value.max = resultObj.SMA_parameters.CT_Limit_Range.MAX;
  // 更新ACCEPTANCE_RANGE
  ACCEPTANCE_RANGE.value.smn1.min = resultObj.SMA_parameters.deltaCT_QC_Range.smn1.MIN*100;
  ACCEPTANCE_RANGE.value.smn1.max = resultObj.SMA_parameters.deltaCT_QC_Range.smn1.MAX*100;
  ACCEPTANCE_RANGE.value.smn2.min = resultObj.SMA_parameters.deltaCT_QC_Range.smn2.MIN*100;
  ACCEPTANCE_RANGE.value.smn2.max = resultObj.SMA_parameters.deltaCT_QC_Range.smn2.MAX*100;
  // 更新SMN1_SMN2_DIFFERENCE
  SC_CT_VALUE.value.SC1.smn1 = resultObj.SC1_Data.smn1.ct_value;
  SC_CT_VALUE.value.SC1.smn2 = resultObj.SC1_Data.smn2.ct_value;
  SC_CT_VALUE.value.SC1.rnp = resultObj.SC1_Data.rnp.ct_value;
  SC_CT_VALUE.value.SC2.smn1 = resultObj.SC2_Data.smn1.ct_value;
  SC_CT_VALUE.value.SC2.smn2 = resultObj.SC2_Data.smn2.ct_value;
  SC_CT_VALUE.value.SC2.rnp = resultObj.SC2_Data.rnp.ct_value;
  // 更新 SMN1_SMN2_DIFFERENCE
  SMN1_SMN2_DIFFERENCE.smn1 = parseInt(Math.abs(SC_CT_VALUE.value.SC1.smn1 - SC_CT_VALUE.value.SC2.smn1)*100);
  SMN1_SMN2_DIFFERENCE.smn2 = parseInt(Math.abs(SC_CT_VALUE.value.SC1.smn2 - SC_CT_VALUE.value.SC2.smn2)*100);
}

// 掛載時
onMounted(async () => {

  // 取得使用者身份
  const { login_status } = updateGetUserInfo();
  is_login.value = login_status.value.is_login;
  user_info.value = login_status.value.user_info;

  // 取得 currentDisplayAnalysisID
  currentDisplayAnalysis.value = getCurrentDisplayAnalysisID();

  // 取得 setting props (為了特殊處理 SMAv4)
  currentSettingProps.value = store.getters["analysis_setting/getSettingProps"];

  // 取得當前分析結果 by 使用者 id, 分析名稱, 分析 id
  currentAnalysisResult.value = await getCurrentAnalysisResult(login_status, currentSettingProps);

  // 如果當前分析結果不存在, 則跳出
  if (!currentAnalysisResult.value) {
    showResult.value = false;
    return;
  }

  // 先嘗試取得當前的分析 ID, 如果沒有則建立新的分析 ID
  currentAnalysisID.value = store.getters['analysis_setting/getCurrentAnalysisID'];
  setAnalysisID(store, 'SMA');

  // 更新 SMA Parameters
  if (currentAnalysisResult.value.resultObj.V1.SMA_parameters) {
    updateSMA_Parameters();
  }

  // 取得 updateDisplaySMNVersion
  const getSMAVersion = store.getters["SMA_analysis_data/displaySMNVersion"];
  smn1_analyzer_version.value = getSMAVersion.smn1;
  smn2_analyzer_version.value = getSMAVersion.smn2;

  nextTick(() => {

    // 重置分析版本
    reset();

    // 更新滑桿資料
    smn1_slider.value.updatePointData(used_SMN1_SLIDER_DATA.value);
    smn2_slider.value.updatePointData(used_SMN2_SLIDER_DATA.value);
  });
});

// 監測 smn1_analyzer_version
watch(smn1_analyzer_version, (newVal) => {
  updateSliderData(newVal, smn1_slider, used_SMN1_SLIDER_DATA.value);

  // 更新 currentSelectedSMAVersion
  store.commit("SMA_analysis_data/updateDisplaySMNVersion", {
    smn1: newVal,
    smn2: smn2_analyzer_version.value,
  });
});

// 監測 smn2_analyzer_version
watch(smn2_analyzer_version, (newVal) => {
  updateSliderData(newVal, smn2_slider, used_SMN2_SLIDER_DATA.value);

  // 更新 currentSelectedSMAVersion
  store.commit("SMA_analysis_data/updateDisplaySMNVersion", {
    smn1: smn1_analyzer_version.value,
    smn2: newVal,
  });
});

// 監測 current_SMN1_Slider_data
watch(current_SMN1_Slider_data, (newVal) => {
  // 檢查是否與原始數據不同
  const isCustom = newVal.some((item, index) => {
    const originalItem = used_SMN1_SLIDER_DATA.value[index+1];
    return originalItem && item.label === originalItem.label && parseFloat(item.value) !== parseFloat(originalItem.var_value);
  });

  if (isCustom) {
    smn1_analyzer_version.value = ANALYZER_VERSION.CUSTOM;
  }
}, { deep: true });

// 監測 current_SMN2_Slider_data
watch(current_SMN2_Slider_data, (newVal) => {
  // 檢查是否與原始數據不同
  const isCustom = newVal.some((item, index) => {
    const originalItem = used_SMN2_SLIDER_DATA.value[index+1];
    return originalItem && item.label === originalItem.label && parseFloat(item.value) !== parseFloat(originalItem.var_value);
  });

  if (isCustom) {
    smn2_analyzer_version.value = ANALYZER_VERSION.CUSTOM;
  }
}, { deep: true });

// 監測 INTERVAL_RATIO
watch(INTERVAL_RATIO, (newVal) => {

  if (flag)
  {
    flag = false;
    return;
  }

  if (newVal.smn1 !== INTERVAL_RATIO_Backup.smn1 && newVal.smn2 === INTERVAL_RATIO_Backup.smn2) {
    // 更新 SMN1 滑桿資料
    for (let i = 0; i < used_SMN1_SLIDER_DATA.value.length; i++) {
      if (i > 0) {
        const origin_point = parseFloat(used_SMN1_SLIDER_DATA.value[i-1].point);
        const float_diff = (parseFloat(used_SMN1_SLIDER_DATA.value[i].point) - parseFloat(used_SMN1_SLIDER_DATA.value[i - 1].point))/100*newVal.smn1;
        used_SMN1_SLIDER_DATA.value[i-1].var_value = (origin_point + float_diff).toFixed(2);
      }
    }

    smn1_analyzer_version.value = ANALYZER_VERSION.CUSTOM;
    smn1_slider.value.updatePointData(used_SMN1_SLIDER_DATA.value);
    INTERVAL_RATIO_Backup.smn1 = newVal.smn1;
  }
  else if (newVal.smn1 === INTERVAL_RATIO_Backup.smn1 && newVal.smn2 !== INTERVAL_RATIO_Backup.smn2) {
    // 更新 SMN2 滑桿資料
    for (let i = 0; i < used_SMN2_SLIDER_DATA.value.length; i++) {
      if (i > 0) {
        const origin_point = parseFloat(used_SMN2_SLIDER_DATA.value[i-1].point);
        const float_diff = (parseFloat(used_SMN2_SLIDER_DATA.value[i].point) - parseFloat(used_SMN2_SLIDER_DATA.value[i - 1].point))/100*newVal.smn2;
        used_SMN2_SLIDER_DATA.value[i-1].var_value = (origin_point + float_diff).toFixed(2);
      }
    }

    smn2_analyzer_version.value = ANALYZER_VERSION.CUSTOM;
    smn2_slider.value.updatePointData(used_SMN2_SLIDER_DATA.value);
    INTERVAL_RATIO_Backup.smn2 = newVal.smn2;
  }
}, { deep: true });

</script>
