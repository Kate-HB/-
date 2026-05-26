<template>
  <Teleport to="body">
    <div class="fixed top-5 right-5 z-[9999] flex flex-col gap-y-2">
      <div v-for="(t, i) in toasts" :key="i"
        class="flex items-center gap-x-2 px-4 py-3 rounded-xl shadow-lg text-sm font-medium animate-slide-in min-w-[240px]"
        :class="t.type === 'error' ? 'bg-red-50 text-red-700 border border-red-200' : 'bg-emerald-50 text-emerald-700 border border-emerald-200'">
        <i :class="'fa-solid ' + (t.type === 'error' ? 'fa-circle-exclamation' : 'fa-circle-check')"></i>
        {{ t.message }}
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue';

const toasts = ref([]);
let id = 0;

function showToast(message, type = 'success', duration = 2500) {
  const tid = ++id;
  toasts.value.push({ message, type, id: tid });
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== tid);
  }, duration);
}

defineExpose({ showToast });
</script>

<style scoped>
.animate-slide-in {
  animation: slideIn 0.3s ease-out;
}
@keyframes slideIn {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}
</style>
