import { defineStore } from 'pinia';
import { login as apiLogin, logout as apiLogout } from '@/api/auth';

function safeParseUser() {
  try {
    return JSON.parse(localStorage.getItem('user') || 'null');
  } catch {
    return null;
  }
}

function safeParseArray(key) {
  try {
    const value = JSON.parse(localStorage.getItem(key) || '[]');
    return Array.isArray(value) ? value : [];
  } catch {
    return [];
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: safeParseUser(),
    token: localStorage.getItem('token') || null,
    permissions: safeParseArray('permissions')
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
    currentUser: (state) => state.user,
    hasPermission: (state) => (code) => state.permissions.includes(code)
  },
  actions: {
    async login(username, password) {
      const res = await apiLogin(username, password);
      const user = res.data?.user;
      const token = res.data?.token;
      if (!token || !user) {
        throw new Error('登录返回数据不完整');
      }
      this.token = token;
      this.user = user;
      this.permissions = Array.isArray(user.permissions) ? user.permissions : [];
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      localStorage.setItem('permissions', JSON.stringify(this.permissions));
    },
    logout() {
      this.token = null;
      this.user = null;
      this.permissions = [];
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('permissions');
      apiLogout().catch(() => {});
    },
    clearAuth() {
      this.token = null;
      this.user = null;
      this.permissions = [];
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('permissions');
    }
  }
});
