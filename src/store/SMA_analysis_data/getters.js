// SMA 評估
function smaAssessment(smn1, smn2) {
  if (smn1.every(s1 => s1 === 1)) {
    return {
      value: "carrier",
      label: "SMA carrier"
    };
  } else if (smn1.every(s1 => s1 >= 2)) {
    return {
      value: "normal",
      label: "Normal"
    };
  } else if (smn1.every(s1 => s1 === 0)) {
    if (smn2.every(s2 => s2 === 2)) {
      // Defined "SMA affected (Werdnig-Hoffmann Disease)" by SMN1:SMN2 =
      // 0:2
      return {
        value: "affected-wh",
        label: "SMA affected (Werdnig-Hoffmann Disease)"
      }
    } else if (smn2.every(s2 => s2 === 3)) {
      // Defined "SMA affected (Dubowitz Disease)" by SMN1:SMN2 =
      // 0:3
      return {
        value: "affected-dub",
        label: "SMA affected (Dubowitz Disease)"
      }
    } else if (smn2.every(s2 => s2 === 1)) {
      // Defined "SMA affected" by SMN1:SMN2 =
      // 0:1
      return {
        value: "affected",
        label: "SMA affected"
      }
    } else if (smn2.every(s2 => s2 === 4)) {
      // Defined "SMA affected (Kugelberg-Welander Disease)" by SMN1:SMN2 =
      // 0:4
      return {
        value: "affected-kw",
        label: "SMA affected (Kugelberg-Welander Disease)"
      }
    } else {
      // Defined "Invalid" (nonsense value) by SMN1:SMN2 =
      // 0:0
      return {
        value: "invalid",
        label: "Invalid"
      }
    }
  } else {
    // Cannot be defined by two analyzer results
    return {
      value: "unfound",
      label: "Unfound"
    }
  }
}

export function resultTableSmaProps(state) {
  // 如果 smaResult 為 null，直接返回空陣列
  if (state.smaResult === null) {
    return [];
  }

  let qc = state.smaResult.qc?.status || "fail-the-criteria";

  return state.smaResult.sample.map((element) => {
    let selectedProp = {};
    let smn1Type = Array.isArray(element.smn1Type) ? [ ...element.smn1Type ] : [ element.smn1Type ];
    let smn2Type = Array.isArray(element.smn2Type) ? [ ...element.smn2Type ] : [ element.smn2Type ];
    selectedProp.sampleId = element.name;
    selectedProp.well = element.well;
    selectedProp.rnp_smn1 = (element.rnp_smn1).toFixed(2);
    selectedProp.rnp_smn2 = (element.rnp_smn2).toFixed(2);
    selectedProp.smn1Type = smn1Type;
    selectedProp.smn2Type = smn2Type;
    selectedProp.assessment = qc === "meet-the-criteria"
      ? smaAssessment(smn1Type, smn2Type)
      : { value: "inconclusive", label: "Inconclusive" };
    return selectedProp;
  });
}

export function exportSmaProps(state) {
  function standardInfoExport() {
    const expectCopy = state.settingProps.reagent === "accuinSma1"
      ? [ "1:1", "2:2" ]
      : [ "1:1", "2:2", "3:3" ];

    let standardInfo = new Array();

    expectCopy.forEach((copy, idx) => {
      standardInfo.push({
        expectCopy: copy,
        testingCopy: state.qualityControlProps.controlAssessment === 'meet-the-criteria'
          ? expectCopy[idx]
          : '-',
        result: state.qualityControlProps.controlAssessment === 'meet-the-criteria'
          ? 'meetTheCriteria'
          : 'failTheCriteria',
      });
    });

    return standardInfo
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
          measurement: [ ...s.result.label ],
          assessment: s.assessment.value,
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

export function displaySMNVersion(state) {
  return {
    smn1: state.displaySMN1Version,
    smn2: state.displaySMN2Version,
  };
}

export function distanceRatio(state) {
  return {
    smn1: state.distanceRatioSmn1,
    smn2: state.distanceRatioSmn2,
  };
}
