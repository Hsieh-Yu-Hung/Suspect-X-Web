<template>
  <q-card bordered>
    <q-card-section>

      <!-- 標題 -->
      <div class="row justify-between">
        <span class="text-h5 text-uppercase text-bold text-blue-grey-7">Quality Control</span>
        <span class="text-caption text-blue-grey-2">Analysis ID: {{ props.analysisId }}</span>
      </div>

      <!-- 第一行 -->
      <div class="row">

        <!-- 產品標示 -->
        <div class="col">
          <q-card class="text-center" flat>
            <q-card-section>
              <div class="text-grey-7 text-overline">Product</div>
              <div class="text-grey-7 text-weight-bolder">
                {{ getProductName }}
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- 儀器標示 -->
        <div class="col">
          <q-card class="text-center" flat>
            <q-card-section>
              <div class="text-grey-7 text-overline">Instrument</div>
              <div class="text-grey-7 text-weight-bolder">
                {{ getInstrumentName }}
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- 試劑標示 -->
        <div class="col">
          <q-card class="text-center" flat>
            <q-card-section >
              <div class="text-grey-7 text-overline">Reagent</div>
              <div class="text-grey-7 text-weight-bolder">
                {{ getReagentName }}
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- 分析方法標示 -->
        <div class="col">
          <q-card class="text-center" flat>
            <q-card-section>
              <div class="text-grey-7 text-overline">Analysis Method</div>
              <div class="text-grey-7 text-weight-bolder">
                {{ props.analysisMethod }}
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- 第二行 -->
      <div class="row">

        <!-- 控制 ID 標示 -->
        <div class="col">
          <q-card class="text-center" flat>
            <q-card-section>
              <div class="text-grey-7 text-overline">Control ID</div>
              <div v-for="id in props.controlId" :key="id" class="text-grey-7 text-weight-bolder">
                {{ id }}
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- QC 結果標示 -->
        <div class="col">
          <q-card class="text-center" flat>
            <q-card-section>
              <div class="text-grey-7 text-overline">Result</div>
              <div class="text-weight-bolder" :class="getQCResultColor">
                {{ getQCResultLabel }}
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- 評估時間標示 -->
        <div class="col">
          <q-card class="text-center" flat>
            <q-card-section>
              <div class="text-grey-7 text-overline">Assessment Time</div>
              <div class="text-grey-7 text-weight-bolder">
                {{ props.assessmentTime }}
              </div>
            </q-card-section>
          </q-card>
        </div>

      </div>

      <!-- 第三行 -->
      <div class="row">

        <!-- QC Message -->
        <div class="col">
          <q-card flat>
            <q-card-section class="q-gutter-x-md" style="display: flex; align-items: center;">
              <div class="text-grey-7 text-overline" style="display: flex;">QC Message:</div>
              <div class="text-deep-orange-4 text-weight-bolder">
                <div v-for="message in getQCMessageContent" :key="message.index">
                  {{ message.message }}
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>

      </div>

    </q-card-section>
  </q-card>
</template>

<script setup>

// 導入模組
import { computed } from 'vue';

// Props
const props = defineProps({
  analysisId: {
    type: String,
    required: true
  },
  product: {
    type: String,
    required: true
  },
  instrument: {
    type: String,
    required: true
  },
  reagent: {
    type: String,
    required: true
  },
  analysisMethod: {
    type: String,
    required: true
  },
  controlId: {
    type: Array,
    required: true
  },
  QCResult: {
    type: String,
    required: true
  },
  assessmentTime: {
    type: String,
    required: true
  },
  QCMessage: {
    type: String,
    required: true
  }
})

// 產品名稱轉換
const getProductName = computed(() => {
  switch (props.product) {
    case 'fx':
      return 'FXS';
    case 'sma':
      return 'SMA';
    case 'mthfr-import':
      return 'MTHFR';
    case 'nudt15':
      return 'NUDT15';
    case 'hd':
      return 'HTD';
    case 'apoe-import':
      return 'APOE';
    default:
      return props.product;
  }
})

// 儀器名稱轉換
const getInstrumentName = computed(() => {
  switch (props.instrument) {
    case 'qsep100':
      return 'Qsep 100';
    case 'qs3':
      return 'QuantStudio™ 3';
    case 'tower':
      return 'qTOWER³';
    case 'z480':
      return 'Roche Cobas® z 480';
    default:
      return props.instrument;
  }
})

// 試劑名稱轉換
const getReagentName = computed(() => {
  switch (props.reagent) {
    case 'accuinFx1':
      return 'ACCUiN BioTech Fragile X v1';
    case 'accuinFx2':
      return 'ACCUiN BioTech Fragile X v2';
    case 'accuinSma1':
      return 'ACCUiN BioTech SMA v1';
    case 'accuinSma2':
      return 'ACCUiN BioTech SMA v2';
    case 'accuinSma3':
      return 'ACCUiN BioTech SMA v3';
    case 'accuinSma4':
      return 'ACCUiN BioTech SMA v4';
    case 'accuinMTHFR1':
      return 'ACCUiN BioTech MTHFR v1';
    case 'accuinMTHFR2':
      return 'ACCUiN BioTech MTHFR v2';
    case 'accuinMTHFR3':
      return 'ACCUiN BioTech MTHFR v3';
    case 'accuinNUDT151':
      return 'ACCUiN BioTech NUDT15 v1';
    case 'accuinNUDT152':
      return 'ACCUiN BioTech NUDT15 v2';
    case 'accuinHD1':
      return 'ACCUiN BioTech HTD v1';
    case 'accuinApoe1':
      return 'ACCUiN BioTech APOE v1';
    default:
      return props.reagent;
  }
})

// QC 結果名稱轉換
const getQCResultLabel = computed(() => {
  switch (props.QCResult) {
    case 'meet-the-criteria':
      return 'Meet the criteria';
    case 'fail-the-criteria':
      return 'Fail the criteria';
    default:
      return props.QCResult;
  }
})

// QC 結果名稱顏色轉換
const getQCResultColor = computed(() => {
  switch (props.QCResult) {
    case 'meet-the-criteria':
      return 'text-green-7';
    case 'fail-the-criteria':
      return 'text-red-7';
    default:
      return 'text-grey-7';
  }
})

// QC Message 內容
const getQCMessageContent = computed(() => {
  if (props.QCMessage === 'N/A' || props.QCMessage === '') {
    return [{index: 0, message: 'There is no QC message.'}];
  }
  else {
    const messages = props.QCMessage.split(';');
    return messages.map((message, index) => ({index,message}));
  }
})

</script>
