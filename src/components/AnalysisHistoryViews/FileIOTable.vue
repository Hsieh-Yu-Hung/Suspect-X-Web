<template>

  <!-- 標題 -->
  <div style="display: flex; justify-content: space-between; align-items: center;">
    <span class="text-h6 text-bold text-uppercase text-blue-grey-7">{{ props.tableTitle }}</span>
    <q-btn icon="archive" color="white" flat no-caps label="Download Selected" text-color="indigo-6" @click="batchDownload" />
  </div>

  <!-- 分隔線 -->
  <div class="q-pa-md">
    <q-table
      :rows="tableData"
      :columns="tableColumns"
      row-key="id"
      selection="multiple"
      :rows-per-page-options="[1000]"
      v-model:selected="selected_files"
      dense
    >
      <!-- 下載連結 -->
      <template v-slot:body-cell-fileURL="props">
        <td>
          <div style="display: flex; justify-content: center; align-items: center;">
            <a :href="props.row.fileURL" target="_blank">
              <q-icon name="cloud_download" />
            </a>
          </div>
        </td>
      </template>

    </q-table>
  </div>

</template>

<script setup>
// 導入模組
import { useStore } from 'vuex';
import { useQuasar } from 'quasar';
import { ref, onMounted, computed, watch } from 'vue';
import { listAllFilesInFolder, listAllFoldersInPath, getFileMetadata, getFileDownloadURL } from '@/firebase/firebaseStorage';
import { updateGetUserInfo } from '@/composables/accessStoreUserInfo';
import JSZip from 'jszip';
import { saveAs } from 'file-saver';

// 定義 Store, Quasar
const store = useStore();
const $q = useQuasar();

// 定義 props
const props = defineProps({
  tableTitle: {
    type: String,
    required: true,
  },
  tableSource: {
    type: String,
    required: true,
    options: ['input', 'output'],
  },
});

// 定義 selected_files
const selected_files = ref([]);

// 使用者身份
const is_login = ref(false);
const user_info = ref(null);
const user_id = computed(() => {
  return user_info.value ? user_info.value.uid : null;
});

// 從 Store 取得當前選中的 Record ID 和 Product
const selected_record_id = computed(() => {
  return store.getters['analysis_history_data/getCurrentDisplayRecordID'];
});
const selected_product = computed(() => {
  return store.getters['analysis_history_data/getCurrentSelectedProduct'];
});

// 定義一個 Table Row 的資料結構
const tableRow = (fileName, group, fileSize, fileURL) => {
  return {
    id: `${fileName}_${group}`,  // 使用文件名和組合作為唯一標識符
    fileName: fileName,
    group: group,
    fileSize: fileSize,
    fileURL: fileURL,
  }
}

// 定義 table 資料
const tableData = ref([]);

// 定義 table 欄位
const tableColumns = [
  {
    name: 'fileName',
    label: 'File Name',
    field: 'fileName',
    align: 'center',
  },
  {
    name: 'group',
    label: 'Group',
    field: 'group',
    align: 'center',
  },
  {
    name: 'fileSize',
    label: 'File Size',
    field: 'fileSize',
    align: 'center',
  },
  {
    name: 'fileURL',
    label: 'Download',
    field: 'fileURL',
    align: 'center',
  },
];

/* Functions */

// 下載選中的檔案
const batchDownload = async () => {
  if (selected_files.value.length === 0) {
    $q.notify({
      type: 'warning',
      message: '請先選擇要下載的檔案',
      position: 'top',
    });
    return;
  }

  try {
    // 顯示下載進度
    $q.loading.show({
      message: '正在準備下載檔案...',
    });

    const zip = new JSZip();
    const downloadPromises = selected_files.value.map(async (file) => {
      const response = await fetch(file.fileURL);
      const blob = await response.blob();
      zip.file(file.fileName, blob);
    });

    await Promise.all(downloadPromises);

    // 生成 zip 檔案
    const content = await zip.generateAsync({ type: 'blob' });

    // 下載 zip 檔案
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    saveAs(content, `files_${timestamp}.zip`);

  } catch (error) {
    console.error('下載檔案時發生錯誤：', error);
    $q.notify({
      type: 'negative',
      message: '下載檔案時發生錯誤',
      position: 'top',
    });
  } finally {
    $q.loading.hide();
  }
}

// 取得 Input Storage 路徑
const getInputStoragePath = (product) => {
  switch (product) {
    case 'APOE':
      return 'apoe_import';
    case 'FXS':
      return 'fx_import';
    case 'HTD':
      return 'htd_import';
    case 'MTHFR':
      return 'mthfr_import';
    case 'NUDT15':
      return 'nudt15_import';
    case 'SMA':
      return 'sma_import';
    case 'SMAv4':
      return 'sma_import';
    case 'THAL_ALPHA':
      return 'thal_alpha_import';
    case 'THAL_BETA':
      return 'thal_beta_import';
    default:
      return product;
  }
}

// 取得 Output Storage 路徑
const getOutputStoragePath = (product) => {
  switch (product) {
    case 'APOE':
      return 'APOE_results';
    case 'FXS':
      return 'FXS_results';
    case 'HTD':
      return 'HTD_results';
    case 'MTHFR':
      return 'MTHFR_results';
    case 'NUDT15':
      return 'NUDT15_results';
    case 'SMA':
      return 'SMA_results';
    case 'SMAv4':
      return 'SMAv4_results';
    case 'THAL_ALPHA':
      return 'THAL_ALPHA_results';
    case 'THAL_BETA':
      return 'THAL_BETA_results';
    default:
      return product;
  }
}

