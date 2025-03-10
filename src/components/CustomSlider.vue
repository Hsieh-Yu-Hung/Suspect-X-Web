<template>

  <!-- 滑桿容器 -->
  <div class="slider-container">

    <!-- 滑桿線 -->
    <div class="slider-line"></div>

    <!-- 固定點數值 -->
    <div class="slider-fixed-point-value"
      v-for="(data, index) in localPointData"
      :key="index"
      :style="{ left: fixedPointLeft(index) }"
    >
      <!-- 點數值和標籤文字 -->
      <div class="label-text-container">
        <div class="label-text">
          <!-- 滑桿點 -->
          <div
            v-if="data.knob"
            class="knob"
            :id="`knob-${index}`"
            :style="{ left: data.knobLeft || '0px' }"
            @mousedown="startDragging($event, index)"
            @mousemove="dragging($event, index)"
            @mouseup="stopDragging($event, index)"
          >
            <div class="knob-label" :style="{ backgroundColor: props.labelColor }">
              <span style="margin-right: 2px;">{{ `${index}N:` }}</span>
              <span style="margin-left: 2px;">{{ localPointData[index].var_value }}</span>
              <div class="label-arrow" :style="{ borderTopColor: props.labelColor }"></div>
            </div>
          </div>

          <!-- 固定點數值 -->
          <span>{{ data.point.toFixed(2) }}</span>
          <br>
          <span>{{ data.label }}</span>
        </div>
      </div>


    </div>

    <!-- 滑桿點 -->
    <div
      v-for="(data, index) in localPointData"
      :key="data.point"
      class="slider-fixed-point"
      :style="{ left: fixedPointLeft(index) }"
    ></div>

  </div>

</template>

<script setup>

// 導入模組
import { ref, computed, onMounted, watch, onUnmounted } from 'vue';

// 接收 Props
const props = defineProps({
  pointData: {
    type: Array,
    required: true,
  },
  labelColor: {
    type: String,
    required: false,
    default: 'rgba(0, 0, 0, 1)',
  },
  name: {
    type: String,
    required: false,
    default: '',
  },
});

// 定義 pointData 的型別
const PointData = (point, knob, label, var_value = null) => {
  return {
    point: parseFloat(point),
    knob: knob,
    label: label,
    knobLeft: '0px',
    var_value: var_value ? parseFloat(var_value) : parseFloat(point),
  };
};

// 處理點數值, 添加 knobLeft 和 var_value
const parsePointData = (pointData) => {
  return pointData.map(item => PointData(item.point, item.knob, item.label, item.var_value));
};

// 處理點數值
const processedPointData = computed(() => parsePointData(props.pointData));
const localPointData = ref(JSON.parse(JSON.stringify(processedPointData.value)));

// 拖曳相關狀態
const isDragging = ref(false);
const currentKnobIndex = ref(null);
const startX = ref(0);

// 開始拖曳
const startDragging = (event, index) => {
  isDragging.value = true;
  currentKnobIndex.value = index;
  startX.value = event.clientX;

  // 添加全局事件監聽
  document.addEventListener('mousemove', handleMouseMove);
  document.addEventListener('mouseup', handleMouseUp);
};

// 拖曳中
const dragging = (event, index) => {
  // 這個函數可以保留，但主要邏輯會在全局事件處理中實現
};

// 停止拖曳
const stopDragging = (event, index) => {
  isDragging.value = false;
  currentKnobIndex.value = null;

  // 移除全局事件監聽
  document.removeEventListener('mousemove', handleMouseMove);
  document.removeEventListener('mouseup', handleMouseUp);
};

// 處理鼠標移動
const handleMouseMove = (event) => {
  if (!isDragging.value) return;

  const sliderContainer = document.querySelector('.slider-container');
  const containerRect = sliderContainer.getBoundingClientRect();
  const containerWidth = containerRect.width;

  // 計算每個點之間的距離
  const pointDistance = containerWidth / (localPointData.value.length - 1);

  // 計算當前點的位置
  const currentIndex = currentKnobIndex.value;
  const currentPointPosition = (pointDistance * currentIndex);

  // 計算前後點的位置限制
  const prevLimit = currentIndex > 0 ? (pointDistance * (currentIndex - 1)) : 0;
  const nextLimit = currentIndex < localPointData.value.length - 1 ? (pointDistance * (currentIndex + 1)) : containerWidth;

  // 計算新位置 (相對於容器)
  const mousePosition = event.clientX - containerRect.left;

  // 限制在前後點之間
  let newPosition = Math.max(prevLimit, Math.min(mousePosition, nextLimit));

  // 計算相對於當前點的偏移量
  const relativePosition = newPosition - currentPointPosition;

  // 更新本地數據中的 knobLeft
  if (currentIndex !== null) {
    localPointData.value[currentIndex].knobLeft = `${relativePosition}px`;
    // 計算並更新 point 值
    // 獲取前後點的值
    const prevPointValue = currentIndex > 0 ? localPointData.value[currentIndex - 1].point : localPointData.value[currentIndex].point;
    const nextPointValue = currentIndex < localPointData.value.length - 1 ? localPointData.value[currentIndex + 1].point : localPointData.value[currentIndex].point;
    const currentOriginalValue = localPointData.value[currentIndex].point;

    // 計算拖動比例 (0-1 之間)
    let dragRatio;
    if (newPosition <= currentPointPosition) {
      // 向左拖動
      dragRatio = (newPosition - prevLimit) / (currentPointPosition - prevLimit);
      // 根據比例計算新的 point 值
      const newPointValue = prevPointValue + (currentOriginalValue - prevPointValue) * dragRatio;
      localPointData.value[currentIndex].var_value = newPointValue.toFixed(2);
    } else {
      // 向右拖動
      dragRatio = (newPosition - currentPointPosition) / (nextLimit - currentPointPosition);
      // 根據比例計算新的 point 值
      const newPointValue = currentOriginalValue + (nextPointValue - currentOriginalValue) * dragRatio;
      localPointData.value[currentIndex].var_value = newPointValue.toFixed(2);
    }
  }
};

