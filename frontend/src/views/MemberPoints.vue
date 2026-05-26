<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div><h2 class="text-2xl font-bold text-slate-800">积分管理</h2><p class="text-sm text-slate-500 mt-0.5">会员积分记录与调整</p></div>
      <button @click="openAdjust" class="btn-primary flex items-center gap-x-2 px-5 py-2.5 rounded-xl text-sm"><i class="fa-solid fa-plus"></i>积分调整</button>
    </div>
    <DataTable ref="tableRef" :columns="columns" apiUrl="/member-points" :actions="actions" />
    <FormModal :visible="modalVisible" title="积分调整" :fields="formFields" :loading="submitting"
      @submit="handleSubmit" @cancel="modalVisible = false" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DataTable from '@/components/DataTable.vue';
import FormModal from '@/components/FormModal.vue';
import { getMemberPoints, addMemberPoints, getMembers } from '@/api/members';
import { formatDateTime } from '@/utils/format';
import { useToast } from '@/utils/toast';
const toast = useToast();

const tableRef = ref(null); const modalVisible = ref(false); const submitting = ref(false);
const memberOptions = ref([]);

const columns = [
  { key: 'record_id', label: 'ID', width: '70px' },
  { key: 'member_name', label: '会员' },
  { key: 'points_change', label: '积分变动' },
  { key: 'change_type', label: '变动类型', render: (v) => ({ consume: '消费', redeem: '兑换', activity: '活动', adjust: '调整', refund: '退款' }[v] || v) },
  { key: 'change_date', label: '日期', render: (v) => formatDateTime(v) },
  { key: 'remarks', label: '备注' }
];

const actions = [];

const formFields = [
  { key: 'member_id', label: '会员', type: 'select', required: true, options: memberOptions, optionValue: 'member_id', optionLabel: 'member_name' },
  { key: 'points_change', label: '积分变动（正数增加，负数减少）', type: 'number', required: true },
  { key: 'remarks', label: '备注', type: 'textarea' }
];

onMounted(async () => { try { const r = await getMembers(); memberOptions.value = r.data || []; } catch {} });

function openAdjust() { modalVisible.value = true; }

async function handleSubmit(data) {
  submitting.value = true;
  try { await addMemberPoints({ ...data, change_type: 'adjust' }); modalVisible.value = false; tableRef.value?.fetchData(); }
  catch (e) { toast.error(e.message); }
  finally { submitting.value = false; }
}
</script>
