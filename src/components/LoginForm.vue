<template>
  <div class="form flex-column-center q-pa-md">
    <q-form @submit="onSubmit" class="q-gutter-md">

      <div class="flex-column-center">

        <!--Logo-->
        <div style="width: 250px; height: 50px; margin: 1em;">
          <img src="/logo.png" alt="Logo" style="width: 100%; height: 100%;"/>
        </div>

        <!-- Login form -->
        <div class="flex-column-center" style="margin: 1em; background-color: white; border-radius: 1em; padding: 1em;">
          <!-- Title -->
          <div class="text-h6 flex-row-center">
            <q-avatar icon="lock_person" color="white" text-color="black" />
            <span class="text-h6" style="margin-inline: 0.5em;">Member Login</span>
            <q-avatar icon="login" color="white" text-color="black" />
          </div>

          <!--Input fields -->
          <div class="flex-column-center" style="min-width: 400px;">
            <!-- Organization input -->
            <DropDownList label="Organization" icon="public" />

            <!-- E-mail input -->
            <q-input label="E-mail" class="input-field">
              <template v-slot:append>
                <q-icon name="email" />
              </template>
            </q-input>

            <!-- Password input -->
            <q-input label="Password" class="input-field">
              <template v-slot:append>
                <q-icon name="lock" />
              </template>
            </q-input>

            <!-- Login button -->
            <div class="flex-column-center input-field" style="width: 100%;">
              <q-btn class="login-button" color="teal-1" label="Enter" text-color="black" rounded />
              <q-btn icon="img:/google_logo.png" class="login-button" color="grey-2" rounded no-caps label="Sing in with Google" text-color="black" />
              <q-btn icon="img:/icon.png" class="login-button" color="grey-2" rounded no-caps label="Register ACCUiN" text-color="black" @click="switch_to_register" />
            </div>
          </div>

        </div>

      </div>

    </q-form>
  </div>
</template>

<script setup>

/* Import modules */
import DropDownList from './DropDownList.vue';
import { useRouter } from 'vue-router';
import { ref } from 'vue';

/* refs */
const router = useRouter();
const organization_list = ref([]);

/* emit */
const emit = defineEmits(['switch_to_register']);

/* functions */

// 送出登入
function onSubmit() {
  console.log('Submit');
}

// 切換表單 -- 註冊
function switch_to_register() {
  emit('switch_to_register');
}

</script>

<style scoped>
.form {
  height: 85vh;
  background-color: rgb(212, 232, 253);
  border-radius: 1em;
}
.flex-row-center{
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
}
.flex-column-center{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.input-field{
  width: 100%;
  margin-block: 1.2em;
}
.login-button{
  width: 100%;
  margin-block: 0.5em;
}
</style>
