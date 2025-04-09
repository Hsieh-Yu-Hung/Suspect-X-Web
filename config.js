/* Beta Thalassemia 測試樣本集 */
const beta_thal_testing_sample = require('./configs/beta_thal_testing_sample.json');
const hbb_mutant_testing_sample = require('./configs/hbb_mutant_testing_sample.json');
const hbb_wild_type_testing_sample = require('./configs/hbb_wild_type_testing_sample.json');
const sanger_low_signal_testing_sample = require('./configs/sanger_low_signal_testing_sample.json');
const non_hbb_sanger_testing_sample = require('./configs/non_hbb_sanger_testing_sample.json');
const non_hbb_highbg_testing_sample = require('./configs/non_hbb_highbg_testing_sample.json');

/* 設定 */
module.exports = {

  // Input A/B Thal Database
  thalassemia: {
    database: '/thal_db/alpha_beta_thalassemia_coverage_v1.xlsx'
  },

  // Testing Samples (TODO:未來加入每一種分析的設定)
  testing_samples: {

    // Beta Thalassemia
    beta_thal: beta_thal_testing_sample,

    // HBB Mutant
    hbb_mutant: hbb_mutant_testing_sample,

    // HBB Wild Type
    hbb_wild_type: hbb_wild_type_testing_sample,

    // Sanger Low Signal
    sanger_low_signal: sanger_low_signal_testing_sample,

    // Non HBB Sanger
    non_hbb_sanger: non_hbb_sanger_testing_sample,

    // Non HBB High BG
    non_hbb_highbg: non_hbb_highbg_testing_sample
  }
}
