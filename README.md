# Suspect-X-Web (suspect-x-web)

This is web service version of Suspect-X project

### 加入新的 Organization

* 只要在 `AppDataConfig.json` 中修改 / 新增 / 刪除 organization 即可, 會自動讀取和處理

AppDataConfig.json

```json
{
// previous settings ......
  "organization_list": [
    "Organization_1",
    "Organization_2",
    "Organization_3",
    "Organization_4",
    "Organization_5",
    "Organization_6",
    "Organization_7",
    "Organization_8",
    "Organization_9",
    "Organization_10"
  ],
// other settings ......
}

```


### Install the dependencies

```bash
npm install
```

### Start the app in development mode (hot-code reloading, error reporting, etc.)

```bash
npm run dev
```

### Lint the files

```bash
npm run lint
```

### Format the files

```bash
npm run format
```

### Build and Deploy to firebase

```bash
npm run deploy
```

### Customize the configuration

See [Configuring quasar.config.js](https://v2.quasar.dev/quasar-cli-webpack/quasar-config-js).
