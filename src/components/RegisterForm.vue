<template>
  <div class="form flex-column-center q-pa-md">
    <q-form @submit="onSubmit" class="q-gutter-md">

      <div class="flex-column-center">

        <!--Logo-->
        <div style="width: 250px; height: 50px; margin: 1em;">
          <img src="/logo.png" alt="Logo" style="width: 100%; height: 100%;"/>
        </div>

        <!-- Register form -->
        <div class="flex-column-center" style="margin: 1em; background-color: white; border-radius: 1em; padding: 1em;">
          <!-- Title -->
          <div class="text-h6 flex-row-center">
            <q-avatar icon="assignment_add" color="white" text-color="black" />
            <span class="text-h6" style="margin-inline: 0.5em;">Registration</span>
            <q-avatar icon="token" color="white" text-color="black" />
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
              <q-btn class="login-button" color="deep-orange-1" label="Register" text-color="black" rounded />
              <q-btn icon="img:/google_logo.png" class="login-button" color="grey-2" rounded no-caps label="Register with Google" text-color="black" />
              <q-btn no-caps icon="undo" class="login-button" color="grey-2" label="Back to Login" text-color="black" rounded @click="switch_to_login" />
            </div>
          </div>

        </div>

      </div>

    </q-form>
  </div>
</template>

<script setup>

/* Import modules */
import { useRouter } from 'vue-router';
import DropDownList from './DropDownList.vue';

/* refs */
const router = useRouter();

/* emit */
const emit = defineEmits(['switch_to_login']);

/* functions */

// 送出註冊
function onSubmit() {
  console.log('Submit');
}

// 切換表單 -- 登入
function switch_to_login() {
  emit('switch_to_login');
}

</script>

<style scoped>
.form {
  height: 85vh;
  background-color: rgb(255, 230, 238);
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
