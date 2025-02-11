<template>

  <!-- FAM file -->
  <div class="q-gutter-sm" v-if="getCurrentInstrument() == 'z480'">
    <q-file
      v-model="famFile"
      use-chips
      color="deep-orange-6"
      stack-label
      label="FAM (465-533) result .txt file"
      :rules="[(val) => val || `Please select FAM result txt file`]"
      accept=".txt"
      lazy-rules
    >
      <template v-slot:before>
        <q-icon name="mdi-text-box-outline" />
      </template>
    </q-file>
  </div>

  <!-- VIC file -->
  <div class="q-gutter-sm" v-if="getCurrentInstrument() == 'z480'">
    <q-file
      v-model="vicFile"
      use-chips
      color="deep-orange-6"
      stack-label
      label="VIC/HEX (523-580) result .txt file"
      :rules="[(val) => val || `Please select VIC result txt file`]"
      accept=".txt"
      lazy-rules
    >
      <template v-slot:before>
        <q-icon name="mdi-text-box-outline" />
      </template>
    </q-file>
  </div>

  <!-- CY5 file -->
  <div class="q-gutter-sm" v-if="getCurrentInstrument() == 'z480' && getCurrentReagent() == 'accuinSma3'">
    <q-file
      v-model="cy5File"
      use-chips
      color="deep-orange-6"
      stack-label
      label="CY5 (610-670) result .txt file"
      :rules="[(val) => val || `Please select CY5 result txt file`]"
      accept=".txt"
      lazy-rules
    >
      <template v-slot:before>
        <q-icon name="mdi-text-box-outline" />
      </template>
    </q-file>
  </div>

  <!-- 上傳檔案 -->
  <div class="q-gutter-sm" v-if="getCurrentInstrument() != 'z480'">
    <q-file
      v-model="resultFile"
      use-chips
      color="deep-orange-6"
      stack-label
      label="Sample result"
      :rules="[(val) => val || `Please select ONE sample result`]"
      :accept="getCurrentInstrument() === 'qs3'? '.xlsx, .xls' : '.csv'"
      lazy-rules
    >
      <template v-slot:before>
        <q-icon :name="getCurrentInstrument() === 'qs3'? 'mdi-microsoft-excel' : 'mdi-file-delimited-outline'" />
      </template>
    </q-file>
  </div>

  <!-- 96-well plate positions Select: Title -->
  <div class="row">
    <q-icon
      name="mdi-pencil-circle-outline"
      size="sm"
      color="grey-7"
      label="96-well plate positions"
      class="q-ql-xs"
    />
    <q-item-label class="q-ml-sm" style="color: #757575; font-size: 90%">
      96-well plate positions
    </q-item-label>
  </div>

  <!-- 96-well plate positions Select: Control -->
  <div class="row" v-for="(ctrlwell, index) in Ctrlwells" :key="index">
    <div class="col">
      <q-select
        v-model="ctrlwell.X"
        :options="wellXArray"
        color="deep-orange-6"
        options-dense
        stack-label
        :label="props.std_control_number > 1 ? `Standard ${index + 1}` : 'Control'"
        :rules="[(val) => WELL(val, ctrlwell.Y) || `Please select row of Control`]"
        reactive-rules
        @update:modelValue="updateCtrlwells(ctrlwell.X, index, 'X')"
      >
        <template v-slot:before>
          <q-icon name="" />
        </template>
      </q-select>
    </div>
    <div class="col">
      <q-select
        v-model="ctrlwell.Y"
        :options="wellYArray"
        color="deep-orange-6"
        options-dense
        label=""
        :rules="[(val) => WELL(ctrlwell.X, val) || `Please select column of Control`]"
        reactive-rules
        @update:modelValue="updateCtrlwells(ctrlwell.Y, index, 'Y')"
      >
      </q-select>
    </div>
  </div>

  <!-- 96-well plate positions Select: NTC -->
  <div class="row">
    <div class="col">
      <q-select
        v-model="NTCwell.X"
        :options="wellXArray"
        color="deep-orange-6"
        options-dense
        stack-label
        label="NTC"
        :rules="[(val) => WELL(val, NTCwell.Y) || `Please select row of NTC`]"
        reactive-rules
      >
        <template v-slot:before>
          <q-icon name="" />
        </template>
      </q-select>
    </div>
    <div class="col">
      <q-select
        v-model="NTCwell.Y"
        :options="wellYArray"
        color="deep-orange-6"
        options-dense
        label=""
        :rules="[(val) => WELL(NTCwell.X, val) || `Please select column of NTC`]"
        reactive-rules
      >
      </q-select>
    </div>
  </div>

</template>

<script setup>
/* import modules */
import { ref, watch, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useQuasar } from 'quasar';
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';
import { CATEGORY_LIST, upload_files_to_storage } from '@/utility/storageManager';

