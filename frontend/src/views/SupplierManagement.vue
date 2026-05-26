<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-2xl font-bold text-slate-800">供应商管理</h2>
        <p class="text-sm text-slate-500 mt-0.5">管理供应商基本信息</p>
      </div>
      <button @click="openAdd" class="btn-primary flex items-center gap-x-2 px-5 py-2.5 rounded-xl text-sm">
        <i class="fa-solid fa-plus"></i>添加供应商
      </button>
    </div>
    <DataTable ref="tableRef" :columns="columns" apiUrl="/suppliers" searchPlaceholder="搜索供应商..." :actions="actions" />
    <FormModal :visible="modalVisible" :title="editingItem ? '编辑供应商' : '添加供应商'"
      :fields="formFields" :initialData="editingItem" :loading="submitting"
      @submit="handleSubmit" @cancel="modalVisible = false; editingItem = null" />
    <ConfirmDialog :visible="deleteVisible" title="删除供应商" message="确定删除该供应商吗？" danger confirmText="确认删除"
      @confirm="confirmDelete" @cancel="deleteVisible = false" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import DataTable from '@/components/DataTable.vue';
import FormModal from '@/components/FormModal.vue';
import ConfirmDialog from '@/components/ConfirmDialog.vue';
import { getSuppliers, createSupplier, updateSupplier, deleteSupplier } from '@/api/suppliers';
import { useToast } from '@/utils/toast';
const toast = useToast();

const tableRef = ref(null);
const modalVisible = ref(false);
const deleteVisible = ref(false);
const editingItem = ref(null);
const submitting = ref(false);
const deleteId = ref(null);

const columns = [
  { key: 'supplier_id', label: 'ID', width: '70px' },
  { key: 'supplier_name', label: '供应商名称' },
  { key: 'contact_person', label: '联系人' },
  { key: 'phone', label: '电话' },
  { key: 'address', label: '地址' },
  { key: 'credit_level', label: '信用等级' }
];

const actions = [
  { label: '编辑', icon: 'fa-edit', color: 'emerald', handler: openEdit },
  { label: '删除', icon: 'fa-trash', color: 'red', handler: (row) => { deleteId.value = row.supplier_id; deleteVisible.value = true; } }
];

const formFields = [
  { key: 'supplier_name', label: '供应商名称', type: 'text', required: true },
  { key: 'contact_person', label: '联系人', type: 'text' },
  { key: 'phone', label: '联系电话', type: 'text' },
  { key: 'address', label: '地址', type: 'text' },
  { key: 'credit_level', label: '信用等级', type: 'text' }
];

function openAdd() { editingItem.value = null; modalVisible.value = true; }
function openEdit(row) { editingItem.value = { ...row }; modalVisible.value = true; }

async function handleSubmit(data) {
  submitting.value = true;
  try {
    if (editingItem.value) { await updateSupplier(editingItem.value.supplier_id, data); }
    else { await createSupplier(data); }
    modalVisible.value = false; editingItem.value = null;
    tableRef.value?.fetchData();
  } catch (e) { toast.error(e.message); }
  finally { submitting.value = false; }
}

async function confirmDelete() {
  try { await deleteSupplier(deleteId.value); deleteVisible.value = false; tableRef.value?.fetchData(); }
  catch (e) { toast.error(e.message); }
}
</script>
