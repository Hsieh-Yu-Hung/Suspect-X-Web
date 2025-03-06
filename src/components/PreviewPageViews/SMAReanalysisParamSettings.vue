<template>
  <q-card bordered>
    <q-card-section>
      <div class="text-h5 text-uppercase text-bold text-blue-grey-7">
        Parameters Settings
      </div>
      <q-card flat>
        <q-card-section class="col q-pb-none">
          <div class="row">
            <div class="text-weight-medium self-center text-blue-grey-8"></div>
          </div>
        </q-card-section>
      </q-card>
      <q-form class="q-gutter-sm col" @reset="onReset" @submit="console.log('submit')">
        <div class="row">
          <q-input
            v-model.number="ct_lowerbound"
            type="number"
            color="deep-orange-6"
            dense
            filled
            class="col-4"
            input-class="text-center"
          >
            <template v-slot:before>
              <div class="text-grey-7 text-subtitle1 text-bold">有效 CT 值範圍：</div>
            </template>
          </q-input>
          <div class="text-grey-7 text-body1 text-bold self-center flex flex-center col-2">-</div>
          <q-input
            v-model.number="ct_upperbound"
            type="number"
            color="deep-orange-6"
            dense
            filled
            class="col-3"
            input-class="text-center"
          />
        </div>

        <div class="row">
          <q-input
            v-model="smn1_factor"
            mask="#.##"
            fill-mask="0"
            reverse-fill-mask
            color="deep-orange-6"
            dense
            filled
            class="col-4"
            input-class="text-center"
          >
            <template v-slot:before>
              <div class="text-grey-7 text-subtitle1 text-bold">SMN1 校正值：</div>
            </template>
          </q-input>
          <q-input
            v-model="smn2_factor"
            mask="#.##"
            fill-mask="0"
            reverse-fill-mask
            color="deep-orange-6"
            dense
            filled
            class="col-4 q-ml-xl q-mr-lg"
            input-class="text-center"
          >
            <template v-slot:before>
              <div class="text-grey-7 text-subtitle1 text-bold">SMN2 校正值：</div>
            </template>
          </q-input>
        </div>

        <div class="row">
          <div class="text-grey-7 text-subtitle1 text-bold">允收範圍：</div>
        </div>
        <div class="row q-pl-xl q-pr-xl">
          <div class="col">
            <div class="text-teal-7 text-subtitle2 text-bold">
              SMN1
            </div>
            <div class="text-grey-7 text-caption">
              SC1: RNP CT <b>{{ (ctrl1.rnp).toFixed(2) }}</b> - SMN1 CT <b>{{ (ctrl1.smn1).toFixed(2) }}</b>
              = <b>{{ (ctrl1.rnp - ctrl1.smn1).toFixed(2) }}</b>
            </div>
            <div class="text-grey-7 text-caption">
              SC2: RNP CT <b>{{ (ctrl2.rnp).toFixed(2) }}</b> - SMN1 CT <b>{{ (ctrl2.smn1).toFixed(2) }}</b>
              = <b>{{ (ctrl2.rnp - ctrl2.smn1).toFixed(2) }}</b>
            </div>
            <q-range
              v-model="sc1_criteria_smn1"
              :min="0"
              :max="200"
              label-always
              color="teal-7"
              drag-range
              marker-labels
              switch-label-side
              :left-label-value="sc1_criteria_smn1.min/100"
              :right-label-value="sc1_criteria_smn1.max/100"
            >
              <template v-slot:marker-label-group="{ markerList }">
                <div v-for="val in markerList" :key="val">
                  <div
                    v-if="val.index === markerSMN1"
                    :class="markerList[val.index].classes"
                    :style="markerList[val.index].style"
                  >
                    <q-icon class="text-deep-orange-8 full-width" name="arrow_drop_up" size="md" />
                    <div class="text-grey-7 text-caption">
                      <b>{{ (ctrl2.rnp - ctrl2.smn1).toFixed(2) }}</b> - <b>{{ (ctrl1.rnp - ctrl1.smn1).toFixed(2) }}</b>
                      = <b>{{ (markerList[val.index].value/100).toFixed(2) }}</b>
                    </div>
                  </div>
                </div>
              </template>
            </q-range>
          </div>
          <div class="col q-pl-xl">
            <div class="text-lime-10 text-subtitle2 text-bold">
              SMN2
            </div><div class="text-grey-7 text-caption">
              SC1: RNP CT <b>{{ (ctrl1.rnp).toFixed(2) }}</b> - SMN2 CT <b>{{ (ctrl1.smn2).toFixed(2) }}</b>
              = <b>{{ (ctrl1.rnp - ctrl1.smn2).toFixed(2) }}</b>
            </div>
            <div class="text-grey-7 text-caption">
              SC2: RNP CT <b>{{ (ctrl2.rnp).toFixed(2) }}</b> - SMN2 CT <b>{{ (ctrl2.smn2).toFixed(2) }}</b>
              = <b>{{ (ctrl2.rnp - ctrl2.smn2).toFixed(2) }}</b>
            </div>
            <q-range
              v-model="sc1_criteria_smn2"
              :min="0"
              :max="200"
              label-always
              color="lime-9"
              drag-range
              marker-labels
              switch-label-side
              :left-label-value="sc1_criteria_smn2.min/100"
              :right-label-value="sc1_criteria_smn2.max/100"
            >
              <template v-slot:marker-label-group="{ markerList }">
                <div v-for="val in markerList" :key="val">
                  <div
                    v-if="val.index === markerSMN2"
                    :class="markerList[val.index].classes"
                    :style="markerList[val.index].style"
                  >
                    <q-icon class="text-deep-orange-8 full-width" name="arrow_drop_up" size="md" />
                    <div class="text-grey-7 text-caption">
                      <b>{{ (ctrl2.rnp - ctrl2.smn2).toFixed(2) }}</b> - <b>{{ (ctrl1.rnp - ctrl1.smn2).toFixed(2) }}</b>
                      = <b>{{ (markerList[val.index].value/100).toFixed(2) }}</b>
                    </div>
                  </div>
                </div>
              </template>
            </q-range>
          </div>
        </div>

        <div class="row q-mt-lg">
          <div class="text-grey-7 text-subtitle1 text-bold">SMN1 判定範圍 (RNP-SMN1)：</div>
        </div>
        <div class="row">
          <q-input
            v-model.number="smn1Ratio"
            type="number"
            color="deep-orange-6"
            dense
            outlined
            stack-label
            class="q-ml-xl col-1"
            input-class="text-center"
            suffix="%"
            label="間距比例："
          ></q-input>
          <q-radio
            class="text-overline text-blue-7"
            color="blue-7"
            v-model="smn1Analyzer"
            checked-icon="task_alt"
            :val="0"
            label="Analyzer QS3"
            unchecked-icon="panorama_fish_eye"
          />
          <q-radio
            class="text-overline text-blue-10"
            color="blue-10"
            v-model="smn1Analyzer"
            checked-icon="task_alt"
            :val="1"
            label="Analyzer QS3L"
            unchecked-icon="panorama_fish_eye"
          />
          <q-radio
            class="text-overline text-green-8"
            color="green-8"
            v-model="smn1Analyzer"
            checked-icon="task_alt"
            :val="3"
            label="Analyzer Z480"
            unchecked-icon="panorama_fish_eye"
          />
          <q-radio
            class="text-overline text-purple-6"
            color="purple-6"
            v-model="smn1Analyzer"
            checked-icon="task_alt"
            :val="2"
            label="Custom"
            unchecked-icon="panorama_fish_eye"
          />
        </div>
        <div class="row q-pl-xl q-pr-xl">
          <vue-slider
            class="full-width q-mb-lg q-mt-xl"
            :lazy="false"
            :process="false"
            :drag-on-click="false"
            :tooltip="'always'"
            :data="getSmn1Data()"
            :marks="getSmn1Marks()"
            :tooltip-style="getSmn1TooltipStyle()"
            v-model="smn1Slider"
          ></vue-slider>
        </div>

        <div class="row">
          <div class="text-grey-7 text-subtitle1 text-bold">SMN2 判定範圍 (RNP-SMN2)：</div>
        </div>
        <div class="row">
          <q-input
            v-model.number="smn2Ratio"
            type="number"
            color="deep-orange-6"
            dense
            outlined
            stack-label
            class="q-ml-xl col-1"
            input-class="text-center"
            suffix="%"
            label="間距比例："
          ></q-input>
          <q-radio
            class="text-overline text-blue-7"
            color="blue-7"
            v-model="smn2Analyzer"
            checked-icon="task_alt"
            :val="0"
            label="Analyzer QS3"
            unchecked-icon="panorama_fish_eye"
          />
          <q-radio
            class="text-overline text-blue-10"
            color="blue-10"
            v-model="smn2Analyzer"
            checked-icon="task_alt"
            :val="1"
            label="Analyzer QS3L"
            unchecked-icon="panorama_fish_eye"
          />
          <q-radio
            class="text-overline text-green-8"
            color="green-8"
            v-model="smn2Analyzer"
            checked-icon="task_alt"
            :val="3"
            label="Analyzer Z480"
            unchecked-icon="panorama_fish_eye"
          />
          <q-radio
            class="text-overline text-purple-6"
            color="purple-6"
            v-model="smn2Analyzer"
            checked-icon="task_alt"
            :val="2"
            label="Custom"
            unchecked-icon="panorama_fish_eye"
          />
        </div>
        <div class="row q-pl-xl q-pr-xl">
          <vue-slider
            class="full-width q-mb-lg q-mt-xl"
            :lazy="false"
            :process="false"
            :drag-on-click="false"
            :tooltip="'always'"
            :data="getSmn2Data()"
            :marks="getSmn2Marks()"
            :tooltip-style="getSmn2TooltipStyle()"
            v-model="smn2Slider"
          ></vue-slider>
        </div>

        <div class="row q-mt-lg justify-end">
          <q-btn label="Reset" icon="refresh" type="reset" flat color="blue-grey-7" />
          <q-btn label="Re-Analysis" type="submit" class="q-ml-lg" color="blue-grey-7" />
        </div>
      </q-form>
    </q-card-section>
  </q-card>
