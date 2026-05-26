<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div><h2 class="text-2xl font-bold text-slate-800">采购订单</h2><p class="text-sm text-slate-500 mt-0.5">管理采购订单与审批</p></div>
      <button @click="openAdd" class="btn-primary flex items-center gap-x-2 px-5 py-2.5 rounded-xl text-sm"><i class="fa-solid fa-plus"></i>新建采购单</button>
    </div>
    <DataTable ref="tableRef" :key="'purchase-' + preStatus" :columns="columns" apiUrl="/purchase-orders" searchPlaceholder="搜索订单号..." :filters="statusFilters" :actions="actions" :extraParams="extraParams" />
    <FormModal :visible="modalVisible" :title="editingItem ? '编辑采购单' : '新建采购单'"
      :fields="formFields" :initialData="editingItem" :loading="submitting"
      @submit="handleSubmit" @cancel="modalVisible = false; editingItem = null" />
    <ConfirmDialog :visible="deleteVisible" title="删除采购单" message="确定删除该采购单吗？" danger confirmText="确认删除"
      @confirm="confirmDelete" @cancel="deleteVisible = false" />
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import DataTable from '@/components/DataTable.vue';
import FormModal from '@/components/FormModal.vue';
import ConfirmDialog from '@/components/ConfirmDialog.vue';
import StatusBadge from '@/components/StatusBadge.vue';
import { getPurchaseOrders, createPurchaseOrder, updatePurchaseOrder, deletePurchaseOrder, approvePurchaseOrder } from '@/api/purchases';
import { getSuppliers } from '@/api/suppliers';
import { getProducts } from '@/api/products';
import { getWarehouses } from '@/api/warehouses';
import { formatCurrency, formatDate } from '@/utils/format';
import { useToast } from '@/utils/toast';
const toast = useToast();

const route = useRoute();
const tableRef = ref(null);
const preStatus = computed(() => route.query.status || '');
const extraParams = computed(() => preStatus.value ? { status: preStatus.value } : {});
const modalVisible = ref(false); const deleteVisible = ref(false);
const editingItem = ref(null); const submitting = ref(false); const deleteId = ref(null);
const supplierOptions = ref([]); const productOptions = ref([]); const warehouseOptions = ref([]);

const columns = [
  { key: 'order_id', label: 'ID', width: '70px' },
  { key: 'order_number', label: '订单编号' },
  { key: 'supplier_name', label: '供应商' },
  { key: 'order_date', label: '订单日期', render: (v) => formatDate(v) },
  { key: 'total_amount', label: '总金额', render: (v) => formatCurrency(v) },
  { key: 'delivery_date', label: '预计到货', render: (v) => formatDate(v) },
  { key: 'status', label: '状态', render: (v) => StatusBadge }
];

const statusFilters = [
  { label: '草稿', value: 'draft' }, { label: '待审批', value: 'pending' }, { label: '已审批', value: 'approved' },
  { label: '已发货', value: 'shipped' }, { label: '已收货', value: 'received' }, { label: '已完成', value: 'completed' }
];

const actions = [
  { label: '编辑', icon: 'fa-edit', color: 'emerald', visible: (row) => row.status === 'draft' || row.status === 'pending', handler: openEdit },
  { label: '审批', icon: 'fa-check', color: 'blue', requiredPermission: 'purchase.approve', visible: (row) => row.status === 'pending', handler: async (row) => { try { await approvePurchaseOrder(row.order_id); tableRef.value?.fetchData(); } catch (e) { toast.error(e.message); } } },
  { label: '删除', icon: 'fa-trash', color: 'red', visible: (row) => row.status === 'draft' || row.status === 'pending', handler: (row) => { deleteId.value = row.order_id; deleteVisible.value = true; } }
];

const formFields = [
  { key: 'supplier_id', label: '供应商', type: 'select', required: true, options: supplierOptions, optionValue: 'supplier_id', optionLabel: 'supplier_name' },
  { key: 'order_date', label: '订单日期', type: 'date' },
  { key: 'delivery_date', label: '预计到货', type: 'date' },
  { key: 'warehouse_id', label: '入库仓库', type: 'select', options: warehouseOptions, optionValue: 'warehouse_id', optionLabel: 'warehouse_name' },
  { key: 'status', label: '状态', type: 'select',
    options: [{ value: 'draft', label: '草稿' }, { value: 'pending', label: '待审批' }, { value: 'approved', label: '已审批' }] },
  { key: 'items', label: '采购明细', type: 'table',
    subColumns: [
      { key: 'product_id', label: '商品', type: 'select', options: productOptions, optionValue: 'product_id', optionLabel: 'product_name' },
      { key: 'quantity', label: '数量', inputType: 'number' },
      { key: 'unit_price', label: '单价', inputType: 'number' }
    ],
    defaultItem: { product_id: '', quantity: 1, unit_price: 0 }
  }
];

onMounted(async () => {
  try { const r = await getSuppliers(); supplierOptions.value = r.data || []; } catch {}
  try { const r = await getProducts(); productOptions.value = r.data || []; } catch {}
  try { const r = await getWarehouses(); warehouseOptions.value = r.data || []; } catch {}
});

function openAdd() { editingItem.value = null; modalVisible.value = true; }
function openEdit(row) { editingItem.value = { ...row, items: row.items || [] }; modalVisible.value = true; }

async function handleSubmit(data) {
  submitting.value = true;
  try {
    data.total_amount = (data.items || []).reduce((sum, item) => sum + (item.quantity || 0) * (item.unit_price || 0), 0);
    if (editingItem.value) { await updatePurchaseOrder(editingItem.value.order_id, data); }
    else { await createPurchaseOrder(data); }
    modalVisible.value = false; editingItem.value = null; tableRef.value?.fetchData();
  } catch (e) { toast.error(e.message); }
  finally { submitting.value = false; }
}

async function confirmDelete() {
  try { await deletePurchaseOrder(deleteId.value); deleteVisible.value = false; tableRef.value?.fetchData(); }
  catch (e) { toast.error(e.message); }
}
</script>
