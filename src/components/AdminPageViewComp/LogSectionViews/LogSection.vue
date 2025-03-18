<template>
  <q-card class="card">

  <!-- Title -->
  <q-card-section >
    <div class="section">

      <!-- 搜尋列和標題 -->
      <div class="q-gutter-x-lg flex flex-center">
        <span class="title">System Logs</span>
        <q-input dense label-color="grey-5" outlined v-model="user_to_filter" label="Search User">
          <template v-slot:append>
            <q-icon name="search" color="grey-5" />
          </template>
        </q-input>
      </div>

      <!--分頁-->
      <div class="q-gutter-lg flex flex-center">
        <q-btn size="sm" dense icon="arrow_back" color="indigo-4" @click="current_page = current_page - 1" />
        <span class="text-indigo-8">Page {{ current_page }} / {{ max_page }}</span>
        <q-btn size="sm" dense icon="arrow_forward" color="indigo-4" @click="current_page = current_page + 1" />
      </div>

      <!-- 按鈕列 -->
      <div class="q-gutter-sm">
        <q-btn icon="info" :color="info_filter_btn_color" flat @click="filter_logs('info')" />
        <q-btn icon="bug_report" :color="debug_filter_btn_color" flat @click="filter_logs('debug')" />
        <q-btn icon="token" :color="analysis_filter_btn_color" flat @click="filter_logs('analysis')" />
        <q-btn icon="warning" :color="warn_filter_btn_color" flat @click="filter_logs('warn')" />
        <q-btn icon="report" :color="error_filter_btn_color" flat @click="filter_logs('error')" />
        <q-btn icon="refresh" color="grey-8" flat @click="update_loaded_logs" />
      </div>

    </div>
  </q-card-section>

  <!-- 我是分隔線 -->
  <q-separator />

  <!-- Content -->
  <q-card-section>
    <LogMessage
      v-for="log in paginated_logs"
      :key="log.id"
      :log_level="log.level"
      :timestamp="log.time"
      :sender="log.user || 'system'"
      :message_content="log.message"
      :source="log.source"
      :style="{ display: log.display ? 'flex' : 'none' }"
    />
  </q-card-section>

  </q-card>
</template>

<script setup>

// 導入元件
import LogMessage from './LogMessage.vue';

// 導入模組
import { ref, onMounted, watch, computed } from 'vue';
import { dataset_list, getData, LOG_DATA } from 'src/firebase/firebaseDatabase';
import { useQuasar } from 'quasar';

// 定義 logs
const all_logs = ref([]);
const loaded_logs = ref([]);

// 定義 quasar
const $q = useQuasar();

// 定義搜尋用戶
const user_to_filter = ref('');

// 定義分頁
const page_size = 200;
const current_page = ref(1);
const max_page = computed(() => {
  return Math.ceil(all_logs.value.length / page_size);
});

// 定義分頁後的 logs
const paginated_logs = computed(() => {
  const start = (current_page.value - 1) * page_size;
  const end = start + page_size;
  return all_logs.value.slice(start, end);
});

// 定義 icon button
const info_filter_btn_color = ref('primary');
const debug_filter_btn_color = ref('lime-8');
const warn_filter_btn_color = ref('orange-8');
const error_filter_btn_color = ref('red-8');
const analysis_filter_btn_color = ref('purple-7');

// 搜集要被過濾掉的項目
const category_to_filter = ref([]);

// 更新 loaded_logs
async function update_loaded_logs() {

  // 顯示 loading
  $q.loading.show({
    message: "取得 logs 中...",
    messageColor: "white",
  });

  // 清除 loaded_logs
  loaded_logs.value = [];

  // 取得 database_logs
  const database_logs = await getData(dataset_list.logs);
  database_logs.data.forEach((log) => {
    // 如果 log id 不在 loaded_logs 中，則加入 loaded_logs
    if (!loaded_logs.value.some(item => item.id === log.id)) {
      loaded_logs.value.push(LOG_DATA(log.id, log.level, log.message, log.timestamp, log.source, log.user));
    }
  });

  // 排序 loaded_logs
  loaded_logs.value.sort((a, b) => {
    return new Date(b.time) - new Date(a.time);
  });

  // 將 all_logs 設為 loaded_logs
  all_logs.value = loaded_logs.value;

  // 隱藏 loading
  setTimeout(() => {
    $q.loading.hide();
  }, 500);
}

// 過濾訊息
function filter_logs(type) {

  // 將 type 加入 category_to_filter
  if (!category_to_filter.value.includes(type)) {
    category_to_filter.value.push(type);
  }

  // 如果 type 已經在 category_to_filter 中，則移除 type
  else {
    category_to_filter.value = category_to_filter.value.filter(item => item !== type);
  }

  // 將所有 logs 的 display 設為 false
  all_logs.value = [];

  // 加入所有 level 為 type 的 logs
  loaded_logs.value.forEach(item => {
    if (!category_to_filter.value.includes(item.level)) {
      all_logs.value.push(item);
    }
  });

  // 更新 icon button 的顏色
  if (type === 'info') {
    info_filter_btn_color.value == 'primary' ? info_filter_btn_color.value = 'blue-1' : info_filter_btn_color.value = 'primary';
  }
  else if (type === 'debug') {
    debug_filter_btn_color.value == 'lime-8' ? debug_filter_btn_color.value = 'lime-2' : debug_filter_btn_color.value = 'lime-8';
  }
  else if (type === 'warn') {
    warn_filter_btn_color.value == 'orange-8' ? warn_filter_btn_color.value = 'orange-2' : warn_filter_btn_color.value = 'orange-8';
  }
  else if (type === 'error') {
    error_filter_btn_color.value == 'red-8' ? error_filter_btn_color.value = 'red-2' : error_filter_btn_color.value = 'red-8';
  }
  else if (type === 'analysis') {
    analysis_filter_btn_color.value == 'purple-7' ? analysis_filter_btn_color.value = 'purple-2' : analysis_filter_btn_color.value = 'purple-7';
  }
}

// 過濾使用者
function filter_user(user) {
  // 將 all_logs 中的所有 user 為 user 的 display 設為反轉
  all_logs.value.forEach(item => {
    if (!item.user.includes(user)) {
      item.display = false;
    }
    else {
      item.display = true;
    }
  });
}

// 掛載時取得 logs
onMounted(async () => {
  await update_loaded_logs();
});

// 監控 user_to_filter
watch(user_to_filter, (new_value) => {
  filter_user(new_value);
});

// 監控 current_page
watch(current_page, (new_value) => {
  if (new_value > max_page.value) {
    current_page.value = 1;
  }
  else if (new_value < 1) {
    current_page.value = max_page.value;
  }
});

</script>

<style scoped>
.card {
  width: 100%;
  overflow: auto;
  height: 100%;
}
.section {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.title {
  font-size: 1.2em;
  font-weight: bold;
}
.subtitle {
  font-size: 1em;
  font-weight: normal;
  font-style: italic;
}
</style>
