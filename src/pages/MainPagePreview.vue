<template>
  <q-page>

    <!-- QC Results 面板-->
    <div class="row justify-between q-mt-lg q-mx-xl">
      <div class="col">
        <QualityControlPanel
          :analysisId="QC_PANEL_DISPLAY.analysis_id"
          :product="QC_PANEL_DISPLAY.product"
          :instrument="QC_PANEL_DISPLAY.instrument"
          :reagent="QC_PANEL_DISPLAY.reagent"
          :analysisMethod="QC_PANEL_DISPLAY.analysis_method"
          :controlId="QC_PANEL_DISPLAY.controlId"
          :QCResult="QC_PANEL_DISPLAY.QCResult"
          :assessmentTime="QC_PANEL_DISPLAY.assessmentTime"
          :QCMessage="QC_PANEL_DISPLAY.QCMessage"
        />
      </div>
    </div>

    <!-- SMA v1-3 devMode 面板 -->
    <div v-if="currentDisplayAnalysis.analysis_name === 'SMA'" class="row justify-between q-mt-lg q-mx-xl">
      <SMAReanalysisParamSettings :style="{ display: is_developer_mode ? 'block' : 'none' }" />
    </div>

    <!-- SMA v4 devMode 面板 -->
    <div v-else-if="currentDisplayAnalysis.analysis_name === 'SMAv4'" class="row justify-between q-mt-lg q-mx-xl">
      <div class="col">
        <SMAv4ReanalysePanel
          ref="ref_SMAv4ReanalysePanel"
          @reAnalysis="callReAnalysisSMAv4"
          :smav4_config_name="getUSE_CONFIG_NAME"
        />
      </div>
    </div>

    <!-- Analysis Results 面板-->
    <div class="row justify-between q-mt-lg q-mx-xl q-pb-lg">

      <!-- APOE -->
      <div class="col" v-if="currentDisplayAnalysis.analysis_name === 'APOE'">
        <ResultViewAPOE />
      </div>

      <!-- FXS -->
      <div class="col" v-else-if="currentDisplayAnalysis.analysis_name === 'FXS'">
        <ResultViewFXS />
      </div>

      <!-- HTD -->
      <div class="col" v-else-if="currentDisplayAnalysis.analysis_name === 'HTD'">
        <ResultViewHTD />
      </div>

      <!-- MTHFR -->
      <div class="col" v-else-if="currentDisplayAnalysis.analysis_name === 'MTHFR'">
        <ResultViewMTHFR />
      </div>

      <!-- NUDT15 -->
      <div class="col" v-else-if="currentDisplayAnalysis.analysis_name === 'NUDT15'">
        <ResultViewNUDT15 />
      </div>

      <!-- SMA v1-3 -->
      <div class="col" v-else-if="currentDisplayAnalysis.analysis_name === 'SMA'">
        <ResultViewSMA />
      </div>

      <!-- SMA v4 -->
      <div class="col" v-else-if="currentDisplayAnalysis.analysis_name === 'SMAv4'">
        <ResultViewSMAv4 ref="ref_resultViewSMAv4" @updatePeakSettings="call_updatePeakSettings" />
      </div>

      <!-- THAL_BETA -->
      <div class="col" v-else-if="currentDisplayAnalysis.analysis_name === 'THAL_BETA'">
        <ResultViewBetaThal />
      </div>

    </div>

  </q-page>
</template>

<script setup>

// 導入模組
import { onMounted, ref, computed } from 'vue';
import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';

// 導入模組 composable
import { useValidateAccountStatus, updateGetUserInfo } from '@/composables/accessStoreUserInfo.js';
import { getCurrentDisplayAnalysisID, getCurrentAnalysisResult } from '@/composables/checkAnalysisStatus.js';
import { getUsers_from_firestore } from '@/firebase/firebaseDatabase';

// 導入元件
import QualityControlPanel from '@/components/PreviewPageViews/QualityControl.vue';
import ResultViewAPOE from '@/components/PreviewPageViews/ResultViewAPOE.vue';
import ResultViewFXS from '@/components/PreviewPageViews/ResultViewFXS.vue';
import ResultViewHTD from '@/components/PreviewPageViews/ResultViewHTD.vue';
import ResultViewMTHFR from '@/components/PreviewPageViews/ResultViewMTHFR.vue';
import ResultViewNUDT15 from '@/components/PreviewPageViews/ResultViewNUDT15.vue';
import ResultViewSMA from '@/components/PreviewPageViews/ResultViewSMA.vue';
import ResultViewSMAv4 from '@/components/PreviewPageViews/ResultViewSMAv4.vue';
import SMAv4ReanalysePanel from '@/components/PreviewPageViews/SMAv4ReanalysePanel.vue';
import SMAReanalysisParamSettings from '@/components/PreviewPageViews/SMAReanalysisParamSettings.vue';
import ResultViewBetaThal from '@/components/PreviewPageViews/ResultViewBetaThal.vue';

// 取得 Quasar 和 Router 和 store
const $q = useQuasar();
const router = useRouter();
const store = useStore();

// 使用者身份
// 使用者身份
const is_login = ref(false);
const user_info = ref(null);

// 定義 QC panel display value
const DEFAULT_QC_PANEL_DISPLAY = {
  analysis_id: 'N/A',
  product: 'N/A',
  instrument: 'N/A',
  reagent: 'N/A',
  analysis_method: 'N/A',
  controlId: [],
  QCResult: 'N/A',
  assessmentTime: 'N/A',
  QCMessage: 'N/A',
}

