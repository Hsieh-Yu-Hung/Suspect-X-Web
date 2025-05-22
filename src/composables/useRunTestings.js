import { ResultObject, AssessmentObject } from '@/types/testingTebleObj';
import { ClinicalSignificance } from '@/composables/useInterpretClinvar.js';

/**
 * 定義 AnalysisResultMatrix
 * @param {string} qc
 * @param {Array<ResultObject>} results
 * @param {Array<AssessmentObject>} assessments
 */
class AnalysisResultMatrix {
  constructor(qc, results, assessments) {
    this.qc = qc;
    this.results = results;
    this.assessments = assessments;
  }
}

// 取得試劑
const getReagent = (dataset_class, reagent) => {
  let reagent_value = null;
  let reagent_label = null;
  switch (dataset_class) {
    case 'FXS':
      switch (reagent) {
        case 'FXS_v1':
          reagent_value = 'accuinFx1';
          reagent_label = 'ACCUiN BioTech Fragile X v1';
          break;
        case 'FXS_v2':
          reagent_value = 'accuinFx2';
          reagent_label = 'ACCUiN BioTech Fragile X v2';
          break;
        default:
          break;
      }
    case 'HTD':
      switch (reagent) {
        case 'HTD_v1':
          reagent_value = 'accuinHD1';
          reagent_label = 'ACCUiN BioTech HTD v1';
          break;
        default:
          break;
      }
    case 'MTHFR':
      switch (reagent) {
        case 'MTHFR_v1':
          reagent_value = 'accuinMTHFR1';
          reagent_label = 'ACCUiN BioTech MTHFR v1';
          break;
        case 'MTHFR_v2':
          reagent_value = 'accuinMTHFR2';
          reagent_label = 'ACCUiN BioTech MTHFR v2';
          break;
        case 'MTHFR_v3':
          reagent_value = 'accuinMTHFR3';
          reagent_label = 'ACCUiN BioTech MTHFR v3';
          break;
        default:
          break;
      }
    case 'NUDT15':
      switch (reagent) {
        case 'NUDT15_v1':
          reagent_value = 'accuinNUDT151';
          reagent_label = 'ACCUiN BioTech NUDT15 v1';
          break;
        case 'NUDT15_v2':
          reagent_value = 'accuinNUDT152';
          reagent_label = 'ACCUiN BioTech NUDT15 v2';
          break;
        default:
          break;
      }
    case 'APOE':
      switch (reagent) {
        case 'APOE_v1':
          reagent_value = 'accuinApoe1';
          reagent_label = 'ACCUiN BioTech APOE v1';
          break;
        default:
          break;
      }
    case 'BETA-THAL':
      switch (reagent) {
        case 'BETA-THAL_v1':
          reagent_value = 'accuinTHALBeta';
          reagent_label = 'ACCUiN BioTech THAL Beta';
          break;
        default:
          break;
      }
    case 'SMA_CE':
      switch (reagent) {
        case 'SMA CE v1':
          reagent_value = 'accuinSma4';
          reagent_label = 'SMA CE v1';
          break;
        default:
          break;
      }
    case 'SMA':
      switch (reagent) {
        case 'SMA_v1':
          reagent_value = 'accuinSma1';
          reagent_label = 'ACCUiN BioTech SMA v1';
          break;
        case 'SMA_v2':
          reagent_value = 'accuinSma2';
          reagent_label = 'ACCUiN BioTech SMA v2';
          break;
        case 'SMA_v3':
          reagent_value = 'accuinSma3';
          reagent_label = 'ACCUiN BioTech SMA v3';
          break;
      }
    default:
      break;
  }
  return {
    reagent_value: reagent_value,
    reagent_label: reagent_label,
  }
}

// 轉換 QC 字串
const getQCString = (qc) => {
  switch (qc) {
    case 'meet-the-criteria':
      return 'Passed';
    case 'fail-the-criteria':
      return 'Failed';
    default:
      return 'not-set';
  }
}

/**
 * 取得解析後的結果
 * @param analysisResult
 * @returns {AnalysisResultMatrix}
 */
const getParsedResult = (analysis_name, reagent, result) => {
  switch (analysis_name) {
    case 'FXS':
      return getFXSResult(result);
    case 'HTD':
      return getHTDResult(result);
    case 'MTHFR':
      return getMTHFRResult(result);
    case 'NUDT15':
      return getNUDT15Result(result);
    case 'APOE':
      return getAPOEResult(result);
    case 'THAL_BETA':
      return getBETA_THALResult(result);
    case 'SMA':
      if (reagent === 'SMA CE v1') {
        return getSMA_CE_Result(result);
      }
      else {
        return getSMA_Result(result, reagent);
      }
    default:
      return null;
  }
}

