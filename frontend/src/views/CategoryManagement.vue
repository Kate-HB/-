<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-2xl font-bold text-slate-800">分类管理</h2>
        <p class="text-sm text-slate-500 mt-0.5">管理商品分类层级</p>
      </div>
      <button @click="openAdd" class="btn-primary flex items-center gap-x-2 px-5 py-2.5 rounded-xl text-sm">
        <i class="fa-solid fa-plus"></i>添加分类
      </button>
    </div>

    <DataTable ref="tableRef" :columns="columns" apiUrl="/categories" :actions="actions" />

    <FormModal :visible="modalVisible" :title="editingItem ? '编辑分类' : '添加分类'"
      :fields="formFields" :initialData="editingItem" :loading="submitting"
      @submit="handleSubmit" @cancel="modalVisible = false; editingItem = null" />

    <ConfirmDialog :visible="deleteVisible" title="删除分类" message="确定删除该分类吗？" danger confirmText="确认删除"
      @confirm="confirmDelete" @cancel="deleteVisible = false" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DataTable from '@/components/DataTable.vue';
import FormModal from '@/components/FormModal.vue';
import ConfirmDialog from '@/components/ConfirmDialog.vue';
import { getCategories, createCategory, updateCategory, deleteCategory } from '@/api/products';
import { useToast } from '@/utils/toast';
const toast = useToast();

const tableRef = ref(null);
const modalVisible = ref(false);
const deleteVisible = ref(false);
const editingItem = ref(null);
const submitting = ref(false);
const deleteId = ref(null);
const categoryOptions = ref([]);

const columns = [
  { key: 'category_id', label: 'ID', width: '70px' },
  { key: 'category_name', label: '分类名称' },
  { key: 'description', label: '描述' }
];

const actions = [
  { label: '编辑', icon: 'fa-edit', color: 'emerald', handler: openEdit },
  { label: '删除', icon: 'fa-trash', color: 'red', handler: (row) => { deleteId.value = row.category_id; deleteVisible.value = true; } }
];

const formFields = [
  { key: 'category_name', label: '分类名称', type: 'text', required: true },
  { key: 'parent_category_id', label: '父分类', type: 'select', options: categoryOptions, optionValue: 'category_id', optionLabel: 'category_name' },
  { key: 'description', label: '描述', type: 'textarea' }
];

onMounted(async () => { try { const r = await getCategories(); categoryOptions.value = r.data || []; } catch {} });

function openAdd() { editingItem.value = null; modalVisible.value = true; }
function openEdit(row) { editingItem.value = { ...row }; modalVisible.value = true; }

async function handleSubmit(data) {
  submitting.value = true;
  try {
    if (editingItem.value) {
      await updateCategory(editingItem.value.category_id, data);
    } else {
      await createCategory(data);
    }
    modalVisible.value = false; editingItem.value = null;
    const r = await getCategories(); categoryOptions.value = r.data || [];
    tableRef.value?.fetchData();
  } catch (e) { toast.error(e.message); }
  finally { submitting.value = false; }
}

async function confirmDelete() {
  try {
    await deleteCategory(deleteId.value);
    deleteVisible.value = false;
    const r = await getCategories(); categoryOptions.value = r.data || [];
    tableRef.value?.fetchData();
  } catch (e) { toast.error(e.message); }
}
</script>
