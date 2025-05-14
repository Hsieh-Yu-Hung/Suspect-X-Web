/**
 * 基本檔案類別
 */
export class BaseFile {
  /**
   * 建立基本檔案
   * @param {string} file_name - 檔案名稱
   * @param {string} file_path - 檔案路徑
   */
  constructor(file_name, file_path) {
    this.file_name = file_name;
    this.file_path = file_path;
  }
}

/**
 * 樣本檔案結構類別
 */
export class SampleFiles {
  /**
   * 建立樣本檔案結構
   * @param {string} name - 樣本名稱
   * @param {Array<BaseFile>} files - 檔案列表
   */
  constructor(name, files) {
    this.name = name;
    this.files = files;
  }
}

/**
 * SMN基因樣本類別
 */
export class SmnSample {
  /**
   * 建立SMN基因樣本
   * @param {string} name - 樣本名稱
   * @param {string} path - 檔案路徑
   * @param {string} expType - 實驗類型
   * @param {string} smnType - SMN類型
   */
  constructor(name, path, expType, smnType) {
    this.name = name;
    this.path = path;
    this.expType = expType;
    this.smnType = smnType;
  }
}

/**
 * 結果矩陣類別
 */
export class ResultMatrix {
  /**
   * 建立結果矩陣
   * @param {string} sample_id - 樣本ID
   * @param {string} result - 結果
   * @param {string} assessment - 評估
   */
  constructor(sample_id = '', result = '', assessment = '') {
    this.sample_id = sample_id;
    this.result = result;
    this.assessment = assessment;
  }

  /**
   * 將類別實例轉換為純 JavaScript 物件
   * @returns {Object} - 純 JavaScript 物件
   */
  toPlainObject() {
    return {
      sample_id: this.sample_id,
      result: this.result,
      assessment: this.assessment
    };
  }
}

/**
 * 基本資料集類別 - 包含通用資料集屬性
 */
export class BaseDataset {
  /**
   * 建立基本資料集
   * @param {string} name - 資料集名稱
   * @param {string} instrument - 使用的儀器
   * @param {string} reagent - 使用的試劑
   * @param {string} storagePath - 儲存路徑
   * @param {Array<ResultMatrix>} result_matrix - 結果矩陣，預設為空陣列
   */
  constructor(name, instrument, reagent, storagePath, result_matrix = []) {
    this.name = name;
    this.originalName = name;
    this.isSelected = false;
    this.edit = false;
    this.instrument = instrument;
    this.reagent = reagent;
    this.storagePath = storagePath;
    this.result_matrix = result_matrix;
  }

  /**
   * 將類別實例轉換為純 JavaScript 物件，適用於 Firebase 儲存
   * @returns {Object} - 純 JavaScript 物件
   */
  toPlainObject() {
    // 取得所有實例屬性的深拷貝
    const plainObj = Object.keys(this).reduce((obj, key) => {
      // 跳過不必要的屬性
      if (['isSelected', 'edit', 'originalName'].includes(key)) {
        return obj;
      }

      // 特殊處理 result_matrix
      if (key === 'result_matrix') {
        // result_matrix 中的元素是普通物件，直接使用
        obj[key] = Array.isArray(this.result_matrix) ? [...this.result_matrix] : [];
        return obj;
      }

      // 深拷貝值
      obj[key] = this[key];
      return obj;
    }, {});

    return plainObj;
  }
}

/**
 * 貝塔地中海貧血資料集類別
 */
export class BetaThalDataset extends BaseDataset {
  /**
   * 建立貝塔地中海貧血資料集
   * @param {string} name - 資料集名稱
   * @param {Array<SampleFiles>} sample_files - 樣本檔案
   * @param {string} instrument - 使用的儀器
   * @param {string} reagent - 使用的試劑
   * @param {string} group - 分組
   * @param {string} qc - 品質控制結果
   * @param {string} storagePath - 儲存路徑
   * @param {Array<ResultMatrix>} result_matrix - 結果矩陣
   */
  constructor(
    name,
    sample_files,
    instrument,
    reagent,
    group,
    qc,
    storagePath,
    result_matrix = []
  ) {
    super(name, instrument, reagent, storagePath, result_matrix);
    this.sample_files = sample_files;
    this.group = group;
    this.qc = qc;
    this.dataset_class = "BETA-THAL";
  }

