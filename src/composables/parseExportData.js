// FXS 導出結果
function exportFxProps(resultObj, selectedExport) {

  function standardInfoExport() {
    const expectedLength = resultObj.config.reagent === "accuinFx1"
      ? [ 311, 374, 462 ]
      : [ 311, 374, 462, 823 ];
    const standardRange = resultObj.config.reagent === "accuinFx1"
      ? [ '280-342', '337-411', '416-508' ]
      : [ '280-342', '337-411', '416-508', '741-905' ];

    const standardInfoRaw = resultObj.resultObj.control_data;

    let standardInfo = new Array();

    expectedLength.forEach((length, idx) => {
      let standard = 'SC' + String(idx + 1);

      standardInfo.push({
        expectLength: length,
        expectRepeat: standardInfoRaw.find((item) => item.peak_type === standard).repeatNum,
        standardRange: standardRange[idx],
        testingLength: standardInfoRaw.find((item) => item.peak_type === standard).peak_size
          ? String(standardInfoRaw.find((item) => item.peak_type === standard).peak_size)
          : '-',
        result: resultObj.qc_status === 'meet-the-criteria'
          ? 'meetTheCriteria'
          : 'failTheCriteria',
      });
    });

    return standardInfo
  };

  function chartFxExport(sampleId) {
    let controlData = {
      label: "Control",
      type: "scatter",
      pointRadius: 6,
      borderWidth: 1,
      borderColor: "#ffffff",
      backgroundColor: "rgba(33, 150, 243)",
      animations: false,
      data: resultObj.config.reagent === "accuinFx1"
        ? [ {
            x: resultObj.resultObj.control_data.find((item) => item.peak_type === 'SC1').peak_size,
            y: resultObj.resultObj.control_data.find((item) => item.peak_type === 'SC1').repeatNum,
          },
          {
            x: resultObj.resultObj.control_data.find((item) => item.peak_type === 'SC2').peak_size,
            y: resultObj.resultObj.control_data.find((item) => item.peak_type === 'SC2').repeatNum,
          },
          {
            x: resultObj.resultObj.control_data.find((item) => item.peak_type === 'SC3').peak_size,
            y: resultObj.resultObj.control_data.find((item) => item.peak_type === 'SC3').repeatNum,
          },
        ]
        : [ {
            x: resultObj.resultObj.control_data.find((item) => item.peak_type === 'SC1').peak_size,
            y: resultObj.resultObj.control_data.find((item) => item.peak_type === 'SC1').repeatNum,
          },
          {
            x: resultObj.resultObj.control_data.find((item) => item.peak_type === 'SC2').peak_size,
            y: resultObj.resultObj.control_data.find((item) => item.peak_type === 'SC2').repeatNum,
          },
          {
            x: resultObj.resultObj.control_data.find((item) => item.peak_type === 'SC3').peak_size,
            y: resultObj.resultObj.control_data.find((item) => item.peak_type === 'SC3').repeatNum,
          },
          {
            x: resultObj.resultObj.control_data.find((item) => item.peak_type === 'SC4').peak_size,
            y: resultObj.resultObj.control_data.find((item) => item.peak_type === 'SC4').repeatNum,
          },
        ]
    };

    let curveData = {
      label: "Standard Curve",
      type: "line",
      pointRadius: 0,
      borderColor: "#546e7a",
      borderWidth: 2,
      animations: false,
      data: [
        {
          x: resultObj.resultObj.control_qc.line[0].x,
          y: resultObj.resultObj.control_qc.line[0].y,
        },
        {
          x: resultObj.resultObj.control_qc.line[1].x,
          y: resultObj.resultObj.control_qc.line[1].y,
        },
      ],
    };

    let fxAnnotations = {
      noraml: {
        type: "box",
        yMin: 0,
        yMax: 44,
        borderWidth: 0,
        backgroundColor: "rgba(0, 240, 110, 0.8)",
        drawTime: "beforeDraw",
      },
      intermediate: {
        type: "box",
        yMin: 45,
        yMax: 54,
        borderWidth: 0,
        backgroundColor: "rgba(135, 135, 135, 0.8)",
        drawTime: "beforeDraw",
      },
      premutation: {
        type: "box",
        yMin: 55,
        yMax: 200,
        borderWidth: 0,
        backgroundColor: "rgba(251, 215, 45, 0.8)",
        drawTime: "beforeDraw",
      },
      mutation: {
        type: "box",
        yMin: 201,
        yMax: 350,
        borderWidth: 0,
        backgroundColor: "rgba(242, 84, 73, 0.8)",
        drawTime: "beforeDraw",
      },
    };

    let chartOptions = {
      devicePixelRatio: 4,
      scales: {
        x: {
          title: {
            display: true,
            text: "Length (bp)",
            font: {
              size: 15,
            },
          },
          grid: {
            display: false,
          },
          min: 200,
          suggestedMax: 1200,
        },
        y: {
          title: {
            display: true,
            text: "Repeats",
            font: {
              size: 15,
            },
          },
          beginAtZero: true,
          max: 350,
        },
      },
      animation: false,
      plugins: {
        legend: {
          display: false,
        },
        annotation: {
          clip: false,
          annotations: fxAnnotations,
        },
        tooltip: {
          enabled: false,
        },
      },
      hover: { mode: null },
      layout: {
        padding: {
          right: 100,
        },
      },
    };

    let sampleScatter = new Array();
    const list_sample_data = Object.values(resultObj.resultObj.sample_data);
    list_sample_data.forEach((sample) => {
      if (sample.sample_id === sampleId) {
        sample.selected_fx_peaks.forEach((peak) => {
          sampleScatter.push({ x: peak.peak_size, y: peak.average_repeatNum });
        });
      }
    });
    sampleScatter.sort(function (a, b) {
      return b.y - a.y;
    });
    sampleScatter.map((s, i) => {
      fxAnnotations[`repeat${i}`] = {
        type: "line",
        yMin: s.y,
        yMax: s.y,
        borderColor: "#8e24aa",
        borderWidth: 1,
        borderDash: [3, 2],
        label: {
          backgroundColor: "#8e24aa",
          content: `${s.y} repeats`,
          display: true,
          position: "end",
          borderWidth: 0,
          yAdjust: i === 0 ? -15 : 15,
          xAdjust: 90,
        },
      };
    });

    let sampleData = {
      label: sampleId,
      type: "scatter",
      pointRadius: 4,
      backgroundColor: "#8e24aa",
      borderWidth: 0,
      borderWidth: 1,
      borderColor: "#ffffff",
      data: sampleScatter,
    };

    return {
      data: {
        datasets: [sampleData, controlData, curveData],
      },
      options: chartOptions,
    };
  };

  function assessmentExport(assessment) {
    const fxAssessment = {
      'Normal': 'normal',
      'Normal/Intermediate': 'intermediate_carrier',
      'Normal/Premutaion': 'premutation_carrier',
      'Normal/Full mutation': 'mutation_carrier',
      'Intermediate/Premutation': 'premutation_carrier',
      'Intermediate/Full mutation': 'mutation_carrier',
      'Intermediate': 'intermediate',
      'Premutation/Full mutation': 'mutation_carrier',
      'Premutation': 'premutation',
      'Full mutation': 'mutation',
      'Invalid': 'invalid',
      'Inconclusive': 'inconclusive'
    };
    return fxAssessment[assessment]
  };

  return selectedExport.map((s) => {
    return {
      result: {
        standard: standardInfoExport(),
        testing: {
          sample: {
            id: s.sampleId,
            name: s.sampleId
          },
          measurement: [ ...s.result.label ],
          assessment: assessmentExport(s.assessment.label),
          chart: s.assessment.value === 'invalid' || s.assessment.value === 'inconclusive'
            ? null
            : chartFxExport(s.sampleId),
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

// HTD 導出結果
export function exportHdProps(resultObj, selectedExport) {

  // 取得標準品資訊
  function standardInfoExport() {
    const expectedLength = [ 121, 199 ];

    const expectRange = [ "109-133", "179-219" ];

    const standardInfoRaw = resultObj.resultObj.standard_control_data;
    const sortedStandardInfoRaw = standardInfoRaw.sort((a, b) => b.peak_size - a.peak_size);

    let standardInfo = new Array();

    expectedLength.forEach((length, idx) => {
      standardInfo.push({
        expectLength: length,
        expectRange: expectRange[idx],
        testedLength: sortedStandardInfoRaw[idx].peak_size
          ? Number(sortedStandardInfoRaw[idx].peak_size)
          : '-',
        result: resultObj.qc_status === 'meet-the-criteria'
          ? 'meetTheCriteria'
          : 'failTheCriteria',
      });
    });

    return standardInfo
  };

  function chartHdExport() {
    let hdChartData = {
      sampleId: undefined,
      bp: new Array(),
      rfu: new Array(),
      repeats: new Array(),
      bpRangeLength: Math.floor((350 - 0) / 50) + 1, // Start from 0 to 350 bp, step 50
    };
    let hdPeak = new Array();
    let bpAnnotation = {};
    let bpAnnotation2 = {};

    const resultData = Object.values(resultObj.resultObj.result_and_data);
    resultData.forEach((s) => {
      hdChartData.sampleId = s.sample_id;
      if (s.selected_target_peaks.length === 1) {
        hdChartData.bp.push(s.selected_target_peaks[0].peak_size);
        hdChartData.rfu.push(s.selected_target_peaks[0].peak_rfu);
        hdChartData.repeats.push(s.selected_target_peaks[0].repeat_num);
        hdPeak = [
          {
            label: hdChartData.sampleId,
            borderColor: "rgb(255, 99, 132)",
            data: [
              { x: 0, y: 0.5 },
              { x: hdChartData.bp[0] - 2, y: 0.5 },
              { x: hdChartData.bp[0], y: hdChartData.rfu[0] },
              { x: hdChartData.bp[0] + 2, y: 0.5 },
              { x: 350, y: 0.5 },
            ],
            pointRadius: 0,
          },
        ];
        bpAnnotation = {
          type: "label",
          content: `${hdChartData.repeats[0]} repeats`,
          font: { size: 15, color: "#435672" },
          xValue: hdChartData.bp[0],
          yAdjust: -15,
          yValue: hdChartData.rfu[0],
        };
      } else {
        hdChartData.bp.push(s.selected_target_peaks[0].peak_size);
        hdChartData.rfu.push(s.selected_target_peaks[0].peak_rfu);
        hdChartData.repeats.push(s.selected_target_peaks[0].repeat_num);
        hdChartData.bp.push(s.selected_target_peaks[1].peak_size);
        hdChartData.rfu.push(s.selected_target_peaks[1].peak_rfu);
        hdChartData.repeats.push(s.selected_target_peaks[1].repeat_num);
        hdPeak = [
          {
            label: hdChartData.sampleId,
            borderColor: "rgb(255, 99, 132)",
            data: [
              { x: 0, y: 0.5 },
              { x: hdChartData.bp[0] - 2, y: 0.5 },
              { x: hdChartData.bp[0], y: hdChartData.rfu[0] },
              { x: hdChartData.bp[0] + 2, y: 0.5 },
              { x: hdChartData.bp[1] - 2, y: 0.5 },
              { x: hdChartData.bp[1], y: hdChartData.rfu[1] },
              { x: hdChartData.bp[1] + 2, y: 0.5 },
              { x: 350, y: 0.5 },
            ],
            pointRadius: 0,
          },
        ];
        bpAnnotation = {
          type: "label",
          content: `${hdChartData.repeats[0]} repeats`,
          font: { size: 15, color: "rgba(245,245,245)" },
          xValue: hdChartData.bp[0],
          yAdjust: -30,
          yValue: hdChartData.rfu[0],
          position: {
            x: "center",
            y: "center",
          },
        };
        bpAnnotation2 = {
          type: "label",
          content: `${hdChartData.repeats[1]} repeats`,
          font: { size: 15, color: "rgba(245,245,245)" },
          xValue: hdChartData.bp[1],
          yAdjust: -15,
          yValue: hdChartData.rfu[1],
          position: {
            x: "start",
            y: "center",
          },
        };
      }

    });
    let hdChart = {
      type: "line",
      data: { datasets: hdPeak },
      options: {
        devicePixelRatio: 4,
        scales: {
          x: {
            type: "linear",
            title: {
              display: true,
              text: "Length (bp)",
              font: {
                size: 15,
              },
            },
            grid: {
              display: false,
            },
            beginAtZero: true,
            suggestedMax: 350,
          },
          y: {
            title: {
              display: true,
              text: "RFU",
              font: {
                size: 15,
              },
            },
            ticks: {
              stepSize: 5,
            },
            beginAtZero: true,
            suggestedMax: 20,
          },
        },
        plugins: {
          annotation: {
            annotations:
              hdChartData.repeats.length > 1
                ? { bpAnnotation, bpAnnotation2 }
                : { bpAnnotation },
          },
          legend: { display: false },
        },
        elements: {
          line: {
            borderWidth: 1,
          },
        },
      },
    };

    return hdChart;
  };

  function assessmentExport(assessment) {
    const hdAssessment = {
      'hd-normal': 'normal',
      'hd-intermediate': 'intermediate',
      'hd-penetrance': 'reducedPenetrance',
      'hd-full': 'fullPenetrance',
      'invalid': 'invalid',
      'inconclusive': 'inconclusive'
    };
    return hdAssessment[assessment]
  };

  return selectedExport.map((s) => {
    return {
      result: {
        standard: standardInfoExport(),
        testing: {
          sample: {
            id: s.sampleId,
            name: s.sampleId
          },
          measurement: s.result.value,
          assessment: assessmentExport(s.assessment.value),
          chart: s.assessment.value === 'invalid' || s.assessment.value === 'inconclusive'
            ? null
            : chartHdExport(),
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

// APOE 導出結果
export function exportApoeProps(resultObj, selectedExport) {
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

  return selectedExport.map((s) => {
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

// MTHFR v1 導出結果
export function exportMthfrv1Props(resultObj, selectedExport) {
  function standardInfoExport() {
    const expectCopy = [ "c.677[C/T]" ];

    let standardInfo = new Array();

    expectCopy.forEach((copy, idx) => {
      standardInfo.push({
        testingGenoType: copy,
        result: resultObj.qc_status === 'meet-the-criteria'
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

  return selectedExport.map((s) => {
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

// MTHFR v2 導出結果
export function exportMthfrv2Props(resultObj, selectedExport) {
  function standardInfoExport() {
    const expectCopy = [ "c.677[C/T]", "c.1298[A/A]" ];

    let standardInfo = new Array();

    expectCopy.forEach((copy) => {
      standardInfo.push({
        testingGenoType: copy,
        result: resultObj.qc_status === 'meet-the-criteria'
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
      'invalid': 'invalid',
    };
    return mthfrAssessment[assessment]
  };

  function measurementExport(measurement) {
    return {
      c677: `${measurement[0]}/${measurement[1]}`,
      c1298: `${measurement[2]}/${measurement[3]}`,
    }
  };

  return selectedExport.map((s) => {
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

// NUDT15 導出結果
export function exportNudt15Props(resultObj, selectedExport) {

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

  return selectedExport.map((s) => {
    return {
      result: {
        testing: {
          sample: {
            id: s.sampleId ? s.sampleId : s.index,
            name: s.sampleId
          },
          measurement: s.result.value,
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

// SMA 導出結果
export function exportSmaProps(resultObj, selectedExport) {
  function standardInfoExport() {
    const expectCopy = resultObj.config.V1.reagent === "accuinSma1"
      ? [ "1:1", "2:2" ]
      : [ "1:1", "2:2", "3:3" ];

    let standardInfo = new Array();

    expectCopy.forEach((copy, idx) => {
      standardInfo.push({
        expectCopy: copy,
        testingCopy: resultObj.qc_status.V1 === 'meet-the-criteria'
          ? expectCopy[idx]
          : '-',
        result: resultObj.qc_status.V1 === 'meet-the-criteria'
          ? 'meetTheCriteria'
          : 'failTheCriteria',
      });
    });

    return standardInfo
  };

  return selectedExport.map((s) => {

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

// SMA v4 導出結果
export function exportSmaV4Props(resultObj, selectedExport) {
  function standardInfoExport() {
    const expectCopy = [ "1:1", "2:2", "3:3" ];

    let standardInfo = new Array();

    expectCopy.forEach((copy, idx) => {
      standardInfo.push({
        expectCopy: copy,
        testingCopy: resultObj.qc_status === 'meet-the-criteria'
          ? expectCopy[idx]
          : '-',
        result: resultObj.qc_status === 'meet-the-criteria'
          ? 'meetTheCriteria'
          : 'failTheCriteria',
      });
    });

    return standardInfo
  };

  return selectedExport.map((s) => {

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

// THAL_BETA 導出結果
export function exportThalBetaProps(resultObj, selectedExport) {

  return selectedExport.map((s) => {

    return {
      result: {
        standard: 'No standard for this product.',
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

export default {
  exportFxProps: exportFxProps,
  exportHdProps: exportHdProps,
  exportApoeProps: exportApoeProps,
  exportMthfrv1Props: exportMthfrv1Props,
  exportMthfrv2Props: exportMthfrv2Props,
  exportSmaProps: exportSmaProps,
  exportSmaV4Props: exportSmaV4Props,
  exportNudt15Props: exportNudt15Props,
  exportThalBetaProps: exportThalBetaProps,
};
