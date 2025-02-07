# Nucleus

ACCUiNspection 資料分析核心模組, 將[舊版 Nucleus ](https://github.com/ACCUiNBio/Nucleus)改成 Python 並進行一些優化。

### 運行 Command Line 模式

#### APOE

由於 APOE 輸入檔案複雜, 使用 `JSON `格式的設定檔指定輸入檔案路徑。

使用方式

1. 建立設定檔, 範例如下

   ```json
   {
     "control1_list": [
       "path/to/Standard1_E2.xlsx",
       "path/to/Standard1_E3.xlsx",
       "path/to/Standard1_E4.xlsx",
     ],
     "control2_list": [
       "path/to/Standard2_E2.xlsx",
       "path/to/Standard2_E3.xlsx",
       "path/to/Standard2_E4.xlsx",
     ],
     "samples_list": {
       "SampleA": [
         "/path/to/SampleA_E2.xlsx",
         "/path/to/SampleA_E3.xlsx",
         "/path/to/SampleA_E4.xlsx"
       ],
       "SampleB": [
         "/path/to/SampleB_E2.xlsx",
         "/path/to/SampleB_E3.xlsx",
         "/path/to/SampleB_E4.xlsx"
       ],
     },
     "user_info": {
       "instrument": "qsep100",
       "reagent": "accuinApoe1",
       "organization": "YourOrg"
     }
   }

   ```
2. 執行腳本

```bash
python apoe.py -i <輸入設定檔> -o <輸出 JSON檔>
```

* 可以在設定檔中指定多組 Sample (例如 "SampleA" "SampleB"), 符合設定檔格式即可。
* 如果不指定 `-o` 參數，則會直接將結果印在 console.
* APOE 分析目前不會用到  `"user_info"` 所以設定檔裡面不用考慮 `"organization"` ,`"instrument"`和 `"reagent"` 該放什麼, 不用改

3. 輸出說明

* `"config"` 區塊：分析設定, 將用於 Preview page 的呈現
* `"qc_status"`：表示整個分析有沒有通過 QC, `"fail-the-criteria"` 或 `"meet-the-criteria"`
* `"control1"` 和 `"control2"` 和 `"samples"`: 紀錄檔案的關鍵資料(PEAK Calling), 和該檔案 Peak QC 狀態
* `"result"`：紀錄 Assessment 結果和 關鍵資料(PEAK Selection), 可以直接看到哪一個 Peak RFU ratio 導致 Failed
* 範例：

```json
{
    "config": {
        "reagent": "accuinApoe1",
        "organization": "AdminOrg",
        "instrument": "qsep100",
        "NucleusVersion": "v3.4.3"
    },
    "qc_status": "fail-the-criteria",
    "control1": [
        {
            "file_name": "20240808-APE_APE-E2-SC1_S1A01_R1",
            "sample_id": "APE-E2-SC1",
            "peak_group": "E2",
            "well": "A01",
            "ic_peaks": {
                "peak_group": "E2",
                "peak_type": "control",
                "peak_size": 229,
                "peak_rfu": 9.59
            },
            "tg_peaks": {
                "peak_group": "Target",
                "peak_type": "target",
                "peak_size": "181",
                "peak_rfu": "10.99"
            },
            "normalized_rfu": 1.15,
            "qc_status": "meet-the-criteria",
            "errorMsg": ""
        },
        {"..."},
        {"..."}
    ],
    "control2": ["...同 control1 ..."],
    "samples": {
        "20240805-APE_APE-E2-A7": [
            {
                "file_name": "20240805-APE_APE-E2-A13_S1F07_R1",
                "sample_id": "APE-E2-A13",
                "peak_group": "E2",
                "well": "F07",
                "ic_peaks": {
                    "peak_group": "E2",
                    "peak_type": "control",
                    "peak_size": 216,
                    "peak_rfu": 9.65
                },
                "tg_peaks": {
                    "peak_group": "Target",
                    "peak_type": "target",
                    "peak_size": "168",
                    "peak_rfu": "18.76"
                },
                "normalized_rfu": 1.94,
                "qc_status": "meet-the-criteria",
                "errorMsg": ""
            },
            {"..."},
            {"..."}
        ]
    },
    "result": {
        "20240805-APE_APE-E2-A7": {
            "qc_status": "fail-the-criteria",
            "assessment": "invalid",
            "rfu_status": [
                {
                    "peak_group": "E2",
                    "rfu_value_ratio": 1.94,
                    "rfu_cutoff": 0.7,
                    "pass_cutoff": true
                },
                {
                    "peak_group": "E3",
                    "rfu_value_ratio": 0.36,
                    "rfu_cutoff": 0.7,
                    "pass_cutoff": false
                }
            ]
        }
    }
}
```

#### FXS

#### HTD

#### MTHFR

#### NUDT15

#### SMA
