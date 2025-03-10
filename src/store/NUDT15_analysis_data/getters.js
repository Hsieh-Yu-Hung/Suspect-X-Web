// NUDT15
export function resultTableNudt15Props(state) {

  let tableProps = new Array();

  if (state.nudt15Result !== null) {
    state.nudt15Result.sample.map((element) => {
      let selectedProp = {};

      selectedProp.sampleId = element.name;
      selectedProp.well = element.well;
      selectedProp.nudt15Type =
        element.type.length !== 2
          ? ["-"]
          : [
            element.type[0].toUpperCase() + "/" + element.type[1].toUpperCase()
          ];
      selectedProp.assessment = element.assessment;
      selectedProp.type = [ element.type[0], element.type[1]];

      tableProps.push(selectedProp)
    })
  }

  return tableProps
}