</template>

<script setup>
// 導入模組
import { useStore } from "vuex";
import { computed, onMounted, ref, watch} from "vue";
import moment from "moment";
import { useQuasar, QSpinnerFacebook } from "quasar";

// 暫時的設定
const tmp_parameters = {
  "SMN1_FACTOR": 0.47,
  "SMN2_FACTOR": 0.52,
  "smn1_threshold": [
      1.455,
      2.425,
      3.395
  ],
  "smn2_threshold": [
      -0.08500000000000002,
      0.7849999999999999,
      1.6549999999999998
  ]
}

const tmp_parameters2 = {
  "STD_CRITERIA_SMN1_2n1n": [
      0.87,
      1.46
  ],
  "STD_CRITERIA_SMN1_3n2n": [
      0.58,
      1.29
  ],
  "STD_CRITERIA_SMN2_2n1n": [
      0.75,
      1.44
  ],
  "STD_CRITERIA_SMN2_3n2n": [
      0.48,
      1.44
  ],
  "CT_UNDETERMINED_UPPERBOUND": 30,
  "smn1_threshold": [
      2.385,
      3.335,
      4.285
  ],
  "smn2_threshold": [
      0.928,
      2.31,
      3.69
  ]
}

// 取得 Quasar 和 Store
const $q = useQuasar();
const $store = useStore();

