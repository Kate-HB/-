<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div><h2 class="text-2xl font-bold text-slate-800">退货管理</h2><p class="text-sm text-slate-500 mt-0.5">管理销售退货记录</p></div>
      <button @click="openAdd" class="btn-primary flex items-center gap-x-2 px-5 py-2.5 rounded-xl text-sm"><i class="fa-solid fa-plus"></i>新建退货</button>
    </div>
    <DataTable ref="tableRef" :columns="columns" apiUrl="/sales-returns" :actions="actions" />
    <FormModal :visible="modalVisible" title="新建退货"
      :fields="formFields" :loading="submitting"
      @submit="handleSubmit" @cancel="modalVisible = false" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DataTable from '@/components/DataTable.vue';
import FormModal from '@/components/FormModal.vue';
import StatusBadge from '@/components/StatusBadge.vue';
import { getSalesReturns, createSalesReturn, approveSalesReturn } from '@/api/sales';
import { getProducts } from '@/api/products';
import { getEmployees } from '@/api/employees';
import { formatCurrency, formatDate } from '@/utils/format';
import { useToast } from '@/utils/toast';
const toast = useToast();

const tableRef = ref(null); const modalVisible = ref(false); const submitting = ref(false);
const productOptions = ref([]); const employeeOptions = ref([]);

const columns = [
  { key: 'return_id', label: 'ID', width: '70px' },
  { key: 'original_order_id', label: '原订单ID' },
  { key: 'member_name', label: '会员' },
  { key: 'employee_name', label: '处理人' },
  { key: 'return_amount', label: '退款金额', render: (v) => formatCurrency(v) },
  { key: 'reason', label: '原因' },
  { key: 'return_date', label: '日期', render: (v) => formatDate(v) },
  { key: 'status', label: '状态', render: (v) => StatusBadge }
];

const actions = [
  { label: '审批', icon: 'fa-check', color: 'blue', requiredPermission: 'sales.return.approve', visible: (row) => row.status === 'pending', handler: async (row) => { try { await approveSalesReturn(row.return_id); tableRef.value?.fetchData(); } catch (e) { toast.error(e.message); } } }
];

const formFields = [
  { key: 'original_order_id', label: '原订单ID', type: 'number', required: true },
  { key: 'employee_id', label: '处理人', type: 'select', required: true, options: employeeOptions, optionValue: 'employee_id', optionLabel: 'employee_name' },
  { key: 'reason', label: '退货原因', type: 'textarea' },
  { key: 'items', label: '退货明细', type: 'table',
    subColumns: [
      { key: 'product_id', label: '商品', type: 'select', options: productOptions, optionValue: 'product_id', optionLabel: 'product_name' },
      { key: 'quantity', label: '数量', inputType: 'number' },
      { key: 'refund_amount', label: '退款金额', inputType: 'number' }
    ],
    defaultItem: { product_id: '', quantity: 1, refund_amount: 0 }
  }
];

onMounted(async () => {
  try { const r = await getProducts(); productOptions.value = r.data || []; } catch {}
  try { const r = await getEmployees(); employeeOptions.value = r.data || []; } catch {}
});

function openAdd() { modalVisible.value = true; }

async function handleSubmit(data) {
  submitting.value = true;
  try { await createSalesReturn(data); modalVisible.value = false; tableRef.value?.fetchData(); }
  catch (e) { toast.error(e.message); }
  finally { submitting.value = false; }
}
</script>