/**
 * 取得 FXS 結果
 * @param analysisResult
 * @returns {AnalysisResultMatrix}
 */
const getFXSResult = (analysisResult) => {

  // 取得 repeat number 字串
  const getRepeatNumberString = (sampleData) => {
    const repeat_number = sampleData.selected_fx_peaks.map((peak) => {
      return peak.average_repeatNum;
    });
    const repeat_number_string = repeat_number.join('/');
    return repeat_number_string;
  }

  // FXS 結果評估標籤
  const interpretationLabel = (value) => {
    if (value === "normal") {
      return "Normal";
    } else if (
      (value === "intermediate") ||
      (value === "normal/intermediate")
    ) {
      return "Intermediate";
    } else if (
      (value === "premutation") ||
      (value === "normal/premutation") ||
      (value === "intermediate/premutation")
    ) {
      return "Premutation";
    } else if (
      (value === "full-mutation") ||
      (value === "normal/full-mutation") ||
      (value === "intermediate/full-mutation") ||
      (value === "premutation/full-mutation")
    ) {
      return "Full";
    } else if (value === "inconclusive"){
      return "Inconclusive";
    } else {
      return "Invalid";
    }
  }

  const resultObj = JSON.parse(analysisResult.result);

  // 取得 QC 字串
  const qc = getQCString(resultObj.qc_status);

  // 取得結果
  const sampleData = resultObj.sample_data;
  const results = sampleData ? Object.values(sampleData).map((sample) => {
    return new ResultObject(sample.sample_id, getRepeatNumberString(sample));
  }) : [];

  // 取得評估
  const sampleResult = resultObj.result
  const assessments = sampleResult ? Object.values(sampleResult).map((sample) => {
    return new AssessmentObject(sample.sample_id, interpretationLabel(sample.assessment));
  }) : [];

  return new AnalysisResultMatrix(qc, results, assessments);
}

/**
 * 取得 HTD 結果
 * @param analysisResult
 * @returns {AnalysisResultMatrix}
 */
const getHTDResult = (analysisResult) => {

  // 取得 repeat number 字串
  const getRepeatNumberString = (sampleData) => {
    const repeat_number = sampleData.selected_target_peaks.map((peak) => {
      return peak.repeat_num;
    });
    const repeat_number_string = repeat_number.join(' / ');
    return repeat_number_string;
  }

  // HTD 結果評估值
  const HTD_assessmentValue = (value) => {
    if (value === "normal") {
      return "Normal";
    } else if (value === "intermediate") {
      return "Intermediate";
    } else if (value === "penetrance") {
      return "Reduced penetrance";
    } else if (value === "full-penetrance") {
      return "Full penetrance";
    } else if (value === "inconclusive") {
      return "Inconclusive";
    } else {
      return "Invalid";
    }
  };

  // 取得 result
  const resultObj = JSON.parse(analysisResult.result);

  // 取得 QC 字串
  const qc = getQCString(resultObj.qc_status);

  // 取得結果和評估
  const sampleData = resultObj.result;
  const results = sampleData ? Object.values(sampleData).map((sample) => {
    return new ResultObject(sample.sample_id, getRepeatNumberString(sample));
  }) : [];
  const assessments = sampleData ? Object.values(sampleData).map((sample) => {
    return new AssessmentObject(sample.sample_id, HTD_assessmentValue(sample.assessment));
  }) : [];

  return new AnalysisResultMatrix(qc, results, assessments);
}

/**
 * 取得 MTHFR 結果
 * @param analysisResult
 * @returns {AnalysisResultMatrix}
 */
const getMTHFRResult = (analysisResult) => {

  // 截取結果字串
  const getResultString = (result_list) => {
    // c.677
    if (result_list.length == 2) {
      return `c677 [${result_list[0]}/${result_list[1]}]`;
    }
    // c.1298
    else if (result_list.length == 4) {
      return `c677 [${result_list[0]}/${result_list[1]}]; c1298 [${result_list[2]}/${result_list[3]}]`;
    }
    // Error
    else {
      return 'not-set';
    }
  }

  // 取得 Assessment
  const getAssessment = (assessment) => {
    if (assessment === 'low-risk') {
      return 'Low Risk';
    } else if (assessment === 'normal-risk') {
      return 'Normal Risk';
    } else if (assessment === 'high-risk') {
      return 'High Risk';
    } else if (assessment === 'invalid') {
      return 'Invalid';
    } else {
      return 'not-set';
    }
  }

  // 取得 result
  const resultObj = JSON.parse(analysisResult.result);

  // 取得 QC 字串
  const qc = getQCString(resultObj.qc_status);

  // 取得 Result, Assessment
  const resultItem = resultObj.resultList;
  const results = resultItem ? resultItem.map((item) => {
    return new ResultObject(item.sample_name, getResultString(item.sample_type));
  }) : [];
  const assessments = resultItem ? resultItem.map((item) => {
    return new AssessmentObject(item.sample_name, getAssessment(item.assessment));
  }) : [];

  return new AnalysisResultMatrix(qc, results, assessments);
}

