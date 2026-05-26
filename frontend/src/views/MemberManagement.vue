<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div><h2 class="text-2xl font-bold text-slate-800">会员管理</h2><p class="text-sm text-slate-500 mt-0.5">管理会员信息</p></div>
      <button @click="openAdd" class="btn-primary flex items-center gap-x-2 px-5 py-2.5 rounded-xl text-sm"><i class="fa-solid fa-plus"></i>添加会员</button>
    </div>
    <DataTable ref="tableRef" :columns="columns" apiUrl="/members" searchPlaceholder="搜索..." :filters="statusFilters" :actions="actions" />
    <FormModal :visible="modalVisible" :title="editingItem ? '编辑会员' : '添加会员'"
      :fields="formFields" :initialData="editingItem" :loading="submitting"
      @submit="handleSubmit" @cancel="modalVisible = false; editingItem = null" />
    <ConfirmDialog :visible="deleteVisible" title="删除会员" message="确定删除该会员吗？关联积分记录也将被删除。" danger confirmText="确认删除"
      @confirm="confirmDelete" @cancel="deleteVisible = false" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import DataTable from '@/components/DataTable.vue';
import FormModal from '@/components/FormModal.vue';
import ConfirmDialog from '@/components/ConfirmDialog.vue';
import StatusBadge from '@/components/StatusBadge.vue';
import { getMembers, createMember, updateMember, deleteMember } from '@/api/members';
import { formatDate } from '@/utils/format';
import { useToast } from '@/utils/toast';
const toast = useToast();

const tableRef = ref(null); const modalVisible = ref(false); const deleteVisible = ref(false);
const editingItem = ref(null); const submitting = ref(false); const deleteId = ref(null);

const columns = [
  { key: 'member_id', label: 'ID', width: '70px' },
  { key: 'member_no', label: '会员卡号' },
  { key: 'member_name', label: '姓名' },
  { key: 'phone', label: '电话' },
  { key: 'level', label: '等级' },
  { key: 'points', label: '积分' },
  { key: 'register_date', label: '注册日期', render: (v) => formatDate(v) },
  { key: 'status', label: '状态', render: (v) => StatusBadge }
];

const statusFilters = [
  { label: '活跃', value: 'active' }, { label: '停用', value: 'inactive' }, { label: '黑名单', value: 'blacklisted' }
];

const actions = [
  { label: '编辑', icon: 'fa-edit', color: 'emerald', handler: openEdit },
  { label: '删除', icon: 'fa-trash', color: 'red', handler: (row) => { deleteId.value = row.member_id; deleteVisible.value = true; } }
];

const formFields = [
  { key: 'member_no', label: '会员卡号', type: 'text', required: true },
  { key: 'member_name', label: '姓名', type: 'text', required: true },
  { key: 'phone', label: '电话', type: 'text' },
  { key: 'email', label: '邮箱', type: 'text' },
  { key: 'level', label: '等级', type: 'text' },
  { key: 'register_date', label: '注册日期', type: 'date' },
  { key: 'status', label: '状态', type: 'select',
    options: [{ value: 'active', label: '活跃' }, { value: 'inactive', label: '停用' }] }
];

function openAdd() { editingItem.value = null; modalVisible.value = true; }
function openEdit(row) { editingItem.value = { ...row }; modalVisible.value = true; }

async function handleSubmit(data) {
  submitting.value = true;
  try {
    if (editingItem.value) { await updateMember(editingItem.value.member_id, data); }
    else { await createMember(data); }
    modalVisible.value = false; editingItem.value = null; tableRef.value?.fetchData();
  } catch (e) { toast.error(e.message); }
  finally { submitting.value = false; }
}

async function confirmDelete() {
  try { await deleteMember(deleteId.value); deleteVisible.value = false; tableRef.value?.fetchData(); }
  catch (e) { toast.error(e.message); }
}
</script>
