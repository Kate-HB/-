import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/Login.vue'),
    meta: { noAuth: true }
  },
  {
    path: '/',
    component: () => import('@/components/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', name: 'dashboard', component: () => import('@/views/Dashboard.vue') },
      { path: 'products', name: 'products', component: () => import('@/views/ProductManagement.vue'), meta: { permission: 'product:crud' } },
      { path: 'products/category', name: 'category', component: () => import('@/views/CategoryManagement.vue'), meta: { permission: 'product:crud' } },
      { path: 'products/promotion', name: 'promotion', component: () => import('@/views/PromotionManagement.vue'), meta: { permission: 'product:crud' } },
      { path: 'suppliers', name: 'suppliers', component: () => import('@/views/SupplierManagement.vue'), meta: { permission: 'supplier:crud' } },
      { path: 'suppliers/contract', name: 'supplierContract', component: () => import('@/views/SupplierContract.vue'), meta: { permission: 'supplier:crud' } },
      { path: 'suppliers/evaluation', name: 'supplierEval', component: () => import('@/views/SupplierEvaluation.vue'), meta: { permission: 'supplier:crud' } },
      { path: 'purchases', name: 'purchases', component: () => import('@/views/PurchaseOrder.vue'), meta: { permission: 'purchase:crud' } },

      { path: 'warehouses', name: 'warehouses', component: () => import('@/views/WarehouseInfo.vue'), meta: { permission: 'warehouse:crud' } },
      { path: 'warehouses/inventory', name: 'inventory', component: () => import('@/views/InventoryQuery.vue'), meta: { permission: 'warehouse:crud' } },
      { path: 'warehouses/inbound', name: 'warehouseInbound', component: () => import('@/views/InboundManagement.vue'), meta: { permission: 'warehouse:crud' } },
      { path: 'warehouses/outbound', name: 'warehouseOutbound', component: () => import('@/views/OutboundManagement.vue'), meta: { permission: 'warehouse:crud' } },
      { path: 'sales', name: 'sales', component: () => import('@/views/SalesOrder.vue'), meta: { permission: 'sales:crud' } },
      { path: 'sales/cashier', name: 'cashier', component: () => import('@/views/CashRegister.vue'), meta: { permission: 'sales:crud' } },
      { path: 'sales/return', name: 'salesReturn', component: () => import('@/views/SalesReturn.vue'), meta: { permission: 'sales:crud' } },
      { path: 'sales/statistics', name: 'salesStats', component: () => import('@/views/SalesStatistics.vue'), meta: { permission: 'sales:crud' } },
      { path: 'members', name: 'members', component: () => import('@/views/MemberManagement.vue'), meta: { permission: 'member:crud' } },
      { path: 'members/level', name: 'memberLevel', component: () => import('@/views/MemberLevel.vue'), meta: { permission: 'member:crud' } },
      { path: 'members/points', name: 'memberPoints', component: () => import('@/views/MemberPoints.vue'), meta: { permission: 'member:crud' } },
      { path: 'employees', name: 'employees', component: () => import('@/views/EmployeeManagement.vue'), meta: { permission: 'employee:crud' } },
      { path: 'employees/schedule', name: 'employeeSchedule', component: () => import('@/views/EmployeeSchedule.vue'), meta: { permission: 'employee:crud' } },
      { path: 'employees/payroll', name: 'employeePayroll', component: () => import('@/views/EmployeePayroll.vue'), meta: { permission: 'employee:crud' } },
      { path: 'finance', name: 'finance', component: () => import('@/views/CashRecords.vue'), meta: { permission: 'finance:crud' } },
      { path: 'finance/journal', name: 'journal', component: () => import('@/views/JournalEntries.vue'), meta: { permission: 'finance:crud' } },
      { path: 'finance/budget', name: 'budget', component: () => import('@/views/BudgetTax.vue'), meta: { permission: 'finance:crud' } },
      { path: 'system', name: 'system', component: () => import('@/views/UserRoles.vue'), meta: { permission: 'sys:manage' } },
      { path: 'system/permissions', name: 'permissions', component: () => import('@/views/PermissionConfig.vue'), meta: { permission: 'sys:manage' } },
      { path: 'system/logs', name: 'systemLogs', component: () => import('@/views/SystemLogs.vue'), meta: { permission: 'sys:manage' } },
      { path: 'system/operation-logs', name: 'operationLogs', component: () => import('@/views/OperationLogs.vue'), meta: { permission: 'sys:manage' } },
      { path: 'system/config', name: 'systemConfig', component: () => import('@/views/SystemConfig.vue'), meta: { permission: 'sys:manage' } }
    ]
  },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' }
];

const router = createRouter({ history: createWebHistory(), routes });

router.beforeEach((to) => {
  const token = localStorage.getItem('token');
  if (to.meta.requiresAuth && !token) return '/login';
  if (to.meta.noAuth && token) return '/dashboard';

  // Check permission from route meta
  const required = to.meta.permission;
  if (required && token) {
    try {
      const perms = JSON.parse(localStorage.getItem('permissions') || '[]');
      if (!perms.includes(required)) return '/dashboard';
    } catch {
      return '/dashboard';
    }
  }
  return true;
});

export default router;
