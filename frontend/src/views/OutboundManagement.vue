<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div><h2 class="text-2xl font-bold text-slate-800">出库管理</h2><p class="text-sm text-slate-500 mt-0.5">管理仓库出库记录</p></div>
      <button @click="openAdd" class="btn-primary flex items-center gap-x-2 px-5 py-2.5 rounded-xl text-sm"><i class="fa-solid fa-plus"></i>新建出库</button>
    </div>
    <DataTable ref="tableRef" :columns="columns" apiUrl="/outbound-records" :filters="statusFilters" :actions="actions" />
    <FormModal :visible="modalVisible" :title="editingItem ? '编辑出库' : '新建出库'"
      :fields="formFields" :initialData="editingItem" :loading="submitting"
      @submit="handleSubmit" @cancel="modalVisible = false; editingItem = null" />
    <ConfirmDialog :visible="delVisible" title="删除出库记录" message="确定要删除该出库记录吗？" confirmText="删除" :danger="true"
      @confirm="handleDelete" @cancel="delVisible = false; delItem = null" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DataTable from '@/components/DataTable.vue';
import FormModal from '@/components/FormModal.vue';
import ConfirmDialog from '@/components/ConfirmDialog.vue';
import StatusBadge from '@/components/StatusBadge.vue';
import { createOutboundRecord, updateOutboundRecord, deleteOutboundRecord, approveOutboundRecord } from '@/api/warehouses';
import { getProducts } from '@/api/products';
import { getWarehouses } from '@/api/warehouses';
import { formatDate } from '@/utils/format';
import { useToast } from '@/utils/toast';
const toast = useToast();

const tableRef = ref(null); const modalVisible = ref(false); const submitting = ref(false);
const editingItem = ref(null); const delVisible = ref(false); const delItem = ref(null);
const productOptions = ref([]); const warehouseOptions = ref([]);

const columns = [
  { key: 'outbound_record_id', label: 'ID', width: '70px' },
  { key: 'outbound_no', label: '单号' },
  { key: 'warehouse_name', label: '仓库' },
  { key: 'total_quantity', label: '数量' },
  { key: 'outbound_date', label: '日期', render: (v) => formatDate(v) },
  { key: 'status', label: '状态', render: (v) => StatusBadge }
];

const statusFilters = [
  { label: '待处理', value: 'pending' }, { label: '已发货', value: 'shipped' }, { label: '已完成', value: 'completed' }
];

const actions = [
  { label: '编辑', icon: 'fa-edit', color: 'emerald', visible: (row) => row.status !== 'completed', handler: openEdit },
  { label: '审批', icon: 'fa-check', color: 'blue', visible: (row) => row.status === 'pending', handler: async (row) => { try { await approveOutboundRecord(row.outbound_record_id); tableRef.value?.fetchData(); } catch (e) { toast.error(e.message); } } },
  { label: '删除', icon: 'fa-trash', color: 'red', handler: (row) => { delItem.value = row; delVisible.value = true; } }
];

const formFields = [
  { key: 'warehouse_id', label: '仓库', type: 'select', required: true, options: warehouseOptions, optionValue: 'warehouse_id', optionLabel: 'warehouse_name' },
  { key: 'outbound_date', label: '出库日期', type: 'date' },
  { key: 'notes', label: '备注', type: 'textarea' },
  { key: 'items', label: '出库明细', type: 'table',
    subColumns: [
      { key: 'product_id', label: '商品', type: 'select', options: productOptions, optionValue: 'product_id', optionLabel: 'product_name' },
      { key: 'quantity', label: '数量', inputType: 'number' },
      { key: 'batch_no', label: '批次', inputType: 'text' },
      { key: 'bin_location', label: '库位', inputType: 'text' }
    ],
    defaultItem: { product_id: '', quantity: 1, batch_no: '', bin_location: '' }
  }
];

onMounted(async () => {
  try { const r = await getProducts(); productOptions.value = r.data || []; } catch {}
  try { const r = await getWarehouses(); warehouseOptions.value = r.data || []; } catch {}
});

function openAdd() { editingItem.value = null; modalVisible.value = true; }
function openEdit(row) { editingItem.value = { ...row }; modalVisible.value = true; }

async function handleSubmit(data) {
  submitting.value = true;
  try {
    if (editingItem.value) { await updateOutboundRecord(editingItem.value.outbound_record_id, data); }
    else { await createOutboundRecord(data); }
    modalVisible.value = false; editingItem.value = null; tableRef.value?.fetchData();
  } catch (e) { toast.error(e.message); }
  finally { submitting.value = false; }
}

async function handleDelete() {
  if (!delItem.value) return;
  try { await deleteOutboundRecord(delItem.value.outbound_record_id); delVisible.value = false; delItem.value = null; tableRef.value?.fetchData(); }
  catch (e) { toast.error(e.message); }
}
</script>
