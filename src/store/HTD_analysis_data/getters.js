// HTD
export function resultTableHdProps(state) {
  return state.hdResult !== null &&
    state.hdResult.qc.status !== "fail-the-criteria"
    ? state.hdResult.result.map((element) => {
        let selectedProp = {};
        selectedProp.sampleId = element.sample_id;
        selectedProp.internalQc = element.internalQc.status
          ? element.internalQc.status === "meet-the-criteria"
            ? "Meet the criteria"
            : "Fail the criteria"
          : "-";
        selectedProp.repeats =
          element.repeats.length != 0
            ? element.repeats.length < 2
              ? element.repeats[0] + " / " + element.repeats[0]
              : element.repeats.map((p) => p).join(" / ")
            : "-";
        selectedProp.assessment = element.assessment;
        return selectedProp;
      })
    : [];
}

export function hdChartProps(state) {
  if (state.showHdChartId) {
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
    state.hdResult.result.forEach((s) => {
      if (s.sample_id === state.showHdChartId) {
        hdChartData.sampleId = s.sample_id;
        let rawTarget = s.raw.filter((r) => {
          if (r.bp === s.bp[0] || r.bp === s.bp[1]) {
            return r;
          }
        });
        if (s.repeats.length === 1) {
          hdChartData.bp.push(rawTarget[0].bp);
          hdChartData.rfu.push(rawTarget[0].rfu);
          hdChartData.repeats.push(rawTarget[0].repeats);
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
          hdChartData.bp.push(rawTarget[0].bp);
          hdChartData.rfu.push(rawTarget[0].rfu);
          hdChartData.repeats.push(rawTarget[0].repeats);
          hdChartData.bp.push(rawTarget[1].bp);
          hdChartData.rfu.push(rawTarget[1].rfu);
          hdChartData.repeats.push(rawTarget[1].repeats);
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
      }
    });
    let hdChart = {
      type: "line",
      data: { datasets: hdPeak },
      options: {
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
            suggestedMax: Math.max(...hdPeak[0].data.map((d) => d.y)) + 5,
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
          title: {
            display: true,
            text: hdChartData.sampleId,
            font: {
              size: 20,
            },
          },
        },
        elements: {
          line: {
            borderWidth: 1,
          },
        },
      },
    };
    return hdChart;
  } else {
    return null;
  }
}

export function exportHdProps(state) {
  function standardInfoExport() {
    const expectedLength = [ 121, 199 ];

    const expectRange = [ "109-133", "179-219" ];

    const standardInfoRaw = state.hdResult.control;

    let standardInfo = new Array();

    expectedLength.forEach((length, idx) => {
      let standard = 'standard_' + String(idx + 1);

      standardInfo.push({
        expectLength: length,
        expectRange: expectRange[idx],
        testedLength: standardInfoRaw[standard].bp
          ? Number(standardInfoRaw[standard].bp)
          : '-',
        result: state.qualityControlProps.controlAssessment === 'meet-the-criteria'
          ? 'meetTheCriteria'
          : 'failTheCriteria',
      });
    });

    return standardInfo
  };

  function chartHdExport(sampleId) {
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

    state.hdResult.result.forEach((s) => {

      if (s.sample_id === state.showHdChartId) {
        hdChartData.sampleId = s.sample_id;
        let rawTarget = s.raw.filter((r) => {
          if (r.bp === s.bp[0] || r.bp === s.bp[1]) {
            return r;
          }
        });
        if (s.repeats.length === 1) {
          hdChartData.bp.push(rawTarget[0].bp);
          hdChartData.rfu.push(rawTarget[0].rfu);
          hdChartData.repeats.push(rawTarget[0].repeats);
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
          hdChartData.bp.push(rawTarget[0].bp);
          hdChartData.rfu.push(rawTarget[0].rfu);
          hdChartData.repeats.push(rawTarget[0].repeats);
          hdChartData.bp.push(rawTarget[1].bp);
          hdChartData.rfu.push(rawTarget[1].rfu);
          hdChartData.repeats.push(rawTarget[1].repeats);
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

  return state.selectedExport.map((s) => {
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
            : chartHdExport(s.sampleId),
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
