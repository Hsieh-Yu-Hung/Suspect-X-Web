<template>
  <q-card bordered>
    <q-card-section>
      <div class="text-h5 text-uppercase text-bold text-blue-grey-7">
        Input
      </div>
      <div class="text-subtitle1">
        Please input the α/β Thal corresponding sample results by variant positions.
      </div>
      <div class="row q-pb-lg q-gutter-sm">
        <div class="col">
          <q-file
            v-model="subjectListFile"
            use-chips
            color="deep-orange-6"
            label="Subject information list file from LIMS (.xls)"
            accept=".xls"
            lazy-rules
            dense
          >
            <template v-slot:before>
              <q-icon name="mdi-microsoft-excel" />
            </template>
          </q-file>
        </div>
      </div>
      <div class="row">
        <q-table
          :rows="inputRows"
          :columns="inputColumns"
          :v-model:pagination="{ rowsPerPage: 0 }"
          :rows-per-page-options="[0]"
          class="col"
          row-key="index"
          flat
          dense
          virtual-scroll
        >
          <template v-slot:body-cell-add="props">
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
                v-model="getInput[props.key].sampleId"
                @update:model-value="(val) => updateInput({index: props.key, col: 'sampleId', update: val})"
                color="deep-orange"
                class="q-mx-lg"
              />
            </q-td>
          </template>
          <template v-slot:body-cell-alpha="props">
            <q-td class="col-1 text-overline" style="width: 200px">
              <div class="row justify-center text-indigo">
                <q-select
                  filled
                  v-model="getInput[props.key].alpha"
                  use-input
                  multiple
                  max-values="2"
                  input-debounce="0"
                  color='indigo'
                  class="text-bold"
                  :options="alphaLst"
                  @filter="filterAlphaFn"
                  @update:model-value="(val) => updateInput({index: props.key, col: 'alpha', update: val})"
                >
                  <template v-slot:selected>
                    <span v-if="getInput[props.key].alpha.length === 1">
                      {{ getInput[props.key].alpha[0].label }} / {{ getInput[props.key].alpha[0].label }}
                    </span>
                    <span v-else-if="getInput[props.key].alpha.length > 1">
                      {{ getInput[props.key].alpha[0].label }} / {{ getInput[props.key].alpha[1].label }}
                    </span>
                  </template>
                  <template v-slot:option="scope">
                    <q-item v-bind="scope.itemProps">
                      <q-item-section side>
                        <q-checkbox
                          left-label
                          color="indigo"
                          v-model="scope.selected"
                          checked-icon="task_alt"
                          unchecked-icon="radio_button_unchecked"
                          @update:model-value="scope.toggleOption(scope.opt)"
                        />
                      </q-item-section>
                      <q-item-section>
                        <q-item-label>{{ scope.opt.label }}</q-item-label>
                      </q-item-section>
                    </q-item>
                  </template>
                </q-select>
              </div>
            </q-td>
          </template>
          <template v-slot:body-cell-beta="props">
            <q-td class="col text-overline" style="width: 200px">
              <div class="row justify-center text-blue text-bold">
                <q-select
                  filled
                  v-model="getInput[props.key].beta"
                  use-input
                  no-wrap
                  multiple
                  input-debounce="0"
                  color="blue"
                  :options="betaLst"
                  @filter="filterBetaFn"
                  @update:model-value="(val) => updateInput({index: props.key, col: 'beta', update: val})"
                >
                <template v-slot:selected-item="scope">
                  <q-chip
                    removable
                    dense
                    @remove="scope.removeAtIndex(scope.index)"
                    :tabindex="scope.tabindex"
                    color="grey-11"
                    text-color="blue"
                  >
                    <span class="text-bold text-overline">
                      {{ scope.opt.label }}
                    </span>
                    <span class="text-overline q-ml-sm">
                      {{ zygosityLabel[getZygosity[props.key - 1][scope.opt.label]] }}
                    </span>
                  </q-chip>
                </template>
                  <template v-slot:option="scope">
                    <q-item v-bind="scope.itemProps" :clickable="!scope.selected">
                      <q-item-section side>
                        <q-checkbox
                          left-label
                          color="blue"
                          v-model="scope.selected"
                          checked-icon="task_alt"
                          unchecked-icon="radio_button_unchecked"
                          @update:model-value="scope.toggleOption(scope.opt)"
                        />
                      </q-item-section>
                      <q-item-section>
                        <q-item-label>{{ scope.opt.label }}</q-item-label>
                        <q-item-label v-if="scope.opt.end" caption>
                          {{ scope.opt.chr }}: {{ scope.opt.start }} - {{ scope.opt.end }}
                        </q-item-label>
                        <q-item-label v-else caption>{{ scope.opt.chr }}: {{ scope.opt.start }}</q-item-label>
                        <q-btn-toggle
                          v-if="scope.selected"
                          v-model="getZygosity[props.key - 1][scope.opt.label]"
                          @update:model-value="(val) => updateInput({index: props.key, col: 'beta', scope: scope.opt.label, update: val})"
                          class="q-ma-sm"
                          no-caps
                          rounded
                          unelevated
                          toggle-color="blue"
                          color="white"
                          text-color="blue"
                          :options="[
                            { label: 'Heterozygous', value: 'hetro' },
                            { label: 'Homozygous', value: 'homo' },
                          ]"
                        />
                      </q-item-section>
                    </q-item>
                  </template>
                </q-select>
              </div>
            </q-td>
          </template>
          <template v-slot:body-cell-result="props">
            <q-td class="text-center text-blue-grey">
              <q-list>
                <q-item>
                  <q-item-section>
                    <q-item-label class="text-overline text-bold" style="font-size: 13px">HBA:</q-item-label>
                    <q-item-label style="font-size: 14px"  v-if="getInput[props.key].alpha.length === 1">
                      {{ getInput[props.key].alpha[0].label }} / {{ getInput[props.key].alpha[0].label }}
                    </q-item-label>
                    <q-item-label style="font-size: 14px"  v-else-if="getInput[props.key].alpha.length > 1">
                      {{ getInput[props.key].alpha[0].label }} / {{ getInput[props.key].alpha[1].label }}
                    </q-item-label>
                    <q-item-label style="font-size: 14px" v-else>
                      -
                    </q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label class="text-overline text-bold" style="font-size: 13px">HBB:</q-item-label>
                    <span v-if="getInput[props.key].beta.length !== 0">
                      <q-item-label
                        style="font-size: 14px"
                        v-for="b in getInput[props.key].beta"
                        :key="b"
                        class="q-ma-xs"
                        no-wrap
                      >
                        {{ b.label }} {{ zygosityLabel[getZygosity[props.key - 1][b.label]] }}
                      </q-item-label></span>
                    <span v-else>
                      -
                    </span>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-td>
          </template>
          <template v-slot:body-cell-assessment="props">
            <q-td class="text-center">
              <q-chip
                class="text-grey-10"
                :color="assessmentColor(getInput[props.key].assessment)"
                :label="getInput[props.key].assessmentLabel"
              />
            </q-td>
          </template>
        </q-table>
      </div>
    </q-card-section>
  </q-card>
