<template>
  <div>
    <div class="mb-8 flex items-end justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-slate-800">首页仪表盘</h2>
        <p class="text-sm text-slate-500 mt-1">超市运营数据概览</p>
      </div>
      <div class="hidden md:flex items-center gap-2 rounded-2xl border border-white/70 bg-white/70 px-4 py-2 text-xs text-slate-500 shadow-sm backdrop-blur">
        <i class="fa-solid fa-chart-line text-blue-500"></i>
        核心经营指标实时汇总
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
      <KPICard title="今日销售额" :value="formatCurrency(kpi.today_sales)"
        icon="fa-yen-sign" color="#10b981" bg-color="#ecfdf5" :to="{ path: '/sales/statistics', query: { period: 'today' } }" />
      <KPICard title="今日订单数" :value="kpi.today_orders"
        icon="fa-receipt" color="#f59e0b" bg-color="#fffbeb" :to="{ path: '/sales', query: { period: 'today' } }" />
      <KPICard title="本月销售额" :value="formatCurrency(kpi.month_sales)"
        icon="fa-calendar-check" color="#3b82f6" bg-color="#eff6ff" :to="{ path: '/sales/statistics', query: { period: 'month' } }" />
      <KPICard title="库存预警" :value="kpi.inventory_alerts"
        icon="fa-triangle-exclamation" color="#ef4444" bg-color="#fef2f2" :to="{ path: '/warehouses/inventory', query: { scope: 'alert' } }" />
      <KPICard title="活跃会员" :value="kpi.active_members"
        icon="fa-users" color="#8b5cf6" bg-color="#f5f3ff" to="/members" />
      <KPICard title="待审批" :value="kpi.pending_approvals"
        icon="fa-clock" color="#6366f1" bg-color="#eef2ff" :to="{ path: '/purchases', query: { status: 'pending' } }" />
    </div>

    <!-- Sales Trend Chart + Notifications -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      <div class="lg:col-span-2 card p-6">
        <h3 class="text-base font-bold text-slate-800 mb-4">
          <i class="fa-solid fa-chart-bar text-blue-500 mr-2"></i>近7日销售额趋势
        </h3>
        <div v-if="chartData.sales_trend && chartData.sales_trend.length" class="flex items-end gap-x-2 h-48">
          <div v-for="(d, i) in chartData.sales_trend" :key="i"
            class="flex-1 flex flex-col items-center gap-y-1 h-full justify-end">
            <span class="text-xs font-medium text-slate-700">{{ formatCurrency(d.amount) }}</span>
            <div class="w-full rounded-t-lg transition-all duration-500"
              :style="{ height: barHeight(d.amount) + '%', background: gradientColor(i, chartData.sales_trend.length) }"
              :title="d.date + ': ' + formatCurrency(d.amount)"></div>
            <span class="text-xs text-slate-400">{{ d.label }}</span>
          </div>
        </div>
        <EmptyState v-else message="暂无销售数据" />
      </div>

      <div class="card p-6">
        <h3 class="text-base font-bold text-slate-800 mb-4">
          <i class="fa-solid fa-bell text-amber-500 mr-2"></i>系统通知
        </h3>
        <div v-if="notifications.length" class="space-y-3">
          <div v-for="(n, i) in notifications" :key="i"
            class="flex items-start gap-x-3 p-3 rounded-xl bg-slate-50 hover:bg-slate-100 transition-colors">
            <div class="w-2 h-2 mt-1.5 rounded-full flex-shrink-0"
              :class="n.log_type === 'exception' ? 'bg-red-500' : 'bg-blue-500'"></div>
            <div class="flex-1 min-w-0">
              <p class="text-sm text-slate-700 truncate">{{ n.description }}</p>
              <p class="text-xs text-slate-400 mt-0.5">{{ formatDateTime(n.log_time) }}</p>
            </div>
          </div>
        </div>
        <EmptyState v-else message="暂无通知" />
      </div>
    </div>

    <!-- Top Products + Low Stock -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <div class="card p-6">
        <h3 class="text-base font-bold text-slate-800 mb-4">
          <i class="fa-solid fa-crown text-amber-500 mr-2"></i>热销商品 TOP10
        </h3>
        <table v-if="chartData.top_products && chartData.top_products.length" class="w-full text-sm">
          <thead>
            <tr class="border-b border-slate-100">
              <th class="text-left py-2 text-xs font-semibold text-slate-500 w-8">#</th>
              <th class="text-left py-2 text-xs font-semibold text-slate-500">商品</th>
              <th class="text-right py-2 text-xs font-semibold text-slate-500">销量</th>
              <th class="text-right py-2 text-xs font-semibold text-slate-500">销售额</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(p, i) in chartData.top_products" :key="p.product_id" class="border-b border-slate-50 hover:bg-slate-50">
              <td class="py-2 font-medium" :class="i < 3 ? 'text-amber-500' : 'text-slate-400'">{{ i + 1 }}</td>
              <td class="py-2 text-slate-700 truncate max-w-[140px]">{{ p.product_name }}</td>
              <td class="py-2 text-right text-slate-600">{{ p.total_quantity }}</td>
              <td class="py-2 text-right text-slate-700 font-medium">{{ formatCurrency(p.total_amount) }}</td>
            </tr>
          </tbody>
        </table>
        <EmptyState v-else message="暂无销售排行" />
      </div>

      <div class="card p-6">
        <h3 class="text-base font-bold text-slate-800 mb-4">
          <i class="fa-solid fa-exclamation-triangle text-red-400 mr-2"></i>低库存预警
        </h3>
        <table v-if="chartData.low_stock && chartData.low_stock.length" class="w-full text-sm">
          <thead>
            <tr class="border-b border-slate-100">
              <th class="text-left py-2 text-xs font-semibold text-slate-500">商品</th>
              <th class="text-right py-2 text-xs font-semibold text-slate-500">当前库存</th>
              <th class="text-right py-2 text-xs font-semibold text-slate-500">安全库存</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="inv in chartData.low_stock" :key="inv.product_id" class="border-b border-slate-50 hover:bg-slate-50">
              <td class="py-2 text-slate-700 truncate max-w-[140px]">{{ inv.product_name }}</td>
              <td class="py-2 text-right">
                <span :class="inv.stock_quantity <= 0 ? 'text-red-600 font-bold' : 'text-amber-600 font-medium'">
                  {{ inv.stock_quantity }}
                </span>
              </td>
              <td class="py-2 text-right text-slate-400">{{ inv.safety_stock }}</td>
            </tr>
          </tbody>
        </table>
        <EmptyState v-else message="暂无库存预警" />
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="card p-6 mb-6">
      <h3 class="text-base font-bold text-slate-800 mb-4">
        <i class="fa-solid fa-bolt text-blue-500 mr-2"></i>快捷操作
      </h3>
      <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
        <router-link v-for="act in quickActions" :key="act.label" :to="act.route"
          class="flex flex-col items-center gap-y-2 p-4 rounded-xl bg-slate-50 hover:bg-blue-50 transition-colors group">
          <div class="w-10 h-10 rounded-xl flex items-center justify-center group-hover:bg-blue-100 transition-colors"
            :class="act.bg">
            <i :class="'fa-solid ' + act.icon + ' ' + act.color"></i>
          </div>
          <span class="text-xs font-medium text-slate-600 group-hover:text-blue-700">{{ act.label }}</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getDashboardKpi, getDashboardCharts, getDashboardNotifications } from '@/api/dashboard';
