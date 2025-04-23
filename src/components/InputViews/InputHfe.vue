<template>
  <q-card bordered>
    <q-card-section>
      <div class="text-h5 text-uppercase text-bold text-blue-grey-7">
        Input
      </div>
      <div class="text-subtitle1">
        Please input the HFE corresponding sample results.
      </div>
      <div class="row q-pb-lg q-gutter-sm">
        <div class="col">
          <q-file
            v-model="subjectListFile"
            use-chips
            color="deep-orange-6"
            label="Subject information list file from LIMS (.xls/.xlsx)"
            accept=".xls, .xlsx"
            lazy-rules
            dense
          >
            <template v-slot:before>
              <q-icon name="mdi-microsoft-excel" />
            </template>
          </q-file>
        </div>
        <div class="col-3 flex justify-center" style="width: fit-content;">
          <q-btn
            label="Download Template"
            color="grey-7"
            icon="mdi-file-download"
            flat
            dense
            @click="downloadTemplate"
          />
        </div>
      </div>
      <div class="row">
        <q-table
          :rows="inputRows"
          :columns="inputColumns"
          class="col"
          :v-model:pagination="{ rowsPerPage: 0 }"
          :rows-per-page-options="[0]"
          row-key="index"
          flat
          dense
          virtual-scroll
        >
          <template v-slot:body-cell-add="props">
            <!-- <q-td class="text-center" style="max-width: 50px"> -->
            <q-td class="text-center">
              <q-btn
                size="sm"
                text-color="blue-grey-7"
                icon="add"
                round
                dense
                flat
                @click="addRow(props.key)"
              />
            </q-td>
          </template>
          <template v-slot:body-cell-remove="props">
            <!-- <q-td class="text-center" style="max-width: 50px"> -->
            <q-td class="text-center">
              <q-btn
                v-if="inputRows.length !== 1"
                size="sm"
                text-color="blue-grey-7"
                icon="remove"
                round
                dense
                flat
                @click="removeRow(props.key)"
              />
            </q-td>
          </template>
          <template v-slot:body-cell-sampleId="props">
            <q-td style="min-width: 180px">
              <q-input
                v-model="updateInput[props.key].sampleId"
                @update:model-value="(val) => updateInput = {index: props.key, col: ['sampleId'], update: val}"
                color="deep-orange"
                class="q-mx-lg"
              />
            </q-td>
          </template>
          <template v-slot:body-cell-h63d="props">
            <q-td class="col text-overline">
              <div :class="props.row.h63d.wt
                ? 'row justify-center text-indigo text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.h63d.wt ? 'indigo' : 'blue-grey'"
                  v-model="updateInput[props.key].h63d.wt"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['h63d', 'wt'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="WT (155 bp)"
                  dense
                />
              </div>
              <div :class="props.row.h63d.mut
                ? 'row justify-center text-indigo text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.h63d.mut ? 'indigo' : 'blue-grey'"
                  v-model="updateInput[props.key].h63d.mut"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['h63d', 'mut'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="MUT (254 bp)"
                  dense
                />
              </div>
              <div :class="props.row.h63d.ic
                ? 'row justify-center text-indigo text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.h63d.ic ? 'indigo' : 'blue-grey'"
                  v-model="updateInput[props.key].h63d.ic"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['h63d', 'ic'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="IC (364 bp)"
                  dense
                />
              </div>
            </q-td>
          </template>
          <template v-slot:body-cell-s65c="props">
            <q-td class="col text-overline">
              <div :class="props.row.s65c.wt
                ? 'row justify-center text-blue text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.s65c.wt ? 'blue' : 'blue-grey'"
                  v-model="updateInput[props.key].s65c.wt"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['s65c', 'wt'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="WT (149 bp)"
                  dense
                />
              </div>
              <div :class="props.row.s65c.mut
                ? 'row justify-center text-blue text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.s65c.mut ? 'blue' : 'blue-grey'"
                  v-model="updateInput[props.key].s65c.mut"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['s65c', 'mut'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="MUT (260 bp)"
                  dense
                />
              </div>

              <div :class="props.row.s65c.ic
                ? 'row justify-center text-blue text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.s65c.ic ? 'blue' : 'blue-grey'"
                  v-model="updateInput[props.key].s65c.ic"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['s65c', 'ic'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="IC (364 bp)"
                  dense
                />
              </div>
            </q-td>
          </template>
          <template v-slot:body-cell-wt="props">
            <q-td class="col text-overline">
              <div :class="props.row.wt.wt
                ? 'row justify-center text-cyan text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.wt.wt ? 'cyan' : 'blue-grey'"
                  v-model="updateInput[props.key].wt.wt"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['wt', 'wt'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="WT (208 bp)"
                  dense
                />
              </div>
              <div :class="props.row.wt.ic
                ? 'row justify-center text-cyan text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.wt.ic ? 'cyan' : 'blue-grey'"
                  v-model="updateInput[props.key].wt.ic"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['wt', 'ic'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="IC (461 bp)"
                  dense
                />
              </div>
            </q-td>
          </template>
          <template v-slot:body-cell-mut="props">
            <q-td class="col text-overline">
              <div :class="props.row.mut.mut
                ? 'row justify-center text-teal text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.mut.mut ? 'teal' : 'blue-grey'"
                  v-model="updateInput[props.key].mut.mut"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['mut', 'mut'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="MUT (319 bp)"
                  dense
                />
              </div>
              <div :class="props.row.mut.ic
                ? 'row justify-center text-teal text-bold'
                : 'row justify-center text-blue-grey text-bold'"
              >
                <q-checkbox
                  keep-color
                  left-label
                  size="lg"
                  :color="props.row.mut.ic ? 'teal' : 'blue-grey'"
                  v-model="updateInput[props.key].mut.ic"
                  @update:model-value="(val) => updateInput = {index: props.key, col: ['mut', 'ic'], update: val}"
                  checked-icon="add_circle"
                  unchecked-icon="remove_circle"
                  label="IC (461 bp)"
                  dense
                />
              </div>
            </q-td>
          </template>
          <template v-slot:body-cell-result="props">
            <q-td
              class='col text-center text-blue-grey text-bold'
            >
              <div
                class="row justify-center"
                v-for="label in updateInput[props.key].resultLabel"
                :key="label"
              >
                {{ label }}
              </div>
            </q-td>
          </template>
          <template v-slot:body-cell-assessment="props">
            <q-td class="text-center">
              <q-chip
                class="text-grey-9"
                :color="assessmentColor(updateInput[props.key].assessment)"
                :label="updateInput[props.key].assessmentLabel"
              />
            </q-td>
          </template>
        </q-table>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useStore } from "vuex";
import { useQuasar } from 'quasar';
import { extract, downloadTemplate } from "@/composables/useExtract";
import { updateGetUserInfo } from "@/composables/accessStoreUserInfo";
import { uploadFile_to_category } from "@/composables/storageManager";

// 使用 store, Quasar
const store = useStore();
const $q = useQuasar();

// 使用者身份
const is_login = ref(false);
const user_info = ref(null);
const currentSettingProps = ref(null);
const subjectListFile = ref(null);

// Input result table
const inputRows = ref([{
  sampleId: '',
  h63d: {
    ic: true,
    mut: false,
    wt: true,
  },
  s65c: {
    ic: true,
    mut: false,
    wt: true,
  },
  wt: {
    ic: true,
    wt: true,
  },
  mut: {
    ic: true,
    mut: false,
  },
  result: 'wt/wt',
  resultLabel: ['HFE基因型wild-type/wild-type'],
  assessment: 'normal-risk',
  assessmentLabel: '一般風險基因型',
}]);

const inputColumns = [
  {
    name: 'add',
    field: 'add',
  },
  {
    name: 'remove',
    field: 'remove',
  },
  {
    name: 'index',
    label: '#',
    field: 'index',
    sortable: true,
  },
  {
    name: "sampleId",
    label: "Sample ID",
    align: "center",
    field: "sampleId",
  },

  // HFE
  {
    name: "h63d",
    label: "H63D PCR",
    field: "h63d",
    align: "center",
  },
  {
    name: "s65c",
    label: "S65C PCR",
    field: "s65c",
    align: "center",
  },
  {
    name: "wt",
    label: "C282Y wt PCR",
    field: "wt",
    align: "center",
  },
  {
    name: "mut",
    label: "C282Y mut PCR",
    field: "mut",
    align: "center",
  },

  {
    name: "result",
    label: "Result",
    field: "resultLabel",
    align: "center",
  },
  {
    name: "assessment",
    label: "Assessment",
    field: "assessmentLabel",
    align: "center",
  },
];

const resultAssessment = (row) => {
  const list = [
    row.h63d.ic, row.h63d.mut, row.h63d.wt,
    row.s65c.ic, row.s65c.mut, row.s65c.wt,
    row.wt.ic, row.wt.wt,
    row.mut.ic, row.mut.mut,
  ];
  if (
    list[0] && !list[1] && list[2] &&
    list[3] && !list[4] && list[5] &&
    list[6] && list[7] &&
    list[8] && !list[9]
  ) {
    return {
      result: 'wt/wt',
      resultLabel: ['HFE基因型wild-type/wild-type'],
      assessment: 'normal-risk',
      assessmentLabel: '一般風險基因型',
    }
  } else if (
    list[0] && !list[1] && list[2] &&
    list[3] && !list[4] && list[5] &&
    list[6] && list[7] &&
    list[8] && list[9]
  ) {
    return {
      result: 'c282y/wt',
      resultLabel: ['HFE基因型C282Y/wild-type'],
      assessment: 'normal-risk',
      assessmentLabel: '一般風險基因型',
    }
  } else if (
    list[0] && !list[1] && list[2] &&
    list[3] && !list[4] && list[5] &&
    list[6] && !list[7] &&
    list[8] && list[9]
  ) {
    return {
      result: 'c282y/c282y',
      resultLabel: ['HFE基因型C282Y/C282Y'],
      assessment: 'high-risk',
      assessmentLabel: '高風險基因型',
    }
  } else if (
    list[0] && !list[1] && list[2] &&
    list[3] && list[4] && !list[5] &&
    list[6] && list[7] &&
    list[8] && !list[9]
  ) {
    return {
      result: 's65c/s65c',
      resultLabel: ['HFE基因型S65C/S65C'],
      assessment: 'normal-risk',
      assessmentLabel: '一般風險基因型',
    }
  } else if (
    list[0] && !list[1] && list[2] &&
    list[3] && list[4] && !list[5] &&
    list[6] && list[7] &&
    list[8] && list[9]
  ) {
    return {
      result: 'c282y/s65c',
      resultLabel: ['HFE基因型C282Y/S65C'],
      assessment: 'high-risk',
      assessmentLabel: '高風險基因型',
    }
  } else if (
    list[0] && !list[1] && list[2] &&
    list[3] && list[4] && !list[5] &&
    list[6] && !list[7] &&
    list[8] && list[9]
  ) {
    return {
      result: 'c282y/c282y_c282y/s65c',
      resultLabel: ['HFE基因型C282Y/C282Y', 'HFE基因型C282Y/S65C'],
      assessment: 'high-risk',
      assessmentLabel: '高風險基因型',
    }
  } else if (
    list[0] && !list[1] && list[2] &&
    list[3] && list[4] && list[5] &&
    list[6] && list[7] &&
    list[8] && !list[9]
  ) {
    return {
      result: 's65c/wt',
      resultLabel: ['HFE基因型S65C/wild-type'],
      assessment: 'normal-risk',
      assessmentLabel: '一般風險基因型',
    }
  } else if (
    list[0] && !list[1] && list[2] &&
    list[3] && list[4] && list[5] &&
    list[6] && list[7] &&
    list[8] && list[9]
  ) {
    return {
      result: 'c282y/s65c',
      resultLabel: ['HFE基因型C282Y/S65C'],
      assessment: 'high-risk',
      assessmentLabel: '高風險基因型',
    }
  } else if (
    list[0] && !list[1] && list[2] &&
    list[3] && list[4] && list[5] &&
    list[6] && !list[7] &&
    list[8] && list[9]
  ) {
    return {
      result: 'c282y/c282y_c282y/s65c',
      resultLabel: ['HFE基因型C282Y/C282Y', 'HFE基因型C282Y/S65C'],
      assessment: 'high-risk',
      assessmentLabel: '高風險基因型',
    }
  } else if (
    list[0] && list[1] && !list[2] &&
    list[3] && !list[4] && list[5] &&
    list[6] && list[7] &&
    list[8] && !list[9]
   ) {
    return {
      result: 'h63d/h63d',
      resultLabel: ['HFE基因型H63D/H63D'],
      assessment: 'normal-risk',
      assessmentLabel: '一般風險基因型',
    }
  } else if (
    list[0] && list[1] && !list[2] &&
    list[3] && !list[4] && list[5] &&
    list[6] && list[7] &&
    list[8] && list[9]
  ) {
    return {
      result: 'c282y/h63d',
      resultLabel: ['HFE基因型C282Y/H63D'],
      assessment: 'high-risk',
      assessmentLabel: '高風險基因型',
    }
  } else if (
    list[0] && list[1] && !list[2] &&
    list[3] && !list[4] && list[5] &&
    list[6] && !list[7] &&
    list[8] && list[9]
  ) {
    return {
      result: 'c282y/c282y_c282y/h63d',
      resultLabel: ['HFE基因型C282Y/C282Y', 'HFE基因型C282Y/H63D'],
      assessment: 'high-risk',
      assessmentLabel: '高風險基因型',
    }
  } else if (
    list[0] && list[1] && !list[2] &&
    list[3] && list[4] && !list[5] &&
    list[6] && list[7] &&
    list[8] && !list[9]
  ) {
    return {
      result: 'h63d/s65c',
      resultLabel: ['HFE基因型H63D/S65C'],
      assessment: 'normal-risk',
      assessmentLabel: '一般風險基因型',
    }
  } else if (
    list[0] && list[1] && !list[2] &&
    list[3] && list[4] && !list[5] &&
    list[6] && list[7] &&
    list[8] && list[9]
  ) {
    return {
      result: 'c282y/h63d_c282y/s65c',
      resultLabel: ['HFE基因型C282Y/H63D', 'HFE基因型C282Y/S65C'],
      assessment: 'high-risk',
      assessmentLabel: '高風險基因型',
    }
  } else if (
    list[0] && list[1] && !list[2] &&
    list[3] && list[4] && !list[5] &&
    list[6] && !list[7] &&
    list[8] && list[9]
  ) {
    return {
      result: 'c282y/c282y_c282y/h63d_c282y/s65c',
      resultLabel: ['HFE基因型C282Y/C282Y', 'HFE基因型C282Y/H63D', 'HFE基因型C282Y/S65C'],
      assessment: 'high-risk',
      assessmentLabel: '高風險基金型',
    }
  } else if (
    list[0] && list[1] && !list[2] &&
    list[3] && list[4] && list[5] &&
    list[6] && list[7] &&
    list[8] && !list[9]
  ) {
    return {
      result: 'h63d/s65c',
      resultLabel: ['HFE基因型H63D/S65C'],
      assessment: 'normal-risk',
      assessmentLabel: '一般風險基因型',
    }
  } else if (
    list[0] && list[1] && !list[2] &&
    list[3] && list[4] && list[5] &&
    list[6] && list[7] &&
    list[8] && list[9]
  ) {
    return {
      result: 'c282y/h63d_c282y/s65c',
      resultLabel: ['HFE基因型C282Y/H63D', 'HFE基因型C282Y/S65C'],
      assessment: 'high-risk',
      assessmentLabel: '高風險基因型',
    }
  } else if (
    list[0] && list[1] && !list[2] &&
    list[3] && list[4] && list[5] &&
    list[6] && !list[7] &&
    list[8] && list[9]
  ) {
    return {
      result: 'c282y/c282y_c282y/h63d_c282y/s65c',
      resultLabel: ['HFE基因型C282Y/C282Y', 'HFE基因型C282Y/H63D', 'HFE基因型C282Y/S65C'],
      assessment: 'high-risk',
      assessmentLabel: '高風險基因型',
    }
  } else if (
    list[0] && list[1] && list[2] &&
    list[3] && !list[4] && list[5] &&
    list[6] && list[7] &&
    list[8] && !list[9]
  ) {
    return {
      result: 'h63d/wt',
      resultLabel: ['HFE基因型H63D/wild-type'],
      assessment: 'normal-risk',
      assessmentLabel: '一般風險基因型',
    }
  } else if (
    list[0] && list[1] && list[2] &&
    list[3] && !list[4] && list[5] &&
    list[6] && list[7] &&
    list[8] && list[9]
  ) {
    return {
      result: 'c282y/h63d',
      resultLabel: ['HFE基因型C282Y/H63D'],
      assessment: 'high-risk',
      assessmentLabel: '高風險基因型',
    }
  } else if (
    list[0] && list[1] && list[2] &&
    list[3] && !list[4] && list[5] &&
    list[6] && !list[7] &&
    list[8] && list[9]
  ) {
    return {
      result: 'c282y/c282y_c282y/h63d',
      resultLabel: ['HFE基因型C282Y/C282Y', 'HFE基因型C282Y/H63D'],
      assessment: 'high-risk',
      assessmentLabel: '高風險基因型',
    }
  } else if (
    list[0] && list[1] && list[2] &&
    list[3] && list[4] && !list[5] &&
    list[6] && list[7] &&
    list[8] && !list[9]
  ) {
    return {
      result: 'h63d/h65c',
      resultLabel: ['HFE基因型H63D/H65C'],
      assessment: 'normal-risk',
      assessmentLabel: '一般風險基因型',
    }
  } else if (
    list[0] && list[1] && list[2] &&
    list[3] && list[4] && !list[5] &&
    list[6] && list[7] &&
    list[8] && list[9]
  ) {
    return {
      result: 'c282y/h63d_c282y/s65c',
      resultLabel: ['HFE基因型C282Y/H63D', 'HFE基因型C282Y/S65C'],
      assessment: 'high-risk',
      assessmentLabel: '高風險基因型',
    }
  } else if (
    list[0] && list[1] && list[2] &&
    list[3] && list[4] && !list[5] &&
    list[6] && !list[7] &&
    list[8] && list[9]
  ) {
    return {
      result: 'c282y/c282y_c282y/h63d_c282y/s65c',
      resultLabel: ['HFE基因型C282Y/C282Y', 'HFE基因型C282Y/H63D', 'HFE基因型C282Y/S65C'],
      assessment: 'high-risk',
      assessmentLabel: '高風險基因型',
    }
  } else if (
    list[0] && list[1] && list[2] &&
    list[3] && list[4] && list[5] &&
    list[6] && list[7] &&
    list[8] && !list[9]
  ) {
    return {
      result: 'h63d/h65c',
      resultLabel: ['HFE基因型H63D/H65C'],
      assessment: 'noraml-risk',
      assessmentLabel: '一般風險基因型',
    }
  } else if (
    list[0] && list[1] && list[2] &&
    list[3] && list[4] && list[5] &&
    list[6] && list[7] &&
    list[8] && list[9]
  ) {
    return {
      result: 'c282y/h63d_c282y/s65c',
      resultLabel: ['HFE基因型C282Y/H63D', 'HFE基因型C282Y/S65C'],
      assessment: 'high-risk',
      assessmentLabel: '高風險基因型',
    }
  } else if (
    list[0] && list[1] && !list[2] &&
    list[3] && list[4] && list[5] &&
    list[6] && !list[7] &&
    list[8] && list[9]
  ) {
    return {
      result: 'c282y/c282y_c282y/h63d_c282y/s65c',
      resultLabel: ['HFE基因型C282Y/C282Y', 'HFE基因型C282Y/H63D', 'HFE基因型C282Y/S65C'],
      assessment: 'high-risk',
      assessmentLabel: '高風險基因型',
    }
  } else {
    return {
      result: '-',
      resultLabel: ['-'],
      assessment: 'invalid',
      assessmentLabel: 'Invalid',
    }
  }
};

const assessmentColor = (assessment) => {
  if (assessment === "low-risk") {
    return "green-13";
  } else if (assessment === "normal-risk") {
    return "orange-5";
  } else if (assessment === "high-risk") {
    return "red";
  } else {
    return "grey-5";
  }
};

const updateInput = computed({
  get: () => {
    let updatedInput = {};
    inputRows.value.map(sample => {
      updatedInput[sample.index] = {
        ...sample,
        result: resultAssessment(sample).result,
        resultLabel: resultAssessment(sample).resultLabel,
        assessment: resultAssessment(sample).assessment,
        assessmentLabel: resultAssessment(sample).assessmentLabel,
      };
    })
    return updatedInput
  },
  set: (val) => {
    if (val.col.length === 1) {
      inputRows.value[val.index - 1][val.col[0]] = val.update;
    } else if (val.col.length === 2) {
      inputRows.value[val.index - 1][val.col[0]][val.col[1]] = val.update;
    }
  }
});

inputRows.value.forEach((row, index) => {
  row.index = index + 1;
});

onMounted(() => {

  // 取得使用者身份
  const { login_status } = updateGetUserInfo();
  is_login.value = login_status.value.is_login;
  user_info.value = login_status.value.user_info;

  // 取得 setting props
  currentSettingProps.value = store.getters["analysis_setting/getSettingProps"];

  // 若 store 有資料則載入
  const storeData = store.getters["export_page_setting/getExportResults"];
  if (storeData.length > 0 && currentSettingProps.value.product === 'hfe') {
    inputRows.value = storeData.map(p => {
      return {
        index: p.index,
        sampleId: p.sampleId,
        h63d: {
          ic: p.h63d_ic,
          mut: p.h63d_mut,
          wt: p.h63d_wt,
        },
        s65c: {
          ic: p.s65c_ic,
          mut: p.s65c_mut,
          wt: p.s65c_wt,
        },
        wt: {
          ic: p.wt_ic,
          wt: p.wt_wt,
        },
        mut: {
          ic: p.mut_ic,
          mut: p.mut_mut,
        },
        result: p.result,
        resultLabel: p.resultLabel,
        assessment: p.assessment,
        assessmentLabel: p.assessmentLabel,

        // 新增以下屬性
        birth: p.birth ? p.birth : '',
        collectingDate: p.collectingDate ? p.collectingDate : '',
        edit: p.edit ? p.edit : '',
        gender: p.gender ? p.gender : '',
        idNumber: p.idNumber ? p.idNumber : '',
        name: p.name ? p.name : '',
        receivedDate: p.receivedDate ? p.receivedDate : '',
        type: p.type ? p.type : '',
      }
    });
  }
});

// Watch handlers
watch(subjectListFile, async (newVal, oldVal) => {
  if (newVal && newVal !== oldVal) {

    // 取得使用者身份
    const user_uid = user_info.value.uid;
    const analysis_uuid = 'LIMS_files';
    const category = 'subject_info';

    // 顯示 loading 視窗
    $q.loading.show();

    // 上傳檔案
    await uploadFile_to_category([newVal], user_uid, analysis_uuid, category, true);

    // 解析檔案
    const extract_result = await extract(newVal);
    let updatedInput = new Array();
    let updatedSubject = {};

    const subjectSampleIdLst = Object.keys(extract_result);
    const inputSampleIdLst = inputRows.value.map(obj => obj.sampleId)

    inputRows.value.forEach(row => {
      updatedInput.push(row);
    });

    subjectSampleIdLst.forEach((sampleId, idx) => {
      const index = inputSampleIdLst.length + idx + 1;

      if (!inputSampleIdLst.includes(sampleId)) {
        updatedInput.push({
          index: index,
          sampleId: sampleId,
          h63d: {
            ic: false,
            mut: false,
            wt: false,
          },
          s65c: {
            ic: false,
            mut: false,
            wt: false,
          },
          wt: {
            ic: false,
            wt: false,
          },
          mut: {
            ic: false,
            mut: false,
          },
          result: '-',
          resultLabel: ['-'],
          assessment: 'invalid',
          assessmentLabel: 'Invalid',

          // 新增以下屬性
          birth: extract_result[sampleId].birth,
          collectingDate: extract_result[sampleId].collectingDate,
          edit: extract_result[sampleId].edit,
          gender: extract_result[sampleId].gender,
          idNumber: extract_result[sampleId].idNumber,
          name: extract_result[sampleId].name,
          receivedDate: extract_result[sampleId].receivedDate,
          type: extract_result[sampleId].type,
        });
      }

      updatedSubject[sampleId] = extract_result[sampleId];
    });

    inputRows.value = updatedInput;

    // 隱藏 loading 視窗
    $q.loading.hide();
  }
});

watch(inputRows, () => {
  let updated = new Array();

  inputRows.value.forEach(row => {
    updated.push({
      index: row.index,
      sampleId: row.sampleId,
      h63d_ic: row.h63d.ic,
      h63d_mut: row.h63d.mut,
      h63d_wt: row.h63d.wt,
      s65c_ic: row.s65c.ic,
      s65c_mut: row.s65c.mut,
      s65c_wt: row.s65c.wt,
      wt_ic: row.wt.ic,
      wt_wt: row.wt.wt,
      mut_ic: row.mut.ic,
      mut_mut: row.mut.mut,
      result: resultAssessment(row).result,
      resultLabel: resultAssessment(row).resultLabel,
      assessment: resultAssessment(row).assessment,
      assessmentLabel: resultAssessment(row).assessmentLabel,

      // 新增以下屬性
      birth: row.birth ? row.birth : '',
      collectingDate: row.collectingDate ? row.collectingDate : '',
      edit: row.edit ? row.edit : '',
      gender: row.gender ? row.gender : '',
      idNumber: row.idNumber ? row.idNumber : '',
      name: row.name ? row.name : '',
      receivedDate: row.receivedDate ? row.receivedDate : '',
      type: row.type ? row.type : '',
    });
  });

  // 更新 store 中的 exportResults
  store.commit("export_page_setting/updateExportResults", updated);

  // 更新產品資訊
  const currentProduct = currentSettingProps.value ? currentSettingProps.value.product : '';
  store.commit("export_page_setting/updateExportedProduct", currentProduct);

}, { deep: true });

// Methods
const removeRow = (idx) => {
  inputRows.value.splice(idx - 1, 1);
  inputRows.value.forEach((row, index) => {
    row.index = index + 1;
  });
};

const addRow = (idx) => {
  inputRows.value.splice(idx, 0, {
    sampleId: '',
    h63d: {
      ic: true,
      mut: false,
      wt: true,
    },
    s65c: {
      ic: true,
      mut: false,
      wt: true,
    },
    wt: {
      ic: true,
      wt: true,
    },
    mut: {
      ic: true,
      mut: false,
    },
    result: 'wt/wt',
    resultLabel: ['HFE基因型wild-type/wild-type'],
    assessment: 'normal-risk',
    assessmentLabel: '一般風險基因型',
    index: idx + 1
  });
  inputRows.value.forEach((row, index) => {
    row.index = index + 1;
  });
};
</script>
