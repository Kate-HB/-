<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div><h2 class="text-2xl font-bold text-slate-800">等级管理</h2><p class="text-sm text-slate-500 mt-0.5">管理会员等级与权益</p></div>
      <button @click="openAdd" class="btn-primary flex items-center gap-x-2 px-5 py-2.5 rounded-xl text-sm"><i class="fa-solid fa-plus"></i>添加等级</button>
    </div>
    <DataTable ref="tableRef" :columns="columns" apiUrl="/member-levels" :actions="actions" />
    <FormModal :visible="modalVisible" :title="editingItem ? '编辑等级' : '添加等级'"
      :fields="formFields" :initialData="editingItem" :loading="submitting"
      @submit="handleSubmit" @cancel="modalVisible = false; editingItem = null" />
    <ConfirmDialog :visible="delVisible" title="删除等级" message="删除后该等级会员将降为普通会员，确定删除？" confirmText="删除" :danger="true"
      @confirm="handleDelete" @cancel="delVisible = false; delItem = null" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import DataTable from '@/components/DataTable.vue';
import FormModal from '@/components/FormModal.vue';
import ConfirmDialog from '@/components/ConfirmDialog.vue';
import { getMemberLevels, createMemberLevel, updateMemberLevel, deleteMemberLevel } from '@/api/members';
import { useToast } from '@/utils/toast';
const toast = useToast();

const tableRef = ref(null); const modalVisible = ref(false);
const editingItem = ref(null); const submitting = ref(false);
const delVisible = ref(false); const delItem = ref(null);

const columns = [
  { key: 'level_id', label: 'ID', width: '70px' },
  { key: 'level_name', label: '等级名称' },
  { key: 'upgrade_condition', label: '升级条件' },
  { key: 'discount_rate', label: '折扣率', render: (v) => v ? (v * 100).toFixed(0) + '%' : '-' },
  { key: 'points_multiplier', label: '积分倍率' },
  { key: 'description', label: '描述' }
];

const actions = [
  { label: '编辑', icon: 'fa-edit', color: 'emerald', handler: openEdit },
  { label: '删除', icon: 'fa-trash', color: 'red', handler: (row) => { delItem.value = row; delVisible.value = true; } }
];

const formFields = [
  { key: 'level_name', label: '等级名称', type: 'text', required: true },
  { key: 'upgrade_condition', label: '升级条件', type: 'text' },
  { key: 'discount_rate', label: '折扣率 (0-1)', type: 'number' },
  { key: 'points_multiplier', label: '积分倍率', type: 'number' },
  { key: 'description', label: '描述', type: 'textarea' }
];

function openAdd() { editingItem.value = null; modalVisible.value = true; }
function openEdit(row) { editingItem.value = { ...row }; modalVisible.value = true; }

async function handleSubmit(data) {
  submitting.value = true;
  try {
    if (editingItem.value) { await updateMemberLevel(editingItem.value.level_id, data); }
    else { await createMemberLevel(data); }
    modalVisible.value = false; editingItem.value = null; tableRef.value?.fetchData();
  } catch (e) { toast.error(e.message); }
  finally { submitting.value = false; }
}

async function handleDelete() {
  if (!delItem.value) return;
  try { await deleteMemberLevel(delItem.value.level_id); delVisible.value = false; delItem.value = null; tableRef.value?.fetchData(); }
  catch (e) { toast.error(e.message); }
}
</script>
