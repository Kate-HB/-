<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div><h2 class="text-2xl font-bold text-slate-800">库存查询</h2><p class="text-sm text-slate-500 mt-0.5">查看各仓库商品库存情况</p></div>
    </div>
    <DataTable ref="tableRef" :columns="columns" apiUrl="/inventory" searchPlaceholder="搜索商品..."
      :filters="statusFilters" :actions="actions" :extraParams="extraParams" />
    <FormModal :visible="adjustVisible" title="库存调整"
      :fields="adjustFields" :loading="submitting"
      @submit="handleAdjust" @cancel="adjustVisible = false" />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useRoute } from 'vue-router';
import DataTable from '@/components/DataTable.vue';
import FormModal from '@/components/FormModal.vue';
import StatusBadge from '@/components/StatusBadge.vue';
import { adjustInventory } from '@/api/warehouses';
import { useToast } from '@/utils/toast';
const toast = useToast();

const route = useRoute();
const tableRef = ref(null); const adjustVisible = ref(false);
const submitting = ref(false); const adjustItem = ref(null);

const extraParams = computed(() => route.query.scope === 'alert'
  ? { status: 'low,out_of_stock' }
  : {}
);

const columns = [
  { key: 'inventory_id', label: 'ID', width: '70px' },
  { key: 'product_name', label: '商品名称' },
  { key: 'warehouse_name', label: '仓库' },
  { key: 'stock_quantity', label: '库存数量' },
  { key: 'safety_stock', label: '安全库存' },
  { key: 'status', label: '状态', render: StatusBadge }
];

const statusFilters = [
  { label: '正常', value: 'normal' }, { label: '库存低', value: 'low' }, { label: '缺货', value: 'out_of_stock' }
];

const actions = [
  { label: '调整', icon: 'fa-sliders', color: 'blue', handler: openAdjust }
];

const adjustFields = [
  { key: 'inventory_id', label: '库存ID', type: 'number' },
  { key: 'stock_quantity', label: '新库存数量', type: 'number', required: true }
];

function openAdjust(row) {
  adjustItem.value = row;
  adjustFields[0].default = row.inventory_id;
  adjustFields[1].default = row.stock_quantity;
  adjustVisible.value = true;
}

async function handleAdjust(data) {
  submitting.value = true;
  try { await adjustInventory(data); adjustVisible.value = false; tableRef.value?.fetchData(); }
  catch (e) { toast.error(e.message); }
  finally { submitting.value = false; }
}
</script>