  /**
   * 覆寫 toPlainObject 方法，處理特定於 BetaThalDataset 的欄位
   * @returns {Object} - 純 JavaScript 物件，包含 BETA-THAL 特有的欄位
   */
  toPlainObject() {
    // 先獲取基本物件
    const plainObj = super.toPlainObject();

    // 對 sample_files 進行深拷貝，確保它是純 JavaScript 物件
    if (Array.isArray(this.sample_files)) {
      plainObj.sample_files = this.sample_files.map(sample => {
        // 深拷貝每個樣本
        const fileCopies = sample.files ? sample.files.map(file => ({
          file_name: file.file_name,
          file_path: file.file_path
        })) : [];

        return {
          name: sample.name,
          files: fileCopies
        };
      });
    }

    return plainObj;
  }
}

/**
 * 脊髓性肌肉萎縮症(SMA)毛細管電泳資料集類別
 */
export class SmaCeDataset extends BaseDataset {
  /**
   * 建立脊髓性肌肉萎縮症(SMA)毛細管電泳資料集
   * @param {string} name - 資料集名稱
   * @param {string} smn1_sc_c - SMN1 標準品C名稱
   * @param {string} smn1_sc_n - SMN1 標準品N名稱
   * @param {Array<SmnSample>} smn1_samples - SMN1 樣本列表
   * @param {string} smn2_sc_c - SMN2 標準品C名稱
   * @param {string} smn2_sc_n - SMN2 標準品N名稱
   * @param {Array<SmnSample>} smn2_samples - SMN2 樣本列表
   * @param {string} instrument - 使用的儀器
   * @param {string} reagent - 使用的試劑
   * @param {string} group - 分組
   * @param {string} qc - 品質控制結果
   * @param {string} storagePath - 儲存路徑
   * @param {Array<ResultMatrix>} result_matrix - 結果矩陣
   */
  constructor(
    name,
    smn1_sc_c,
    smn1_sc_n,
    smn1_samples,
    smn2_sc_c,
    smn2_sc_n,
    smn2_samples,
    instrument,
    reagent,
    group,
    qc,
    storagePath,
    result_matrix = []
  ) {
    super(name, instrument, reagent, storagePath, result_matrix);
    this.smn1_sc_c = smn1_sc_c;
    this.smn1_sc_n = smn1_sc_n;
    this.smn1_samples = smn1_samples;
    this.smn2_sc_c = smn2_sc_c;
    this.smn2_sc_n = smn2_sc_n;
    this.smn2_samples = smn2_samples;
    this.group = group;
    this.qc = qc;
    this.dataset_class = "SMA_CE";
  }

  /**
   * 覆寫 toPlainObject 方法，處理特定於 SmaCeDataset 的欄位
   * @returns {Object} - 純 JavaScript 物件，包含 SMA_CE 特有的欄位
   */
  toPlainObject() {
    // 先獲取基本物件
    const plainObj = super.toPlainObject();

    // 添加 SmaCeDataset 特有的陣列欄位
    plainObj.SMN1_SC_C = [];
    if (this.smn1_sc_c) {
      plainObj.SMN1_SC_C.push({
        name: this.smn1_sc_c,
        path: `testing_data/${this.storagePath}/${this.smn1_sc_c}`,
        expType: "std1",
        smnType: "smn1"
      });
    }

    plainObj.SMN1_SC_N = [];
    if (this.smn1_sc_n) {
      plainObj.SMN1_SC_N.push({
        name: this.smn1_sc_n,
        path: `testing_data/${this.storagePath}/${this.smn1_sc_n}`,
        expType: "std2",
        smnType: "smn1"
      });
    }

    plainObj.SMN1_Samples = Array.isArray(this.smn1_samples) ?
      this.smn1_samples.map(sample => ({
        name: sample.name,
        path: sample.path,
        expType: "sample",
        smnType: "smn1"
      })) : [];

    plainObj.SMN2_SC_C = [];
    if (this.smn2_sc_c) {
      plainObj.SMN2_SC_C.push({
        name: this.smn2_sc_c,
        path: `testing_data/${this.storagePath}/${this.smn2_sc_c}`,
        expType: "std1",
        smnType: "smn2"
      });
    }

    plainObj.SMN2_SC_N = [];
    if (this.smn2_sc_n) {
      plainObj.SMN2_SC_N.push({
        name: this.smn2_sc_n,
        path: `testing_data/${this.storagePath}/${this.smn2_sc_n}`,
        expType: "std2",
        smnType: "smn2"
      });
    }

    plainObj.SMN2_Samples = Array.isArray(this.smn2_samples) ?
      this.smn2_samples.map(sample => ({
        name: sample.name,
        path: sample.path,
        expType: "sample",
        smnType: "smn2"
      })) : [];

    return plainObj;
  }
}

