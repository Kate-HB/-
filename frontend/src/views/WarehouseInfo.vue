<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div><h2 class="text-2xl font-bold text-slate-800">仓库信息</h2><p class="text-sm text-slate-500 mt-0.5">管理仓库基本信息</p></div>
      <button @click="openAdd" class="btn-primary flex items-center gap-x-2 px-5 py-2.5 rounded-xl text-sm"><i class="fa-solid fa-plus"></i>添加仓库</button>
    </div>
    <DataTable ref="tableRef" :columns="columns" apiUrl="/warehouses" :actions="actions" />
    <FormModal :visible="modalVisible" :title="editingItem ? '编辑仓库' : '添加仓库'"
      :fields="formFields" :initialData="editingItem" :loading="submitting"
      @submit="handleSubmit" @cancel="modalVisible = false; editingItem = null" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import DataTable from '@/components/DataTable.vue';
import FormModal from '@/components/FormModal.vue';
import StatusBadge from '@/components/StatusBadge.vue';
import { getWarehouses, createWarehouse, updateWarehouse } from '@/api/warehouses';
import { useToast } from '@/utils/toast';
const toast = useToast();

const tableRef = ref(null); const modalVisible = ref(false);
const editingItem = ref(null); const submitting = ref(false);

const columns = [
  { key: 'warehouse_id', label: 'ID', width: '70px' },
  { key: 'warehouse_name', label: '仓库名称' },
  { key: 'location', label: '位置' },
  { key: 'capacity', label: '容量' },
  { key: 'status', label: '状态', render: (v) => StatusBadge }
];

const actions = [
  { label: '编辑', icon: 'fa-edit', color: 'emerald', handler: openEdit }
];

const formFields = [
  { key: 'warehouse_name', label: '仓库名称', type: 'text', required: true },
  { key: 'location', label: '位置', type: 'text' },
  { key: 'capacity', label: '容量', type: 'number' },
  { key: 'status', label: '状态', type: 'select',
    options: [{ value: 'active', label: '正常' }, { value: 'full', label: '已满' }, { value: 'maintenance', label: '维护中' }] }
];

function openAdd() { editingItem.value = null; modalVisible.value = true; }
function openEdit(row) { editingItem.value = { ...row }; modalVisible.value = true; }

async function handleSubmit(data) {
  submitting.value = true;
  try {
    if (editingItem.value) { await updateWarehouse(editingItem.value.warehouse_id, data); }
    else { await createWarehouse(data); }
    modalVisible.value = false; editingItem.value = null; tableRef.value?.fetchData();
  } catch (e) { toast.error(e.message); }
  finally { submitting.value = false; }
}
</script>
