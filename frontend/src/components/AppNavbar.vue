<template>
  <header class="bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between shadow-sm">
    <div class="flex items-center gap-x-3">
      <div class="w-9 h-9 bg-blue-600 rounded-lg flex items-center justify-center">
        <i class="fa-solid fa-store text-white text-sm"></i>
      </div>
      <div>
        <h1 class="text-lg font-bold text-slate-800 tracking-tight">鲜丰超市管理系统</h1>
        <p class="text-xs text-slate-400">Xianfeng Supermarket Management</p>
      </div>
    </div>
    <div class="flex items-center gap-x-4">
      <span class="text-xs text-slate-500 font-mono">{{ currentTime }}</span>
      <div class="relative">
        <i class="fa-solid fa-bell text-slate-400 cursor-pointer hover:text-slate-600"></i>
        <span v-if="notificationCount" class="absolute -top-1.5 -right-1.5 bg-red-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">{{ notificationCount }}</span>
      </div>
      <div class="flex items-center gap-x-2 pl-4 border-l border-slate-200">
        <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
          <i class="fa-solid fa-user text-blue-600 text-xs"></i>
        </div>
        <span class="text-sm font-medium text-slate-700">{{ auth.user?.username || '管理员' }}</span>
        <button @click="handleLogout" class="text-xs text-slate-400 hover:text-red-500 ml-2" title="退出登录">
          <i class="fa-solid fa-right-from-bracket"></i>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();
const router = useRouter();
const currentTime = ref('');
const notificationCount = ref(0);
let timer;

onMounted(() => {
  const update = () => {
    currentTime.value = new Date().toLocaleString('zh-CN', { hour12: false });
  };
  update();
  timer = setInterval(update, 1000);
});

onUnmounted(() => clearInterval(timer));

async function handleLogout() {
  try {
    await auth.logout();
  } finally {
    router.push('/login');
  }
}
</script>
