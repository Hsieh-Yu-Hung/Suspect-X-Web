// Database 路徑
const common_testing_db = 'testing_data';
const beta_thal_testing_db = 'beta_thal_testings';

// 讀取 configs 中的 json 檔案
const beta_thal_testing_sample = require("../configs/beta_thal_testing_sample.json");

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
addTestingData(beta_thal_testing_sample, beta_thal_testing_db);