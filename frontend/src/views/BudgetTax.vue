<template>
  <div>
    <div class="mb-6"><h2 class="text-2xl font-bold text-slate-800">预算与税务</h2><p class="text-sm text-slate-500 mt-0.5">管理预算和税务申报</p></div>
    <div class="flex gap-x-3 mb-4">
      <button @click="tab = 'budget'" :class="tab === 'budget' ? 'bg-blue-600 text-white' : 'bg-white text-slate-600 border border-slate-200'"
        class="px-4 py-2 rounded-xl text-sm font-medium transition-colors">预算管理</button>
      <button @click="tab = 'tax'" :class="tab === 'tax' ? 'bg-blue-600 text-white' : 'bg-white text-slate-600 border border-slate-200'"
        class="px-4 py-2 rounded-xl text-sm font-medium transition-colors">税务申报</button>
    </div>

    <div v-if="tab === 'budget'">
      <div class="flex justify-end mb-4">
        <button @click="openBudget" class="btn-primary flex items-center gap-x-2 px-4 py-2 rounded-xl text-sm"><i class="fa-solid fa-plus"></i>添加预算</button>
      </div>
      <DataTable ref="budgetRef" :columns="budgetCols" apiUrl="/budgets" :actions="budgetActions" />
      <FormModal :visible="budgetVisible" :title="editingBudget ? '编辑预算' : '添加预算'"
        :fields="budgetFields" :initialData="editingBudget" :loading="submitting"
        @submit="handleBudgetSubmit" @cancel="budgetVisible = false; editingBudget = null" />
      <ConfirmDialog :visible="delBudgetVisible" title="删除预算" message="确定要删除该预算记录吗？" confirmText="删除" :danger="true"
        @confirm="handleBudgetDelete" @cancel="delBudgetVisible = false; delBudgetItem = null" />
    </div>

    <div v-if="tab === 'tax'">
      <div class="flex justify-end mb-4">
        <button @click="openTax" class="btn-primary flex items-center gap-x-2 px-4 py-2 rounded-xl text-sm"><i class="fa-solid fa-plus"></i>添加申报</button>
      </div>
      <DataTable ref="taxRef" :columns="taxCols" apiUrl="/tax-declarations" :actions="taxActions" />
      <FormModal :visible="taxVisible" :title="editingTax ? '编辑申报' : '添加申报'"
        :fields="taxFields" :initialData="editingTax" :loading="submitting"
        @submit="handleTaxSubmit" @cancel="taxVisible = false; editingTax = null" />
      <ConfirmDialog :visible="delTaxVisible" title="删除申报" message="确定要删除该税务申报吗？" confirmText="删除" :danger="true"
        @confirm="handleTaxDelete" @cancel="delTaxVisible = false; delTaxItem = null" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DataTable from '@/components/DataTable.vue';
import FormModal from '@/components/FormModal.vue';
import ConfirmDialog from '@/components/ConfirmDialog.vue';
import StatusBadge from '@/components/StatusBadge.vue';
import { getBudgets, createBudget, updateBudget, deleteBudget, approveBudget, getAccounts } from '@/api/finance';
import { getTaxDeclarations, createTaxDeclaration, updateTaxDeclaration, deleteTaxDeclaration } from '@/api/finance';
import { formatCurrency } from '@/utils/format';
import { useToast } from '@/utils/toast';
const toast = useToast();

const tab = ref('budget');
const submitting = ref(false);
const budgetVisible = ref(false); const taxVisible = ref(false);
const editingBudget = ref(null); const editingTax = ref(null);
const delBudgetVisible = ref(false); const delBudgetItem = ref(null);
const delTaxVisible = ref(false); const delTaxItem = ref(null);
const budgetRef = ref(null); const taxRef = ref(null);
const accountOptions = ref([]);

const budgetCols = [
  { key: 'budget_id', label: 'ID', width: '70px' },
  { key: 'budget_period', label: '周期' },
  { key: 'account_name', label: '科目' },
  { key: 'planned_amount', label: '计划金额', render: (v) => formatCurrency(v) },
  { key: 'actual_amount', label: '实际金额', render: (v) => formatCurrency(v) },
  { key: 'variance', label: '差异', render: (v) => formatCurrency(v) },
  { key: 'status', label: '状态', render: (v) => StatusBadge }
];

