/* 設定 state */
export default function () {
  return {
    // 預設設定
    defaultSettingProps: {
      instrument: "qsep100",
      product: "fx",
      reagent: "accuinFx1",
      instrumentLabel: "Qsep 100",
      productLabel: "FXS",
      reagentLabel: "ACCUiN BioTech Fragile X v1",
    },
    // 當前設定
    settingProps: {
      instrument: "",
      product: "",
      reagent: "",
      instrumentLabel: "",
      productLabel: "",
      reagentLabel: "",
    },
    // Analysis ID
    currentAnalysisID: {
      analysis_name: null,
      analysis_uuid: null,
    },
  }
}
