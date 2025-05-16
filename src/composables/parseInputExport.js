// THAL
function exportThalProps(inputData) {

  function variantsExport(result) {
    let resultExport = new Array();

    // alpha variants
    if (result.alpha.length === 1) {
      result.alpha.forEach(a => {
        if (a.type !== "Wild Type") {
          resultExport.push({
            gene: a.gene,
            position: a.chr
              ? a.start
                ? a.end
                  ? a.chr + ':' + a.start + '-' + a.end
                  : a.chr + ':' + a.start
                : '-'
              : '-',
            variantType: a.type,
            diseaseType: a.disease,
            zygosity: "Homozygous"
          });
        }
      })
    } else if (result.alpha.length === 2) {
      result.alpha.forEach(a => {
        if (a.type !== "Wild Type") {
          resultExport.push({
            gene: a.gene,
            position: a.chr
              ? a.start
                ? a.end
                  ? a.chr + ':' + a.start + '-' + a.end
                  : a.chr + ':' + a.start
                : '-'
              : '-',
            variantType: a.type,
            diseaseType: a.disease,
            zygosity: "Heterozygous"
          });
        }
      })
    }

    // beta variants
    if (result.beta.length !== 0) {
      result.beta.forEach(a => {
        resultExport.push({
          gene: a.gene,
          position: a.end
            ? a.chr + ':' + a.start + '-' + a.end
            : a.chr + ':' + a.start,
          variantType: a.type,
          diseaseType: a.disease,
          zygosity: a.zygosity
        });
      });
    }

    return resultExport
  };

  return inputData.map((s) => {
    return {
      result: {
        testing: {
          sample: {
            id: s.sampleId ? s.sampleId : s.index,
            name: s.sampleId
          },
          assessment: {
            alpha: {
              type: s.resultLabel.alpha.category === 'negative' ? '-' : s.resultLabel.alpha.type.join('/'),
              category: s.resultLabel.alpha.category,
            },
            beta: {
              type: [ ...s.resultLabel.beta.type ],
              category: s.resultLabel.beta.category,
            }
          },
          variants: variantsExport(s.result),
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

// ALCOHOL
function exportAlcoholProps(inputData) {
  // 將 inputData 中的 result 轉換為 assessment
  function assessmentExport(assessment) {
    const aldhAssessment = {
      'low-risk': 'lowRisk',
      'normal-risk': 'generalRisk',
      'high-risk': 'highRisk',
      'invalid': 'invalid',
    };
    return aldhAssessment[assessment]
  };

  function measurementExport(measurement) {
    const result = measurement.toUpperCase();

    return {
      c143: result.slice(0, 2).replace(/(.)(.)/, '$1/$2'),
      c1510: result.slice(2, 4).replace(/(.)(.)/, '$1/$2'),
    }
  };
  return inputData.map((s) => {
    return {
      collectionDate: s.collectingDate,
      receivingDate: s.receivedDate,
      result: {
        testing: {
          sample: {
            id: s.sampleId ? s.sampleId : s.index,
            name: s.sampleId
          },
          measurement: measurementExport(s.result),
          assessment: assessmentExport(s.assessment),
        },
      },
      subject: {
        name: s.name,
        birth: s.birth,
        gender: s.gender,
        idNumber: s.idNumber,
        sampleType: s.type
      },
    }
  });
}

// APOE
function exportApoeProps(inputData) {
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

  return inputData.map((s) => {
    return {
      result: {
        testing: {
          sample: {
            id: s.sampleId ? s.sampleId : s.index,
            name: s.sampleId
          },
          measurement: measurementExport(s.result),
          assessment: assessmentExport(s.assessment),
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

// APOE CVD
function exportCvdProps(inputData) {
  function assessmentExport(assessment) {
    const cvdAssessment = {
      'low-risk': 'lowRisk',
      'high-risk': 'highRisk',
      'normal-risk': 'generalRisk',
      'invalid': 'invalid',
    };
    return cvdAssessment[assessment]
  };

  function measurementExport(measurement) {
    const cvdMeasurement = {
      'e2e2': 'E2/E2',
      'e3e3': 'E3/E3',
      'e4e4': 'E4/E4',
      'e2e3': 'E2/E3',
      'e2e4': 'E2/E4',
      'e3e4': 'E3/E4',
      '-': '-',
    };

    return cvdMeasurement[measurement]
  };

  return inputData.map((s) => {
    return {
      result: {
        testing: {
          sample: {
            id: s.sampleId ? s.sampleId : s.index,
            name: s.sampleId
          },
          measurement: measurementExport(s.result),
          assessment: assessmentExport(s.assessment),
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

// B27
function exportB27Props(inputData) {
  return inputData.map((s) => {
    return {
      result: {
        testing: {
          sample: {
            id: s.sampleId ? s.sampleId : s.index,
            name: s.sampleId
          },
          measurement: s.result,
          assessment: s.assessment,
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

// CYP1A2
function exportCyp1a2Props(inputData) {
  function assessmentExport(assessment) {
    const cyp1a2Assessment = {
      'low-risk': 'lowRisk',
      'normal-risk': 'generalRisk',
      'high-risk': 'highRisk',
      'invalid': 'invalid',
    };
    return cyp1a2Assessment[assessment]
  };

  return inputData.map((s) => {
    return {
      result: {
        testing: {
          sample: {
            id: s.sampleId ? s.sampleId : s.index,
            name: s.sampleId
          },
          measurement: s.result.charAt(0).toUpperCase() + '/' + s.result.charAt(1).toUpperCase(),
          assessment: assessmentExport(s.assessment),
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

// CD
function exportCdProps(inputData) {
  function assessmentExport(assessment) {
    const cdAssessment = {
      'low-risk': 'lowRisk',
      'normal-risk': 'generalRisk',
      'high-risk': 'highRisk',
      'invalid': 'invalid',
    };
    return cdAssessment[assessment]
  };

  return inputData.map((s) => {
    return {
      result: {
        testing: {
          sample: {
            id: s.sampleId ? s.sampleId : s.index,
            name: s.sampleId
          },
          measurement: s.result,
          assessment: assessmentExport(s.assessment),
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

// F2F5
function exportF2f5Props(inputData) {
  function assessmentExport(assessment) {
    const f2f5Assessment = {
      'low-risk': 'lowRisk',
      'normal-risk': 'generalRisk',
      'high-risk': 'highRisk',
      'invalid': 'invalid',
    };
    return f2f5Assessment[assessment]
  };

  function measurementExport(measurement) {
    const result = measurement.toUpperCase();

    return {
      c20210: result.slice(0, 2).replace(/(.)(.)/, '$1/$2'),
      c1691: result.slice(2, 4).replace(/(.)(.)/, '$1/$2'),
    }
  };

  return inputData.map((s) => {
    return {
      result: {
        testing: {
          sample: {
            id: s.sampleId ? s.sampleId : s.index,
            name: s.sampleId
          },
          measurement: measurementExport(s.result),
          assessment: assessmentExport(s.assessment),
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

// PD
function exportPdProps(inputData) {
  function assessmentExport(assessment) {
    const pdAssessment = {
      'low-risk': 'lowRisk',
      'normal-risk': 'generalRisk',
      'high-risk': 'highRisk',
      'invalid': 'invalid',
    };
    return pdAssessment[assessment]
  };

  function measurementExport(measurement) {
    const result = measurement.toUpperCase();

    return {
      gba: result.slice(0, 2).replace(/(.)(.)/, '$1/$2'),
      lrrk21628: result.slice(2, 4).replace(/(.)(.)/, '$1/$2'),
      lrrk22385: result.slice(4, 6).replace(/(.)(.)/, '$1/$2'),
    }
  };

  return inputData.map((s) => {
    return {
      result: {
        testing: {
          sample: {
            id: s.sampleId ? s.sampleId : s.index,
            name: s.sampleId
          },
          measurement: measurementExport(s.result),
          assessment: assessmentExport(s.assessment),
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

// HFE
function exportHfeProps(inputData) {
  function assessmentExport(assessment) {
    const hfeAssessment = {
      'low-risk': 'lowRisk',
      'high-risk': 'highRisk',
      'normal-risk': 'generalRisk',
      'invalid': 'invalid',
    };
    return hfeAssessment[assessment]
  };

  return inputData.map((s) => {
    return {
      result: {
        testing: {
          sample: {
            id: s.sampleId ? s.sampleId : s.index,
            name: s.sampleId
          },
          measurement: s.result.toUpperCase(),
          assessment: assessmentExport(s.assessment),
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

// LCT
function exportLctProps(inputData) {
  function assessmentExport(assessment) {
    const lctAssessment = {
      'low-risk': 'lowRisk',
      'normal-risk': 'generalRisk',
      'high-risk': 'highRisk',
      'invalid': 'invalid',
    };
    return lctAssessment[assessment]
  };

  function measurementExport(measurement) {
    const result = measurement.toUpperCase();

    return {
      lct13910: result.slice(0, 2).replace(/(.)(.)/, '$1/$2'),
      lct22018: result.slice(2, 4).replace(/(.)(.)/, '$1/$2'),
    }
  };

  return inputData.map((s) => {
    return {
      result: {
        testing: {
          sample: {
            id: s.sampleId ? s.sampleId : s.index,
            name: s.sampleId
          },
          measurement: measurementExport(s.result),
          assessment: assessmentExport(s.assessment),
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

// NOTCH3
function exportNotch3Props(inputData) {
  function assessmentExport(assessment) {
    const notch3Assessment = {
      'low-risk': 'lowRisk',
      'high-risk': 'highRisk',
      'normal-risk': 'generalRisk',
      'invalid': 'invalid',
    };
    return notch3Assessment[assessment]
  };

  return inputData.map((s) => {
    return {
      result: {
        testing: {
          sample: {
            id: s.sampleId ? s.sampleId : s.index,
            name: s.sampleId
          },
          measurement: s.result.charAt(0).toUpperCase() + '/' + s.result.charAt(1).toUpperCase(),
          assessment: assessmentExport(s.assessment),
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

// MTHFR v1
function exportMthfrv1Props(inputData) {

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

  return inputData.map((s) => {
    return {
      result: {
        testing: {
          sample: {
            id: s.sampleId,
            name: s.sampleId
          },
          measurement: {
            mthfr: mthfrMeasurement([ ...s.result]),
            folate: '-',
          },
          assessment: assessmentExport(s.assessment),
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

// MTHFR v2
function exportMthfrv2Props(inputData) {

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
    return {
      c677: `${measurement[0].toUpperCase()}/${measurement[1].toUpperCase()}`,
      c1298: `${measurement[2].toUpperCase()}/${measurement[3].toUpperCase()}`,
    }
  };

  return inputData.map((s) => {
    return {
      result: {
        testing: {
          sample: {
            id: s.sampleId ? s.sampleId : s.index,
            name: s.sampleId
          },
          measurement: measurementExport(s.result),
          assessment: assessmentExport(s.assessment),
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

export default {
  exportThalProps: exportThalProps,
  exportAlcoholProps: exportAlcoholProps,
  exportApoeProps: exportApoeProps,
  exportCvdProps: exportCvdProps,
  exportB27Props: exportB27Props,
  exportCyp1a2Props: exportCyp1a2Props,
  exportCdProps: exportCdProps,
  exportF2f5Props: exportF2f5Props,
  exportPdProps: exportPdProps,
  exportHfeProps: exportHfeProps,
  exportLctProps: exportLctProps,
  exportNotch3Props: exportNotch3Props,
  exportMthfrv1Props: exportMthfrv1Props,
  exportMthfrv2Props: exportMthfrv2Props,
};