// 導入 store, Quasar
const store = useStore();
const $q = useQuasar();

// Definition
const WELL = (setX = null, setY = null) => {
  return { X: setX, Y: setY };
}

// Props
const props = defineProps({
  std_control_number: {
    type: Number,
    required: false,
    default: 1,
  },
});

// Emit
const emit = defineEmits(['update_dialog_error_message', 'update_result_files', 'update_wells']);

// consts
const resultFile = ref(null);
const famFile = ref(null);
const vicFile = ref(null);
const cy5File = ref(null);
const Ctrlwells = ref([]);
const NTCwell = ref(WELL());

// 使用者身份
const is_login = ref(false);
const user_info = ref(null);

// 下拉式選單選項, 96-well plate positions
const wellXArray = ref(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']);
const wellYArray = ref(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']);

// 上傳分類 matrix
const categoryMatrix = {
  'MTHFR': CATEGORY_LIST.mthfr_import,
  'NUDT15': CATEGORY_LIST.nudt15_import,
  'SMA': CATEGORY_LIST.sma_import,
}

// Expose
defineExpose({
  resultFile: resultFile,
  famFile: famFile,
  vicFile: vicFile,
  cy5File: cy5File,
  Ctrlwells: Ctrlwells,
  NTCwell: NTCwell,
});

/* functions */

// 取得 settingProps: instrument
function getCurrentInstrument() {
  return store.getters["analysis_setting/getSettingProps"].instrument;
}

// 取得 settingProps: instrument
function getCurrentReagent() {
  return store.getters["analysis_setting/getSettingProps"].reagent;
}

// 初始化 Ctrlwells
function initCtrlwells() {
  Ctrlwells.value = Array.from({ length: props.std_control_number }, () => ({ X: null, Y: null }));
}

// 選擇後上傳檔案
async function uploadFile(file) {

  // 如果沒有檔案, 則返回
  if (!file) return;

  // 顯示 loading 視窗
  $q.loading.show();

  // 存到當前使用者
  const user_uid = user_info.value.uid;

  // 存到 data 資料夾
  const analysis_name = store.getters['analysis_setting/getCurrentAnalysisID'].analysis_name;
  const analysis_uuid = store.getters['analysis_setting/getCurrentAnalysisID'].analysis_uuid;
  const category = categoryMatrix[analysis_name];
  const subDir = getCurrentInstrument();

  // 上傳檔案
  const uploading = await upload_files_to_storage(
    file, user_uid, category, analysis_uuid, subDir
  );

  // 檢查是否有 error
  if (uploading.status === 'error'){
    emit('update_dialog_error_message', uploading.message);
  }
  else {
    file.path = uploading.storage_path;
  }

  // 隱藏 loading 視窗
  $q.loading.hide();
}

// 更新 Ctrlwells
function updateCtrlwells(newVal, index, type) {
  if (type === 'X'){
    Ctrlwells.value[index].X = newVal;
  }
  else if (type === 'Y'){
    Ctrlwells.value[index].Y = newVal;
  }
  emit('update_wells', 'Ctrlwells');
}

// 監聽 instrument
watch(getCurrentInstrument, () => {
  // 如果儀器改變, 則清空 resultFile
  resultFile.value = null;
  famFile.value = null;
  vicFile.value = null;
  Ctrlwells.value.forEach(well => {
    well.X = null;
    well.Y = null;
  });
  NTCwell.value.X = null;
  NTCwell.value.Y = null;
});

// 監聽 resultFile
watch(resultFile, async(newVal, oldVal) => {
  if (newVal !== oldVal){
    await uploadFile(resultFile.value);
    emit('update_result_files', 'resultFile');
  }
});

// 監聽 famFile
watch(famFile, async(newVal, oldVal) => {
  if (newVal !== oldVal){
    await uploadFile(famFile.value);
    emit('update_result_files', 'famFile');
  }
});

// 監聽 vicFile
watch(vicFile, async(newVal, oldVal) => {
  if (newVal !== oldVal){
    await uploadFile(vicFile.value);
    emit('update_result_files', 'vicFile');
  }
});

// 監聽 cy5File
watch(cy5File, async(newVal, oldVal) => {
  if (newVal !== oldVal){
    await uploadFile(cy5File.value);
    emit('update_result_files', 'cy5File');
  }
});

// 監聽 NTCwell
watch(NTCwell.value, async() => {
  emit('update_wells', 'NTCwell');
}, {deep: true});

// 掛載時
onMounted(() => {
  // 取得使用者身份
  const { login_status } = updateGetUserInfo();
  is_login.value = login_status.value.is_login;
  user_info.value = login_status.value.user_info;

  // 初始化 Ctrlwells
  initCtrlwells();
});

</script>
