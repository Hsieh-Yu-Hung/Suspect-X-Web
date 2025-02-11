<template>
  <q-card bordered>
    <q-card-section>

      <!-- Title -->
      <div class="text-h5 text-uppercase text-bold text-blue-grey-7">
        Settings
      </div>

      <!-- Description -->
      <div class="text-subtitle1">
        Please choose the name of the analysis product along with its corresponding instrument and reagent.
      </div>

      <!--Setting Form-->
      <q-form class="q-gutter-sm row justify-between">

        <!-- 下拉式選單：產品選擇-->
        <q-btn-dropdown flat no-caps class="col-3" icon="category" color="grey-7" :ripple="false">

          <!-- 顯示產品名稱 -->
          <template v-slot:label>
            <div class="row q-mx-md">
              <div class="text-weight-regular">
                Product:
              </div>
              <div class="q-ml-lg text-subtitle1 text-bold text-deep-orange-6">
                {{ currentSelectProduct.label }}
              </div>
            </div>
          </template>

          <!-- 下拉式選單：產品選擇的選項 -->
          <q-list dense>

            <!-- 分區：Import files -->
            <q-item-label header class="q-pb-xs text-blue-grey-7">
              <q-avatar icon="upload_file" color="white" text-color="blue-grey-7" size="md"/>
              Import files
            </q-item-label>

            <!-- 選項內容：Import files -->
            <q-item v-for="n in importArray" :key="n.val" clickable v-close-popup tabindex="0" @click="handleProductChange(n)">
              <q-item-section>
                <q-item-label class="q-ml-lg">{{ n.label }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-separator inset spaced />

            <!-- 分區：Input results -->
            <q-item-label header class="q-pb-xs text-blue-grey-7">
              <q-avatar icon="drive_file_rename_outline" color="white" text-color="blue-grey-7" size="lg" />
              Input results
            </q-item-label>

            <!-- 選項內容：Input results -->
            <q-item v-for="n in inputArray" :key="n.val" clickable v-close-popup tabindex="0" @click="handleProductChange(n)">
              <q-item-section>
                <q-item-label class="q-ml-lg">{{ n.label }}</q-item-label>
              </q-item-section>
            </q-item>

          </q-list>
        </q-btn-dropdown>

        <!-- 下拉式選單：儀器選擇 -->
        <q-select
          class="col q-mr-lg"
          v-model="currentSelectInstrument.label"
          :options="instrumentArray(currentSelectProduct.val)"
          color="deep-orange-6"
          stack-label
          label="Instrument"
          @update:model-value="handleInstrumentChange"
        >
          <template v-slot:before>
            <q-icon name="construction" />
          </template>
        </q-select>

        <!-- 下拉式選單：試劑選擇 -->
        <q-select
          class="col"
          v-model="currentSelectReagent.label"
          :options="reagentArray(currentSelectProduct.val, currentSelectInstrument.val)"
          color="deep-orange-6"
          stack-label
          label="Reagent"
          @update:model-value="handleReagentChange"
        >
          <template v-slot:before>
            <q-icon name="mdi-beaker-outline" />
          </template>
        </q-select>

      </q-form>

    </q-card-section>
  </q-card>
</template>

<script setup>
// 導入模組
import { ref, onMounted } from 'vue';
import { useStore } from 'vuex';

// 使用 Vuex Store
const store = useStore();

// 取得預設設定
const defaultSettingProps = ref(store.getters["analysis_setting/getDefaultSettingProps"]);

// 取得目前選擇的產品
const currentSelectProduct = ref({
  label: defaultSettingProps.value.productLabel,
  val: defaultSettingProps.value.product
});

// 取得目前選擇的儀器
const currentSelectInstrument = ref({
  label: defaultSettingProps.value.instrumentLabel,
  val: defaultSettingProps.value.instrument
});

// 取得目前選擇的試劑
const currentSelectReagent = ref({
  label: defaultSettingProps.value.reagentLabel,
  val: defaultSettingProps.value.reagent
});

/* 顯示 import 檔案的選項 */
const importArray = [
  { label: "FXS", val: "fx" },
  { label: "HTD", val: "hd" },
  { label: "MTHFR", val: "mthfr-import" },
  { label: "SMA", val: "sma" },
  { label: "APOE", val: "apoe-import" },
  { label: "NUDT15", val: "nudt15" },
];

/* 顯示 input 結果的選項 */
const inputArray = [
  { label: "α/β Thal", val: "thal" },
  { label: "ADH1B/ALDH2", val: "alcohol" },
  { label: "APOE (AD)", val: "apoe" },
  { label: "APOE (CVD)", val: "cvd" },
  { label: "B27", val: "b27" },
  { label: "CYP1A2", val: "cyp1a2" },
  { label: "DQ2/DQ8", val: "cd" },
  { label: "F2/F5", val: "f2f5" },
  { label: "LRRK2/GBA", val: "pd" },
  { label: "HFE", val: "hfe" },
  { label: "LCT", val: "lct" },
  { label: "MTHFR", val: "mthfr-input" },
  { label: "NOTCH3", val: "notch3" },
];

/* 更新目前顯示的下拉式選單 */
const updateCurrentSelects = () => {
  // 取得新的設定
  const newSettingProps = ref(store.getters["analysis_setting/getSettingProps"]);

  // 更新目前選擇的儀器和試劑
  currentSelectProduct.value = {
    label: newSettingProps.value.productLabel,
    val: newSettingProps.value.product
  };
  currentSelectInstrument.value = {
    label: newSettingProps.value.instrumentLabel,
    val: newSettingProps.value.instrument
  };
  currentSelectReagent.value = {
    label: newSettingProps.value.reagentLabel,
    val: newSettingProps.value.reagent
  };
}

// 更新 settingProps
const updateSettingProps = (update_target_list, new_settings) => {

  // 取得新的設定 (預設為當前)
  let new_product = currentSelectProduct.value;
  let new_instrument = currentSelectInstrument.value;
  let new_reagent = currentSelectReagent.value;

  // 更新新的設定
  if (update_target_list.includes('product')) {
    new_product = new_settings.product;
  }
  if (update_target_list.includes('instrument')) {
    new_instrument = new_settings.instrument;
  }
  if (update_target_list.includes('reagent')) {
    new_reagent = new_settings.reagent;
  }

  // 將選擇的產品、儀器、試劑更新到 store 中
  store.commit("analysis_setting/updateSettingProps", {
    product: new_product.val,
    instrument: new_instrument.val,
    reagent: new_reagent.val,
    instrumentLabel: new_instrument.label,
    productLabel: new_product.label,
    reagentLabel: new_reagent.label,
  });

  // 更新目前顯示的下拉式選單
  updateCurrentSelects();
}

/* 處理下拉式選單的選擇, 改變產品時觸發 */
const handleProductChange = (new_product) => {

  // 取得新的儀器
  const new_instrument = instrumentArray(new_product.val)[0];

  // 取得新的試劑
  const new_reagent = reagentArray(new_product.val, new_instrument.val)[0];

  // 更新 settingProps
  const update_targets = ['product', 'instrument', 'reagent'];
  const new_settings = {
    product: new_product,
    instrument: new_instrument,
    reagent: new_reagent,
  };
  updateSettingProps(update_targets, new_settings);
};

/* 處理儀器選擇的選項 */
const handleInstrumentChange = (new_instrument) => {

  // Get new reagent
  const new_reagent = reagentArray(currentSelectProduct.value.val, new_instrument.val)[0];

  // update target
  const update_targets = ['instrument', 'reagent'];
  const new_settings = {
    instrument: new_instrument,
    reagent: new_reagent,
  };
  updateSettingProps(update_targets, new_settings);
};

/* 處理試劑選擇的選項 */
const handleReagentChange = (new_reagent) => {
  // update target
  const update_targets = ['reagent'];
  const new_settings = { reagent: new_reagent };
  updateSettingProps(update_targets, new_settings);
}

/* 顯示儀器選擇的選項 */
const instrumentArray = (product) => {
  if (product == 'fx' || product == 'hd' || product == 'apoe-import') {
    return [
      { label: "Qsep 100", val: "qsep100" },
    ]
  } else if (product == 'sma') {
    return [
      { label: "QuantStudio™ 3", val: "qs3" },
      { label: "qTOWER³", val: "tower" },
      { label: "Roche Cobas® z 480", val: "z480" },
      { label: "Qsep 100", val: "qsep100"}
    ]
  } else if (product == 'mthfr-import') {
    return [
      { label: "QuantStudio™ 3", val: "qs3" },
      { label: "qTOWER³", val: "tower" },
      { label: "Roche Cobas® z 480 / LightCycler® 480 II Analyzer", val: "z480" },
    ]
  } else if (product == 'nudt15') {
    return [
      { label: "QuantStudio™ 3", val: "qs3" },
      { label: "Roche Cobas® z 480", val: "z480" },
    ]
  } else {
    return [
      { label: '', val: ''}
    ]
  }
};

/* 顯示試劑選擇的選項 */
const reagentArray = (product, instrument) => {
  if (product == 'fx') {
    return [
      { label: "ACCUiN BioTech Fragile X v1", val: "accuinFx1" },
      { label: "ACCUiN BioTech Fragile X v2", val: "accuinFx2" },
    ];
  } else if (product == 'sma' && instrument == 'qs3') {
    return [
      { label: "ACCUiN BioTech SMA v1", val: "accuinSma1" },
      { label: "ACCUiN BioTech SMA v2", val: "accuinSma2" },
    ]
  } else if (product == 'sma' && instrument == 'tower') {
    return [
      { label: "ACCUiN BioTech SMA v1", val: "accuinSma1" },
    ]
  } else if (product == 'sma' && instrument == 'z480') {
    return [
      { label: "ACCUiN BioTech SMA v3", val: "accuinSma3" },
    ]
  } else if (product == 'sma' && instrument == 'qsep100') {
    return [
      { label: "ACCUiN BioTech SMA v4", val: "accuinSma4" },
    ]
  } else if (product == 'mthfr-import' && instrument == 'z480') {
    return [
      { label: "ACCUiN BioTech MTHFR v3", val: "accuinMTHFR3" },
    ]
  } else if (product == 'mthfr-import' && (instrument == 'qs3' || instrument == 'tower')) {
    return [
      { label: "ACCUiN BioTech MTHFR v1", val: "accuinMTHFR1" },
      { label: "ACCUiN BioTech MTHFR v2", val: "accuinMTHFR2" },
    ]
  } else if (product == 'mthfr-input') {
    return [
      { label: "ACCUiN BioTech MTHFR v1", val: "accuinMTHFR1" },
      { label: "ACCUiN BioTech MTHFR v2", val: "accuinMTHFR2" },
    ]
  } else if (product == 'nudt15' && instrument == 'qs3') {
    return [
      { label: "ACCUiN BioTech NUDT15 v1", val: "accuinNUDT151" },
    ]
  } else if (product == 'nudt15' && instrument == 'z480') {
    return [
      { label: "ACCUiN BioTech NUDT15 v2", val: "accuinNUDT152" },
    ]
  } else if (product == 'hd') {
    return [
      { label: "ACCUiN BioTech HTD v1", val: "accuinHD1" },
    ]
  } else if (product == 'apoe-import') {
    return [
      { label: "ACCUiN BioTech APOE v1", val: "accuinApoe1" },
    ]
  } else {
    return [
      { label: '', val: ''}
    ]
  }
};

/* 掛載時 */
onMounted(() => {
  // 更新目前顯示的下拉式選單
  updateCurrentSelects();
});

</script>
