<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div><h2 class="text-2xl font-bold text-slate-800">薪资管理</h2><p class="text-sm text-slate-500 mt-0.5">管理员工工资记录</p></div>
      <button @click="openAdd" class="btn-primary flex items-center gap-x-2 px-5 py-2.5 rounded-xl text-sm"><i class="fa-solid fa-plus"></i>生成工资</button>
    </div>
    <DataTable ref="tableRef" :columns="columns" apiUrl="/payrolls" :filters="periodFilters" :actions="actions" />
    <FormModal :visible="modalVisible" :title="editingItem ? '编辑工资' : '生成工资'"
      :fields="formFields" :initialData="editingItem" :loading="submitting"
      @submit="handleSubmit" @cancel="modalVisible = false; editingItem = null" />
    <ConfirmDialog :visible="delVisible" title="删除工资记录" message="确定要删除该工资记录吗？" confirmText="删除" :danger="true"
      @confirm="handleDelete" @cancel="delVisible = false; delItem = null" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DataTable from '@/components/DataTable.vue';
import FormModal from '@/components/FormModal.vue';
import ConfirmDialog from '@/components/ConfirmDialog.vue';
import StatusBadge from '@/components/StatusBadge.vue';
import { getPayrolls, createPayroll, updatePayroll, deletePayroll, approvePayroll, getEmployees } from '@/api/employees';
import { formatCurrency } from '@/utils/format';
import { useToast } from '@/utils/toast';
const toast = useToast();

const tableRef = ref(null); const modalVisible = ref(false); const submitting = ref(false);
const editingItem = ref(null); const delVisible = ref(false); const delItem = ref(null);
const employeeOptions = ref([]);

const columns = [
  { key: 'payroll_id', label: 'ID', width: '70px' },
  { key: 'employee_name', label: '员工' },
  { key: 'pay_period', label: '工资周期' },
  { key: 'base_salary', label: '基本工资', render: (v) => formatCurrency(v) },
  { key: 'bonus', label: '奖金', render: (v) => formatCurrency(v) },
  { key: 'deduction', label: '扣款', render: (v) => formatCurrency(v) },
  { key: 'net_pay', label: '实发', render: (v) => formatCurrency(v) },
  { key: 'status', label: '状态', render: (v) => StatusBadge }
];

const periodFilters = [];

const actions = [
  { label: '编辑', icon: 'fa-edit', color: 'emerald', visible: (row) => row.status === 'pending', handler: openEdit },
  { label: '发放', icon: 'fa-check', color: 'blue', visible: (row) => row.status === 'pending', handler: async (row) => { try { await approvePayroll(row.payroll_id); tableRef.value?.fetchData(); } catch (e) { toast.error(e.message); } } },
  { label: '删除', icon: 'fa-trash', color: 'red', visible: (row) => row.status === 'pending', handler: (row) => { delItem.value = row; delVisible.value = true; } }
];

const formFields = [
  { key: 'employee_id', label: '员工', type: 'select', required: true, options: employeeOptions, optionValue: 'employee_id', optionLabel: 'employee_name' },
  { key: 'pay_period', label: '工资周期', type: 'text', required: true, placeholder: '2026-05' },
  { key: 'base_salary', label: '基本工资', type: 'number', required: true },
  { key: 'bonus', label: '奖金', type: 'number' },
  { key: 'deduction', label: '扣款', type: 'number' }
];

onMounted(async () => { try { const r = await getEmployees(); employeeOptions.value = r.data || []; } catch {} });

function openAdd() { editingItem.value = null; modalVisible.value = true; }
function openEdit(row) { editingItem.value = { ...row }; modalVisible.value = true; }

async function handleSubmit(data) {
  submitting.value = true;
  try {
    if (editingItem.value) { await updatePayroll(editingItem.value.payroll_id, data); }
    else { await createPayroll(data); }
    modalVisible.value = false; editingItem.value = null; tableRef.value?.fetchData();
  } catch (e) { toast.error(e.message); }
  finally { submitting.value = false; }
}

async function handleDelete() {
  if (!delItem.value) return;
  try { await deletePayroll(delItem.value.payroll_id); delVisible.value = false; delItem.value = null; tableRef.value?.fetchData(); }
  catch (e) { toast.error(e.message); }
}
</script>