// 取得參數
const parameters = ref(tmp_parameters2);
const qc = ref('meet-the-criteria');
const markerSMN1 = computed(() => parseInt(($store.state.data.smaResult.qc.rnp_smn1_2n - $store.state.data.smaResult.qc.rnp_smn1_1n)*100));
const markerSMN2 = computed(() => parseInt(($store.state.data.smaResult.qc.rnp_smn2_2n - $store.state.data.smaResult.qc.rnp_smn2_1n)*100));
const ctrl1 = computed(() => $store.state.data.smaResult.control.ctrl1);
const ctrl2 = computed(() => $store.state.data.smaResult.control.ctrl2);
const importData = computed(() => $store.state.data.smaImportData);
const settingProps = computed(() => $store.state.data.settingProps);

// 設定變數
const smn1Analyzer = ref(0);
const smn2Analyzer = ref(0);
const smn1Ratio = ref(0);
const smn2Ratio = ref(0);
const smn1_factor = ref(parameters.value.default.SMN1_FACTOR ?? 0);
const smn2_factor = ref(parameters.value.default.SMN2_FACTOR ?? 0);
const ct_lowerbound = ref(parameters.value.default.CT_UNDETERMINED_LOWERBOUND ?? 0);
const ct_upperbound = ref(parameters.value.default.CT_UNDETERMINED_UPPERBOUND ?? 0);