/**
 * 取得 NUDT15 結果
 * @param analysisResult
 * @returns {AnalysisResultMatrix}
 */
const getNUDT15Result = (analysisResult) => {

  // Result 字串
  const getResultString = (sample_type) => {
    return sample_type.join('/');
  }

  // 取得 Assessment
  const getAssessment = (assessment) => {
    switch (assessment) {
      case 'low-risk':
        return 'Low Risk';
      case 'normal-risk':
        return 'Normal Risk';
      case 'high-risk':
        return 'High Risk';
      case 'inconclusive':
        return 'Inconclusive';
      case 'invalid':
        return 'Invalid';
      default:
        return 'not-set';
    }
  }

  // 取得 result
  const resultObj = JSON.parse(analysisResult.result);

  // 取得 QC 字串
  const qc = getQCString(resultObj.qc_status);

  // 取得結果
  const result_list = resultObj.resultList;
  const results = result_list ? result_list.map((item) => {
    return new ResultObject(item.sample_name, getResultString(item.sample_type));
  }) : [];

  // 取得評估
  const assessments = result_list ? result_list.map((item) => {
    return new AssessmentObject(item.sample_name, getAssessment(item.assessment));
  }) : [];

  return new AnalysisResultMatrix(qc, results, assessments);
}

/**
 * 取得 APOE 結果
 * @param analysisResult
 * @returns {AnalysisResultMatrix}
 */
const getAPOEResult = (analysisResult) => {

  // 解析 APOE 結果
  const parseAPOEResult = (rfu_status) => {
    const rfu_status_list = rfu_status.map((item) => {
      return item.peak_group;
    })
    const rfu_status_list_string = rfu_status_list.join('/');
    return rfu_status_list_string;
  }

  // 評估結果
  const getAssessment = (value) => {
    if (value === 'low-risk') {
      return "Low risk";
    } else if (value === 'normal-risk') {
      return "Normal risk";
    } else if (value === 'high-risk') {
      return "High risk";
    } else if (value === 'inconclusive') {
      return "Inconclusive";
    } else {
      return "Invalid";
    }
  };

  // 取得 result
  const resultObj = JSON.parse(analysisResult.result);

  // 取得 QC 字串
  const qc = getQCString(resultObj.qc_status);

  // 取得 Sample_id 對 Sample_name 的對應
  const sample_name = Object.keys(resultObj.samples);
  const sample_name_to_id = sample_name.map((name) => {
    return {
      sample_name: name,
      sample_id: resultObj.samples[name][0].sample_id
    }
  });

  // 取得 Result, Assessment
  const results = sample_name_to_id.map((item) => {
    return new ResultObject(item.sample_id, parseAPOEResult(resultObj.result[item.sample_name].rfu_status));
  });
  const assessments = sample_name_to_id.map((item) => {
    return new AssessmentObject(item.sample_id, getAssessment(resultObj.result[item.sample_name].assessment));
  });

  return new AnalysisResultMatrix(qc, results, assessments);
}

/**
 * 取得 BETA-THAL 結果
 * @param analysisResult
 * @returns {AnalysisResultMatrix}
 */
