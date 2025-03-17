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

// APOE
export function exportApoeProps(inputData) {
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
      'E2E2': 'E2/E2',
      'E3E3': 'E3/E3',
      'E4E4': 'E4/E4',
      'E2E3': 'E2/E3',
      'E2E4': 'E2/E4',
      'E3E4': 'E3/E4',
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

export default {
  exportThalProps: exportThalProps,
  exportAlcoholProps: exportAlcoholProps,
  exportApoeProps: exportApoeProps,
};