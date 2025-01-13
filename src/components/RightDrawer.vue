<template>
  <div class="drawer-content">
    <q-item style="background-color: #f5f5f5; width: 100%;">
      <q-item-section side>
        <q-avatar color="teal-2" text-color="white" icon="person"/>
      </q-item-section>
      <q-item-section>
        <span class="drawer-lebel-text">{{ display_account_name }}</span>
      </q-item-section>
    </q-item>
    <q-item>
      <q-item-section side>
        <q-icon name="badge" />
      </q-item-section>
      <q-item-section>
        <span class="drawer-lebel-text">身份：{{ display_account_role }}</span>
      </q-item-section>
    </q-item>
    <q-item>
      <q-item-section side>
        <q-icon name="location_city" />
      </q-item-section>
      <q-item-section>
        <span class="drawer-lebel-text">組織：{{ display_account_organization }}</span>
      </q-item-section>
    </q-item>
    <q-item>
      <q-item-section side>
        <q-icon name="lock_open" />
      </q-item-section>
      <q-item-section>
        <span class="drawer-lebel-text">帳號狀態：{{ display_account_status ? '已啟用' : '未啟用' }}</span>
      </q-item-section>
    </q-item>
  </div>
  <div style="display: flex; flex-direction: row; align-items: center; justify-content: center; margin-block: 1em;">
    <q-btn style="width: 100%;" flat label="登出" color="blue-grey-5" @click="on_logout" />
  </div>
</template>

<script setup>

/* Import modules */
import { ref, onMounted, watch } from 'vue';
import { logout } from '@/firebase';
import logger from '@/utility/logger';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';

// 定義 options
defineOptions({
  name: 'RightDrawer'
});

/* expose */
defineExpose({
  update_display_account_name
});

/* refs */
const display_account_name = ref('');
const display_account_status = ref(false);
const display_account_organization = ref('');
const display_account_role = ref('');

// router
const router = useRouter();

// store
const store = useStore();

/* props */
const props = defineProps({
  account_name: {
    type: String,
    required: true
  },
  account_role: {
    type: String,
    required: true
  },
  account_organization: {
    type: String,
    required: true
  },
  account_status: {
    type: Boolean,
    required: true
  }
});

// 登出
async function on_logout() {
  await logout()
  .then((result) => {
    if (result.status === 'success') {
      logger.debug(result.message);
      store.commit('login_status/init_login_status');
      router.push('/');
    }
  })
  .catch((error) => {
    logger.error(error);
  });
}

// 更新 display_account_name
function update_display_account_name() {
  display_account_name.value = props.account_name.split('@')[0];
  display_account_role.value = props.account_role;
  display_account_organization.value = props.account_organization;
  display_account_status.value = props.account_status;
}

/* onMounted */
onMounted(() => {
  update_display_account_name();
});

/* watch props */
watch(() => props, () => {
  update_display_account_name();
}, { deep: true });

</script>

<style scoped>
.drawer-content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;
}
.drawer-lebel-text{
  margin-block: 1em;
  margin-left: 1em;
}
</style>