const sc1_criteria_smn1 = ref(
  parameters.value.default.STD_CRITERIA_SMN1_2n1n
    ? {
        min: (parameters.value.default.STD_CRITERIA_SMN1_2n1n[0]*100).toFixed(2),
        max: (parameters.value.default.STD_CRITERIA_SMN1_2n1n[1]*100).toFixed(2),
      }
    : {
        min: 0,
        max: 0,
      }
);

const sc1_criteria_smn2 = ref(
  parameters.value.default.STD_CRITERIA_SMN2_2n1n
    ? {
        min: (parameters.value.default.STD_CRITERIA_SMN2_2n1n[0]*100).toFixed(2),
        max: (parameters.value.default.STD_CRITERIA_SMN2_2n1n[1]*100).toFixed(2),
      }
    : {
        min: 0,
        max: 0,
      }
);

const sc2_criteria_smn1 = ref(
  parameters.value.default.STD_CRITERIA_SMN1_3n2n
    ? {
        min: (parameters.value.default.STD_CRITERIA_SMN1_3n2n[0]*100).toFixed(2),
        max: (parameters.value.default.STD_CRITERIA_SMN1_3n2n[1]*100).toFixed(2),
      }
    : {
        min: 0,
        max: 0,
      }
);

const sc2_criteria_smn2 = ref(
  parameters.value.default.STD_CRITERIA_SMN2_3n2n
    ? {
        min: (parameters.value.default.STD_CRITERIA_SMN2_3n2n[0]*100).toFixed(2),
        max: (parameters.value.default.STD_CRITERIA_SMN2_3n2n[1]*100).toFixed(2),
      }
    : {
        min: 0,
        max: 0,
      }
);

const smn1Slider = ref([
  parameters.value.default.smn1_threshold[0].toFixed(2),
  parameters.value.default.smn1_threshold[1].toFixed(2),
  parameters.value.default.smn1_threshold[2].toFixed(2),
]);

const smn2Slider = ref([
  parameters.value.default.smn2_threshold[0].toFixed(2),
  parameters.value.default.smn2_threshold[1].toFixed(2),
  parameters.value.default.smn2_threshold[2].toFixed(2),
]);

function getSmn1Slider() {
  if (smn1Analyzer.value === 0) {
    smn1Slider.value = [
      parameters.value.v1.smn1_threshold[0].toFixed(2),
      parameters.value.v1.smn1_threshold[1].toFixed(2),
      parameters.value.v1.smn1_threshold[2].toFixed(2),
    ];
  } else if (smn1Analyzer.value === 1) {
    smn1Slider.value = [
      parameters.value.v2.smn1_threshold[0].toFixed(2),
      parameters.value.v2.smn1_threshold[1].toFixed(2),
      parameters.value.v2.smn1_threshold[2].toFixed(2),
    ];
  } else if (smn1Analyzer.value === 2) {
    if (parameters.value.custom.smn1_threshold) {
      smn1Slider.value = [
        parameters.value.custom.smn1_threshold[0].toFixed(2),
        parameters.value.custom.smn1_threshold[1].toFixed(2),
        parameters.value.custom.smn1_threshold[2].toFixed(2),
      ];
    }
  } else if (smn1Analyzer.value === 3) {
    if (parameters.value.v3.smn1_threshold) {
      smn1Slider.value = [
        parameters.value.v3.smn1_threshold[0].toFixed(2),
        parameters.value.v3.smn1_threshold[1].toFixed(2),
        parameters.value.v3.smn1_threshold[2].toFixed(2),
      ];
    }
  }
}

