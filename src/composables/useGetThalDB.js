import config from "/config";
import ExcelJS from 'exceljs';

// 輔助函數：將任何可能的富文本轉換為純文本字串
const getRichTextAsString = (value) => {
  if (!value) return '';
  if (typeof value === 'string') return value;
  if (value.richText && Array.isArray(value.richText)) {
    return value.richText.map(rt => rt.text || '').join('');
  }
  return String(value);
};

// 取得 α/β Thal 資料庫
export const getThalassemia = (type) => {
  return new Promise((resolve, reject) => {
    try {
      // 使用相對於網站根目錄的路徑
      const thalDatabasePath = config.thalassemia.database;

      // 使用 fetch 獲取檔案
      fetch(thalDatabasePath)
        .then(response => {
          if (!response.ok) {
            throw new Error(`無法獲取檔案: ${response.status} ${response.statusText}`);
          }
          return response.arrayBuffer();
        })
        .then(buffer => {
          // 使用 ExcelJS 讀取 ArrayBuffer
          const workbook = new ExcelJS.Workbook();
          return workbook.xlsx.load(buffer);
        })
        .then(workbook => {
          // 假設數據在第一個工作表
          const worksheet = workbook.getWorksheet(type); // 使用第一個工作表
          const thalRaw = [];

          // 獲取標題行以確定列索引
          const headerRow = worksheet.getRow(1);
          const headers = {};
          headerRow.eachCell((cell, colNumber) => {
            headers[cell.value] = colNumber;
          });

          // 從第二行開始讀取數據
          worksheet.eachRow((row, rowNumber) => {
            if (rowNumber > 1) { // 跳過標題行
              const gene = row.getCell(headers['Gene Name']).value;
              const variantType = row.getCell(headers['Variant Type']).value;
              const name = row.getCell(headers['Variant Name']).value;
              const disease = row.getCell(headers['Disease']).value;
              const chr = row.getCell(headers['Chromosome']).value;
              const start = row.getCell(headers['Position Start']).value;
              const end = row.getCell(headers['Position End']).value;
              const common = row.getCell(headers['Common']).value;

              // 只添加符合指定類型的數據
              thalRaw.push({
                gene: getRichTextAsString(gene),
                label: getRichTextAsString(name),
                value: getRichTextAsString(name),
                type: getRichTextAsString(variantType),
                chr: getRichTextAsString(chr),
                start: start,
                end: end ? end : null,
                common: common,
                zygosity: 'hetro',
                disease: getRichTextAsString(disease),
              });
            }
          });
          resolve(thalRaw);
        })
        .catch(err => {
          console.error('讀取Excel文件時出錯:', err);
          reject(err);
        });
    } catch (err) {
      console.error('讀取地中海貧血數據庫時出錯:', err);
      reject(err);
    }
  });
};