</template>

<script>
import { ref, onMounted } from "vue";

import extract from "@/composables/useExtract.vue";
import useGetThalassemia from "@/composables/useGetThalassemia.vue";

const alphaRawLst = useGetThalassemia('alpha');
const betaRawLst = useGetThalassemia('beta');

export default {
  props: {
    exportResults: {
      type: Array
    }
  },
  setup(props) {
    let alphaLst = ref([]);
    let betaLst = ref([]);

    // Input result table
    const inputRows = ref([{
      sampleId: '',
      alpha: [],
      beta: [],
      result: [
        ['α2', 'α2'],
        []
      ],
      resultLabel: [
        ['α2', 'α2'],
        []
      ],
      assessment: 'negative',
      assessmentLabel: '未檢出致病性基因突變',
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

      // Thal
      {
        name: "alpha",
        label: "α-Thalassemia Variant(s)",
        field: "alpha",
        align: "center",
      },
      {
        name: "beta",
        label: "β-Thalassemia Variant(s)",
        field: "beta",
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

    const zygosityLabel = {
      'hetro' : 'Heterozygous',
      'homo': 'Homozygous',
      'Heterozygous' : 'Heterozygous',    // lazy code
      'Homozygous': 'Homozygous'    // lazy code
    };

    const resultAssessment = (row) => {
      let resultAlpha = new Array();
      let resultBeta = new Array();
      let resultAlphaLabel = new Array();
      let resultBetaLabel = new Array();

      // alpha
      if (row.alpha.length === 1) {
        resultAlpha.push(row.alpha[0].value)
        resultAlpha.push(row.alpha[0].value)
        resultAlphaLabel.push(row.alpha[0].label);
        resultAlphaLabel.push(row.alpha[0].label);
      } else if (row.alpha.length === 2) {
        row.alpha.map(a => resultAlpha.push(a.value));
        row.alpha.map(a => resultAlphaLabel.push(a.label));
      }

      // beta
      if (row.beta.length !== 0) {
        row.beta.map(b => resultBeta.push(b.value));
        row.beta.map(b => resultBetaLabel.push(b.label));
      }

      if (
        resultAlpha.every(a => a === 'α2')
        && resultAlpha.length !== 0
        && resultBeta.length === 0
      ) {
        return {
          result: [resultAlpha, resultBeta],
          resultLabel: [resultAlphaLabel, resultBetaLabel],
          assessment: 'negative',
          assessmentLabel: '未檢出致病性基因突變',
        }
      } else if (
        resultAlpha.some(a => a !== 'α2')
        && resultAlpha.length !== 0
        && resultBeta.length === 0
      ) {
        return {
          result: [resultAlpha, resultBeta],
          resultLabel: [resultAlphaLabel, resultBetaLabel],
          assessment: 'alpha',
          assessmentLabel: 'α型地中海貧血',
        }
      } else if (
        resultAlpha.every(a => a === 'α2')
        && resultAlpha.length !== 0
        && resultBeta.length !== 0
      ) {
        return {
          result: [resultAlpha, resultBeta],
          resultLabel: [resultAlphaLabel, resultBetaLabel],
          assessment: 'beta',
          assessmentLabel: 'β型地中海貧血',
        }
      } else if (
        resultAlpha.some(a => a !== 'α2')
        && resultAlpha.length !== 0
        && resultBeta.length !== 0
      ) {
        return {
          result: [resultAlpha, resultBeta],
          resultLabel: [resultAlphaLabel, resultBetaLabel],
          assessment: 'alphabeta',
          assessmentLabel: 'α和β型地中海貧血',
        }
      } else {
        return {
          result: [[], []],
          resultLabel: [[], []],
          assessment: 'invalid',
          assessmentLabel: 'Invalid',
        }
      }
    };

    const assessmentColor = (assessment) => {
      if (assessment === "negative") {
        return "green-13";
      } else if (
        assessment === "alpha" ||
        assessment === "beta" ||
        assessment === "alphabeta"
      ) {
        return "red";
      } else {
        return "grey-5";
      }
    };

    alphaRawLst.then(alpha => {
      alphaLst.value = alpha;
      inputRows.value = inputRows.value.map(row => {
        return {
          index: row.index,
          sampleId: row.sampleId,
          alpha: alpha.filter(r => row.result[0].includes(r.label)),
          beta: row.beta,
          result: row.result,
          resultLabel: row.resultLabel,
          assessment: row.assessment,
          assessmentLabel: row.assessmentLabel,
        }
      })
    });
    betaRawLst.then(beta => {
      betaLst.value = beta;
    });

      inputRows.value.forEach((row, index) => {
        row.index = index + 1;
      });

    function filterAlphaFn (val, update, abort) {
      update(() => {
        const needle = val.toLowerCase()
        alphaRawLst.then(alpha => {
          alphaLst.value = alpha.filter(v =>
            v.label.toLowerCase().indexOf(needle) > -1 ||
            (Number(needle) >= Number(v.start) && Number(needle) <= Number(v.end))
          )
        });
      })
    };

    function filterBetaFn (val, update, abort) {
      update(() => {
        const needle = val.toLowerCase()
        betaRawLst.then(beta => {
          if (val) {
            betaLst.value = beta.filter(v =>
              v.label.toLowerCase().indexOf(needle) > -1 ||
              (Number(needle) >= Number(v.start) && Number(needle) <= Number(v.end))
            )
          } else {
            betaLst.value = beta.filter(v => v.common)
            betaLst.value = betaLst.value.filter(v =>
              v.label.toLowerCase().indexOf(needle) > -1 ||
              (Number(needle) >= Number(v.start) && Number(needle) <= Number(v.end))
            )
          }
        });
      })
    };

    onMounted(() => {
      if (props.exportResults.length !== 0) {
        inputRows.value = props.exportResults.map(p => {
          return {
            index: p.index,
            sampleId: p.sampleId,
            alpha: p.result.alpha,
            beta: p.result.beta,
            result: [[...new Set(p.resultLabel.alpha.type)], p.resultLabel.beta.type],
            resultLabel: [[...new Set(p.resultLabel.alpha.type)], p.resultLabel.beta.type],
            assessment: p.assessment,
            assessmentLabel: p.assessmentLabel,
          }
        });
      }
    });

    return {
      // Import
      subjectListFile: ref(null),

      // Input
      inputRows,
      inputColumns,
      filterAlphaFn,
      filterBetaFn,

      resultAssessment,
      assessmentColor,
      zygosityLabel,
      alphaLst,
      betaLst,
    };
  },
  computed: {
    getInput() {
      let updatedInput = {};
      this.inputRows.map(sample => {
        updatedInput[sample.index] = {
          ...sample,
          result: this.resultAssessment(sample).result,
          resultLabel: this.resultAssessment(sample).resultLabel,
          assessment: this.resultAssessment(sample).assessment,
          assessmentLabel: this.resultAssessment(sample).assessmentLabel,
        };
      })
      return updatedInput
    },
    getZygosity() {
      let sampleArr = new Array();
      let betaObj;

      this.inputRows.map(sample => {
        betaObj = sample.beta.reduce((acc, obj) => {
          acc[obj.label] = obj.zygosity;
          return acc;
        }, {});
        sampleArr.push(betaObj)
      })
      return sampleArr
    }
  },
  watch: {
    subjectListFile: function() {
      if (this.subjectListFile) {
        extract(this.subjectListFile.path)
          .then(subjectInfo => {
            let updatedInput = new Array();
            let updatedSubject = {};

            const subjectSampleIdLst = Object.keys(subjectInfo);
            const inputSampleIdLst = this.inputRows.map(obj => obj.sampleId)

            this.inputRows.forEach(row => {
              updatedInput.push(row);
            });

            subjectSampleIdLst.forEach((sampleId, idx) => {
              const index = inputSampleIdLst.length + idx + 1;

              if (!inputSampleIdLst.includes(sampleId)) {
                alphaRawLst.then(alpha => {
                  updatedInput.push({
                    index: index,
                    sampleId: sampleId,
                    alpha: alpha.filter(r => r.label === 'α2'),
                    beta: [],
                    result: [['α2', 'α2'], []],
                    resultLabel: [['α2', 'α2'], []],
                    assessment: 'negative',
                    assessmentLabel: '未檢出致病性基因突變',
                  });
                });
              }

              updatedSubject[sampleId] = subjectInfo[sampleId];
            });

            this.inputRows = updatedInput;
            this.$store.commit("data/updateSubjectInfo", updatedSubject);
          });
      }
    },
    inputRows: {
      handler(newVal, oldVal) {
        let updated = new Array();

        this.inputRows.forEach((row, index) => {
          let rowResult = this.resultAssessment(row).result;
          let rowAssessment = this.resultAssessment(row).assessment;
          let rowAssessmentLabel = this.resultAssessment(row).assessmentLabel;

          updated.push({
            index: row.index,
            sampleId: row.sampleId,
            result: {
              alpha: row.alpha,
              beta: row.beta.map(b => {
                return { ...b, zygosity: this.zygosityLabel[b.zygosity] }
              }),
            },
            resultLabel: {
              alpha: {
                type: rowResult[0],
                category: rowAssessment.replace('beta', '') === ''
                  ? 'negative'
                  : rowAssessment.replace('beta', ''),
              },
              beta: {
                type: rowResult[1],
                category: rowAssessment.replace('alpha', '') === ''
                  ? 'negative'
                  : rowAssessment.replace('alpha', ''),
              }
            },
            assessment: rowAssessment,
            assessmentLabel: rowAssessmentLabel,
          });
        });
        this.$store.commit("data/updateExportResults", updated);
      },
      deep: true
    },
  },
  methods: {
    removeRow: function(idx) {
      this.inputRows.splice(idx - 1, 1);
      this.inputRows.forEach((row, index) => {
        row.index = index + 1;
      });
    },
    addRow: function(idx) {
      alphaRawLst.then(alpha => {
        this.inputRows.splice(idx, 0, ...[{
          sampleId: '',
          alpha: alpha.filter(r => r.label === 'α2'),
          beta: [],
          result: [['α2', 'α2'], []],
          resultLabel: [['α2', 'α2'], []],
          assessment: 'negative',
          assessmentLabel: '未檢出致病性基因突變',
          index: idx + 1
        }]);
        this.inputRows.forEach((row, index) => {
          row.index = index + 1;
        });
      });
    },
    updateInput: function(val) {
      let updated;

      if (val.scope) {
        // for update zygosity ONLY
        let arr = this.inputRows[val.index - 1][val.col].map(p => ({ ...p }));
        updated = arr.map(obj => {
          if (obj.label === val.scope) {
            return { ...obj, zygosity: val.update };
          }
          return obj;
        });
      } else if (Array.isArray(val.update)) {
        updated = val.update.map(obj => {
          return { ...obj }
        });
      } else {
        updated = val.update
      }

      this.inputRows[val.index - 1][val.col] = updated;
    }
  },
};
</script>