// 設定當前顯示為 default
const QC_PANEL_DISPLAY = ref(DEFAULT_QC_PANEL_DISPLAY);

// 保存當前分析結果
const currentAnalysisResult = ref(null);
const currentSettingProps = ref(null);

// 保存 currentDisplayAnalysis
const currentDisplayAnalysis = ref({
  analysis_uuid: '',
  analysis_name: '',
});

// 取得當前使用者的權限動作列表
const current_user_actions = ref([]);

// 判斷是否開啟開發者模式
const is_developer_mode = computed(() => {
  return current_user_actions.value.some(action => action.action_name === "dev_mode" && action.action_active);
});

// 管理 ResultViewSMAv4
const ref_resultViewSMAv4 = ref(null);

// 管理 SMAv4ReanalysePanel
const ref_SMAv4ReanalysePanel = ref(null);

/* Functions */

const getUSE_CONFIG_NAME = computed(() => {
  if (currentAnalysisResult.value){
    return currentAnalysisResult.value.resultObj.USE_CONFIG_NAME;
  }
  else{
    return "N/A";
  }
});

// 更新 QC_PANEL_DISPLAY
function updateQC_PANEL_DISPLAY(currentAnalysisResult){

  // 取得 SMA 分析器選項
  const SMA_analyser_selection = "V1";

  // 如果找到 Result , 則更新 QC_PANEL_DISPLAY
  if (currentAnalysisResult){

    // 如果是 SMA 則要特殊處理
    if (currentAnalysisResult.analysis_name === "SMA"){
      QC_PANEL_DISPLAY.value.analysis_id = currentAnalysisResult.analysis_id;
      QC_PANEL_DISPLAY.value.product = currentAnalysisResult.analysis_name;
      QC_PANEL_DISPLAY.value.instrument = currentAnalysisResult.config[SMA_analyser_selection].instrument;
      QC_PANEL_DISPLAY.value.reagent = currentAnalysisResult.config[SMA_analyser_selection].reagent;
      QC_PANEL_DISPLAY.value.analysis_method = "ACCUiN BioTech Analyzer";
      QC_PANEL_DISPLAY.value.controlId = currentAnalysisResult.control_ids[SMA_analyser_selection];
      QC_PANEL_DISPLAY.value.QCResult = currentAnalysisResult.qc_status[SMA_analyser_selection];
      QC_PANEL_DISPLAY.value.assessmentTime = currentAnalysisResult.analysis_time;
      QC_PANEL_DISPLAY.value.QCMessage = currentAnalysisResult.qc_message[SMA_analyser_selection];
    }

    // 如果不是 SMA 則正常處理
    else {
      QC_PANEL_DISPLAY.value.analysis_id = currentAnalysisResult.analysis_id;
      QC_PANEL_DISPLAY.value.product = currentAnalysisResult.analysis_name;
      QC_PANEL_DISPLAY.value.instrument = currentAnalysisResult.config?currentAnalysisResult.config.instrument:"N/A";
      QC_PANEL_DISPLAY.value.reagent = currentAnalysisResult.config?currentAnalysisResult.config.reagent:"N/A";
      QC_PANEL_DISPLAY.value.analysis_method = "ACCUiN BioTech Analyzer";
      QC_PANEL_DISPLAY.value.controlId = currentAnalysisResult?currentAnalysisResult.control_ids:"N/A";
      QC_PANEL_DISPLAY.value.QCResult = currentAnalysisResult?currentAnalysisResult.qc_status:"N/A";
      QC_PANEL_DISPLAY.value.assessmentTime = currentAnalysisResult?currentAnalysisResult.analysis_time:"N/A";
      QC_PANEL_DISPLAY.value.QCMessage = currentAnalysisResult?currentAnalysisResult.qc_message:"N/A";
    }
  }

  // 如果找不到 Result , 則代表尚未分析, 則將顯示改為 Default
  else{
    QC_PANEL_DISPLAY.value = DEFAULT_QC_PANEL_DISPLAY;
  }
}

// 重新分析 SMAv4
function callReAnalysisSMAv4() {
  ref_resultViewSMAv4.value.reAnalysisSMAv4();
}

// 保存 Peak Settings
function call_updatePeakSettings(newPeakSettings){
  ref_SMAv4ReanalysePanel.value.updatePeakSettings(newPeakSettings);
}

// 掛載時
onMounted(async () => {

  // 取得使用者身份
  const { login_status } = updateGetUserInfo();
  is_login.value = login_status.value.is_login;
  user_info.value = login_status.value.user_info;

  // 檢查帳號狀態, 若未開通則跳轉到 not-active
  useValidateAccountStatus($q, router, store);

  // 取得 currentDisplayAnalysisID
  currentDisplayAnalysis.value = getCurrentDisplayAnalysisID();

  if (!currentDisplayAnalysis.value.analysis_uuid){
    return;
  }

  // 取得 setting props (為了特殊處理 SMAv4)
  currentSettingProps.value = store.getters["analysis_setting/getSettingProps"];

  // 取得當前分析結果 by 使用者 id, 分析名稱, 分析 id
  currentAnalysisResult.value = await getCurrentAnalysisResult(login_status, currentSettingProps);

  // 更新 QC_PANEL_DISPLAY
  updateQC_PANEL_DISPLAY(currentAnalysisResult.value);

  // 取得當前使用者的權限動作列表
  const current_user_info = await getUsers_from_firestore(user_info.value.uid);
  current_user_actions.value = current_user_info.actions;
});

</script>
