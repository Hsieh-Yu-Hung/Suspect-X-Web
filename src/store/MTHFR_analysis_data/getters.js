// MTHFR
export function resultTableMthfrProps(state) {

  let tableProps = new Array();

  if (state.mthfrResult !== null) {
    if (state.mthfrResult.config.reagent === 'accuinMTHFR1' || state.mthfrResult.config.reagent === 'accuinMTHFR3') {
      state.mthfrResult.sample.map((element) => {
        let selectedProp = {};

        selectedProp.sampleId = element.name;
        selectedProp.well = element.well;
        selectedProp.mthfrType =
          element.type.length !== 2
            ? ["-"]
            : [
              "c.677 [" + element.type[0].toUpperCase() + "/" + element.type[1].toUpperCase() + "]"
            ];
        selectedProp.assessment = element.assessment;
        selectedProp.type = [ element.type[0], element.type[1]];

        tableProps.push(selectedProp)
      })
    } else if (state.mthfrResult.config.reagent === 'accuinMTHFR2') {
      state.mthfrResult.sample.map((element) => {
        let selectedProp = {};

        selectedProp.sampleId = element.name;
        selectedProp.well = element.well;
        selectedProp.mthfrType =
          element.type.length !== 4
            ? ["-"]
            : [
              "c.677 [" + element.type[0].toUpperCase() + "/" + element.type[1].toUpperCase() + "]",
              "c.1298 [" + element.type[2].toUpperCase() + "/" + element.type[3].toUpperCase() + "]",
            ]
        selectedProp.assessment = element.assessment;
        selectedProp.type = [ element.type[0], element.type[1], element.type[2], element.type[3]];

        tableProps.push(selectedProp)
      })
    }
  }

  return tableProps
}

export const getInputResults = (state) => {
  return state.inputResults;
};
