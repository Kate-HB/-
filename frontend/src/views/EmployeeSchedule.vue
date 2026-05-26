<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div><h2 class="text-2xl font-bold text-slate-800">排班管理</h2><p class="text-sm text-slate-500 mt-0.5">管理员工排班</p></div>
      <button @click="openAdd" class="btn-primary flex items-center gap-x-2 px-5 py-2.5 rounded-xl text-sm"><i class="fa-solid fa-plus"></i>添加排班</button>
    </div>
    <DataTable ref="tableRef" :columns="columns" apiUrl="/schedules" :actions="actions" />
    <FormModal :visible="modalVisible" :title="editingItem ? '编辑排班' : '添加排班'"
      :fields="formFields" :initialData="editingItem" :loading="submitting"
      @submit="handleSubmit" @cancel="modalVisible = false; editingItem = null" />
    <ConfirmDialog :visible="delVisible" title="删除排班" message="确定要删除该排班记录吗？" confirmText="删除" :danger="true"
      @confirm="handleDelete" @cancel="delVisible = false; delItem = null" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DataTable from '@/components/DataTable.vue';
import FormModal from '@/components/FormModal.vue';
import ConfirmDialog from '@/components/ConfirmDialog.vue';
import { getSchedules, createSchedule, updateSchedule, deleteSchedule, getEmployees } from '@/api/employees';
import { formatDate } from '@/utils/format';
import { useToast } from '@/utils/toast';
const toast = useToast();

const shiftLabel = (v) => ({ morning: '早班', afternoon: '中班', night: '晚班', rest: '休息' }[v] || v);

const tableRef = ref(null); const modalVisible = ref(false); const submitting = ref(false);
const editingItem = ref(null); const delVisible = ref(false); const delItem = ref(null);
const employeeOptions = ref([]);

const columns = [
  { key: 'schedule_id', label: 'ID', width: '70px' },
  { key: 'employee_name', label: '员工' },
  { key: 'work_date', label: '日期', render: (v) => formatDate(v) },
  { key: 'shift_type', label: '班次', render: (v) => shiftLabel(v) },
  { key: 'start_time', label: '开始' },
  { key: 'end_time', label: '结束' }
];

const actions = [
  { label: '编辑', icon: 'fa-edit', color: 'emerald', handler: openEdit },
  { label: '删除', icon: 'fa-trash', color: 'red', handler: (row) => { delItem.value = row; delVisible.value = true; } }
];

const formFields = [
  { key: 'employee_id', label: '员工', type: 'select', required: true, options: employeeOptions, optionValue: 'employee_id', optionLabel: 'employee_name' },
  { key: 'work_date', label: '工作日期', type: 'date', required: true },
  { key: 'shift_type', label: '班次', type: 'select', required: true,
    options: [{ value: 'morning', label: '早班' }, { value: 'afternoon', label: '中班' }, { value: 'night', label: '晚班' }, { value: 'rest', label: '休息' }] },
  { key: 'start_time', label: '开始时间', type: 'text', placeholder: 'HH:MM' },
  { key: 'end_time', label: '结束时间', type: 'text', placeholder: 'HH:MM' }
];

onMounted(async () => { try { const r = await getEmployees(); employeeOptions.value = r.data || []; } catch {} });

function openAdd() { editingItem.value = null; modalVisible.value = true; }
function openEdit(row) { editingItem.value = { ...row }; modalVisible.value = true; }

async function handleSubmit(data) {
  submitting.value = true;
  try {
    if (editingItem.value) { await updateSchedule(editingItem.value.schedule_id, data); }
    else { await createSchedule(data); }
    modalVisible.value = false; editingItem.value = null; tableRef.value?.fetchData();
  } catch (e) { toast.error(e.message); }
  finally { submitting.value = false; }
}

async function handleDelete() {
  if (!delItem.value) return;
  try { await deleteSchedule(delItem.value.schedule_id); delVisible.value = false; delItem.value = null; tableRef.value?.fetchData(); }
  catch (e) { toast.error(e.message); }
}
</script>
