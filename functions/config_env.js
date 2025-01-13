/**
 * 集中管理後端取用 env
 * 這裡設定的 env 會被傳到 後端 中
 * 取用範例：
 * import configEnv from "./config_env.js";
 * console.log("configEnv", configEnv.VUE_APP_FILE_ENV);
 */

// 選擇環境 ../.env.production (production) 或 ../.env.development (development)
const envPath = "../.env.development";

// 讀取 .env 檔案
const dotenv = require("dotenv");

// 讀取 ENV_PATH 環境變數，預設為 .env
const env = dotenv.config({path: envPath}).parsed;

module.exports = {
  /* 加入新的 env 到這裡 */

  // 選擇環境
  VUE_APP_FILE_ENV: env.VUE_APP_FILE_ENV,
};
