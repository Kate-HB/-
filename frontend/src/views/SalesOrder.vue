<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div><h2 class="text-2xl font-bold text-slate-800">销售订单</h2><p class="text-sm text-slate-500 mt-0.5">管理销售订单记录</p></div>
      <button @click="openAdd" class="btn-primary flex items-center gap-x-2 px-5 py-2.5 rounded-xl text-sm"><i class="fa-solid fa-plus"></i>新建销售单</button>
    </div>
    <DataTable ref="tableRef" :columns="columns" apiUrl="/sales-orders" searchPlaceholder="搜索订单号..." :filters="statusFilters" :actions="actions" :extraParams="extraParams" />
    <FormModal :visible="modalVisible" title="新建销售单"
      :fields="formFields" :loading="submitting"
      @submit="handleSubmit" @cancel="modalVisible = false" />
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import DataTable from '@/components/DataTable.vue';
import FormModal from '@/components/FormModal.vue';
import StatusBadge from '@/components/StatusBadge.vue';
import { createSalesOrder } from '@/api/sales';
import { getProducts } from '@/api/products';
import { getMembers } from '@/api/members';
import { getEmployees } from '@/api/employees';
import { formatCurrency, formatDate } from '@/utils/format';
import { useToast } from '@/utils/toast';
const toast = useToast();

const route = useRoute();
const tableRef = ref(null); const modalVisible = ref(false); const submitting = ref(false);
const productOptions = ref([]); const memberOptions = ref([]); const employeeOptions = ref([]);
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

const formFields = [
  { key: 'member_id', label: '会员', type: 'select', options: memberOptions, optionValue: 'member_id', optionLabel: 'member_name' },
  { key: 'employee_id', label: '收银员', type: 'select', required: true, options: employeeOptions, optionValue: 'employee_id', optionLabel: 'employee_name' },
  { key: 'payment_method', label: '支付方式', type: 'select',
    options: ['现金', '微信支付', '支付宝', '银行卡', '会员卡'].map(v => ({ value: v, label: v })) },
  { key: 'items', label: '销售明细', type: 'table',
    subColumns: [
      { key: 'product_id', label: '商品', type: 'select', options: productOptions, optionValue: 'product_id', optionLabel: 'product_name' },
      { key: 'quantity', label: '数量', inputType: 'number' },
      { key: 'unit_price', label: '单价', inputType: 'number' }
    ],
    defaultItem: { product_id: '', quantity: 1, unit_price: 0 }
  }
];

onMounted(async () => {
  try { const r = await getProducts(); productOptions.value = r.data || []; } catch {}
  try { const r = await getMembers(); memberOptions.value = r.data || []; } catch {}
  try { const r = await getEmployees(); employeeOptions.value = r.data || []; } catch {}
});

function openAdd() { modalVisible.value = true; }

async function handleSubmit(data) {
  submitting.value = true;
  try { await createSalesOrder(data); modalVisible.value = false; tableRef.value?.fetchData(); }
  catch (e) { toast.error(e.message); }
  finally { submitting.value = false; }
}
</script>