const getBETA_THALResult = (analysisResult) => {
  // 取得 result
  const resultObj = JSON.parse(analysisResult.result);

  // 取得 QC 字串
  const qc = getQCString(resultObj.qc_status);

  // 計算嚴重度
  const result_rows = resultObj.result.rows;
  result_rows.forEach(row => {

    // 處理 ClinicalSignificance
    if (row.ClinicalSignificance) {
      // 將 ; 轉換為 /
      if (row.ClinicalSignificance.includes(';')) {
        row.ClinicalSignificance = row.ClinicalSignificance.replace(';', '/');
      }
      // 將 ClinicalSignificance 轉換為列表
      row["ClinSigList"] = row.ClinicalSignificance.split('/');
    }
    else {
      row["ClinSigList"] = [];
    }

    // 計算嚴重度(取最嚴重)
    const separator = '___SEP_ANNO___';
    if (row.ClinSigList.length > 0) {
      const severity = row.ClinSigList.map(items => {
        const item = items.split(separator);
        const severity_level = item.map(i => ClinicalSignificance[i.replaceAll(' ', '_')].severity_level);
        return Math.max(...severity_level);
      });
      row["Severity"] = Math.max(...severity);
    }
    else {
      row["Severity"] = 0;
    }
  });

  // 挑出 Severity 最高的 row 當作結果回報
  const selected_Row = result_rows.sort((a, b) => b.Severity - a.Severity)[0];

  // 結果為 selected_Row 的 Name
  let ResultLabel = selected_Row ? (selected_Row.Name ? selected_Row.Name : 'Not detected') : 'Not detected';
  const resultO = new ResultObject(resultObj.sample_name, ResultLabel);

  // 如果 selected_Row (最嚴重) 有包含 "Pathogenic" 或 "Likely pathogenic" 則回報 "β-thalassemia", 否則回報 "Not detected"
  const key_word_pathogenic = [ClinicalSignificance["Pathogenic"].value, ClinicalSignificance["Likely_pathogenic"].value];
  let AssessmentLabel = selected_Row ? (selected_Row.ClinSigList.some(item => key_word_pathogenic.includes(item)) ? "Pathogenic Detected" : "Not detected") : "Not detected";
  const assessmentO = new AssessmentObject(resultObj.sample_name, AssessmentLabel);

  return new AnalysisResultMatrix(qc, [resultO], [assessmentO]);
}

/**
 * 解釋 SMN 類型
 * @param {integer} smn1
 * @param {integer} smn2
 * @returns {Object}
 */
const smnTypeInterpretation = (smn1, smn2) => {
  const type = String(smn1) + String(smn2);

  const isNormal = (typeArray) => [
    "20", "21", "22", "23", "24",
    "30", "31", "32", "33", "34",
    "41", "42", "43", "44"
  ].includes(typeArray);

  const isCarrier = (typeArray) => ["10", "11", "12", "13", "14"].includes(typeArray);
  const isAffected = (typeArray) => ["01", "02", "03", "04"].includes(typeArray);

  if (isNormal(type)) {
    return { value: "normal", label: "Normal" };
  } else if (isCarrier(type)) {
    return { value: "carrier", label: "SMA carrier" };
  } else if (isAffected(type)) {
    return { value: "affected", label: "SMA affected" };
  } else {
    return { value: "invalid", label: "Invalid" };
  }
};

/**
 * 取得 SMA 結果
 * @param analysisResult
 * @returns {AnalysisResultMatrix}
 */
const getSMA_Result = (analysisResult, reagent) => {

  // 由 reagent 決定用哪個版本
  // SMA_v1: v1 (SMN1 寬鬆; SMN2 寬鬆)
  // SMA_v2: v2 (SMN1 寬鬆; SMN2 嚴格)
  // SMA_v3: v3 (SMN1 嚴格; SMN2 嚴格)
  const usedResult = reagent === 'SMA_v1' ? 'v1' : reagent === 'SMA_v2' ? 'v2' : 'v3';
  console.log("Reagent:", reagent, "Use Result:", usedResult);

  // 取得 result
  const resultObj = JSON.parse(analysisResult.result[usedResult]);

  // 取得 QC 字串
  const qc = getQCString(resultObj.qc_status);

  // 取得 result
  const results = Object.values(resultObj.resultList).map((item) => {
    return new ResultObject(item.sample_name, item.typeStr);
  });

  // 取得 Assessment
  const assessments = Object.values(resultObj.resultList).map((item) => {
    return new AssessmentObject(item.sample_name, smnTypeInterpretation(item.smn1_Type, item.smn2_Type).label);
  });

  return new AnalysisResultMatrix(qc, results, assessments);
}

/**
 * 取得 SMA_CE 結果
 * @param analysisResult
 * @returns {AnalysisResultMatrix}
 */
const getSMA_CE_Result = (analysisResult) => {
  // 取得 result
  const resultObj = JSON.parse(analysisResult.result);

  // 取得 QC 字串
  const qc = getQCString(resultObj.qc_status);

  // 取得 result
  const results = Object.values(resultObj.RESULT_LIST).map((item) => {
    return new ResultObject(item.sample_name, item.typeStr);
  });

  // 取得 Assessment
  const assessments = Object.values(resultObj.RESULT_LIST).map((item) => {
    return new AssessmentObject(item.sample_name, smnTypeInterpretation(item.smn1_copy_number, item.smn2_copy_number).label);
  });

  return new AnalysisResultMatrix(qc, results, assessments);
}

export {
  AnalysisResultMatrix,
  getReagent,
  getQCString,
  getParsedResult,
  getFXSResult,
  getHTDResult,
  getMTHFRResult,
  getNUDT15Result
};
