<template>
  <div>
    <div class="mb-6 flex items-end justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-slate-800">销售统计</h2>
        <p class="text-sm text-slate-500 mt-0.5">{{ periodLabel }}销售数据与商品排行</p>
      </div>
      <div class="flex rounded-xl border border-slate-200 bg-white p-1 shadow-sm">
        <button v-for="option in periodOptions" :key="option.value" @click="setPeriod(option.value)"
          class="px-3 py-1.5 text-sm rounded-lg transition-colors"
          :class="period === option.value ? 'bg-blue-600 text-white' : 'text-slate-600 hover:bg-slate-50'">
          {{ option.label }}
        </button>
      </div>
    </div>
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="card p-5">
        <h3 class="text-base font-bold text-slate-800 mb-3">销售统计</h3>
        <DataTable :key="'stat-' + period" :columns="statColumns" apiUrl="/sales-statistics" :extraParams="{ period }" />
      </div>
      <div class="card p-5">
        <h3 class="text-base font-bold text-slate-800 mb-3">商品排行榜</h3>
        <DataTable :key="'rank-' + period" :columns="rankColumns" apiUrl="/product-rankings" :extraParams="{ period }" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import DataTable from '@/components/DataTable.vue';
import { formatCurrency } from '@/utils/format';

const route = useRoute();
const router = useRouter();
const periodOptions = [
  { value: 'today', label: '今日' },
  { value: 'month', label: '本月' },
  { value: 'all', label: '全部' }
];

const period = computed(() => {
  const value = route.query.period;
  return ['today', 'month', 'all'].includes(value) ? value : 'all';
});

const periodLabel = computed(() => ({ today: '今日', month: '本月', all: '全部' }[period.value] || '全部'));

function setPeriod(value) {
  router.replace({ query: value === 'all' ? {} : { period: value } });
}

const statColumns = [
  { key: 'stat_period', label: '统计周期' },
  { key: 'total_amount', label: '销售总额', render: (v) => formatCurrency(v) },
  { key: 'order_count', label: '订单数' },
  { key: 'product_count', label: '商品种类数' }
];

const rankColumns = [
  { key: 'rank_position', label: '排名', width: '60px' },
  { key: 'product_name', label: '商品名称' },
  { key: 'sales_quantity', label: '销售数量' },
  { key: 'sales_amount', label: '销售金额', render: (v) => formatCurrency(v) },
  { key: 'rank_period', label: '周期' }
];
</script>