import { formatCurrency, formatDateTime } from '@/utils/format';
import KPICard from '@/components/KPICard.vue';
import EmptyState from '@/components/EmptyState.vue';

const kpi = ref({
  today_sales: 0, today_orders: 0, month_sales: 0,
  inventory_alerts: 0, active_members: 0, pending_approvals: 0
});
const chartData = ref({ sales_trend: [], top_products: [], low_stock: [] });
const notifications = ref([]);
const loading = ref(true);

const quickActions = [
  { label: '收银台', route: '/sales/cashier', icon: 'fa-cash-register', color: 'text-emerald-600', bg: 'bg-emerald-50' },
  { label: '销售订单', route: '/sales', icon: 'fa-file-invoice', color: 'text-blue-600', bg: 'bg-blue-50' },
  { label: '采购订单', route: '/purchases', icon: 'fa-cart-shopping', color: 'text-purple-600', bg: 'bg-purple-50' },
  { label: '库存查询', route: '/warehouses/inventory', icon: 'fa-warehouse', color: 'text-amber-600', bg: 'bg-amber-50' },
  { label: '会员管理', route: '/members', icon: 'fa-id-card', color: 'text-indigo-600', bg: 'bg-indigo-50' },
  { label: '商品管理', route: '/products', icon: 'fa-boxes', color: 'text-teal-600', bg: 'bg-teal-50' },
];

function normalizeKpi(data) {
  return {
    today_sales: Number(data?.today_sales ?? 0),
    today_orders: Number(data?.today_orders ?? 0),
    month_sales: Number(data?.month_sales ?? 0),
    inventory_alerts: Number(data?.inventory_alerts ?? 0),
    active_members: Number(data?.active_members ?? 0),
    pending_approvals: Number(data?.pending_approvals ?? 0)
  };
}

function normalizeChartData(data) {
  return {
    sales_trend: Array.isArray(data?.sales_trend) ? data.sales_trend.map((item) => ({
      ...item,
      amount: Number(item?.amount ?? 0)
    })) : [],
    top_products: Array.isArray(data?.top_products) ? data.top_products.map((item) => ({
      ...item,
      total_quantity: Number(item?.total_quantity ?? 0),
      total_amount: Number(item?.total_amount ?? 0)
    })) : [],
    low_stock: Array.isArray(data?.low_stock) ? data.low_stock.map((item) => ({
      ...item,
      stock_quantity: Number(item?.stock_quantity ?? 0),
      safety_stock: Number(item?.safety_stock ?? 0)
    })) : []
  };
}

function barHeight(amount) {
  const max = Math.max(...chartData.value.sales_trend.map(d => Number(d.amount) || 0), 1);
  return Math.max(((Number(amount) || 0) / max) * 100, 2);
}

function gradientColor(i, len) {
  const colors = ['#dbeafe', '#bfdbfe', '#93c5fd', '#60a5fa', '#3b82f6', '#2563eb', '#1d4ed8'];
  return colors[i] || colors[colors.length - 1];
}

onMounted(async () => {
  loading.value = true;
  try {
    const [kpiRes, chartRes, notifRes] = await Promise.all([
      getDashboardKpi(), getDashboardCharts(), getDashboardNotifications()
    ]);
    kpi.value = normalizeKpi(kpiRes.data);
    chartData.value = normalizeChartData(chartRes.data);
    notifications.value = Array.isArray(notifRes.data) ? notifRes.data : [];
  } catch {
    kpi.value = normalizeKpi();
    chartData.value = normalizeChartData();
    notifications.value = [];
  } finally {
    loading.value = false;
  }
});
</script>
