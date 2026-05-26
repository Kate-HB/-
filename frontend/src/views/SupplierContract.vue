<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-2xl font-bold text-slate-800">合同管理</h2>
        <p class="text-sm text-slate-500 mt-0.5">管理供应商合同</p>
      </div>
      <button @click="openAdd" class="btn-primary flex items-center gap-x-2 px-5 py-2.5 rounded-xl text-sm">
        <i class="fa-solid fa-plus"></i>添加合同
      </button>
    </div>
    <DataTable ref="tableRef" :columns="columns" apiUrl="/supplier-contracts" :filters="statusFilters" :actions="actions" />
    <FormModal :visible="modalVisible" :title="editingItem ? '编辑合同' : '添加合同'"
      :fields="formFields" :initialData="editingItem" :loading="submitting"
      @submit="handleSubmit" @cancel="modalVisible = false; editingItem = null" />
    <ConfirmDialog :visible="deleteVisible" title="删除合同" message="确定删除该合同吗？" danger confirmText="确认删除"
      @confirm="confirmDelete" @cancel="deleteVisible = false" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DataTable from '@/components/DataTable.vue';
import FormModal from '@/components/FormModal.vue';
import ConfirmDialog from '@/components/ConfirmDialog.vue';
import StatusBadge from '@/components/StatusBadge.vue';
import { getContracts, createContract, updateContract, deleteContract } from '@/api/suppliers';
import { getSuppliers } from '@/api/suppliers';
import { formatCurrency, formatDate } from '@/utils/format';
import { useToast } from '@/utils/toast';
const toast = useToast();

const tableRef = ref(null);
const modalVisible = ref(false);
const deleteVisible = ref(false);
const editingItem = ref(null);
const submitting = ref(false);
const deleteId = ref(null);
const supplierOptions = ref([]);

const columns = [
  { key: 'contract_id', label: 'ID', width: '70px' },
  { key: 'contract_number', label: '合同编号' },
  { key: 'supplier_name', label: '供应商' },
  { key: 'contract_type', label: '合同类型' },
  { key: 'start_date', label: '开始日期', render: (v) => formatDate(v) },
  { key: 'end_date', label: '结束日期', render: (v) => formatDate(v) },
  { key: 'total_amount', label: '总金额', render: (v) => formatCurrency(v) },
  { key: 'status', label: '状态', render: (v) => StatusBadge }
];

const statusFilters = [
  { label: '待审批', value: 'pending' }, { label: '已审批', value: 'approved' },
  { label: '执行中', value: 'active' }, { label: '已终止', value: 'terminated' }, { label: '已过期', value: 'expired' }
];

const actions = [
  { label: '编辑', icon: 'fa-edit', color: 'emerald', handler: openEdit },
  { label: '删除', icon: 'fa-trash', color: 'red', handler: (row) => { deleteId.value = row.contract_id; deleteVisible.value = true; } }
];

const formFields = [
  { key: 'supplier_id', label: '供应商', type: 'select', required: true, options: supplierOptions, optionValue: 'supplier_id', optionLabel: 'supplier_name' },
  { key: 'contract_number', label: '合同编号', type: 'text', required: true },
  { key: 'contract_type', label: '合同类型', type: 'text' },
  { key: 'start_date', label: '开始日期', type: 'date' },
  { key: 'end_date', label: '结束日期', type: 'date' },
  { key: 'total_amount', label: '总金额', type: 'number' },
  { key: 'status', label: '状态', type: 'select',
    options: [{ value: 'pending', label: '待审批' }, { value: 'approved', label: '已审批' }, { value: 'active', label: '执行中' }, { value: 'terminated', label: '已终止' }] },
  { key: 'signed_date', label: '签订日期', type: 'date' }
];

onMounted(async () => { try { const r = await getSuppliers(); supplierOptions.value = r.data || []; } catch {} });

function openAdd() { editingItem.value = null; modalVisible.value = true; }
function openEdit(row) { editingItem.value = { ...row }; modalVisible.value = true; }

async function handleSubmit(data) {
  submitting.value = true;
  try {
    if (editingItem.value) { await updateContract(editingItem.value.contract_id, data); }
    else { await createContract(data); }
    modalVisible.value = false; editingItem.value = null; tableRef.value?.fetchData();
  } catch (e) { toast.error(e.message); }
  finally { submitting.value = false; }
}

async function confirmDelete() {
  try { await deleteContract(deleteId.value); deleteVisible.value = false; tableRef.value?.fetchData(); }
  catch (e) { toast.error(e.message); }
}
</script>