/**
 * qPCR資料集類別
 */
export class QPCRDataset extends BaseDataset {
  /**
   * 建立qPCR資料集
   * @param {string} name - 資料集名稱
   * @param {string} file - 結果檔案路徑
   * @param {string} controlWell - 對照孔位置
   * @param {string} NTCWell - NTC孔位置
   * @param {string} SC1Well - 標準品1孔位置（僅SMA測試）
   * @param {string} SC2Well - 標準品2孔位置（僅SMA測試）
   * @param {string} instrument - 使用的儀器
   * @param {string} reagent - 使用的試劑
   * @param {string} VIC - VIC檔案路徑（僅Z480儀器）
   * @param {string} FAM - FAM檔案路徑（僅Z480儀器）
   * @param {string} CY5 - CY5檔案路徑（僅Z480儀器且僅SMA測試）
   * @param {string} storagePath - 儲存路徑
   * @param {string} group - 分組
   * @param {string} qc - 品質控制結果
   * @param {string} dataset_class - 資料集類別
   * @param {Array<ResultMatrix>} result_matrix - 結果矩陣
   */
  constructor(
    name,
    file,
    controlWell,
    NTCWell,
    SC1Well,
    SC2Well,
    instrument,
    reagent,
    VIC,
    FAM,
    CY5,
    storagePath,
    group,
    qc,
    dataset_class,
    result_matrix = []
  ) {
    super(name, instrument, reagent, storagePath, result_matrix);
    this.file = file;
    this.controlWell = controlWell;
    this.NTCWell = NTCWell;
    this.SC1Well = SC1Well;
    this.SC2Well = SC2Well;
    this.VIC = VIC;
    this.FAM = FAM;
    this.CY5 = CY5;
    this.group = group;
    this.qc = qc;
    this.dataset_class = dataset_class;
  }

  /**
   * 覆寫 toPlainObject 方法，處理特定於 QPCRDataset 的欄位
   * @returns {Object} - 純 JavaScript 物件，包含 qPCR 特有的欄位
   */
  toPlainObject() {
    // 先獲取基本物件
    const plainObj = super.toPlainObject();

    // 添加 QPCRDataset 特有的欄位
    plainObj.resultFile = this.file;
    plainObj.controlWell = this.controlWell;
    plainObj.NTCWell = this.NTCWell;

    // 有條件地加入 SC 相關欄位（SMA測試）
    if (this.SC1Well) plainObj.SC1Well = this.SC1Well;
    if (this.SC2Well) plainObj.SC2Well = this.SC2Well;

    // 有條件地加入 Z480 相關欄位
    if (this.VIC) plainObj.VIC = this.VIC;
    if (this.FAM) plainObj.FAM = this.FAM;
    if (this.CY5) plainObj.CY5 = this.CY5;

    return plainObj;
  }
}

/**
 * Qsep資料集類別
 */
export class QSEPDataset extends BaseDataset {
  /**
   * 建立Qsep資料集
   * @param {string} name - 資料集名稱
   * @param {string} controlFile - Type I: 對照檔案路徑
   * @param {Array<string>} sampleFiles - Type I: 樣本檔案路徑列表
   * @param {Array<string>} sc1_files - Type II: SC1 檔案路徑列表
   * @param {Array<string>} sc2_files - Type II: SC2 檔案路徑列表
   * @param {Array<{group: number, path: string}>} sample_files - Type II: 分組樣本檔案路徑列表
   * @param {string} instrument - 使用的儀器
   * @param {string} reagent - 使用的試劑
   * @param {string} storagePath - 儲存路徑
   * @param {string} dataset_class - 資料集類別
   * @param {string} group - 分組
   * @param {string} qc - 品質控制結果
   * @param {Array<ResultMatrix>} result_matrix - 結果矩陣
   */
  constructor(
    name,
    controlFile,
    sampleFiles,
    sc1_files,
    sc2_files,
    sample_files,
    instrument,
    reagent,
    storagePath,
    dataset_class,
    group,
    qc,
    result_matrix = []
  ) {
    super(name, instrument, reagent, storagePath, result_matrix);
    this.controlFile = controlFile;
    this.sampleFiles = sampleFiles;
    this.sc1_files = sc1_files;
    this.sc2_files = sc2_files;
    this.sample_files = sample_files;
    this.dataset_class = dataset_class;
    this.group = group;
    this.qc = qc;
  }

