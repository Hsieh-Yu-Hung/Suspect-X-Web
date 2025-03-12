<template>
  <q-card bordered>
    <q-card-section>
      <div class="text-h5 text-uppercase text-bold text-blue-grey-7">
        Lab Information
      </div>
      <q-form @submit="onExport">
        <div class="row justify-evenly q-gutter-xl">
          <q-input
            v-model="subjectOrder.labName"
            class="col"
            label="Laboratory"
            color="deep-orange"
          />
          <q-input
            v-model="subjectOrder.issuedPhysician"
            class="col"
            label="Authorized by"
            color="deep-orange"
          />
          <q-input
            v-model="subjectOrder.issuedContact"
            class="col"
            label="Contact"
            color="deep-orange"
          />
          <q-select
            v-model="exportOption"
            :options="exportOptions"
            label="Export Format"
            class="col"
            color="deep-orange"
            label-color="deep-orange"
            behavior="menu"
            :rules="[(val) => val || `Please select export format.`]"
            lazy-rules
            map-options
            outlined
          />
        </div>
        <div class="row justify-end">
          <q-btn
            label="Export"
            type="submit"
            color="blue-grey-7"
            size="lg"
          />
        </div>
      </q-form>
    </q-card-section>
  </q-card>
</template>

<script setup>
import { ref, computed } from "vue";
import { useStore } from "vuex";
import { useQuasar, QSpinnerDots } from "quasar";
import moment from "moment";

const props = defineProps({
  settingProps: {
    type: Object
  },
  qualityControlProps: {
    type: Object
  },
});

const $q = useQuasar();
const $store = useStore();

const selectedSample = computed(() => $store.state.data.selectedExport);

const exportOption = ref(null);
const subjectOrder = ref({
  labName: "",
  issuedContact: "",
  issuedPhysician: "",
});

const exportOptions = [
  // { label: 'PDF - 中文', value: 'pdf_zhTW'},
  // { label: 'PDF - English', value: 'pdf_enUS'},
  // { label: 'JSON - English', value: 'json_enUS'},
  // { label: 'JSON - 中文', value: 'json_zhTW'},
  { label: 'JSON', value: 'json_enUS' },
  { label: 'Excel', value: 'xlsx_enUS'},
];

