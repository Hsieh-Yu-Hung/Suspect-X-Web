// FXS 結果表格
export function resultTableFxProps(state) {
  return state.fragileXResult !== null
    ? state.fragileXResult.result.map((element) => {
        let selectedProp = {};
        selectedProp.sampleId = element.sample_id;
        selectedProp.gender = element.gender;
        selectedProp.repeats =
          element.position.length != 0
            ? element.gender === "female"
              ? element.position.length < 2
                ? element.position[0].repeats +
                  "/" +
                  element.position[0].repeats
                : element.position.map((p) => p.repeats).join("/")
              : element.position[0].repeats
            : "-";
        selectedProp.interpretation =
          element.interpretation.length != 0
            ? element.interpretation
            : element.assessment === "Invalid"
            ? ["Invalid"]
            : ["Inconclusive"];
        selectedProp.assessment = element.assessment;
        selectedProp.position = element.position;

        return selectedProp;
      })
    : [];
}

// FXS 圖表
export function fxChartProps(state) {
  if (
    state.fragileXResult !== null &&
    state.fragileXResult.qc.status === "Meet the criteria"
  ) {
    let controlData = {
      label: "Control",
      type: "scatter",
      pointRadius: 6,
      borderWidth: 1,
      borderColor: "#ffffff",
      backgroundColor: "rgba(33, 150, 243)",
      animations: false,
      data:
        state.fragileXResult.config.reagent === "accuinFx1"
          ? [
              {
                x: state.fragileXResult.control.standard_1.bp,
                y: state.fragileXResult.control.standard_1.repeats_standard,
              },
              {
                x: state.fragileXResult.control.standard_2.bp,
                y: state.fragileXResult.control.standard_2.repeats_standard,
              },
              {
                x: state.fragileXResult.control.standard_3.bp,
                y: state.fragileXResult.control.standard_3.repeats_standard,
              },
            ]
          : [
              {
                x: state.fragileXResult.control.standard_1.bp,
                y: state.fragileXResult.control.standard_1.repeats_standard,
              },
              {
                x: state.fragileXResult.control.standard_2.bp,
                y: state.fragileXResult.control.standard_2.repeats_standard,
              },
              {
                x: state.fragileXResult.control.standard_3.bp,
                y: state.fragileXResult.control.standard_3.repeats_standard,
              },
              {
                x: state.fragileXResult.control.standard_4.bp,
                y: state.fragileXResult.control.standard_4.repeats_standard,
              },
            ],
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
          x: state.fragileXResult.qc.linear[0][0],
          y: state.fragileXResult.qc.linear[0][1],
        },
        {
          x: state.fragileXResult.qc.linear[1][0],
          y: state.fragileXResult.qc.linear[1][1],
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
    if (!state.showFxChartId) {
      // Only control and standard curve
      return {
        data: {
          datasets: [controlData, curveData],
        },
        options: chartOptions,
      };
    } else {
      // control and standard curve and sample repeats
      let sampleScatter = new Array();
      state.fragileXResult.result.forEach((element) => {
        if (element.sample_id === state.showFxChartId) {
          element.position.forEach((sample) => {
            sampleScatter.push({ x: sample.bp, y: sample.repeats });
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
        label: state.showFxChartId,
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
    }
  } else {
    return null;
  }
}

// FXS 導出結果
export function exportFxProps(state) {
  function standardInfoExport() {
    const expectedLength = state.settingProps.reagent === "accuinFx1"
      ? [ 311, 374, 462 ]
      : [ 311, 374, 462, 823 ];
    const standardRange = state.settingProps.reagent === "accuinFx1"
      ? [ '280-342', '337-411', '416-508' ]
      : [ '280-342', '337-411', '416-508', '741-905' ];

    const standardInfoRaw = state.fragileXResult.control;

    let standardInfo = new Array();

    expectedLength.forEach((length, idx) => {
      let standard = 'standard_' + String(idx + 1);

      standardInfo.push({
        expectLength: length,
        expectRepeat: standardInfoRaw[standard].repeats_standard,
        standardRange: standardRange[idx],
        testingLength: standardInfoRaw[standard].bp
          ? String(standardInfoRaw[standard].bp)
          : '-',
        result: state.qualityControlProps.controlAssessment === 'Meet the criteria'
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
      data: state.settingProps.reagent === "accuinFx1"
        ? [ {
            x: state.fragileXResult.control.standard_1.bp,
            y: state.fragileXResult.control.standard_1.repeats_standard,
          },
          {
            x: state.fragileXResult.control.standard_2.bp,
            y: state.fragileXResult.control.standard_2.repeats_standard,
          },
          {
            x: state.fragileXResult.control.standard_3.bp,
            y: state.fragileXResult.control.standard_3.repeats_standard,
          },
        ]
        : [ {
            x: state.fragileXResult.control.standard_1.bp,
            y: state.fragileXResult.control.standard_1.repeats_standard,
          },
          {
            x: state.fragileXResult.control.standard_2.bp,
            y: state.fragileXResult.control.standard_2.repeats_standard,
          },
          {
            x: state.fragileXResult.control.standard_3.bp,
            y: state.fragileXResult.control.standard_3.repeats_standard,
          },
          {
            x: state.fragileXResult.control.standard_4.bp,
            y: state.fragileXResult.control.standard_4.repeats_standard,
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
          x: state.fragileXResult.qc.linear[0][0],
          y: state.fragileXResult.qc.linear[0][1],
        },
        {
          x: state.fragileXResult.qc.linear[1][0],
          y: state.fragileXResult.qc.linear[1][1],
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

    state.fragileXResult.result.forEach((element) => {
      if (element.sample_id === sampleId) {
        element.position.forEach((sample) => {
          sampleScatter.push({ x: sample.bp, y: sample.repeats });
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