// 換算檔案大小成為字串
const convertFileSizeToString = (file_size) => {
  if (file_size < 1024) {
    return `${file_size} B`;
  }
  else if (file_size < 1024 * 1024) {
    return `${(file_size / 1024).toFixed(2)} KB`;
  }
  else if (file_size < 1024 * 1024 * 1024) {
    return `${(file_size / 1024 / 1024).toFixed(2)} MB`;
  }
  else if (file_size < 1024 * 1024 * 1024 * 1024) {
    return `${(file_size / 1024 / 1024 / 1024).toFixed(2)} GB`;
  }
}

// 更新 Input Table Data
async function updateInputTableData(product) {

  async function Add_file_to_Row(path, Group) {
    const files = await listAllFilesInFolder(path);
    files.forEach(async (file) => {
      const file_metadata = await getFileMetadata(file.fullPath);
      const file_name = file.name;
      const file_size = convertFileSizeToString(file_metadata.size);
      const file_url = await getFileDownloadURL(file.fullPath);
      const newRow = tableRow(file_name, Group, file_size, file_url);
      tableData.value.push(newRow);
    });
  }

  // 開啟 Loading
  $q.loading.show({
    message: 'Loading...',
  });

  // 清空 Table Data
  tableData.value = [];

  // 取得 Storage 中的選中檔案
  const storage_path = getInputStoragePath(selected_product.value);
  const search_path = `${user_id.value}/${storage_path}/${selected_record_id.value}`;
  const folders = await listAllFoldersInPath(search_path);

  // 依照 Product 更新 Table Data
  switch (product) {

    // APOE
    case "APOE":
      folders.forEach(async (folder) => {
        if (folder.name.includes('control')) {
          await Add_file_to_Row(`${search_path}/${folder.name}`, folder.name);
        }
        else {
          const sampleList = await listAllFoldersInPath(`${search_path}/${folder.name}`);
          sampleList.forEach(async (sample) => {
            await Add_file_to_Row(`${search_path}/${folder.name}/${sample.name}`, "Sample");
          });
        }
      });
      break;

    // FXS
    case "FXS":
      folders.forEach(async (folder) => {
        await Add_file_to_Row(`${search_path}/${folder.name}`, folder.name);
      });
      break;

    // SMA
    case "SMA":
      folders.forEach(async (folder) => {
        await Add_file_to_Row(`${search_path}/${folder.name}`, folder.name);
      });
      break;

    // HTD
    case "HTD":
      folders.forEach(async (folder) => {
        await Add_file_to_Row(`${search_path}/${folder.name}`, folder.name);
      });
      break;

    // MTHFR
    case "MTHFR":
      folders.forEach(async (folder) => {
        await Add_file_to_Row(`${search_path}/${folder.name}`, folder.name);
      });
      break;

    // NUDT15
    case "NUDT15":
      folders.forEach(async (folder) => {
        await Add_file_to_Row(`${search_path}/${folder.name}`, folder.name);
      });
      break;

    // SMAv4
    case "SMAv4":
      folders.forEach(async (folder) => {
        await Add_file_to_Row(`${search_path}/${folder.name}`, folder.name);
      });
      break;

    // THAL_ALPHA
    case "THAL_ALPHA":
      console.log('THAL_ALPHA not implemented');
      break;

    // THAL_BETA
    case "THAL_BETA":
      const files = await listAllFilesInFolder(search_path);
      files.forEach(async (file) => {
        const file_metadata = await getFileMetadata(file.fullPath);
        const file_name = file.name;
        const file_size = convertFileSizeToString(file_metadata.size);
        const file_url = await getFileDownloadURL(file.fullPath);
        const newRow = tableRow(file_name, 'sanger', file_size, file_url);
        tableData.value.push(newRow);
      });
      break;

    default:
      console.error('Error: Invalid product');
      break;
  }

  // 關閉 Loading
  $q.loading.hide();
}

// 更新 Output Table Data
async function updateOutputTableData(product) {

  async function Add_file_to_Row(file, Group) {
    const file_metadata = await getFileMetadata(file);
    const file_name = file.name;
    const file_size = convertFileSizeToString(file_metadata.size);
    const file_url = await getFileDownloadURL(file);
    const newRow = tableRow(file_name, Group, file_size, file_url);
    tableData.value.push(newRow);
  }

  // 開啟 Loading
  $q.loading.show({
    message: 'Loading...',
  });

  // 清空 Table Data
  tableData.value = [];

  // 取得 Storage 中的選中檔案
  const storage_path = getOutputStoragePath(product);
  const search_path = `${user_id.value}/${storage_path}/${selected_record_id.value}`;
  const files = await listAllFilesInFolder(search_path);
  files.forEach(async (file) => {
    await Add_file_to_Row(file, "result");
  });

  // 關閉 Loading
  $q.loading.hide();
}

// Clear Table Data
function clearTableData() {
  tableData.value = [];
}

// Expose
defineExpose({
  clearTableData,
});

// 掛載
onMounted(async () => {
  // 取得使用者身份
  const { login_status } = updateGetUserInfo();
  is_login.value = login_status.value.is_login;
  user_info.value = login_status.value.user_info;

  // 依照 Table Source 更新 Table Data
  if (props.tableSource === 'input') {
    updateInputTableData(selected_product.value);
  }
  else if (props.tableSource === 'output') {
    updateOutputTableData(selected_product.value);
  }
  else {
    console.error('Props Error: Invalid table source');
  }
});

// 監控 selected_record_id
watch(selected_record_id, async () => {
  // 依照 Table Source 更新 Table Data
  if (props.tableSource === 'input') {
    updateInputTableData(selected_product.value);
  }
  else if (props.tableSource === 'output') {
    updateOutputTableData(selected_product.value);
  }
  else {
    console.error('Props Error: Invalid table source');
  }

});

</script>