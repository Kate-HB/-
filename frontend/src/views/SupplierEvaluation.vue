<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-2xl font-bold text-slate-800">评价管理</h2>
        <p class="text-sm text-slate-500 mt-0.5">供应商评价记录</p>
      </div>
      <button @click="openAdd" class="btn-primary flex items-center gap-x-2 px-5 py-2.5 rounded-xl text-sm">
        <i class="fa-solid fa-plus"></i>添加评价
      </button>
    </div>
    <DataTable ref="tableRef" :columns="columns" apiUrl="/supplier-evaluations" :actions="actions" />
    <FormModal :visible="modalVisible" :title="editingItem ? '编辑评价' : '添加评价'"
      :fields="formFields" :initialData="editingItem" :loading="submitting"
      @submit="handleSubmit" @cancel="modalVisible = false; editingItem = null" />
    <ConfirmDialog :visible="delVisible" title="删除评价" message="确定要删除该评价吗？" confirmText="删除" :danger="true"
      @confirm="handleDelete" @cancel="delVisible = false; delItem = null" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DataTable from '@/components/DataTable.vue';
import FormModal from '@/components/FormModal.vue';
import ConfirmDialog from '@/components/ConfirmDialog.vue';
import { getEvaluations, createEvaluation, updateEvaluation, deleteEvaluation } from '@/api/suppliers';
import { getSuppliers } from '@/api/suppliers';
import { getEmployees } from '@/api/employees';
import { formatDate } from '@/utils/format';
import { useToast } from '@/utils/toast';
const toast = useToast();

const tableRef = ref(null);
const modalVisible = ref(false);
const editingItem = ref(null);
const submitting = ref(false);
const delVisible = ref(false);
const delItem = ref(null);
const supplierOptions = ref([]);
const employeeOptions = ref([]);

const columns = [
  { key: 'evaluation_id', label: 'ID', width: '70px' },
  { key: 'supplier_name', label: '供应商' },
  { key: 'evaluator_name', label: '评价人' },
  { key: 'score', label: '总评分' },
  { key: 'quality_score', label: '质量' },
  { key: 'delivery_score', label: '交付' },
  { key: 'service_score', label: '服务' },
  { key: 'evaluation_date', label: '评价日期', render: (v) => formatDate(v) },
  { key: 'comments', label: '评价内容' }
];

const actions = [
  { label: '编辑', icon: 'fa-edit', color: 'emerald', handler: openEdit },
  { label: '删除', icon: 'fa-trash', color: 'red', handler: (row) => { delItem.value = row; delVisible.value = true; } }
];

const formFields = [
  { key: 'supplier_id', label: '供应商', type: 'select', required: true, options: supplierOptions, optionValue: 'supplier_id', optionLabel: 'supplier_name' },
  { key: 'evaluator_id', label: '评价人', type: 'select', required: true, options: employeeOptions, optionValue: 'employee_id', optionLabel: 'employee_name' },
  { key: 'score', label: '总评分', type: 'number', required: true },
  { key: 'quality_score', label: '质量评分', type: 'number' },
  { key: 'delivery_score', label: '交付评分', type: 'number' },
  { key: 'service_score', label: '服务评分', type: 'number' },
  { key: 'evaluation_date', label: '评价日期', type: 'date', required: true },
  { key: 'comments', label: '评价内容', type: 'textarea' }
];

onMounted(async () => {
  try { const r = await getSuppliers(); supplierOptions.value = r.data || []; } catch {}
  try { const r = await getEmployees(); employeeOptions.value = r.data || []; } catch {}
});

function openAdd() { editingItem.value = null; modalVisible.value = true; }
function openEdit(row) { editingItem.value = { ...row }; modalVisible.value = true; }

async function handleSubmit(data) {
  submitting.value = true;
  try {
    if (editingItem.value) { await updateEvaluation(editingItem.value.evaluation_id, data); }
    else { await createEvaluation(data); }
    modalVisible.value = false; editingItem.value = null; tableRef.value?.fetchData();
  } catch (e) { toast.error(e.message); }
  finally { submitting.value = false; }
}

async function handleDelete() {
  if (!delItem.value) return;
  try { await deleteEvaluation(delItem.value.evaluation_id); delVisible.value = false; delItem.value = null; tableRef.value?.fetchData(); }
  catch (e) { toast.error(e.message); }
}
</script>
