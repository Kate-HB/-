<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div><h2 class="text-2xl font-bold text-slate-800">采购入库</h2><p class="text-sm text-slate-500 mt-0.5">管理采购入库记录</p></div>
      <button @click="openAdd" class="btn-primary flex items-center gap-x-2 px-5 py-2.5 rounded-xl text-sm"><i class="fa-solid fa-plus"></i>新建入库</button>
    </div>
    <DataTable ref="tableRef" :columns="columns" apiUrl="/inbound-records" :filters="statusFilters" :actions="actions" />
    <FormModal :visible="modalVisible" title="新建入库单"
      :fields="formFields" :loading="submitting"
      @submit="handleSubmit" @cancel="modalVisible = false" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DataTable from '@/components/DataTable.vue';
import FormModal from '@/components/FormModal.vue';
import StatusBadge from '@/components/StatusBadge.vue';
import { getInboundRecords, createInboundRecord } from '@/api/purchases';
import { getSuppliers } from '@/api/suppliers';
import { getProducts } from '@/api/products';
import { getWarehouses } from '@/api/warehouses';
import { formatDate } from '@/utils/format';
import { useToast } from '@/utils/toast';
const toast = useToast();

const tableRef = ref(null);
const modalVisible = ref(false); const submitting = ref(false);
const supplierOptions = ref([]); const productOptions = ref([]); const warehouseOptions = ref([]);

const columns = [
  { key: 'inbound_record_id', label: 'ID', width: '70px' },
  { key: 'inbound_no', label: '入库单号' },
  { key: 'supplier_name', label: '供应商' },
  { key: 'warehouse_name', label: '仓库' },
  { key: 'total_quantity', label: '总数量' },
  { key: 'inbound_date', label: '入库日期', render: (v) => formatDate(v) },
  { key: 'status', label: '状态', render: (v) => StatusBadge }
];

const statusFilters = [
  { label: '待处理', value: 'pending' }, { label: '已收货', value: 'received' }, { label: '已完成', value: 'completed' }
];

const actions = [];

const formFields = [
  { key: 'supplier_id', label: '供应商', type: 'select', required: true, options: supplierOptions, optionValue: 'supplier_id', optionLabel: 'supplier_name' },
  { key: 'warehouse_id', label: '入库仓库', type: 'select', required: true, options: warehouseOptions, optionValue: 'warehouse_id', optionLabel: 'warehouse_name' },
  { key: 'inbound_date', label: '入库日期', type: 'date' },
  { key: 'notes', label: '备注', type: 'textarea' },
  { key: 'items', label: '入库商品', type: 'table',
    subColumns: [
      { key: 'product_id', label: '商品', type: 'select', options: productOptions, optionValue: 'product_id', optionLabel: 'product_name' },
      { key: 'quantity', label: '数量', inputType: 'number' },
      { key: 'batch_no', label: '批次号', inputType: 'text' },
      { key: 'unit_price', label: '单价', inputType: 'number' },
      { key: 'bin_location', label: '库位', inputType: 'text' }
    ],
    defaultItem: { product_id: '', quantity: 1, batch_no: '', unit_price: 0, bin_location: '' }
  }
];

onMounted(async () => {
  try { const r = await getSuppliers(); supplierOptions.value = r.data || []; } catch {}
  try { const r = await getProducts(); productOptions.value = r.data || []; } catch {}
  try { const r = await getWarehouses(); warehouseOptions.value = r.data || []; } catch {}
});

function openAdd() { modalVisible.value = true; }

async function handleSubmit(data) {
  submitting.value = true;
  try { await createInboundRecord(data); modalVisible.value = false; tableRef.value?.fetchData(); }
  catch (e) { toast.error(e.message); }
  finally { submitting.value = false; }
}
</script>
