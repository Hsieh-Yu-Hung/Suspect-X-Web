// 定義一個 RObject
export class RObject {
  /**
   * 建立 RObject
   * @param {string} sample_id - 樣本ID
   * @param {string} context - 內容
   */
  constructor(sample_id, context) {
    this.sample_id = sample_id;
    this.context = context;
  }
}

// 定義一個 AssessmentObject
export class AssessmentObject extends RObject {
  /**
   * 建立 AssessmentObject
   * @param {string} sample_id - 樣本ID
   * @param {string} context - 內容
   */
  constructor(sample_id, context) {
    super(sample_id, context);
  }
}

// 定義一個 ResultObject
export class ResultObject extends RObject {
  /**
   * 建立 ResultObject
   * @param {string} sample_id - 樣本ID
   * @param {string} context - 內容
   */
  constructor(sample_id, context) {
    super(sample_id, context);
  }
}

// 定義一個 DObject
export class DObject {
  /**
   * 建立 DObject
   * @param {string} dataset_name - 資料集名稱
   * @param {Array<RObject>} anwser_set - 答案集
   * @param {Array<RObject>} test_set - 測試集
   */
  constructor(dataset_name, anwser_set, testing_set) {
    this.dataset_name = dataset_name;
    this.anwser_set = anwser_set;
    this.testing_set = testing_set;
    this.validation = 'not-set';
    this.valid_number = 0;
    this.total_number = this.anwser_set.length;
  }

  // 檢查 anwser_set 和 testing_set 是否符合
  validate() {
    // 創建一個 Map 來存儲 testing_set 中的 sample_id
    const testingSetMap = new Map();
    this.testing_set.forEach(item => {
      testingSetMap.set(item.sample_id, item);
    });

    // 重置符合數量
    this.valid_number = 0;

    // 清理字串的輔助函數
    const cleanString = (str) => {
      return str
        .replace(/[\t\n\r\f\v]+/g, '') // 將所有特殊空白字元轉換為單個空格
        .trim()
        .replace(/\s+/g, ' ') // 將多個連續空格轉換為單個空格
    };

    // 檢查每個 answer 是否在 testing_set 中有對應的 sample_id 且 context 相符
    for (const answer of this.anwser_set) {
      const testingItem = testingSetMap.get(answer.sample_id);
      if (testingItem) {
        const cleanedAnswerContext = cleanString(answer.context);
        const cleanedTestingContext = cleanString(testingItem.context);
        if (cleanedAnswerContext === cleanedTestingContext) {
          this.valid_number++;
        }
      }
    }

    // 根據符合數量判斷整體驗證結果
    if (this.valid_number === this.total_number) {
      this.validation = 'valid';
      return true;
    } else {
      this.validation = 'invalid';
      return false;
    }
  }
}

/* 建立 Array<RObject> 的工廠函數 */
/**
 * 建立 RObject
 * @param {string} sample_id - 樣本ID
 * @param {string} context - 內容
 * @param {string} type - 類型
 * @returns {RObject}
 */
export const createRObject = (sample_id, context, type) => {
  switch (type) {
    case 'assessment':
      return new AssessmentObject(sample_id, context);
    case 'result':
      return new ResultObject(sample_id, context);
  }
}

/* 建立 Array<DObject> 的工廠函數 */
/**
 * 建立 DObject
 * @param {string} dataset_name - 資料集名稱
 * @param {Array<RObject>} anwser_set - 答案集
 * @param {Array<RObject>} testing_set - 測試集
 */
export const createDObject = (dataset_name, anwser_set, testing_set) => {
  return new DObject(dataset_name, anwser_set, testing_set);
}