<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div><h2 class="text-2xl font-bold text-slate-800">会计凭证</h2><p class="text-sm text-slate-500 mt-0.5">管理会计凭证与分录</p></div>
      <button @click="openAdd" class="btn-primary flex items-center gap-x-2 px-5 py-2.5 rounded-xl text-sm"><i class="fa-solid fa-plus"></i>新建凭证</button>
    </div>
    <DataTable ref="tableRef" :columns="columns" apiUrl="/journal-entries" :filters="statusFilters" :actions="actions" />
    <FormModal :visible="modalVisible" :title="editingItem ? '编辑凭证' : '新建凭证'"
      :fields="formFields" :initialData="editingItem" :loading="submitting"
      @submit="handleSubmit" @cancel="modalVisible = false; editingItem = null" />
    <ConfirmDialog :visible="delVisible" title="删除凭证" message="确定要删除该凭证吗？" confirmText="删除" :danger="true"
      @confirm="handleDelete" @cancel="delVisible = false; delItem = null" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DataTable from '@/components/DataTable.vue';
import FormModal from '@/components/FormModal.vue';
import ConfirmDialog from '@/components/ConfirmDialog.vue';
import StatusBadge from '@/components/StatusBadge.vue';
import { getJournalEntries, createJournalEntry, updateJournalEntry, deleteJournalEntry, postJournalEntry } from '@/api/finance';
import { getAccounts } from '@/api/finance';
import { formatCurrency, formatDate } from '@/utils/format';
import { useToast } from '@/utils/toast';
const toast = useToast();

const tableRef = ref(null); const modalVisible = ref(false); const submitting = ref(false);
const editingItem = ref(null); const delVisible = ref(false); const delItem = ref(null);
const accountOptions = ref([]);

const columns = [
  { key: 'journal_entry_id', label: 'ID', width: '70px' },
  { key: 'voucher_no', label: '凭证号' },
  { key: 'entry_date', label: '日期', render: (v) => formatDate(v) },
  { key: 'description', label: '摘要' },
  { key: 'total_debit', label: '借方合计', render: (v) => formatCurrency(v) },
  { key: 'total_credit', label: '贷方合计', render: (v) => formatCurrency(v) },
  { key: 'status', label: '状态', render: (v) => StatusBadge }
];

const statusFilters = [
  { label: '草稿', value: 'draft' }, { label: '已过账', value: 'posted' }
];

const actions = [
  { label: '编辑', icon: 'fa-edit', color: 'emerald', visible: (row) => row.status === 'draft', handler: openEdit },
  { label: '过账', icon: 'fa-check', color: 'blue', visible: (row) => row.status === 'draft', handler: async (row) => { try { await postJournalEntry(row.journal_entry_id); tableRef.value?.fetchData(); } catch (e) { toast.error(e.message); } } },
  { label: '删除', icon: 'fa-trash', color: 'red', visible: (row) => row.status === 'draft', handler: (row) => { delItem.value = row; delVisible.value = true; } }
];

const formFields = [
  { key: 'entry_date', label: '记账日期', type: 'date', required: true },
  { key: 'description', label: '摘要', type: 'textarea' },
  { key: 'items', label: '分录明细', type: 'table',
    subColumns: [
      { key: 'account_id', label: '科目', type: 'select', options: accountOptions, optionValue: 'account_id', optionLabel: 'account_name' },
      { key: 'debit_amount', label: '借方金额', inputType: 'number' },
      { key: 'credit_amount', label: '贷方金额', inputType: 'number' },
      { key: 'description', label: '摘要', inputType: 'text' }
    ],
    defaultItem: { account_id: '', debit_amount: 0, credit_amount: 0, description: '' }
  }
];

onMounted(async () => { try { const r = await getAccounts(); accountOptions.value = r.data || []; } catch {} });

function openAdd() { editingItem.value = null; modalVisible.value = true; }
function openEdit(row) { editingItem.value = { ...row }; modalVisible.value = true; }

async function handleSubmit(data) {
  submitting.value = true;
  try {
    if (editingItem.value) { await updateJournalEntry(editingItem.value.journal_entry_id, data); }
    else { await createJournalEntry(data); }
    modalVisible.value = false; editingItem.value = null; tableRef.value?.fetchData();
  } catch (e) { toast.error(e.message); }
  finally { submitting.value = false; }
}

async function handleDelete() {
  if (!delItem.value) return;
  try { await deleteJournalEntry(delItem.value.journal_entry_id); delVisible.value = false; delItem.value = null; tableRef.value?.fetchData(); }
  catch (e) { toast.error(e.message); }
}
</script>
