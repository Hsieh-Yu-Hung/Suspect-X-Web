/**
 * 集中管理後端 admin 的設定
 */

import admin from "firebase-admin";
import {applicationDefault} from "firebase-admin/app";

// Storage Bucket
const storageBucket = "gs://accuinbio-suspect-x.firebasestorage.app/";

// Project ID
const projectId = "accuinbio-suspect-x";

// 初始化 Firebase Admin SDK
admin.initializeApp({
  credential: applicationDefault(),
  projectId: projectId, // 使用你的專案 ID
  storageBucket: storageBucket,
});

// 將 admin 傳出
export default {
  admin,
};