  /**
   * 覆寫 toPlainObject 方法，處理特定於 QSEPDataset 的欄位
   * @returns {Object} - 純 JavaScript 物件，包含 QSEP 特有的欄位
   */
  toPlainObject() {
    // 先獲取基本物件
    const plainObj = super.toPlainObject();

    // 添加 dataset_name 與 name 相同的值（適配已有的資料結構）
    plainObj.dataset_name = this.name;

    // 根據資料類型不同，添加不同的欄位
    if (this.controlFile) {
      plainObj.controlFile = this.controlFile;
    }

    if (Array.isArray(this.sampleFiles)) {
      plainObj.sampleFiles = this.sampleFiles;
    }

    if (Array.isArray(this.sc1_files)) {
      plainObj.sc1_files = this.sc1_files;
    }

    if (Array.isArray(this.sc2_files)) {
      plainObj.sc2_files = this.sc2_files;
    }

    if (Array.isArray(this.sample_files)) {
      plainObj.sample_files = this.sample_files;
    }

    return plainObj;
  }
}

/**
 * 創建基本檔案的工廠函數
 * @param {string} file_name - 檔案名稱
 * @param {string} file_path - 檔案路徑
 * @returns {BaseFile} - 基本檔案
 */
export function createBaseFile(file_name, file_path) {
  return new BaseFile(file_name, file_path);
}

/**
 * 創建樣本檔案結構的工廠函數
 * @param {string} name - 樣本名稱
 * @param {Array<BaseFile>} files - 檔案列表
 * @returns {SampleFiles} - 樣本檔案結構
 */
export function createSampleFiles(name, files) {
  return new SampleFiles(name, files);
}

/**
 * 創建SMN基因樣本的工廠函數
 * @param {string} name - 樣本名稱
 * @param {string} path - 檔案路徑
 * @param {string} expType - 實驗類型
 * @param {string} smnType - SMN類型
 * @returns {SmnSample} - SMN基因樣本
 */
export function createSmnSample(name, path, expType, smnType) {
  return new SmnSample(name, path, expType, smnType);
}

/**
 * 創建貝塔地中海貧血資料集的工廠函數
 * @param {string} name - 資料集名稱
 * @param {Array<SampleFiles>} sample_files - 樣本檔案
 * @param {string} instrument - 使用的儀器
 * @param {string} reagent - 使用的試劑
 * @param {string} group - 分組
 * @param {string} qc - 品質控制結果
 * @param {string} storagePath - 儲存路徑
 * @param {Array<ResultMatrix>} result_matrix - 結果矩陣
 * @returns {BetaThalDataset} - 貝塔地中海貧血資料集
 */
export function createBetaThalDataset(
  name,
  sample_files,
  instrument,
  reagent,
  group,
  qc,
  storagePath,
  result_matrix = []
) {
  return new BetaThalDataset(
    name,
    sample_files,
    instrument,
    reagent,
    group,
    qc,
    storagePath,
    result_matrix
  );
}

/**
 * 創建脊髓性肌肉萎縮症(SMA)毛細管電泳資料集的工廠函數
 * @param {string} name - 資料集名稱
 * @param {string} smn1_sc_c - SMN1 標準品C名稱
 * @param {string} smn1_sc_n - SMN1 標準品N名稱
 * @param {Array<SmnSample>} smn1_samples - SMN1 樣本列表
 * @param {string} smn2_sc_c - SMN2 標準品C名稱
 * @param {string} smn2_sc_n - SMN2 標準品N名稱
 * @param {Array<SmnSample>} smn2_samples - SMN2 樣本列表
 * @param {string} instrument - 使用的儀器
 * @param {string} reagent - 使用的試劑
 * @param {string} group - 分組
 * @param {string} qc - 品質控制結果
 * @param {string} storagePath - 儲存路徑
 * @param {Array<ResultMatrix>} result_matrix - 結果矩陣
 * @returns {SmaCeDataset} - 脊髓性肌肉萎縮症(SMA)毛細管電泳資料集
 */
