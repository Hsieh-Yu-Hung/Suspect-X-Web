// APOE
export function resultTableApoeProps(state) {

  let tableProps = new Array();

  if (state.apoeResult !== null) {
    state.apoeResult.result.map((element) => {
      let selectedProp = {};

      selectedProp.sampleId = element.e2.id;
      selectedProp.well = {
        e2: element.e2.well,
        e3: element.e3.well,
        e4: element.e4.well,
      };
      selectedProp.apoeType = element.type.length !== 2
        ? "-"
        : `${element.type[0].toUpperCase()}/${element.type[1].toUpperCase()}`;
      selectedProp.type = [ ...element.type ]
      selectedProp.assessment = element.assessment;

      tableProps.push(selectedProp)
    })
  }

  return tableProps
}

export function resultWellInfo(state) {
  let wellObj = {};
  let typeArr = [ 'e2', 'e3', 'e4' ];
  let ctrlArr = [ 'standard1', 'standard2' ]

  if (state.apoeResult !== null) {
    for (let c of ctrlArr) {
      for (let e of typeArr) {
        let well = state.apoeResult.control[c][e].well;
        if (!wellObj[well]) wellObj[well] = new Array();
        wellObj[well].push({
          sampleId: state.apoeResult.control[c][e].id,
          id: state.apoeResult.control[c][e].id,
          type: e,
          sampleType: c,
          filename: state.apoeResult.control[c][e].filename,
        })
      }
    }

    state.apoeResult.result.map((element) => {
      for (let e of typeArr) {
        let well = element[e].well;
        if (!wellObj[well]) wellObj[well] = new Array();
        wellObj[well].push({
          sampleId: element.e2.id,
          id: element[e].id,
          type: e,
          sampleType: 'sample',
          filename: element[e].filename,
        });
      }
    })
  }

  return wellObj
}

export function exportApoeProps(state) {
  function assessmentExport(assessment) {
    const apoeAssessment = {
      'low-risk': 'lowRisk',
      'high-risk': 'highRisk',
      'normal-risk': 'generalRisk',
      'invalid': 'invalid',
    };
    return apoeAssessment[assessment]
  };

  function measurementExport(measurement) {
    const apoeMeasurement = {
      'e2e2': 'E2/E2',
      'e3e3': 'E3/E3',
      'e4e4': 'E4/E4',
      'e2e3': 'E2/E3',
      'e2e4': 'E2/E4',
      'e3e4': 'E3/E4',
      '-': '-',
    };

    return apoeMeasurement[measurement]
  };

  return state.selectedExport.map((s) => {
    return {
      result: {
        testing: {
          sample: {
            id: s.sampleId ? s.sampleId : s.index,
            name: s.sampleId
          },
          measurement: measurementExport(s.result.value),
          assessment: assessmentExport(s.assessment.value),
        },
      },
      subject: {
        name: s.name,
        birth: s.birth,
        gender: s.gender,
        idNumber: s.idNumber,
        sampleType: s.type
      },
      collectionDate: s.collectingDate,
      receivingDate: s.receivedDate,
    }
  });
}
