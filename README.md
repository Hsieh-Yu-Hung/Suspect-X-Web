# Suspect-X Web Service

This is web service version of Suspect-X project

### 開發者工具

1. [使用 utility/logger.js 輸出和儲存 logs 檔案](https://github.com/Hsieh-Yu-Hung/Suspect-X-Web/wiki/%E9%81%8B%E8%A1%8C%E4%B8%AD-Log-%E7%94%9F%E6%88%90)
2. [使用 firebase functions](https://github.com/Hsieh-Yu-Hung/Suspect-X-Web/wiki/%E4%BD%BF%E7%94%A8-firebase-function(%E5%BE%8C%E7%AB%AF))
3. [使用 .env 控制環境變數](https://github.com/Hsieh-Yu-Hung/Suspect-X-Web/wiki/%E6%8E%A7%E5%88%B6%E7%92%B0%E5%A2%83%E8%AE%8A%E6%95%B8)
4. [使用 firebase SDK](https://github.com/Hsieh-Yu-Hung/Suspect-X-Web/wiki/%E4%BD%BF%E7%94%A8%E6%A8%A1%E7%B5%84%E5%8C%96%E7%9A%84firebase-SDK)

### Install the dependencies

```bash
npm install
```

### Dev mode

* Start the app in development mode (hot-code reloading, error reporting, etc.)
* 該模式無法使用 firebase function, 適合用於介面開發

```bash
npm run dev
```

### Build and Enumerate

* 需要中斷以及重新啟動才能更新！
* Production 設定會使用真正的 firebase 功能, deploy 之後才能用！
* Development 設定會模擬全部的 firebase 功能, 不用 deploy.

```bash
npm run emulate:prod # 用 production 設定開啟模擬
npm run emulate:dev  # 用 development 設定開啟模擬
```

### Build and Deploy

* Deploy 應用 production 設定

```bash
npm run deploy
```

### Customize configuration

Quasar 設定： [Configuring quasar.config.js](https://v2.quasar.dev/quasar-cli-webpack/quasar-config-js).

### 設定 Service Account 憑證

1. 生成 Service Account 憑證

```
firebase console --> Suspect-X --> 專案總覽 --> 專案設定 --> 服務脹戶 --> Firebase Admin SDK --> 產生新的密鑰
```

2. 下載密鑰 (json) 之後 , 放到 Suspect-X-web 專案資料夾中
3. 在專案中設定 Service Account 憑證, 執行以下指令

```bash
firebase functions:config:set google.credentials="/path/to/your/credentials.json"
```

4. 在程式碼中使用 applicationDefault() 預設就可以使用到 Service Account 憑證了

＊ 目前 firebase function 相關的 admin 設定被集中管理在 `config_admin.js`