export function createSmaCeDataset(
  name,
  smn1_sc_c,
  smn1_sc_n,
  smn1_samples,
  smn2_sc_c,
  smn2_sc_n,
  smn2_samples,
  instrument,
  reagent,
  group,
  qc,
  storagePath,
  result_matrix = []
) {
  return new SmaCeDataset(
    name,
    smn1_sc_c,
    smn1_sc_n,
    smn1_samples,
    smn2_sc_c,
    smn2_sc_n,
    smn2_samples,
    instrument,
    reagent,
    group,
    qc,
    storagePath,
    result_matrix
  );
}

/**
 * 創建qPCR資料集的工廠函數
 * @param {string} name - 資料集名稱
 * @param {string} file - 結果檔案路徑
 * @param {string} controlWell - 對照孔位置
 * @param {string} NTCWell - NTC孔位置
 * @param {string} SC1Well - 標準品1孔位置（僅SMA測試）
 * @param {string} SC2Well - 標準品2孔位置（僅SMA測試）
 * @param {string} instrument - 使用的儀器
 * @param {string} reagent - 使用的試劑
 * @param {string} VIC - VIC檔案路徑（僅Z480儀器）
 * @param {string} FAM - FAM檔案路徑（僅Z480儀器）
 * @param {string} CY5 - CY5檔案路徑（僅Z480儀器且僅SMA測試）
 * @param {string} storagePath - 儲存路徑
 * @param {string} group - 分組
 * @param {string} qc - 品質控制結果
 * @param {string} dataset_class - 資料集類別
 * @param {Array<ResultMatrix>} result_matrix - 結果矩陣
 * @returns {QPCRDataset} - qPCR資料集
 */
export function createQPCRDataset(
  name,
  file,
  controlWell,
  NTCWell,
  SC1Well,
  SC2Well,
  instrument,
  reagent,
  VIC,
  FAM,
  CY5,
  storagePath,
  group,
  qc,
  dataset_class,
  result_matrix = []
) {
  return new QPCRDataset(
    name,
    file,
    controlWell,
    NTCWell,
    SC1Well,
    SC2Well,
    instrument,
    reagent,
    VIC,
    FAM,
    CY5,
    storagePath,
    group,
    qc,
    dataset_class,
    result_matrix
  );
}

/**
 * 創建Qsep資料集的工廠函數
 * @param {Object} params - 參數物件
 * @param {string} params.name - 資料集名稱
 * @param {string} params.controlFile - Type I: 對照檔案路徑
 * @param {Array<string>} params.sampleFiles - Type I: 樣本檔案路徑列表
 * @param {Array<string>} params.sc1_files - Type II: SC1 檔案路徑列表
 * @param {Array<string>} params.sc2_files - Type II: SC2 檔案路徑列表
 * @param {Array<{group: number, path: string}>} params.sample_files - Type II: 分組樣本檔案路徑列表
 * @param {string} params.instrument - 使用的儀器
 * @param {string} params.reagent - 使用的試劑
 * @param {string} params.storagePath - 儲存路徑
 * @param {string} params.dataset_class - 資料集類別
 * @param {string} params.group - 分組
 * @param {string} params.qc - 品質控制結果
 * @param {Array<ResultMatrix>} params.result_matrix - 結果矩陣，預設為空陣列
 * @returns {QSEPDataset} - Qsep資料集
 */
export function createQSEPDataset({
  name,
  controlFile,
  sampleFiles,
  sc1_files,
  sc2_files,
  sample_files,
  instrument,
  reagent,
  storagePath,
  dataset_class,
  group,
  qc,
  result_matrix = []
}) {
  return new QSEPDataset(
    name,
    controlFile,
    sampleFiles,
    sc1_files,
    sc2_files,
    sample_files,
    instrument,
    reagent,
    storagePath,
    dataset_class,
    group,
    qc,
    result_matrix
  );
}

// 可以為其它類型的資料集添加對應的類別和工廠函數
