<template>
  <q-select
    outlined
    dense
    :disable="props.disableEdit"
    style="width: 100%; overflow: hidden;"
    :label="display_label"
     v-model="display_selected_value"
     :options="display_options">
    <template v-slot:prepend>
      <q-icon v-if="display_icon" :name="display_icon" />
    </template>
  </q-select>
</template>

<script setup>
/* Import */
import { ref, watch, onMounted } from 'vue';

/* Props */
const props = defineProps({
  name: {
    type: String,
    required: true
  },
  label: {
    type: String,
    required: false
  },
  icon: {
    type: String,
    required: false
  },
  list_data: {
    type: Array,
    required: true
  },
  selected_value: {
    type: String,
    required: false
  },
  disableEdit: {
    type: Boolean,
    required: false
  }
});

/* refs */
const display_options = ref(props.list_data);
const display_selected_value = ref(null);

// UI
const display_label = ref(props.label);
const display_icon = ref(props.icon);

// 發送事件
const emit = defineEmits(['update_selected_value']);

// 套用 UI, 如果存在設定值則套用否則設定為 display_options 的第一個值
if (props.selected_value && display_options.value.includes(props.selected_value)) {
  display_selected_value.value = props.selected_value;
} else {
  display_selected_value.value = display_options.value[0];
}

// 監聽狀態更新
watch(display_selected_value, (new_value, old_value) => {
  const toEmit = {
    name: props.name,
    new_value: new_value,
    old_value: old_value
  };
  emit('update_selected_value', toEmit);
});

// expose
defineExpose({
  display_selected_value
});

</script>

