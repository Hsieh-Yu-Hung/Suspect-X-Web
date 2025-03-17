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

export default {
  exportThalProps: exportThalProps,
};