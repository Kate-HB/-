<template>
  <div>
    <div class="mb-6"><h2 class="text-2xl font-bold text-slate-800">系统日志</h2><p class="text-sm text-slate-500 mt-0.5">查看系统操作日志</p></div>
    <DataTable ref="tableRef" :columns="columns" apiUrl="/logs" :filters="logFilters" />
  </div>
</template>

<script setup>
import DataTable from '@/components/DataTable.vue';
import StatusBadge from '@/components/StatusBadge.vue';
import { formatDateTime } from '@/utils/format';

const columns = [
  { key: 'log_id', label: 'ID', width: '80px' },
  { key: 'log_type', label: '类型', render: (v) => StatusBadge },
  { key: 'module', label: '模块' },
  { key: 'action', label: '操作' },
  { key: 'description', label: '描述' },
  { key: 'username', label: '用户' },
  { key: 'ip_address', label: 'IP' },
  { key: 'log_time', label: '时间', render: (v) => formatDateTime(v) }
];

const logFilters = [
  { label: '操作', value: 'operation' }, { label: '登录', value: 'login' },
  { label: '异常', value: 'exception' }, { label: '审计', value: 'audit' }
];
</script>
