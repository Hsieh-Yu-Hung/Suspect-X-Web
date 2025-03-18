/* 設定 state */
export default function () {
  return {
    // Exports
    selectedExport: [],

    // Subject info 表格資訊
    subjectInfoTable: [],
    xsubi: [],

    // LAB information
    labInfomation: {
      laboratory: '',
      authorized: '',
      contact: ''
    },

    // 匯出格式
    exportOption: {
      label: 'Excel',
      value: 'xlsx_enUS'
    },

    // Input 的 Export Results
    exportResults: [],
    exportedProduct:''
  }
}