# Suspect-X Web Service

This is web service version of Suspect-X project

### 開發者工具

1. 使用 utility/logger.js 輸出和儲存 logs 檔案 --> 說明

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

```bash
npm run emulate:prod # 用 production 設定開啟模擬
npm run emulate:dev  # 用 development 設定開啟模擬
```

### Build and Deploy

```bash
npm run deploy
```

### Customize configuration

See [Configuring quasar.config.js](https://v2.quasar.dev/quasar-cli-webpack/quasar-config-js).