// Export
const onExport = async () => {
  if (selectedSample.value.length > 0) {
    $q.loading.show({
      spinner: QSpinnerDots,
      message: `Exporting report...`,
      messageColor: 'white',
      spinnerColor: 'deep-orange-6',
    });
    const lang = exportOption.value.value.split('_')[1];
    const format = exportOption.value.value.split('_')[0];

    let productExport;
    let exportSample;

    try {
      /** Create export object */
      if (props.settingProps.product === 'fx') {
        exportSample = computed(() => $store.getters["data/exportFxProps"]);
        productExport = props.settingProps.reagent === 'accuinFx1' ? 'FXSv1' : 'FXSv2';
      } else if (props.settingProps.product === 'hd') {
        exportSample = computed(() => $store.getters["data/exportHdProps"]);
        productExport = 'HTD';
      } else if (props.settingProps.reagent === 'accuinMTHFR1' || props.settingProps.reagent === 'accuinMTHFR3') {
        exportSample = computed(() => $store.getters["data/exportMthfrv1Props"]);
        productExport = 'MTHFR_c677';
      } else if (props.settingProps.reagent === 'accuinMTHFR2') {
        exportSample = computed(() => $store.getters["data/exportMthfrv2Props"]);
        productExport = 'MTHFR_c677_c1298';
      } else if (props.settingProps.product === 'sma') {
        exportSample = computed(() => $store.getters["data/exportSmaProps"]);
        productExport = 'SMA';
      } else if (props.settingProps.product === 'cd') {
        exportSample = computed(() => $store.getters["data/exportCdProps"]);
        productExport = 'DQ2_DQ8';
      } else if (props.settingProps.product === 'alcohol') {
        exportSample = computed(() => $store.getters["data/exportAlcoholProps"]);
        productExport = 'ADH1B_ALDH2';
      } else if (props.settingProps.product === 'apoe' || props.settingProps.product === 'apoe-import') {
        exportSample = computed(() => $store.getters["data/exportApoeProps"]);
        productExport = 'APOE_AD';
      } else if (props.settingProps.product === 'cvd') {
        exportSample = computed(() => $store.getters["data/exportCvdProps"]);
        productExport = 'APOE_CVD';
      } else if (props.settingProps.product === 'b27') {
        exportSample = computed(() => $store.getters["data/exportB27Props"]);
        productExport = 'B27';
      } else if (props.settingProps.product === 'cyp1a2') {
        exportSample = computed(() => $store.getters["data/exportCyp1a2Props"]);
        productExport = 'CYP';
      } else if (props.settingProps.product === 'notch3') {
        exportSample = computed(() => $store.getters["data/exportNotch3Props"]);
        productExport = 'NOTCH3';
      } else if (props.settingProps.product === 'f2f5') {
        exportSample = computed(() => $store.getters["data/exportF2f5Props"]);
        productExport = 'F2_F5';
      } else if (props.settingProps.product === 'pd') {
        exportSample = computed(() => $store.getters["data/exportPdProps"]);
        productExport = 'LRRK2_GBA';
      } else if (props.settingProps.product === 'lct') {
        exportSample = computed(() => $store.getters["data/exportLctProps"]);
        productExport = 'LCT';
      } else if (props.settingProps.product === 'hfe') {
        exportSample = computed(() => $store.getters["data/exportHfeProps"]);
        productExport = 'HFE';
      } else if (props.settingProps.product === 'thal') {
        exportSample = computed(() => $store.getters["data/exportThalProps"]);
        productExport = 'THAL';
      }

      /** Export report object */
      if (format === 'pdf' || format === 'json') {
        const exportPath = await window.api.openExportFolder();

        if (exportPath.cancel) {
          $q.loading.hide();
        } else {
          const reportAll = exportSample.value.length;

          $q.loading.show({
            spinner: QSpinnerDots,
            message: `Exporting report... 0 / ${reportAll}`,
            messageColor: 'white',
            spinnerColor: 'deep-orange-6',
          });

          for (let [idx, s] of exportSample.value.entries()) {
            let res;

            const exportObj = {
              version: "v3",
              product: {
                name: productExport
              },
              format: {
                lang: lang,
                client: "ACCUIN"
              },
              export: {
                path: exportPath.path,
              },
              info: {
                laboratory: {
                  lab: subjectOrder.value.labName,
                  collectionDate: s.collectingDate,
                  receivingDate: s.receivedDate,
                  reportingDate: moment().format("YYYY/MM/DD"),
                },
                subject: s.subject,
                order: {
                  name: subjectOrder.value.issuedPhysician,
                  contact: subjectOrder.value.issuedContact
                }
              },
              result: s.result
            };

            if (format === 'pdf') {
              res = await window.api.runExportPDF(exportObj);
            } else if (format === 'json') {
              res = await window.api.runExportJSON(exportObj);
            }

            if (res.isExported) {
              $q.loading.show({
                spinner: QSpinnerDots,
                message: `Exporting report... ${idx+1} / ${reportAll}`,
                messageColor: 'white',
                spinnerColor: 'deep-orange-6',
              });
              console.log(`${res.exportPath} is exported`);
              $q.notify(`Sample: ${res.exportPath} is exported`);
            }
            else{
              console.log(`Report is not exported`);
              $q.notify(`Sample: ${res.exportPath} is failed to exported`);
            }
          };
        }
      } else if (format === 'xlsx') {
        const defaultFilename = productExport + '_' + moment(new Date()).format('YYYYMMDD') + '.xlsx';
        const exportPath = await window.api.openExportFile({ defaultFilename });

        if (exportPath.cancel) {
          $q.loading.hide();
        } else {
          $q.loading.show({
            spinner: QSpinnerDots,
            message: `Exporting results to Excel...`,
            messageColor: 'white',
            spinnerColor: 'deep-orange-6',
          });

          const saveExcel = await window.api.downloadReportFile([
            exportPath.path,
            selectedSample.value.map((s) => {
              return {
                sampleId: s.sampleId,
                well: s.well ? s.well : '-',
                results: s.assessment.value === 'invalid' || s.assessment.value === 'inconclusive'
                  ? '-'
                  : s.result.label.join(' / '),
                assessment: s.assessment.label,
                qc: s.assessment.value === 'inconclusive' ? 'Fail' : 'Pass',
                name: s.name,
                birth: s.birth,
                gender: s.gender,
                idNumber: s.idNumber,
                type: s.type,
                receivedDate: s.receivedDate,
                collectingDate: s.collectingDate,
                reportingDate: moment().format("YYYY/MM/DD"),
              }
            }),
            {
              product: productExport,
              instrument: props.qualityControlProps.instrument,
              analyzer: [ ...props.qualityControlProps.analysisMethod ],
              reagent: props.qualityControlProps.reagent,
              assessmentTime: props.qualityControlProps.assessmentTime,
              controlId: Array.isArray(props.qualityControlProps.controlId)
                ? props.qualityControlProps.controlId.join(', ')
                : props.qualityControlProps.controlId,
              labName: subjectOrder.value.labName,
              issuedPhysician: subjectOrder.value.issuedPhysician,
              issuedContact: subjectOrder.value.issuedContact,
              softwareVersion: process.env.VUE_APP_SOFTWARE_VERSION,
              analysisPackage: process.env.VUE_APP_ANALYSIS_PACKAGE,
            },
          ]);
          console.log("softwareVersion", process.env.VUE_APP_SOFTWARE_VERSION);
          console.log("analysisPackage", process.env.VUE_APP_ANALYSIS_PACKAGE);
          console.log(`${saveExcel} is exported`);
          $q.notify(`${saveExcel} is exported`);
        }
      }
    } catch (err) {
      console.log(err);
      $q.notify({
        type: 'negative',
        message: `Failed to export reports.`,
      });
    }

    setTimeout(() => {
      $q.loading.hide();
    }, 1500);
  } else {
    $q.notify({
      type: 'negative',
      message: `Please select at least ONE sample to export.`,
    });
  }
};
</script>