// 處理鼠標釋放
const handleMouseUp = () => {
  stopDragging();
};

// 計算 fixed point 的 left 位置
const fixedPointLeft = (index) => {
  if (index === 0) {
    return '0%';
  } else {
    return `${(100 / (localPointData.value.length - 1)) * index}%`;
  }
};

/* Exposed Methods */

// 回傳當前顯示的資料
const getDisplayPointData = () => {
  return localPointData.value.filter(item => item.knob).map(item => ({
    label: item.label,
    value: item.var_value,
  }));
};

// 更新點數值
function updatePointData(newData) {

  // 檢查 newData, 如果 point 有重複的, 只保留一個
  const uniquePoints = new Set();
  const filteredData = newData.filter(item => {
    if (uniquePoints.has(item.point)) {
      return false; // 過濾掉重複的 point
    }
    uniquePoints.add(item.point);
    return true;
  });

  // Update Data
  localPointData.value = parsePointData(filteredData);

  // Get UI
  const sliderContainer = document.querySelector('.slider-container');
  const containerRect = sliderContainer.getBoundingClientRect();
  const containerWidth = containerRect.width;
  const pointDistance = containerWidth / (localPointData.value.length - 1);

  // Get Data value
  let diff_list = [];
  for (let i = 0; i < localPointData.value.length; i++) {
    if (i > 0) {
      diff_list.push(localPointData.value[i].point - localPointData.value[i - 1].point);
    }
  }

  // Update Knob Left
  newData.forEach((item, index) => {
    const local_item = localPointData.value.find(local => local.label === item.label && item.knob);
    if (local_item) {
      const knob_left = (((item.var_value - item.point) / diff_list[index]) * pointDistance).toFixed(2);
      local_item.knobLeft = `${knob_left}px`;
    }
  });
}

// Expose 方法
defineExpose({
  getDisplayPointData,
  updatePointData,
  name: props.name,
});

// 監聽 window 的 resize
const handleWindowResize = () => {
  // 更新滑桿點的位置
  const currentlocalData = JSON.parse(JSON.stringify(localPointData.value));
  updatePointData(currentlocalData);
};

onMounted(() => {
  // 監聽 window 的 resize
  window.addEventListener('resize', handleWindowResize);
});

onUnmounted(() => {
  // 移除 window 的 resize 監聽
  window.removeEventListener('resize', handleWindowResize);
});

</script>

<style scoped>

.slider-container {
  position: relative;
  width: 100%;
  height: 50px;
  margin-bottom: 3em;
  margin-top: 1.5em;
}

.slider-line {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 3px;
  background-color: #ccc;
  border-radius: 5px;
}

.slider-fixed-point {
  position: absolute;
  top: 53%;
  transform: translateY(-50%);
  width: 10px;
  height: 10px;
  background-color: #ccc;
  border-radius: 5px;
}

.slider-fixed-point-value {
  position: absolute;
  top: 80%;
  font-size: 14px;
  font-weight: bold;
  text-align: center;
  color: #979797;
}

.label-text-container {
  position: relative;
}

.label-text {
  position: absolute;
  left: -6px;
  -webkit-user-select: none;  /* Safari */
  -moz-user-select: none;     /* Firefox */
  -ms-user-select: none;      /* IE/Edge */
  user-select: none;          /* 標準語法 */
}

.knob {
  height: 16px;
  width: 16px;
  background-color: white;
  border-radius: 10px;
  position: absolute;
  top: -22px;
  transform: translateX(18%);
  box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.7);
  z-index: 10;
  cursor: pointer;
}

.knob-label {
  position: absolute;
  top: -35px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 12px;
  color: white;
  font-weight: normal;
  background-color: #000;
  padding: 2px 5px;
  border-radius: 5px;
}

.label-arrow {
  position: absolute;
  left: 50%;
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 6px solid #000; /* 預設顏色，會被動態覆蓋 */
  transform: translateX(-50%);
  bottom: -6px;
}

</style>