const budgetActions = [
  { label: '编辑', icon: 'fa-edit', color: 'emerald', visible: (row) => row.status === 'draft', handler: (row) => { editingBudget.value = { ...row }; budgetVisible.value = true; } },
  { label: '审批', icon: 'fa-check', color: 'blue', visible: (row) => row.status === 'draft', handler: async (row) => { try { await approveBudget(row.budget_id); budgetRef.value?.fetchData(); } catch (e) { toast.error(e.message); } } },
  { label: '删除', icon: 'fa-trash', color: 'red', visible: (row) => row.status === 'draft', handler: (row) => { delBudgetItem.value = row; delBudgetVisible.value = true; } }
];

const budgetFields = [
  { key: 'budget_period', label: '预算周期', type: 'text', required: true, placeholder: '2026-05' },
  { key: 'account_id', label: '科目', type: 'select', required: true, options: accountOptions, optionValue: 'account_id', optionLabel: 'account_name' },
  { key: 'planned_amount', label: '计划金额', type: 'number', required: true },
  { key: 'actual_amount', label: '实际金额', type: 'number' }
];

const taxCols = [
  { key: 'tax_declaration_id', label: 'ID', width: '70px' },
  { key: 'tax_type', label: '税种' },
  { key: 'declaration_period', label: '期间' },
  { key: 'tax_amount', label: '应纳税额', render: (v) => formatCurrency(v) },
  { key: 'paid_amount', label: '已缴金额', render: (v) => formatCurrency(v) },
  { key: 'payment_status', label: '状态', render: (v) => StatusBadge }
];

const taxActions = [
  { label: '编辑', icon: 'fa-edit', color: 'emerald', visible: (row) => row.payment_status !== 'paid', handler: (row) => { editingTax.value = { ...row }; taxVisible.value = true; } },
  { label: '删除', icon: 'fa-trash', color: 'red', handler: (row) => { delTaxItem.value = row; delTaxVisible.value = true; } }
];

const taxFields = [
  { key: 'tax_type', label: '税种', type: 'text', required: true },
  { key: 'declaration_period', label: '申报期间', type: 'text', required: true, placeholder: '2026-05' },
  { key: 'tax_amount', label: '应纳税额', type: 'number', required: true },
  { key: 'paid_amount', label: '已缴金额', type: 'number' },
  { key: 'submitted_to', label: '提交对象', type: 'text' },
  { key: 'submission_date', label: '申报日期', type: 'date' }
];

onMounted(async () => { try { const r = await getAccounts(); accountOptions.value = r.data || []; } catch {} });

function openBudget() { editingBudget.value = null; budgetVisible.value = true; }
function openTax() { editingTax.value = null; taxVisible.value = true; }

async function handleBudgetSubmit(data) {
  submitting.value = true;
  try {
    if (editingBudget.value) { await updateBudget(editingBudget.value.budget_id, data); }
    else { await createBudget(data); }
    budgetVisible.value = false; editingBudget.value = null; budgetRef.value?.fetchData();
  } catch (e) { toast.error(e.message); }
  finally { submitting.value = false; }
}

async function handleBudgetDelete() {
  if (!delBudgetItem.value) return;
  try { await deleteBudget(delBudgetItem.value.budget_id); delBudgetVisible.value = false; delBudgetItem.value = null; budgetRef.value?.fetchData(); }
  catch (e) { toast.error(e.message); }
}

async function handleTaxSubmit(data) {
  submitting.value = true;
  try {
    if (editingTax.value) { await updateTaxDeclaration(editingTax.value.tax_declaration_id, data); }
    else { await createTaxDeclaration(data); }
    taxVisible.value = false; editingTax.value = null; taxRef.value?.fetchData();
  } catch (e) { toast.error(e.message); }
  finally { submitting.value = false; }
}

async function handleTaxDelete() {
  if (!delTaxItem.value) return;
  try { await deleteTaxDeclaration(delTaxItem.value.tax_declaration_id); delTaxVisible.value = false; delTaxItem.value = null; taxRef.value?.fetchData(); }
  catch (e) { toast.error(e.message); }
}
</script>
