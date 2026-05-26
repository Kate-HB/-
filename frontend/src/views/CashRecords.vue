<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div><h2 class="text-2xl font-bold text-slate-800">收银记录</h2><p class="text-sm text-slate-500 mt-0.5">查看销售收银记录</p></div>
      <button @click="openAdd" class="btn-primary flex items-center gap-x-2 px-5 py-2.5 rounded-xl text-sm"><i class="fa-solid fa-plus"></i>添加记录</button>
    </div>
    <DataTable ref="tableRef" :columns="columns" apiUrl="/cash-records" :filters="methodFilters" />
    <FormModal :visible="modalVisible" title="添加收银记录"
      :fields="formFields" :loading="submitting"
      @submit="handleSubmit" @cancel="modalVisible = false" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DataTable from '@/components/DataTable.vue';
import FormModal from '@/components/FormModal.vue';
import StatusBadge from '@/components/StatusBadge.vue';
import { createCashRecord } from '@/api/finance';
import { getEmployees } from '@/api/employees';
import { formatCurrency, formatDateTime } from '@/utils/format';
import { useToast } from '@/utils/toast';
const toast = useToast();

const tableRef = ref(null);
const modalVisible = ref(false);
const submitting = ref(false);
const employeeOptions = ref([]);

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

const formFields = [
  { key: 'order_id', label: '订单ID', type: 'number', required: true },
  { key: 'employee_id', label: '收银员', type: 'select', required: true, options: employeeOptions, optionValue: 'employee_id', optionLabel: 'employee_name' },
  { key: 'amount', label: '金额', type: 'number', required: true },
  { key: 'payment_method', label: '支付方式', type: 'select', required: true,
    options: [{ value: '现金', label: '现金' }, { value: '微信支付', label: '微信支付' }, { value: '支付宝', label: '支付宝' }, { value: '银行卡', label: '银行卡' }] },
  { key: 'transaction_time', label: '交易时间', type: 'datetime' }
];

onMounted(async () => { try { const r = await getEmployees(); employeeOptions.value = r.data || []; } catch {} });

function openAdd() { modalVisible.value = true; }

async function handleSubmit(data) {
  submitting.value = true;
  try { await createCashRecord(data); modalVisible.value = false; tableRef.value?.fetchData(); }
  catch (e) { toast.error(e.message); }
  finally { submitting.value = false; }
}
</script>
