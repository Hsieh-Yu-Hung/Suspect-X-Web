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
