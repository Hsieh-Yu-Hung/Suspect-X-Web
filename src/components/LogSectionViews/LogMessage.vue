<template>
  <!-- 訊息區塊 -->
  <div
    class="message-block"
    :class="{ 'block-expand': expand_msg_block }"
    :style="{ backgroundColor: message_color(log_level) }"
    @click="!expand_msg_block ? toggle_expand_msg_block() : null"
  >

    <!-- Icon -->
    <q-icon :name="icon_name(log_level)" :color="icon_color(log_level)" size="sm"/>

    <!-- level-->
    <div :style="{ display: expand_msg_block ? 'block' : 'none' }">
      <span>Level：</span>
      <span>{{ log_level.toUpperCase() }}</span>
    </div>

    <!-- 時間 -->
    <div style="display: flex; flex-direction: row; gap: 10px;">
      <span :style="{ display: expand_msg_block ? 'block' : 'none' }">時間：</span>
      <span>{{ timestamp }}</span>
    </div>

    <!-- 發送者 -->
    <div :class="{ 'sender-collapse': !expand_msg_block, 'sender-expand': expand_msg_block }">
      <span :style="{ display: expand_msg_block ? 'block' : 'none' }">發送者：</span>
      <q-chip dense :color="sender_color(sender)" size="md" :label="sender" />
    </div>

    <!-- 訊息內容 -->
    <div :class="{ 'text-ellipsis': !expand_msg_block }" style="flex: 1; height: 1.5em; flex-direction: row; gap: 10px;">
      <span :style="{ display: expand_msg_block ? 'block' : 'none' }">訊息內容：</span>
      <p>{{ message_content }}</p>
    </div>

    <!-- 程式碼來源-->
    <div :style="{ display: expand_msg_block ? 'block' : 'none' }">
      <span>程式碼來源：</span>
      <span>{{ source }}</span>
    </div>

    <!-- 展開按鈕 -->
    <q-btn
      dense
      flat
      :icon="expand_msg_block ? 'expand_less' : 'expand_more'"
      color="deep-orange-7"
      size="sm"
      :style="{
        width: expand_msg_block ? '100%' : 'auto',
        border: expand_msg_block ? '0.5px solid pink' : 'none',
      }"
      @click.stop="toggle_expand_msg_block"
    />

  </div>
</template>

<script setup>

// 導入模組
import { ref } from 'vue';

// Props
const props = defineProps({
  log_level: {
    type: String,
    required: true
  },
  timestamp: {
    type: String,
    required: true
  },
  sender: {
    type: String,
    required: true
  },
  message_content: {
    type: String,
    required: true
  },
  source: {
    type: String,
    required: true
  }
});

// 控制訊息展開變數
const expand_msg_block = ref(false);

// 取得 icon 名稱
const icon_name = (level) => {
  switch (level) {
    case 'info':
      return 'info';
    case 'warn':
      return 'warning';
    case 'debug':
      return 'bug_report';
    case 'error':
      return 'report';
    case 'analysis':
      return 'token';
    default:
      return 'info';
  }
}

// 取得 icon 顏色
const icon_color = (level) => {
  switch (level) {
    case 'info':
      return 'primary';
    case 'warn':
      return 'warning';
    case 'debug':
      return 'grey-8';
    case 'error':
      return 'red-9';
    case 'analysis':
      return 'purple-7';
  }
}

// 取得訊息顏色
const message_color = (level) => {
  switch (level) {
    case 'info':
      return 'white';
    case 'warn':
      return 'rgb(255, 255, 0, 0.2)';
    case 'debug':
      return 'white';
    case 'error':
      return 'rgb(255, 0, 0, 0.1)';
  }
}

// Sender Color
const sender_color = (sender) => {
  switch (sender) {
    case 'admin':
      return 'green-4';
    case 'system':
      return 'red-2';
    default:
      return 'blue-1';
  }
}

// 控制訊息展開功能
function toggle_expand_msg_block() {
  expand_msg_block.value = !expand_msg_block.value;
}
</script>

<style scoped>
.message-block {
  display: flex;
  flex-direction: row;
  gap: 2em;
  margin-block: 1em;
  cursor: pointer;
  align-items: center;
}

.block-expand {
  flex-direction: column;
  align-items: flex-start;
  cursor: default;
  border: 1px solid #cdcdcd;
  border-radius: 1em;
  padding: 1em;
  transition: all 0.5s;
}

.text-ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sender-collapse {
  display: flex;
  flex-direction: row;
  gap: 10px;
  width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  justify-content: center;
  align-items: center;
}

.sender-expand {
  display: flex;
  flex-direction: row;
  gap: 10px;
  width: fit-content;
  overflow: hidden;
  text-overflow: ellipsis;
  justify-content: center;
  align-items: center;
}
</style>
