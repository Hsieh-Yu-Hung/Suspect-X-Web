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
      <peakSetting
        ref="peakSettingRef"
        @update_PeakSelectRange="update_PeakSelectRange"
        @apply_PeakSelectRange="applyPeakSelectRange"
      ></peakSetting>
    </q-card-section>
  </q-card>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useQuasar } from 'quasar';
import peakSetting from '@/components/SMAImportViewComp/peakSetting.vue';
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';
import { update_userAnalysisData, getData, dataset_list } from '@/firebase/firebaseDatabase';

// 定義 Props
const props = defineProps({
  smav4_config_name: {
    type: String,
    required: true
  }
});

// 使用者身份
const is_login = ref(false);
const user_info = ref(null);

// database config path
const databaseConfigPath = 'smav4_import_config';

// 定義 emits
const emit = defineEmits(['reAnalysis']);

// 取得 store, quasar
const store = useStore();
const $q = useQuasar();

// 重新分析選項
const re_analyse_selection = ref(['new_std']);

// 取得 peakSettingRef
const peakSettingRef = ref(null);

// 目前峰值選擇範圍
const currentPeakCondition = ref(null);

// 重新分析
async function reAnalysis() {
  await applyPeakSelectRange();
  emit('reAnalysis');
}

// 將 re_analyse_selection 存到 store
function saveReAnalyseSelection() {
  const copy_of_re_analyse_selection = JSON.parse(JSON.stringify(re_analyse_selection.value));
  store.commit("analysis_setting/saveReAnalyseSelection", copy_of_re_analyse_selection);
}

// 更新 Peak 選擇範圍
function update_PeakSelectRange(new_peak_condition) {
  if (!re_analyse_selection.value.includes('new_peak')) {
    re_analyse_selection.value.push('new_peak');
  }
  currentPeakCondition.value = new_peak_condition;
}

function updatePeakSettings(newPeakSettings){
  peakSettingRef.value.update_current_settings(newPeakSettings);
}

// 取得 Database 中的 Config
const getConfigsFromDatabase = async () => {
  const dataPath = `${dataset_list.user_analysis}/${user_info.value.uid}/${databaseConfigPath}`;
  const response = await getData(dataPath);
  if (response.status === 'success') {
    return response.data;
  }
  else {
    console.error(response.message);
    return [];
  }
}

async function applyPeakSelectRange() {

  // 顯示等待動畫
  $q.loading.show({
    message: 'Applying peak select range...'
  });

  // 取得資料庫中的 Config
  const loaded_configs = await getConfigsFromDatabase();
  const use_config = loaded_configs.find(config => config.id === props.smav4_config_name);

  // 更新資料庫
  const data = {files: use_config.files, peak_condition: currentPeakCondition.value};
  update_userAnalysisData(user_info.value.uid, databaseConfigPath, data, props.smav4_config_name);

  // 隱藏等待動畫
  $q.loading.hide();

  // 通知
  $q.notify({
    message: 'Config saved',
    color: 'green',
    icon: 'mdi-check',
    position: 'top',
    timeout: 300,
    progress: true,
  });
}

// Expose
defineExpose({
  updatePeakSettings
});

// 掛載時
onMounted(async () => {
  // 取得使用者身份
  const { login_status } = updateGetUserInfo();
  is_login.value = login_status.value.is_login;
  user_info.value = login_status.value.user_info;

  // 初始化時將 re_analyse_selection 存到 store
  saveReAnalyseSelection();
});

// 監聽 re_analyse_selection 的變化
watch(re_analyse_selection, saveReAnalyseSelection, { deep: true });
</script>
