<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div><h2 class="text-2xl font-bold text-slate-800">收银记录</h2><p class="text-sm text-slate-500 mt-0.5">查看 POS 收银产生的记录</p></div>
    </div>
    <DataTable ref="tableRef" :columns="columns" apiUrl="/cash-records" :filters="methodFilters" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import DataTable from '@/components/DataTable.vue';
import StatusBadge from '@/components/StatusBadge.vue';
import { formatCurrency, formatDateTime } from '@/utils/format';

const tableRef = ref(null);

const columns = [
  { key: 'cash_record_id', label: 'ID', width: '70px' },
  { key: 'order_id', label: '订单ID' },
  { key: 'employee_name', label: '收银员' },
  { key: 'amount', label: '金额', render: (v) => formatCurrency(v) },
  { key: 'payment_method', label: '支付方式' },
  { key: 'transaction_time', label: '交易时间', render: (v) => formatDateTime(v) },
  { key: 'status', label: '状态', render: (v) => StatusBadge }
];

const methodFilters = [
  { key: 'payment_method', label: '现金', value: '现金' },
  { key: 'payment_method', label: '微信支付', value: '微信支付' },
  { key: 'payment_method', label: '支付宝', value: '支付宝' },
  { key: 'payment_method', label: '银行卡', value: '银行卡' }
];
</script>
