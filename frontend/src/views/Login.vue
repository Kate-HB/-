<template>
  <div class="min-h-screen flex bg-[radial-gradient(circle_at_top_left,_rgba(59,130,246,0.18),_transparent_35%),linear-gradient(135deg,_#eff6ff_0%,_#f8fafc_45%,_#eef2ff_100%)]">
    <div class="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-600 to-blue-800 items-center justify-center p-12">
      <div class="text-white text-center max-w-md">
        <div class="w-20 h-20 bg-white/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
          <i class="fa-solid fa-store text-4xl"></i>
        </div>
        <h1 class="text-3xl font-bold mb-3">鲜丰超市管理系统</h1>
        <p class="text-blue-100 text-sm leading-relaxed">一站式管理采购、库存、销售、财务、会员与人力资源，助力超市高效运营</p>
        <div class="mt-10 grid grid-cols-3 gap-4 text-center text-blue-100 text-xs">
          <div><div class="text-2xl font-bold text-white mb-1">10+</div>业务模块</div>
          <div><div class="text-2xl font-bold text-white mb-1">28</div>功能页面</div>
          <div><div class="text-2xl font-bold text-white mb-1">49</div>数据模型</div>
        </div>
      </div>
    </div>

    <div class="w-full lg:w-1/2 flex items-center justify-center p-8 bg-slate-50">
      <div class="w-full max-w-sm">
        <div class="lg:hidden text-center mb-8">
          <div class="w-14 h-14 bg-blue-600 rounded-xl flex items-center justify-center mx-auto mb-3">
            <i class="fa-solid fa-store text-2xl text-white"></i>
          </div>
          <h1 class="text-xl font-bold text-slate-800">鲜丰超市管理系统</h1>
        </div>

        <div class="bg-white/90 backdrop-blur rounded-3xl shadow-[0_20px_60px_rgba(15,23,42,0.08)] border border-white/70 p-6 sm:p-7">
          <h2 class="text-lg font-bold text-slate-800 mb-1">登录</h2>
          <p class="text-xs text-slate-400 mb-5">请输入账号密码进入系统</p>

          <div v-if="errorMsg" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-xs flex items-center gap-x-2">
            <i class="fa-solid fa-circle-exclamation"></i>{{ errorMsg }}
          </div>

          <form @submit.prevent="handleLogin" class="space-y-4">
            <div>
              <label class="block text-xs font-medium text-slate-600 mb-1">用户名</label>
              <div class="relative">
                <i class="fa-solid fa-user absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm"></i>
                <input v-model="username" type="text" placeholder="请输入用户名" required
                  class="w-full pl-9 pr-3 py-2.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition" />
              </div>
            </div>

            <div>
              <label class="block text-xs font-medium text-slate-600 mb-1">密码</label>
              <div class="relative">
                <i class="fa-solid fa-lock absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm"></i>
                <input v-model="password" :type="showPwd ? 'text' : 'password'" placeholder="请输入密码" required
                  class="w-full pl-9 pr-10 py-2.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition" />
                <button type="button" @click="showPwd = !showPwd" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-sm">
                  <i :class="showPwd ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye'"></i>
                </button>
              </div>
            </div>

            <button type="submit" :disabled="loading"
              class="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition flex items-center justify-center gap-x-2 disabled:opacity-60">
              <i v-if="loading" class="fa-solid fa-spinner animate-spin"></i>
              {{ loading ? '登录中...' : '登录' }}
            </button>
          </form>
        </div>

        <p class="text-center text-xs text-slate-400 mt-6">&copy; 2026 鲜丰超市管理系统</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const username = ref('');
const password = ref('');
const showPwd = ref(false);
const loading = ref(false);
const errorMsg = ref('');

async function handleLogin() {
  errorMsg.value = '';
  loading.value = true;
  try {
    await authStore.login(username.value, password.value);
    router.push('/dashboard');
  } catch (e) {
    errorMsg.value = e.message || '登录失败，请检查用户名和密码';
  } finally {
    loading.value = false;
  }
}
</script>
