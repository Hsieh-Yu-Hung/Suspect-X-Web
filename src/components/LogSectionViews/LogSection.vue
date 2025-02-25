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

      <!-- 按鈕列 -->
      <div class="q-gutter-sm">
        <q-btn icon="info" :color="info_filter_btn_color" flat @click="filter_logs('info')" />
        <q-btn icon="bug_report" :color="debug_filter_btn_color" flat @click="filter_logs('debug')" />
        <q-btn icon="token" :color="analysis_filter_btn_color" flat @click="filter_logs('analysis')" />
        <q-btn icon="warning" :color="warn_filter_btn_color" flat @click="filter_logs('warn')" />
        <q-btn icon="report" :color="error_filter_btn_color" flat @click="filter_logs('error')" />
        <q-btn icon="refresh" color="grey-8" flat @click="update_display_logs" />
      </div>

    </div>
  </q-card-section>

  <!-- 我是分隔線 -->
  <q-separator />

  <!-- Content -->
  <q-card-section>
    <LogMessage
      v-for="log in display_logs"
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
import { ref, onMounted, watch } from 'vue';
import { dataset_list, getData, LOG_DATA } from 'src/firebase/firebaseDatabase';

// 定義 logs
const display_logs = ref([]);

// 定義搜尋用戶
const user_to_filter = ref('');

// 定義 icon button
const info_filter_btn_color = ref('primary');
const debug_filter_btn_color = ref('lime-8');
const warn_filter_btn_color = ref('orange-8');
const error_filter_btn_color = ref('red-8');
const analysis_filter_btn_color = ref('purple-7');

// 更新 display_logs
async function update_display_logs() {
  // 清除 display_logs
  display_logs.value = [];

  // 取得 database_logs
  const database_logs = await getData(dataset_list.logs);
  database_logs.data.forEach((log) => {
    // 如果 log id 不在 display_logs 中，則加入 display_logs
    if (!display_logs.value.some(item => item.id === log.id)) {
      display_logs.value.push(LOG_DATA(log.id, log.level, log.message, log.timestamp, log.source, log.user));
    }
  });

  // 排序 display_logs
  display_logs.value.sort((a, b) => {
    return new Date(b.time) - new Date(a.time);
  });
}

// 過濾訊息
function filter_logs(type) {
  // 將 display_logs 中的所有 level 為 type 的 display 設為反轉
  display_logs.value.forEach(item => {
    if (item.level === type) {
      item.display = !item.display;
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
  // 將 display_logs 中的所有 user 為 user 的 display 設為反轉
  display_logs.value.forEach(item => {
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
  await update_display_logs();
});

// 監控 user_to_filter
watch(user_to_filter, (new_value) => {
  filter_user(new_value);
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