function getSmn2Slider() {
  if (smn2Analyzer.value === 0) {
    smn2Slider.value = [
      parameters.value.v1.smn2_threshold[0].toFixed(2),
      parameters.value.v1.smn2_threshold[1].toFixed(2),
      parameters.value.v1.smn2_threshold[2].toFixed(2),
    ];
  } else if (smn2Analyzer.value === 1) {
    smn2Slider.value = [
      parameters.value.v2.smn2_threshold[0].toFixed(2),
      parameters.value.v2.smn2_threshold[1].toFixed(2),
      parameters.value.v2.smn2_threshold[2].toFixed(2),
    ];
  } else if (smn2Analyzer.value === 2) {
    if (parameters.value.custom.smn2_threshold) {
      smn2Slider.value = [
        parameters.value.custom.smn2_threshold[0].toFixed(2),
        parameters.value.custom.smn2_threshold[1].toFixed(2),
        parameters.value.custom.smn2_threshold[2].toFixed(2),
      ];
    }
  } else if (smn2Analyzer.value === 3) {
    if (parameters.value.v3.smn2_threshold) {
      smn2Slider.value = [
        parameters.value.v3.smn2_threshold[0].toFixed(2),
        parameters.value.v3.smn2_threshold[1].toFixed(2),
        parameters.value.v3.smn2_threshold[2].toFixed(2),
      ];
    }
  }
}

function getSmn1TooltipStyle() {
  if (smn1Analyzer.value === 0) {
    return {
      backgroundColor: '#1e88e5',
      borderColor: '#1e88e5',
    }
  } else if (smn1Analyzer.value === 1) {
    return {
      backgroundColor: '#0d47a1',
      borderColor: '#0d47a1',
    }
  } else if (smn1Analyzer.value === 3) {
    return {
      backgroundColor: '#388e3c',
      borderColor: '#388e3c',
    }
  } else {
    return {
      backgroundColor: '#9c27b0',
      borderColor: '#9c27b0',
    }
  }
}

function getSmn1Marks() {
  let smn1_1n = qc.value.rnp_smn1_1n.toFixed(2);
  let smn1_2n = qc.value.rnp_smn1_2n.toFixed(2);
  let smn1_3n = qc.value.rnp_smn1_3n
    ? qc.value.rnp_smn1_3n.toFixed(2)
    : qc.value.smn1_3n.toFixed(2);
  let smn1_4n = qc.value.smn1_4n.toFixed(2);

  let style = {
    width: '8px',
    height: '8px',
    display: 'block',
    backgroundColor: '#757575',
    transform: 'translate(-2px, -2px)'
  };
  let labelStyle = {
    color: "#757575",
    'font-weight': 'bold',
  };
  let marks = {
    0: { label: "0N", style: style, labelStyle: labelStyle },
    [smn1_1n]: { label: `1N: ${smn1_1n}`, style: style, labelStyle: labelStyle },
    [smn1_2n]: { label: `2N: ${smn1_2n}`, style: style, labelStyle: labelStyle },
    [smn1_3n]: { label: `3N: ${smn1_3n}`, style: style, labelStyle: labelStyle },
    [smn1_4n]: { label: `4N: ${smn1_4n}`, style: style, labelStyle: labelStyle },
  };

  return marks;
}

function getSmn1Data() {
  let array = [];
  for (let i = 0; i <= qc.value.smn1_4n; i += 0.01) {
    array.push(i.toFixed(2));
  }
  return array;
}

function getSmn2TooltipStyle() {
  if (smn2Analyzer.value === 0) {
    return {
      backgroundColor: '#1e88e5',
      borderColor: '#1e88e5',
    }
  } else if (smn2Analyzer.value === 1) {
    return {
      backgroundColor: '#0d47a1',
      borderColor: '#0d47a1',
    }
  } else if (smn2Analyzer.value === 3) {
    return {
      backgroundColor: '#388e3c',
      borderColor: '#388e3c',
    }
  } else {
    return {
      backgroundColor: '#9c27b0',
      borderColor: '#9c27b0',
    }
  }
}

function getSmn2Marks() {
  let smn2_1n = qc.value.rnp_smn2_1n.toFixed(2);
  let smn2_2n = qc.value.rnp_smn2_2n.toFixed(2);
  let smn2_3n = qc.value.rnp_smn2_3n
    ? qc.value.rnp_smn2_3n.toFixed(2)
    : qc.value.smn2_3n.toFixed(2);
  let smn2_4n = qc.value.smn2_4n.toFixed(2);

  let style = {
    width: '8px',
    height: '8px',
    display: 'block',
    backgroundColor: '#757575',
    transform: 'translate(-2px, -2px)'
  };
  let labelStyle = {
    color: "#757575",
    'font-weight': 'bold',
  };
  let marks = {
    0: { label: "0N", style: style, labelStyle: labelStyle },
    [smn2_1n]: { label: `1N: ${smn2_1n}`, style: style, labelStyle: labelStyle },
    [smn2_2n]: { label: `2N: ${smn2_2n}`, style: style, labelStyle: labelStyle },
    [smn2_3n]: { label: `3N: ${smn2_3n}`, style: style, labelStyle: labelStyle },
    [smn2_4n]: { label: `4N: ${smn2_4n}`, style: style, labelStyle: labelStyle },
  };

  return marks;
}

