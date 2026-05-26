<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-2xl font-bold text-slate-800">促销管理</h2>
        <p class="text-sm text-slate-500 mt-0.5">管理促销活动和折扣</p>
      </div>
      <button @click="openAdd" class="btn-primary flex items-center gap-x-2 px-5 py-2.5 rounded-xl text-sm">
        <i class="fa-solid fa-plus"></i>添加促销
      </button>
    </div>

    <DataTable ref="tableRef" :columns="columns" apiUrl="/promotions"
      :filters="statusFilters" :actions="actions" />

    <FormModal :visible="modalVisible" :title="editingItem ? '编辑促销' : '添加促销'"
      :fields="formFields" :initialData="editingItem" :loading="submitting"
      @submit="handleSubmit" @cancel="modalVisible = false; editingItem = null" />

    <ConfirmDialog :visible="deleteVisible" title="删除促销" message="确定删除该促销吗？" danger confirmText="确认删除"
      @confirm="confirmDelete" @cancel="deleteVisible = false" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DataTable from '@/components/DataTable.vue';
import FormModal from '@/components/FormModal.vue';
import ConfirmDialog from '@/components/ConfirmDialog.vue';
import StatusBadge from '@/components/StatusBadge.vue';
import { getPromotions, createPromotion, updatePromotion, deletePromotion, getProducts } from '@/api/products';
import { formatCurrency, formatDate } from '@/utils/format';
import { useToast } from '@/utils/toast';
const toast = useToast();

const tableRef = ref(null);
const modalVisible = ref(false);
const deleteVisible = ref(false);
const editingItem = ref(null);
const submitting = ref(false);
const deleteId = ref(null);
const productOptions = ref([]);

const columns = [
  { key: 'promotion_id', label: 'ID', width: '70px' },
  { key: 'promotion_name', label: '促销名称' },
  { key: 'promotion_type', label: '类型', render: (v) => ({ discount: '折扣', full_reduction: '满减', buy_gift: '买赠', points: '积分' }[v] || v) },
  { key: 'discount_rate', label: '折扣率', render: (v) => v ? (v * 100).toFixed(0) + '%' : '-' },
  { key: 'fixed_amount', label: '减免金额', render: (v) => v ? formatCurrency(v) : '-' },
  { key: 'min_amount', label: '满减门槛', render: (v) => v ? formatCurrency(v) : '-' },
  { key: 'min_quantity', label: '购买件数', render: (v) => v || '-' },
  { key: 'gift_product_name', label: '赠品', render: (v) => v || '-' },
  { key: 'gift_quantity', label: '赠送数量', render: (v) => v || '-' },
  { key: 'start_date', label: '开始日期', render: (v) => formatDate(v) },
  { key: 'end_date', label: '结束日期', render: (v) => formatDate(v) },
  { key: 'status', label: '状态', render: StatusBadge }
];

const statusFilters = [
  { label: '待审批', value: 'pending' },
  { label: '进行中', value: 'active' },
  { label: '已结束', value: 'ended' },
  { label: '已取消', value: 'cancelled' }
];

const actions = [
  { label: '编辑', icon: 'fa-edit', color: 'emerald', handler: openEdit },
  { label: '删除', icon: 'fa-trash', color: 'red', handler: (row) => { deleteId.value = row.promotion_id; deleteVisible.value = true; } }
];

const formFields = [
  { key: 'promotion_name', label: '促销名称', type: 'text', required: true },
  { key: 'promotion_type', label: '促销类型', type: 'select', required: true,
    options: [{ value: 'discount', label: '折扣' }, { value: 'full_reduction', label: '满减' }, { value: 'buy_gift', label: '买赠' }, { value: 'points', label: '积分' }] },
  { key: 'discount_rate', label: '折扣率 (0-1)', type: 'number' },
  { key: 'fixed_amount', label: '固定减免金额', type: 'number' },
  { key: 'min_amount', label: '满减门槛', type: 'number',
    visible: (fd) => fd.promotion_type === 'full_reduction' },
  { key: 'min_quantity', label: '购买件数', type: 'number',
    visible: (fd) => fd.promotion_type === 'buy_gift' },
  { key: 'gift_product_id', label: '赠品', type: 'select', options: productOptions, optionValue: 'product_id', optionLabel: 'product_name',
    visible: (fd) => fd.promotion_type === 'buy_gift' },
  { key: 'gift_quantity', label: '赠送数量', type: 'number', default: 1,
    visible: (fd) => fd.promotion_type === 'buy_gift' },
  { key: 'start_date', label: '开始日期', type: 'date', required: true },
  { key: 'end_date', label: '结束日期', type: 'date', required: true },
  { key: 'status', label: '状态', type: 'select',
    options: [{ value: 'pending', label: '待审批' }, { value: 'active', label: '进行中' }, { value: 'ended', label: '已结束' }, { value: 'cancelled', label: '已取消' }] },
  { key: 'product_ids', label: '适用商品', type: 'select', options: productOptions, optionValue: 'product_id', optionLabel: 'product_name', multiple: true }
];

onMounted(async () => {
  try { const r = await getProducts({ per_page: 1000 }); productOptions.value = r.data || []; } catch {}
});

function openAdd() { editingItem.value = null; modalVisible.value = true; }
function openEdit(row) {
  editingItem.value = {
    ...row,
    gift_product_id: row.gift_product_id || '',
    product_ids: (row.products || []).map(p => p.product_id)
  };
  modalVisible.value = true;
}

async function handleSubmit(data) {
  submitting.value = true;
  try {
    data.products = (data.product_ids || []).map(id => ({ product_id: id }));
    delete data.product_ids;
    if (editingItem.value) {
      await updatePromotion(editingItem.value.promotion_id, data);
    } else {
      await createPromotion(data);
    }
    modalVisible.value = false; editingItem.value = null;
    tableRef.value?.fetchData();
  } catch (e) { toast.error(e.message); }
  finally { submitting.value = false; }
}

async function confirmDelete() {
  try { await deletePromotion(deleteId.value); deleteVisible.value = false; tableRef.value?.fetchData(); }
  catch (e) { toast.error(e.message); }
}
</script>
