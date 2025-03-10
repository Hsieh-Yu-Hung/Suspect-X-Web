export const updateSmaResult = (state, val) => {
  state.smaResult = val;
};

export const updateExportResults = (state, val) => {
  state.exportResults = val;
};

export const updateDisplaySMNVersion = (state, val) => {
  state.displaySMN1Version = val.smn1;
  state.displaySMN2Version = val.smn2;
};

export const updateDistanceRatio = (state, val) => {
  state.distanceRatioSmn1 = val.smn1;
  state.distanceRatioSmn2 = val.smn2;
};
