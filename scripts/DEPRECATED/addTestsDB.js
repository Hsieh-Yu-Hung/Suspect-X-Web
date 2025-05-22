// Database 路徑
const common_testing_db = 'testing_data';

// 檢查命令列參數
if (process.argv.length !== 4) {
  console.error('使用方式: node addTestsDB.js <database_path> <testing_sample_file>');
  console.error('例如: node addTestsDB.js beta_thal_testings ../configs/beta_thal_testing_sample.json');
  process.exit(1);
}

// 從命令列參數獲取值
const testing_db_path = process.argv[2];
const testing_sample_path = process.argv[3];

// 讀取 configs 中的 json 檔案
let testing_sample;
try {
  testing_sample = require(testing_sample_path);
} catch (error) {
  console.error('無法讀取測試樣本檔案：', error.message);
  process.exit(1);
}

// 初始化 Firebase Admin SDK
const admin = require('firebase-admin');
const serviceAccount = require('../suspect-x-web-service.json');

// 初始化 Firebase Admin
admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

// 取得 Firestore 實例
const db = admin.firestore();

// 將資料加入到 Firestore
async function addTestingData(data_content, database_path) {
  try {
    const batch = db.batch();

    // 遍歷測試數據
    const data_list = Object.keys(data_content);
    data_list.forEach((sample, index) => {

      // 先檢查數據格式
      const documentData = {
        ...{sample_list: data_content[sample]},
      };

      // 確保數據是純物件
      const cleanData = JSON.parse(JSON.stringify(documentData));
      const testingDataRef = db.collection(common_testing_db).doc(database_path);
      batch.set(testingDataRef, cleanData);
    });

    // 提交批次寫入
    await batch.commit();
    console.log('成功添加所有測試數據！');
  } catch (error) {
    console.error('添加數據時發生錯誤：', error);
  } finally {
    // 關閉 Firebase 連接
    admin.app().delete();
  }
}

// 執行函數
addTestingData(testing_sample, testing_db_path);