<template>
  <div>
    <div class="flex items-center justify-between mb-8 gap-4">
      <div>
        <h2 class="text-2xl font-bold text-slate-800">商品管理</h2>
        <p class="text-sm text-slate-500 mt-0.5">管理商品信息、库存与价格</p>
      </div>
      <button @click="openAdd" class="btn-primary flex items-center gap-x-2 px-5 py-2.5 rounded-xl text-sm">
        <i class="fa-solid fa-plus"></i>添加商品
      </button>
    </div>

    <DataTable ref="tableRef" :columns="columns" apiUrl="/products"
      searchPlaceholder="搜索商品名称..."
      :filters="statusFilters" :actions="actions" />

    <FormModal :visible="modalVisible" :title="editingItem ? '编辑商品' : '添加商品'"
      :fields="formFields" :initialData="editingItem" :loading="submitting"
      @submit="handleSubmit" @cancel="modalVisible = false; editingItem = null" />

    <ConfirmDialog :visible="deleteVisible" title="删除商品" message="确定删除该商品吗？关联库存也将被删除。"
      danger confirmText="确认删除" @confirm="confirmDelete" @cancel="deleteVisible = false" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DataTable from '@/components/DataTable.vue';
import FormModal from '@/components/FormModal.vue';
import ConfirmDialog from '@/components/ConfirmDialog.vue';
import StatusBadge from '@/components/StatusBadge.vue';
import { createProduct, updateProduct, deleteProduct, getCategories } from '@/api/products';
import { getSuppliers } from '@/api/suppliers';
import { formatCurrency } from '@/utils/format';
import { useToast } from '@/utils/toast';
const toast = useToast();

const tableRef = ref(null);
const modalVisible = ref(false);
const deleteVisible = ref(false);
const editingItem = ref(null);
const submitting = ref(false);
const deleteId = ref(null);
const errorMsg = ref('');
const categoryOptions = ref([]);
const supplierOptions = ref([]);

const columns = [
  { key: 'product_id', label: 'ID', width: '70px' },
  { key: 'product_name', label: '商品名称' },
  { key: 'barcode', label: '条码' },
  { key: 'category_name', label: '分类' },
  { key: 'supplier_name', label: '供应商' },
  { key: 'base_price', label: '售价', render: (v) => formatCurrency(v) },
  { key: 'cost_price', label: '成本价', render: (v) => v ? formatCurrency(v) : '-' },
  { key: 'stock_quantity', label: '库存' },
  { key: 'status', label: '状态', render: StatusBadge }
];

const statusFilters = [
  { label: '在售', value: 'active' },
  { label: '下架', value: 'inactive' },
  { label: '停产', value: 'discontinued' }
];

const actions = [
  { label: '编辑', icon: 'fa-edit', color: 'emerald', handler: openEdit },
  { label: '删除', icon: 'fa-trash', color: 'red', handler: (row) => { deleteId.value = row.product_id; deleteVisible.value = true; } }
];

const formFields = [
  { key: 'product_name', label: '商品名称', type: 'text', required: true },
  { key: 'barcode', label: '商品条码', type: 'text' },
  { key: 'category_id', label: '分类', type: 'select', required: true, options: categoryOptions, optionValue: 'category_id', optionLabel: 'category_name' },
  { key: 'supplier_id', label: '供应商', type: 'select', required: true, options: supplierOptions, optionValue: 'supplier_id', optionLabel: 'supplier_name' },
  { key: 'base_price', label: '售价', type: 'number', required: true },
  { key: 'cost_price', label: '成本价', type: 'number' },
  { key: 'spec', label: '规格', type: 'text' },
  { key: 'unit', label: '单位', type: 'text' },
  { key: 'description', label: '描述', type: 'textarea' },
  { key: 'status', label: '状态', type: 'select', options: [{ value: 'active', label: '在售' }, { value: 'inactive', label: '下架' }, { value: 'discontinued', label: '停产' }], default: 'active' }
];

async function loadOptions() {
  try { const r = await getCategories(); categoryOptions.value = r.data || []; } catch {}
  try { const r = await getSuppliers(); supplierOptions.value = r.data || []; } catch {}
}

onMounted(loadOptions);

function openAdd() {
  errorMsg.value = '';
  editingItem.value = null;
  modalVisible.value = true;
}

function openEdit(row) {
  errorMsg.value = '';
  editingItem.value = {
    ...row,
    base_price: Number(row.base_price ?? 0)
  };
  modalVisible.value = true;
}

async function handleSubmit(data) {
  errorMsg.value = '';
  submitting.value = true;
  try {
    if (editingItem.value) {
      await updateProduct(editingItem.value.product_id, data);
    } else {
      await createProduct(data);
    }
    modalVisible.value = false;
    editingItem.value = null;
    tableRef.value?.fetchData();
  } catch (e) {
    errorMsg.value = e.message;
    toast.error(e.message);
  } finally {
    submitting.value = false;
  }
}

async function confirmDelete() {
  try {
    await deleteProduct(deleteId.value);
    deleteVisible.value = false;
    tableRef.value?.fetchData();
  } catch (e) {
    toast.error(e.message);
  }
}
</script>
