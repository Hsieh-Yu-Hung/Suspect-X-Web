# Suspect-X Web Service

This is web service version of Suspect-X project

### 開發者工具

1. 使用 utility/logger.js 輸出和儲存 logs 檔案 --> [說明](https://github.com/Hsieh-Yu-Hung/Suspect-X-Web/wiki/%E9%81%8B%E8%A1%8C%E4%B8%AD-Log-%E7%94%9F%E6%88%90)

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

See [Configuring quasar.config.js](https://v2.quasar.dev/quasar-cli-webpack/quasar-config-js).