function getSmn2Data() {
  let array = [];
  for (let i = 0; i <= qc.value.smn2_4n; i += 0.01) {
    array.push(i.toFixed(2));
  }
  return array;
}

function smnTypeInterpretation(smn1, smn2) {
  let type = String(smn1) + String(smn2);

  // Defined interpretation
  function isNormal(typeArray) {
    return [
      "20", "21", "22", "23", "24",
      "30", "31", "32", "33", "34",
      "41", "42", "43", "44",
    ].includes(typeArray);
  }

  function isCarrier(typeArray) {
    return ["10", "11", "12", "13", "14"].includes(typeArray);
  }

  function isAffected(typeArray) {
    return ["01", "02", "03", "04"].includes(typeArray);
  }

  if (isNormal(type)) {
    return {
      value: "normal",
      label: "Normal",
    };
  } else if (isCarrier(type)) {
    return {
      value: "carrier",
      label: "SMA carrier",
    };
  } else if (isAffected(type)) {
    return {
      value: "affected",
      label: "SMA affected",
    };
  } else {
    return {
      value: "invalid",
      label: "Invalid",
    };
  }
}

const onSubmit = () => {
  new Promise(async (resolve, reject) => {
    $q.loading.show({
      spinner: QSpinnerFacebook,
      spinnerColor: "deep-orange-6",
      spinnerSize: 100,
      message: "Re-analyzing...",
      messageColor: "white",
    });

    const para = {
      ...importData.value,
      analyzer: 'custom',
      parameters: {
        CT_UNDETERMINED_UPPERBOUND: ct_upperbound.value,
        CT_UNDETERMINED_LOWERBOUND: ct_lowerbound.value,
        STD_CRITERIA_SMN1_2n1n: [
          sc1_criteria_smn1.value.min/100,
          sc1_criteria_smn1.value.max/100,
        ],
        STD_CRITERIA_SMN2_2n1n: [
          sc1_criteria_smn2.value.min/100,
          sc1_criteria_smn2.value.max/100,
        ],
        STD_CRITERIA_SMN1_3n2n: [
          sc2_criteria_smn1.value.min/100,
          sc2_criteria_smn1.value.max/100,
        ],
        STD_CRITERIA_SMN2_3n2n: [
          sc2_criteria_smn2.value.min/100,
          sc2_criteria_smn2.value.max/100,
        ],
        SMN1_1N_THRESHOLD: smn1Slider.value[0],
        SMN1_2N_THRESHOLD: smn1Slider.value[1],
        SMN1_3N_THRESHOLD: smn1Slider.value[2],
        SMN2_1N_THRESHOLD: smn2Slider.value[0],
        SMN2_2N_THRESHOLD: smn2Slider.value[1],
        SMN2_3N_THRESHOLD: smn2Slider.value[2],
        SMN1_FACTOR: smn1_factor.value,
        SMN2_FACTOR: smn2_factor.value,
      }
    };

    try {
      const resultRaw = await analysis(para);
      const result = resultRaw.result;
      resolve({
        qc: result.qc,
        control: result.control,
        result: result.sample,
        logger: result.config.logger,
        parameters: {
          custom: para,
          default: parameters.value.default,
        }
      });
    } catch (err) {
      reject(err);
    }
  }).then((analysisResult) => {
    const qualityControlProps = {
      controlId: analysisResult.qc.run_id,
      instrument: settingProps.value.instrumentLabel,
      reagent: settingProps.value.reagentLabel,
      product: settingProps.value.productLabel,
      controlAssessment: analysisResult.qc.status,
      assessmentTime: moment(Date()).format("YYYY-MM-DD HH:mm:ss"),
      analysisMethod: [ "ACCUiN BioTech Analyzer Custom" ],
    };

    $store.commit("data/updateQualityControlProps", qualityControlProps);
    $store.commit("data/updateParameters", {
      v1: parameters.value.v1,
      v2: parameters.value.v2,
      v3: parameters.value.v3,
      custom: analysisResult.parameters.custom,
      default: analysisResult.parameters.default,
    });

    $store.commit("data/updateLog", analysisResult.logger);

    const sample = analysisResult.result.map(r => ({
      ...r,
      smn1Type: r.smn1_type,
      smn2Type: r.smn2_type,
    }));

    $store.commit("data/updateSmaResult", {
      control: analysisResult.control,
      qc: analysisResult.qc,
      sample: sample,
    });

    return qualityControlProps;
  }).then((qualityControlProps) => {
    const resultTableSmaProps = computed(
      () => $store.getters["data/resultTableSmaProps"]
    );

    const updated = resultTableSmaProps.value.map((row, index) => {
      const smn1 = row.smn1Type[0];
      const smn2 = row.smn2Type[0];
      const smnInterpretation = qualityControlProps.controlAssessment === 'meet-the-criteria'
        ? smnTypeInterpretation(smn1, smn2)
        : { value: 'inconclusive', label: 'Inconclusive' };

      return {
        index: index + 1,
        sampleId: row.sampleId,
        result: qualityControlProps.controlAssessment === 'meet-the-criteria'
          ? `${smn1}:${smn2}`
          : '-',
        resultLabel: qualityControlProps.controlAssessment === 'meet-the-criteria'
          ? [ `${smn1}:${smn2}` ]
          : ['-'],
        assessment: smnInterpretation.value.includes("affected")
          ? "affected"
          : smnInterpretation.value,
        assessmentLabel: smnInterpretation.label,
      };
    });

    $store.commit("data/updateExportResults", updated);
  }).then(() => {
    setTimeout(() => {
      $q.loading.hide();
      $q.notify({
        type: 'positive',
        message: `Re-analysis completed.`,
      });
    }, 3000);
  }).catch(err => {
    console.error(err);
    $q.loading.hide();
    $q.notify({
      type: 'negative',
      message: `Re-analysis failed.`,
    });
  });
};

