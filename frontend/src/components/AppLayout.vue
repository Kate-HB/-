<template>
  <div class="min-h-screen flex flex-col management-bg text-slate-800">
    <AppNavbar />
    <div class="flex flex-1 min-h-0">
      <AppSidebar />
      <main class="flex-1 overflow-auto">
        <div class="p-6 lg:p-8 max-w-[1600px] mx-auto w-full">
          <router-view />
        </div>
      </main>
    </div>
    <Toast ref="toastRef" />
  </div>
</template>

<script setup>
import { ref, provide } from 'vue';
import AppNavbar from './AppNavbar.vue';
import AppSidebar from './AppSidebar.vue';
import Toast from './Toast.vue';

const toastRef = ref(null);
provide('toast', {
  success: (msg) => toastRef.value?.showToast(msg, 'success'),
  error: (msg) => toastRef.value?.showToast(msg, 'error')
});
</script>
