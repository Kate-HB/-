<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div><h2 class="text-2xl font-bold text-slate-800">用户角色</h2><p class="text-sm text-slate-500 mt-0.5">管理系统用户与角色分配</p></div>
      <button @click="openAdd" class="btn-primary flex items-center gap-x-2 px-5 py-2.5 rounded-xl text-sm"><i class="fa-solid fa-plus"></i>添加用户</button>
    </div>
    <DataTable ref="tableRef" :columns="columns" apiUrl="/users" searchPlaceholder="搜索用户名..." :actions="actions" />
    <FormModal :visible="modalVisible" :title="editingItem ? '编辑用户' : '添加用户'"
      :fields="formFields" :initialData="editingItem" :loading="submitting"
      @submit="handleSubmit" @cancel="modalVisible = false; editingItem = null" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import DataTable from '@/components/DataTable.vue';
import FormModal from '@/components/FormModal.vue';
import StatusBadge from '@/components/StatusBadge.vue';
import { getUsers, createUser, updateUser, toggleUserLock, getRoles } from '@/api/system';
import { getEmployees } from '@/api/employees';
import { formatDateTime } from '@/utils/format';
import { useToast } from '@/utils/toast';
const toast = useToast();

const tableRef = ref(null); const modalVisible = ref(false);
const editingItem = ref(null); const submitting = ref(false);
const roleOptions = ref([]); const employeeOptions = ref([]);

const columns = [
  { key: 'user_id', label: 'ID', width: '70px' },
  { key: 'username', label: '用户名' },
  { key: 'roles', label: '角色', render: (v) => (v || []).map(r => r.role_name).join('、') || '-' },
  { key: 'status', label: '状态', render: (v) => StatusBadge },
  { key: 'last_login', label: '最后登录', render: (v) => formatDateTime(v) }
];

const actions = [
  { label: '编辑', icon: 'fa-edit', color: 'emerald', handler: openEdit },
  { label: '锁定', icon: 'fa-lock', color: 'amber', requiredPermission: 'system.user.manage', handler: async (row) => { try { await toggleUserLock(row.user_id); tableRef.value?.fetchData(); } catch (e) { toast.error(e.message); } } }
];

const formFields = computed(() => [
  { key: 'username', label: '用户名', type: 'text', required: true },
  { key: 'password', label: '密码', type: 'text', required: !editingItem.value },
  { key: 'employee_id', label: '关联员工', type: 'select', options: employeeOptions, optionValue: 'employee_id', optionLabel: 'employee_name' },
  { key: 'status', label: '状态', type: 'select',
    options: [{ value: 'active', label: '正常' }, { value: 'inactive', label: '停用' }] },
  { key: 'role_ids', label: '角色', type: 'select', options: roleOptions, optionValue: 'role_id', optionLabel: 'role_name', multiple: true }
]);

onMounted(async () => {
  try { const r = await getRoles(); roleOptions.value = r.data || []; } catch {}
  try { const r = await getEmployees(); employeeOptions.value = r.data || []; } catch {}
});

function openAdd() { editingItem.value = null; modalVisible.value = true; }
function openEdit(row) { editingItem.value = { ...row, password: '' }; modalVisible.value = true; }

async function handleSubmit(data) {
  submitting.value = true;
  try {
    if (!data.password) delete data.password;
    if (editingItem.value) { await updateUser(editingItem.value.user_id, data); }
    else { await createUser(data); }
    modalVisible.value = false; editingItem.value = null; tableRef.value?.fetchData();
  } catch (e) { toast.error(e.message); }
  finally { submitting.value = false; }
}
</script>
