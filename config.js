const beta_thal_testing_sample = require('./configs/beta_thal_testing_sample.json');

/* 設定 */
module.exports = {

  // Input A/B Thal Database
  thalassemia: {
    database: '/thal_db/alpha_beta_thalassemia_coverage_v1.xlsx'
  },

  // Testing Samples (TODO:未來加入每一種分析的設定)
  testing_samples: {

    // Beta Thalassemia
    beta_thal: beta_thal_testing_sample

  }
}
