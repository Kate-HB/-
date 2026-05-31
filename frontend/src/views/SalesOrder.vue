<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div><h2 class="text-2xl font-bold text-slate-800">销售订单</h2><p class="text-sm text-slate-500 mt-0.5">查看 POS 收银产生的销售订单</p></div>
    </div>
    <DataTable ref="tableRef" :columns="columns" apiUrl="/sales-orders" searchPlaceholder="搜索订单号..." :filters="statusFilters" :actions="actions" :extraParams="extraParams" />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useRoute } from 'vue-router';
import DataTable from '@/components/DataTable.vue';
import StatusBadge from '@/components/StatusBadge.vue';
import { formatCurrency, formatDate } from '@/utils/format';

const route = useRoute();
const tableRef = ref(null);
const extraParams = computed(() => route.query.period === 'today' ? { period: 'today' } : {});

const columns = [
  { key: 'order_id', label: 'ID', width: '70px' },
  { key: 'order_number', label: '订单编号' },
  { key: 'member_name', label: '会员' },
  { key: 'employee_name', label: '收银员' },
  { key: 'total_amount', label: '金额', render: (v) => formatCurrency(v) },
  { key: 'payment_method', label: '支付方式' },
  { key: 'order_date', label: '时间', render: (v) => formatDate(v) },
  { key: 'status', label: '状态', render: StatusBadge }
];

const statusFilters = [
  { label: '待处理', value: 'pending' }, { label: '已完成', value: 'completed' }, { label: '已取消', value: 'cancelled' }, { label: '已退款', value: 'refunded' }
];

const actions = [];
</script>
