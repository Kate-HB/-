<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div><h2 class="text-2xl font-bold text-slate-800">员工管理</h2><p class="text-sm text-slate-500 mt-0.5">管理员工基本信息</p></div>
      <button @click="openAdd" class="btn-primary flex items-center gap-x-2 px-5 py-2.5 rounded-xl text-sm"><i class="fa-solid fa-plus"></i>添加员工</button>
    </div>
    <DataTable ref="tableRef" :columns="columns" apiUrl="/employees" searchPlaceholder="搜索..." :filters="statusFilters" :actions="actions" />
    <FormModal :visible="modalVisible" :title="editingItem ? '编辑员工' : '添加员工'"
      :fields="formFields" :initialData="editingItem" :loading="submitting"
      @submit="handleSubmit" @cancel="modalVisible = false; editingItem = null" />
    <ConfirmDialog :visible="deleteVisible" title="删除员工" message="确定删除该员工吗？关联排班和薪资记录也将被删除。" danger confirmText="确认删除"
      @confirm="confirmDelete" @cancel="deleteVisible = false" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DataTable from '@/components/DataTable.vue';
import FormModal from '@/components/FormModal.vue';
import ConfirmDialog from '@/components/ConfirmDialog.vue';
import StatusBadge from '@/components/StatusBadge.vue';
import { getEmployees, createEmployee, updateEmployee, deleteEmployee, getPositions, getDepartments } from '@/api/employees';
import { formatDate } from '@/utils/format';
import { useToast } from '@/utils/toast';
const toast = useToast();

const tableRef = ref(null); const modalVisible = ref(false); const deleteVisible = ref(false);
const editingItem = ref(null); const submitting = ref(false); const deleteId = ref(null);
const positionOptions = ref([]);
const departmentOptions = ref([]);

const columns = [
  { key: 'employee_id', label: 'ID', width: '70px' },
  { key: 'employee_no', label: '工号' },
  { key: 'employee_name', label: '姓名' },
  { key: 'department', label: '部门' },
  { key: 'position_name', label: '岗位' },
  { key: 'phone', label: '电话' },
  { key: 'hire_date', label: '入职日期', render: (v) => formatDate(v) },
  { key: 'status', label: '状态', render: (v) => StatusBadge }
];

const statusFilters = [
  { label: '在职', value: 'active' }, { label: '停职', value: 'inactive' }, { label: '离职', value: 'resigned' }
];

const actions = [
  { label: '编辑', icon: 'fa-edit', color: 'emerald', handler: openEdit },
  { label: '删除', icon: 'fa-trash', color: 'red', handler: (row) => { deleteId.value = row.employee_id; deleteVisible.value = true; } }
];

const formFields = [
  { key: 'employee_no', label: '工号', type: 'text', required: true },
  { key: 'employee_name', label: '姓名', type: 'text', required: true },
  { key: 'id_card', label: '身份证号', type: 'text' },
  { key: 'department', label: '部门', type: 'select', options: departmentOptions },
  { key: 'position_id', label: '岗位', type: 'select', options: positionOptions, optionValue: 'position_id', optionLabel: 'position_name' },
  { key: 'phone', label: '电话', type: 'text' },
  { key: 'email', label: '邮箱', type: 'text' },
  { key: 'hire_date', label: '入职日期', type: 'date' },
  { key: 'status', label: '状态', type: 'select',
    options: [{ value: 'active', label: '在职' }, { value: 'inactive', label: '停职' }, { value: 'resigned', label: '离职' }] }
];

onMounted(async () => {
  try { const r = await getPositions(); positionOptions.value = r.data || []; } catch {}
  try { const r = await getDepartments(); departmentOptions.value = r.data || []; } catch {}
});

function openAdd() { editingItem.value = null; modalVisible.value = true; }
function openEdit(row) { editingItem.value = { ...row }; modalVisible.value = true; }

async function handleSubmit(data) {
  submitting.value = true;
  try {
    if (editingItem.value) { await updateEmployee(editingItem.value.employee_id, data); }
    else { await createEmployee(data); }
    modalVisible.value = false; editingItem.value = null; tableRef.value?.fetchData();
  } catch (e) { toast.error(e.message); }
  finally { submitting.value = false; }
}

async function confirmDelete() {
  try { await deleteEmployee(deleteId.value); deleteVisible.value = false; tableRef.value?.fetchData(); }
  catch (e) { toast.error(e.message); }
}
</script>
