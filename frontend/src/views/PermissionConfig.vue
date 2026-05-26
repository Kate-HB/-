<template>
  <div>
    <div class="mb-6"><h2 class="text-2xl font-bold text-slate-800">权限配置</h2><p class="text-sm text-slate-500 mt-0.5">管理角色与权限</p></div>
    <div class="flex gap-x-3 mb-4">
      <button @click="tab = 'roles'" :class="tab === 'roles' ? 'bg-blue-600 text-white' : 'bg-white text-slate-600 border'"
        class="px-4 py-2 rounded-xl text-sm font-medium transition-colors">角色管理</button>
      <button @click="tab = 'perms'" :class="tab === 'perms' ? 'bg-blue-600 text-white' : 'bg-white text-slate-600 border'"
        class="px-4 py-2 rounded-xl text-sm font-medium transition-colors">权限管理</button>
    </div>

    <div v-if="tab === 'roles'">
      <div class="flex justify-end mb-4">
        <button @click="openRole" class="btn-primary flex items-center gap-x-2 px-4 py-2 rounded-xl text-sm"><i class="fa-solid fa-plus"></i>添加角色</button>
      </div>
      <DataTable ref="roleRef" :columns="roleCols" apiUrl="/roles" :actions="roleActions" />
      <FormModal :visible="roleVisible" :title="editingRole ? '编辑角色' : '添加角色'"
        :fields="roleFields" :initialData="editingRole" :loading="submitting"
        @submit="handleRoleSubmit" @cancel="roleVisible = false; editingRole = null" />
    </div>

    <div v-if="tab === 'perms'">
      <div class="flex justify-end mb-4">
        <button @click="openPerm" class="btn-primary flex items-center gap-x-2 px-4 py-2 rounded-xl text-sm"><i class="fa-solid fa-plus"></i>添加权限</button>
      </div>
      <DataTable ref="permRef" :columns="permCols" apiUrl="/permissions" :actions="permActions" />
      <FormModal :visible="permVisible" :title="editingPerm ? '编辑权限' : '添加权限'" :fields="permFields" :initialData="editingPerm" :loading="submitting"
        @submit="handlePermSubmit" @cancel="permVisible = false; editingPerm = null" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import DataTable from '@/components/DataTable.vue';
import FormModal from '@/components/FormModal.vue';
import { getRoles, createRole, updateRole, deleteRole, getPermissions, createPermission, updatePermission, deletePermission } from '@/api/system';
import { useToast } from '@/utils/toast';
const toast = useToast();

const tab = ref('roles'); const submitting = ref(false);
const roleVisible = ref(false); const permVisible = ref(false);
const editingRole = ref(null); const editingPerm = ref(null);
const roleRef = ref(null); const permRef = ref(null);
const permOptions = ref([]);

const roleCols = [
  { key: 'role_id', label: 'ID', width: '70px' },
  { key: 'role_name', label: '角色名称' },
  { key: 'description', label: '描述' },
  { key: 'permission_ids', label: '权限', render: (v) => (v || []).map(id => { const p = permOptions.value.find(o => o.permission_id === id); return p ? p.permission_name : id; }).join('、') || '-' }
];

const roleActions = [
  { label: '编辑', icon: 'fa-edit', color: 'emerald', handler: (row) => { editingRole.value = { ...row }; roleVisible.value = true; } },
  { label: '删除', icon: 'fa-trash', color: 'red', handler: async (row) => { if (!confirm('确认删除此角色？')) return; try { await deleteRole(row.role_id); roleRef.value?.fetchData(); } catch (e) { toast.error(e.message); } } }
];

const roleFields = computed(() => [
  { key: 'role_name', label: '角色名称', type: 'text', required: true },
  { key: 'description', label: '描述', type: 'textarea' },
  { key: 'permission_ids', label: '权限', type: 'select', options: permOptions.value, optionValue: 'permission_id', optionLabel: 'permission_name', multiple: true }
]);

const permCols = [
  { key: 'permission_id', label: 'ID', width: '70px' },
  { key: 'permission_code', label: '权限代码' },
  { key: 'permission_name', label: '权限名称' },
  { key: 'module', label: '模块' },
  { key: 'description', label: '描述' }
];

const permActions = [
  { label: '编辑', icon: 'fa-edit', color: 'emerald', handler: (row) => { editingPerm.value = { ...row }; permVisible.value = true; } },
  { label: '删除', icon: 'fa-trash', color: 'red', handler: async (row) => { if (!confirm('确认删除此权限？')) return; try { await deletePermission(row.permission_id); permRef.value?.fetchData(); } catch (e) { toast.error(e.message); } } }
];

const permFields = [
  { key: 'permission_code', label: '权限代码', type: 'text', required: true },
  { key: 'permission_name', label: '权限名称', type: 'text', required: true },
  { key: 'module', label: '模块', type: 'text' },
  { key: 'description', label: '描述', type: 'textarea' }
];

onMounted(async () => { try { const r = await getPermissions(); permOptions.value = r.data || []; } catch {} });

function openRole() { editingRole.value = null; roleVisible.value = true; }
function openPerm() { editingPerm.value = null; permVisible.value = true; }

async function handleRoleSubmit(data) {
  submitting.value = true;
  try {
    if (editingRole.value) { await updateRole(editingRole.value.role_id, data); }
    else { await createRole(data); }
    roleVisible.value = false; editingRole.value = null; roleRef.value?.fetchData();
  } catch (e) { toast.error(e.message); }
  finally { submitting.value = false; }
}

async function handlePermSubmit(data) {
  submitting.value = true;
  try {
    if (editingPerm.value) { await updatePermission(editingPerm.value.permission_id, data); }
    else { await createPermission(data); }
    permVisible.value = false; editingPerm.value = null; permRef.value?.fetchData();
  } catch (e) { toast.error(e.message); }
  finally { submitting.value = false; }
}
</script>
