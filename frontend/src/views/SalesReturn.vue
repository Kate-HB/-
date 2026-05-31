<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div><h2 class="text-2xl font-bold text-slate-800">退货管理</h2><p class="text-sm text-slate-500 mt-0.5">管理销售退货记录</p></div>
      <button @click="openAdd" class="btn-primary flex items-center gap-x-2 px-5 py-2.5 rounded-xl text-sm"><i class="fa-solid fa-plus"></i>新建退货</button>
    </div>
    <DataTable ref="tableRef" :columns="columns" apiUrl="/sales-returns" :actions="actions" />

    <!-- Custom return form -->
    <Teleport to="body">
      <div v-if="modalVisible" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="modalVisible = false">
        <div class="bg-white rounded-2xl w-full max-w-lg mx-4 shadow-2xl max-h-[90vh] flex flex-col">
          <div class="px-6 pt-5 pb-3 border-b border-slate-100">
            <h3 class="text-lg font-bold text-slate-800">新建退货</h3>
          </div>
          <div class="px-6 py-4 space-y-4 overflow-y-auto flex-1">
            <div class="space-y-1.5">
              <label class="text-sm font-medium text-slate-700">原订单<span class="text-red-500">*</span></label>
              <select v-model="form.original_order_id" class="form-input" required @change="lookupOrder">
                <option value="">请选择订单</option>
                <option v-for="o in orderOptions" :key="o.order_id" :value="o.order_id">{{ o.order_number }}</option>
              </select>
            </div>
            <div class="space-y-1.5">
              <label class="text-sm font-medium text-slate-700">处理人<span class="text-red-500">*</span></label>
              <select v-model="form.employee_id" class="form-input" required>
                <option value="">请选择</option>
                <option v-for="e in employeeOptions" :key="e.employee_id" :value="e.employee_id">{{ e.employee_name }}</option>
              </select>
            </div>
            <div class="space-y-1.5">
              <label class="text-sm font-medium text-slate-700">退货原因</label>
              <textarea v-model="form.reason" class="form-input min-h-[60px]" placeholder="退货原因"></textarea>
            </div>
            <div v-if="returnItems.length" class="border border-slate-200 rounded-xl overflow-hidden">
              <table class="w-full text-sm">
                <thead class="bg-slate-50">
                  <tr>
                    <th class="px-3 py-2 text-left text-xs font-semibold text-slate-500">商品</th>
                    <th class="px-3 py-2 text-right text-xs font-semibold text-slate-500 w-20">数量</th>
                    <th class="px-3 py-2 text-right text-xs font-semibold text-slate-500 w-28">退款金额</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, i) in returnItems" :key="i">
                    <td class="px-3 py-2 text-sm">{{ item.product_name }}</td>
                    <td class="px-3 py-2">
                      <input v-model.number="item.quantity" type="number" min="1" class="form-input text-sm py-1 w-16 text-center" />
                    </td>
                    <td class="px-3 py-2">
                      <input v-model.number="item.refund_amount" type="number" step="0.01" min="0" class="form-input text-sm py-1 w-24 text-right" />
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-if="returnItems.length" class="flex justify-between text-sm font-medium p-2 bg-slate-50 rounded-lg">
              <span>退款合计</span>
              <span class="text-red-600">¥ {{ totalRefund.toFixed(2) }}</span>
            </div>
          </div>
          <div class="flex gap-x-3 justify-end px-6 py-4 border-t border-slate-100">
            <button @click="modalVisible = false" class="px-5 py-2.5 rounded-xl border border-slate-200 text-sm font-medium text-slate-600 hover:bg-slate-50">取消</button>
            <button @click="handleSubmit" :disabled="submitting" class="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium disabled:opacity-50">
              <i v-if="submitting" class="fa-solid fa-spinner fa-spin mr-1"></i>提交
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import DataTable from '@/components/DataTable.vue';
import StatusBadge from '@/components/StatusBadge.vue';
import { getSalesReturns, createSalesReturn, approveSalesReturn, getSalesOrders, getSalesOrderItems } from '@/api/sales';
import { getEmployees } from '@/api/employees';
import { formatCurrency, formatDate } from '@/utils/format';
import { useToast } from '@/utils/toast';
const toast = useToast();

const tableRef = ref(null); const modalVisible = ref(false); const submitting = ref(false);
const employeeOptions = ref([]); const orderOptions = ref([]);
const returnItems = ref([]);

const form = reactive({
  original_order_id: '',
  employee_id: '',
  reason: ''
});

const totalRefund = computed(() => returnItems.value.reduce((s, i) => s + (i.quantity * i.refund_amount), 0));

const columns = [
  { key: 'return_id', label: 'ID', width: '70px' },
  { key: 'original_order_id', label: '原订单ID' },
  { key: 'member_name', label: '会员' },
  { key: 'employee_name', label: '处理人' },
  { key: 'return_amount', label: '退款金额', render: (v) => formatCurrency(v) },
  { key: 'reason', label: '原因' },
  { key: 'return_date', label: '日期', render: (v) => formatDate(v) },
  { key: 'status', label: '状态', render: (v) => StatusBadge }
];

const actions = [
  { label: '审批', icon: 'fa-check', color: 'blue', requiredPermission: 'sales.return.approve', visible: (row) => row.status === 'pending', handler: async (row) => { try { await approveSalesReturn(row.return_id); tableRef.value?.fetchData(); } catch (e) { toast.error(e.message); } } }
];

onMounted(async () => {
  try { const r = await getEmployees(); employeeOptions.value = r.data || []; } catch {}
  try { const r = await getSalesOrders({ per_page: 200 }); orderOptions.value = r.data || []; } catch {}
});

function openAdd() {
  form.original_order_id = '';
  form.employee_id = '';
  form.reason = '';
  returnItems.value = [];
  modalVisible.value = true;
}

async function lookupOrder() {
  if (!form.original_order_id) { returnItems.value = []; return; }
  try {
    const r = await getSalesOrderItems(form.original_order_id);
    if (r.data && r.data.items) {
      returnItems.value = r.data.items.map(item => ({
        product_id: item.product_id,
        product_name: item.product_name,
        quantity: item.quantity,
        refund_amount: item.subtotal
      }));
    }
  } catch (e) { toast.error(e.message); }
}

async function handleSubmit() {
  if (!form.original_order_id || !form.employee_id) { toast.error('请填写必填字段'); return; }
  submitting.value = true;
  try {
    await createSalesReturn({
      original_order_id: form.original_order_id,
      employee_id: form.employee_id,
      reason: form.reason,
      return_amount: totalRefund.value,
      items: returnItems.value.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity,
        refund_amount: item.refund_amount
      }))
    });
    modalVisible.value = false;
    tableRef.value?.fetchData();
  } catch (e) { toast.error(e.message); }
  finally { submitting.value = false; }
}
</script>
