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

export function exportMthfrv1Props(state) {
  function standardInfoExport() {
    const expectCopy = [ "c.677[C/T]" ];

    let standardInfo = new Array();

    expectCopy.forEach((copy, idx) => {
      standardInfo.push({
        testingGenoType: copy,
        result: state.qualityControlProps.controlAssessment === 'meet-the-criteria'
          ? 'meetTheCriteria'
          : 'failTheCriteria',
      });
    });

    return standardInfo
  };

  function assessmentExport(assessment) {
    const mthfrAssessment = {
      'low-risk': 'lowRisk',
      'normal-risk': 'generalRisk',
      'high-risk': 'highRisk',
      'Invalid': 'invalid',
      'Inconclusive': 'inconclusive'
    };
    return mthfrAssessment[assessment]
  };

  function mthfrMeasurement(result) {
    if (result[0] && result[1]) {
      return result.map(item => item.toUpperCase()).join("/")
    } else {
      return "-"
    }
  };

  return state.selectedExport.map((s) => {
    return {
      result: {
        standard: standardInfoExport(),
        testing: {
          sample: {
            id: s.sampleId,
            name: s.sampleId
          },
          measurement: {
            mthfr: mthfrMeasurement([ ...s.result.value ]),
            folate: s.result.label.length > 1
              ? parseFloat(s.result.label[1].match(/(\d+(\.\d+)?)/)).toFixed(2)
              : '-',
          },
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

export function exportMthfrv2Props(state) {
  function standardInfoExport() {
    const expectCopy = [ "c.677[C/T]", "c.1298[A/A]" ];

    let standardInfo = new Array();

    expectCopy.forEach((copy) => {
      standardInfo.push({
        testingGenoType: copy,
        result: 'meetTheCriteria'
      });
    });

    return standardInfo
  };

  function assessmentExport(assessment) {
    const mthfrAssessment = {
      'low-risk': 'lowRisk',
      'normal-risk': 'generalRisk',
      'high-risk': 'highRisk',
      'invalid': 'invalid',
    };
    return mthfrAssessment[assessment]
  };

  function measurementExport(measurement) {
    const result = measurement.toUpperCase();

    return {
      c677: result.slice(0, 2).replace(/(.)(.)/, '$1/$2'),
      c1298: result.slice(2, 4).replace(/(.)(.)/, '$1/$2'),
    }
  };

  return state.selectedExport.map((s) => {
    return {
      result: {
        standard: standardInfoExport(),
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

export const getInputResults = (state) => {
  return state.inputResults;
};