const onReset = () => {
  smn1Analyzer.value = importData.value.instrument === 'custom'
    ? 2
    : importData.value.instrument === 'qs3'
      ? 0
      : importData.value.instrument === 'z480'
        ? 3
        : 1;
  smn2Analyzer.value = importData.value.instrument === 'custom'
    ? 2
    : importData.value.instrument === 'qs3'
      ? 0
      : importData.value.instrument === 'z480'
        ? 3
        : 1;
  smn1_factor.value = parameters.value.default.SMN1_FACTOR ?? 0;
  smn2_factor.value = parameters.value.default.SMN2_FACTOR ?? 0;
  ct_lowerbound.value = parameters.value.default.CT_UNDETERMINED_LOWERBOUND ?? 0;
  ct_upperbound.value = parameters.value.default.CT_UNDETERMINED_UPPERBOUND ?? 0;
  sc1_criteria_smn1.value = parameters.value.default.STD_CRITERIA_SMN1_2n1n
    ? {
      min: (parameters.value.default.STD_CRITERIA_SMN1_2n1n[0]*100).toFixed(2),
      max: (parameters.value.default.STD_CRITERIA_SMN1_2n1n[1]*100).toFixed(2),
    }
    : {
      min: 0,
      max: 0,
    };
  sc1_criteria_smn2.value = parameters.value.default.STD_CRITERIA_SMN2_2n1n
    ? {
      min: (parameters.value.default.STD_CRITERIA_SMN2_2n1n[0]*100).toFixed(2),
      max: (parameters.value.default.STD_CRITERIA_SMN2_2n1n[1]*100).toFixed(2),
    }
    : {
      min: 0,
      max: 0,
    };
  sc2_criteria_smn1.value = parameters.value.default.STD_CRITERIA_SMN1_3n2n
    ? {
      min: (parameters.value.default.STD_CRITERIA_SMN1_3n2n[0]*100).toFixed(2),
      max: (parameters.value.default.STD_CRITERIA_SMN1_3n2n[1]*100).toFixed(2),
    }
    : {
      min: 0,
      max: 0,
    };
  sc2_criteria_smn2.value = parameters.value.default.STD_CRITERIA_SMN2_3n2n
    ? {
      min: (parameters.value.default.STD_CRITERIA_SMN2_3n2n[0]*100).toFixed(2),
      max: (parameters.value.default.STD_CRITERIA_SMN2_3n2n[1]*100).toFixed(2),
    }
    : {
      min: 0,
      max: 0,
    };
  smn1Slider.value = [
    parameters.value.default.smn1_threshold[0].toFixed(2),
    parameters.value.default.smn1_threshold[1].toFixed(2),
    parameters.value.default.smn1_threshold[2].toFixed(2),
  ];
  smn2Slider.value = [
    parameters.value.default.smn2_threshold[0].toFixed(2),
    parameters.value.default.smn2_threshold[1].toFixed(2),
    parameters.value.default.smn2_threshold[2].toFixed(2),
  ];
};

