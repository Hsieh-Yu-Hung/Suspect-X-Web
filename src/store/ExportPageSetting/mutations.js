export const updateSelectedExport = (state, val) => {
  state.selectedExport = val;
};

export const updateSubjectInfoTable = (state, newSubjectInfoTable) => {
  state.subjectInfoTable = newSubjectInfoTable;
};

export const updateXsubi = (state, newXsubi) => {
  state.xsubi = newXsubi;
};

export const updateLabInfomation = (state, newLabInfomation) => {
  state.labInfomation.laboratory = newLabInfomation.laboratory;
  state.labInfomation.authorized = newLabInfomation.authorized;
  state.labInfomation.contact = newLabInfomation.contact;
};

export const updateExportOption = (state, newExportOption) => {
  state.exportOption.label = newExportOption.label;
  state.exportOption.value = newExportOption.value;
};

export const initExportPageSetting = (state) => {
  state.subjectInfoTable = [];
  state.xsubi = [];
  state.labInfomation = {
    laboratory: '',
    authorized: '',
    contact: ''
  };
  state.exportOption = {
    label: 'Excel',
    value: 'xlsx_enUS'
  };
};

// Input 用的 Export Results
export const updateExportResults = (state, newExportResults) => {
  state.exportResults = newExportResults;
};

// 初始化 Export Results
export const initExportResults = (state) => {
  state.exportResults = [];
};

// 更新 exportedProduct
export const updateExportedProduct = (state, newExportedProduct) => {
  state.exportedProduct = newExportedProduct;
};
