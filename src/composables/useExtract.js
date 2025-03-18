import ExcelJS from "exceljs";
import { ParseInputAnalysisLims } from "@/firebase/firebaseFunction";

export function extract(subjectFile) {
  return new Promise((resolve, reject) => {
    const file_path = subjectFile.path;
    ParseInputAnalysisLims({ file_path: file_path })
      .then(response => {
        resolve(response.data.result);
      })
      .catch(err => {
        reject(err);
      });
  });
}

export function downloadTemplate() {
  return new Promise((resolve, reject) => {
    try {
      const workbook = new ExcelJS.Workbook();
      const worksheet = workbook.addWorksheet('工作表1');

      // 設定標題行
      const headers = [
        '開單日期', '流水號', '場次', '院所代號', '院所簡稱',
        '原病歷號', '姓名', '身分證號', '生日', '性別',
        '申報', '列印', '審核', '待件', '原就醫日',
        '就醫序號', '審核人', '開單人'
      ];

      // 添加標題行
      worksheet.addRow(headers);

      // 設定標題行樣式
      const headerRow = worksheet.getRow(1);
      headerRow.eachCell((cell) => {
        cell.font = { bold: true };
        cell.fill = {
          type: 'pattern',
          pattern: 'solid',
          fgColor: { argb: 'FFD3D3D3' } // 淺灰色背景
        };
        cell.border = {
          top: { style: 'thin' },
          left: { style: 'thin' },
          bottom: { style: 'thin' },
          right: { style: 'thin' }
        };
        cell.alignment = { vertical: 'middle', horizontal: 'center' };
      });

      // 設定必要欄位的樣式（以紅色標記）
      const requiredColumns = ['開單日期', '流水號', '姓名', '身分證號', '生日', '性別', '原就醫日'];
      requiredColumns.forEach(colName => {
        const colIndex = headers.indexOf(colName);
        if (colIndex !== -1) {
          const cell = headerRow.getCell(colIndex + 1);
          cell.font = { bold: true, color: { argb: 'FFFF0000' } }; // 紅色字體
        }
      });

      // 設定列寬
      headers.forEach((header, i) => {
        worksheet.getColumn(i + 1).width = 15;
      });

      // 添加範例資料行
      const exampleRow = [
        '112/01/01', 'A001', '上午', 'H123456789', '範例醫院',
        '12345', '王小明', 'A123456789', '80/01/01', '男',
        'Y', 'Y', 'Y', 'N', '112/01/01',
        '001', '審核員', '醫師名'
      ];
      worksheet.addRow(exampleRow);

      // 生成 Blob 並下載
      workbook.xlsx.writeBuffer()
        .then(buffer => {
          const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = 'LIMS_Template.xlsx';
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);
          resolve();
        })
        .catch(err => {
          console.error('生成 Excel 檔案時發生錯誤:', err);
          reject(err);
        });
    } catch (err) {
      console.error('建立 Excel 範本時發生錯誤:', err);
      reject(err);
    }
  });
}
