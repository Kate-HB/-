<template>
  <aside class="w-60 bg-slate-800 text-white flex flex-col flex-shrink-0 min-h-screen">
    <nav class="flex-1 py-4 overflow-y-auto">
      <div v-for="group in menus" :key="group.id" class="mb-1">
        <div v-if="group.children" class="px-4 py-2">
          <button @click="toggleGroup(group.id)"
            class="flex items-center justify-between w-full text-xs font-semibold text-slate-400 uppercase tracking-wider hover:text-slate-200 transition-colors">
            <span><i :class="'fa-solid ' + group.icon + ' mr-2'"></i>{{ group.label }}</span>
            <i :class="'fa-solid fa-chevron-' + (openGroups[group.id] ? 'down' : 'right') + ' text-xs'"></i>
          </button>
          <div v-show="openGroups[group.id]" class="mt-1 space-y-0.5">
            <router-link v-for="child in group.children" :key="child.route" :to="child.route"
              class="flex items-center gap-x-2 px-4 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-700 hover:text-white transition-colors"
              :class="{ 'bg-slate-700 text-white': isActive(child.route) }">
              <span class="w-1.5 h-1.5 rounded-full" :class="isActive(child.route) ? 'bg-blue-400' : 'bg-slate-600'"></span>
              {{ child.label }}
            </router-link>
          </div>
        </div>
        <router-link v-else :to="group.route"
          class="flex items-center gap-x-3 mx-3 px-4 py-2.5 rounded-lg text-sm text-slate-300 hover:bg-slate-700 hover:text-white transition-colors"
          :class="{ 'bg-blue-600 text-white hover:bg-blue-700': isActive(group.route) }">
          <i :class="'fa-solid ' + group.icon + ' w-5 text-center'"></i>{{ group.label }}
        </router-link>
      </div>
    </nav>
    <div class="px-4 py-3 border-t border-slate-700 text-xs text-slate-500">
      &copy; 2026 鲜丰超市 v4.17
    </div>
  </aside>
</template>

<script setup>
import { reactive, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth.js';

const route = useRoute();
const auth = useAuthStore();
const openGroups = reactive({
  product: true, supplier: false, purchase: false, warehouse: false,
  sales: false, member: false, employee: false, finance: false, system: false
});

const allMenus = [
  { id: 'dashboard', icon: 'fa-tachometer-alt', label: '首页仪表盘', route: '/dashboard', permission: null },
  { id: 'product', icon: 'fa-boxes', label: '商品管理', permission: 'product:crud', children: [
    { label: '商品列表', route: '/products' },
    { label: '分类管理', route: '/products/category' },
    { label: '价格与促销', route: '/products/promotion' }
  ]},
  { id: 'supplier', icon: 'fa-truck', label: '供应商管理', permission: 'supplier:crud', children: [
    { label: '供应商列表', route: '/suppliers' },
    { label: '合同管理', route: '/suppliers/contract' },
    { label: '评价管理', route: '/suppliers/evaluation' }
  ]},
  { id: 'purchase', icon: 'fa-cart-shopping', label: '采购管理', permission: 'purchase:crud', children: [
    { label: '采购订单', route: '/purchases' }
  ]},
  { id: 'warehouse', icon: 'fa-warehouse', label: '仓库管理', permission: 'warehouse:crud', children: [
    { label: '仓库信息', route: '/warehouses' },
    { label: '库存查询', route: '/warehouses/inventory' },
    { label: '入库管理', route: '/warehouses/inbound' },
    { label: '出库管理', route: '/warehouses/outbound' }
  ]},
  { id: 'sales', icon: 'fa-cash-register', label: '销售管理', permission: 'sales:crud', children: [
    { label: 'POS收银', route: '/sales/cashier' },
    { label: '销售订单', route: '/sales' },
    { label: '退货管理', route: '/sales/return' },
    { label: '销售统计', route: '/sales/statistics' }
  ]},
  { id: 'member', icon: 'fa-id-card', label: '会员管理', permission: 'member:crud', children: [
    { label: '会员列表', route: '/members' },
    { label: '等级管理', route: '/members/level' },
    { label: '积分管理', route: '/members/points' }
  ]},
  { id: 'employee', icon: 'fa-users', label: '员工管理', permission: 'employee:crud', children: [
    { label: '员工列表', route: '/employees' },
    { label: '排班管理', route: '/employees/schedule' },
    { label: '薪资管理', route: '/employees/payroll' }
  ]},
  { id: 'finance', icon: 'fa-coins', label: '财务管理', permission: 'finance:crud', children: [
    { label: '收银记录', route: '/finance' },
    { label: '会计凭证', route: '/finance/journal' },
    { label: '预算税务', route: '/finance/budget' }
  ]},
  { id: 'system', icon: 'fa-gear', label: '系统管理', permission: 'sys:manage', children: [
    { label: '用户角色', route: '/system' },
    { label: '权限配置', route: '/system/permissions' },
    { label: '系统日志', route: '/system/logs' },
    { label: '操作日志', route: '/system/operation-logs' },
    { label: '系统配置', route: '/system/config' }
  ]}
];

const menus = computed(() =>
  allMenus.filter(m => !m.permission || auth.hasPermission(m.permission))
);

function toggleGroup(id) { openGroups[id] = !openGroups[id]; }
function isActive(path) { return route.path === path || route.path.startsWith(path + '/'); }
</script>