watch(smn1Analyzer, () => {
  getSmn1Slider();
});

watch(smn2Analyzer, () => {
  getSmn2Slider();
});

watch(smn1Ratio, () => {
  if (smn1Ratio.value === 0) {
    smn1Analyzer.value = 0;
  } else {
    smn1Analyzer.value = 2;
    if (smn1Ratio.value !== 0) {
      smn1Slider.value = [
        (((qc.value.rnp_smn1_2n-qc.value.rnp_smn1_1n)*smn1Ratio.value/100)+qc.value.rnp_smn1_1n).toFixed(2),
        (((qc.value.smn1_3n-qc.value.rnp_smn1_2n)*smn1Ratio.value/100)+qc.value.rnp_smn1_2n).toFixed(2),
        (((qc.value.smn1_4n-qc.value.smn1_3n)*smn1Ratio.value/100)+qc.value.smn1_3n).toFixed(2),
      ];
    }
  }
});

watch(smn2Ratio, () => {
  if (smn2Ratio.value === 0) {
    smn2Analyzer.value = 0;
  } else {
    smn2Analyzer.value = 2;
    if (smn2Ratio.value !== 0) {
      smn2Slider.value = [
        (((qc.value.rnp_smn2_2n-qc.value.rnp_smn2_1n)*smn2Ratio.value/100)+qc.value.rnp_smn2_1n).toFixed(2),
        (((qc.value.smn2_3n-qc.value.rnp_smn2_2n)*smn2Ratio.value/100)+qc.value.rnp_smn2_2n).toFixed(2),
        (((qc.value.smn2_4n-qc.value.smn2_3n)*smn2Ratio.value/100)+qc.value.smn2_3n).toFixed(2),
      ];
    }
  }
});

watch(smn1Slider, () => {
  if (smn1Analyzer.value === 0) {
    smn1Ratio.value = 0;
    for (let i in smn1Slider.value) {
      if (smn1Slider.value[i] !== parameters.value.v1.smn1_threshold[i].toFixed(2)) {
        smn1Analyzer.value = 2;
      }
    }
  } else if (smn1Analyzer.value === 1) {
    smn1Ratio.value = 50;
    for (let i in smn1Slider.value) {
      if (smn1Slider.value[i] !== parameters.value.v2.smn1_threshold[i].toFixed(2)) {
        smn1Analyzer.value = 2;
      }
    }
  } else if (smn1Analyzer.value === 3) {
    smn1Ratio.value = 50;
    for (let i in smn1Slider.value) {
      if (smn1Slider.value[i] !== parameters.value.v3.smn1_threshold[i].toFixed(2)) {
        smn1Analyzer.value = 2;
      }
    }
  }
});

watch(smn2Slider, () => {
  if (smn2Analyzer.value === 0) {
    smn2Ratio.value = 0;
    for (let i in smn2Slider.value) {
      if (smn2Slider.value[i] !== parameters.value.v1.smn2_threshold[i].toFixed(2)) {
        smn2Analyzer.value = 2;
      }
    }
  } else if (smn2Analyzer.value === 1) {
    smn2Ratio.value = 50;
    for (let i in smn2Slider.value) {
      if (smn2Slider.value[i] !== parameters.value.v2.smn2_threshold[i].toFixed(2)) {
        smn2Analyzer.value = 2;
      }
    }
  } else if (smn2Analyzer.value === 3) {
    smn2Ratio.value = 50;
    for (let i in smn2Slider.value) {
      if (smn2Slider.value[i] !== parameters.value.v3.smn2_threshold[i].toFixed(2)) {
        smn2Analyzer.value = 2;
      }
    }
  }
});

onMounted(() => {
  onReset();
});
</script>
