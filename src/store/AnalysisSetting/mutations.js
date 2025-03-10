export const updateSettingProps = (state, newSettingProps) => {
  state.settingProps = newSettingProps;
};

export const initCurrentAnalysisID = (state) => {
  state.currentAnalysisID = {
    analysis_name: null,
    analysis_uuid: null,
  };
};

export const updateCurrentAnalysisID = (state, newAnalysisID) => {
  state.currentAnalysisID = newAnalysisID;
};

export const updateCurrentDisplayAnalysisID = (state, newAnalysisID) => {
  state.currentDisplayAnalysisID = newAnalysisID;
};

export const saveReAnalyseSelection = (state, val) => {
  state.SMAv4ReanalyseSelection = val;
};

export const saveSMAv4ReanalysePeakSettings = (state, val) => {
  state.SMAv4ReanalysePeakSettings = val;
};
