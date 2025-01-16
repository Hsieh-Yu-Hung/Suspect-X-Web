<template>
  <q-select outlined :disable="props.disableEdit" dense style="width: 100%;" :label="display_label" v-model="display_selected_value" :options="display_options">
    <template v-slot:prepend>
      <q-icon v-if="display_icon" :name="display_icon" />
    </template>
  </q-select>
</template>

<script setup>
/* Import */
import { ref } from 'vue';

/* Props */
const props = defineProps({
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
const display_options = ref([]);
const display_selected_value = ref(null);
const display_disable_edit = ref(false);

// UI
const display_label = ref(null);
const display_icon = ref(null);

// 套用 UI
display_options.value = props.list_data;
display_disable_edit.value = props.disableEdit;
display_label.value = props.label;
display_icon.value = props.icon;
if (props.selected_value && display_options.value.includes(props.selected_value)) {
  display_selected_value.value = props.selected_value;
} else {
  display_selected_value.value = display_options.value[0];
}

// expose
defineExpose({
  display_selected_value
});

</script>

