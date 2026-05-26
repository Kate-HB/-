<template>
  <div>
    <div class="mb-6">
      <h2 class="text-2xl font-bold text-slate-800">操作日志</h2>
      <p class="text-sm text-slate-500 mt-0.5">记录所有业务操作，支持按模块、操作类型、日期筛选</p>
    </div>

    <!-- Filter Bar -->
    <div class="flex flex-wrap items-center gap-3 mb-4 bg-white p-4 rounded-xl border border-slate-200">
      <select v-model="filterModule" @change="fetchData" class="input-field text-sm px-3 py-2 rounded-lg border border-slate-300 bg-white min-w-[120px]">
        <option value="">全部模块</option>
        <option value="product">商品管理</option>
        <option value="supplier">供应商管理</option>
        <option value="purchase">采购管理</option>
        <option value="warehouse">仓库管理</option>
        <option value="sales">销售管理</option>
        <option value="member">会员管理</option>
        <option value="employee">员工管理</option>
        <option value="finance">财务管理</option>
        <option value="system">系统管理</option>
      </select>
      <select v-model="filterOperation" @change="fetchData" class="input-field text-sm px-3 py-2 rounded-lg border border-slate-300 bg-white min-w-[110px]">
        <option value="">全部操作</option>
        <option value="create">创建</option>
        <option value="update">更新</option>
        <option value="delete">删除</option>
        <option value="approve">审批</option>
        <option value="cancel">取消</option>
        <option value="post">过账</option>
        <option value="login">登录</option>
        <option value="logout">登出</option>
        <option value="adjust">调整</option>
      </select>
      <input type="date" v-model="filterStartDate" @change="fetchData" class="input-field text-sm px-3 py-2 rounded-lg border border-slate-300 bg-white" />
      <span class="text-slate-400 text-sm">至</span>
      <input type="date" v-model="filterEndDate" @change="fetchData" class="input-field text-sm px-3 py-2 rounded-lg border border-slate-300 bg-white" />
      <input v-model="searchText" @keyup.enter="fetchData" placeholder="搜索目标名称..." class="input-field text-sm px-3 py-2 rounded-lg border border-slate-300 bg-white flex-1 min-w-[200px]" />
      <button @click="resetFilters" class="text-sm px-4 py-2 rounded-lg border border-slate-300 text-slate-600 hover:bg-slate-50">重置</button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="bg-white rounded-xl border border-slate-200 p-12 text-center">
      <i class="fa-solid fa-spinner fa-spin text-2xl text-slate-400 mb-3"></i>
      <p class="text-slate-500">加载中...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="rows.length === 0 && !loading" class="bg-white rounded-xl border border-slate-200 p-12 text-center">
      <i class="fa-solid fa-clipboard-list text-4xl text-slate-300 mb-3"></i>
      <p class="text-slate-500">暂无操作日志</p>
    </div>

    <!-- Table -->
    <div v-else class="bg-white rounded-xl border border-slate-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 border-b border-slate-200">
            <tr>
              <th class="text-left px-4 py-3 font-semibold text-slate-600 w-[60px]">ID</th>
              <th class="text-left px-4 py-3 font-semibold text-slate-600 w-[90px]">操作人</th>
              <th class="text-left px-4 py-3 font-semibold text-slate-600 w-[100px]">模块</th>
              <th class="text-left px-4 py-3 font-semibold text-slate-600 w-[80px]">操作</th>
              <th class="text-left px-4 py-3 font-semibold text-slate-600 w-[110px]">目标类型</th>
              <th class="text-left px-4 py-3 font-semibold text-slate-600">目标名称</th>
              <th class="text-left px-4 py-3 font-semibold text-slate-600 w-[130px]">IP地址</th>
              <th class="text-left px-4 py-3 font-semibold text-slate-600 w-[160px]">操作时间</th>
              <th class="text-center px-4 py-3 font-semibold text-slate-600 w-[60px]">详情</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in rows" :key="r.log_id" class="border-b border-slate-100 hover:bg-slate-50/50">
              <td class="px-4 py-2.5 text-slate-500">{{ r.log_id }}</td>
              <td class="px-4 py-2.5 font-medium">{{ r.operator_name || '-' }}</td>
              <td class="px-4 py-2.5">
                <span :class="moduleBadgeClass(r.module)">{{ moduleLabel(r.module) }}</span>
              </td>
              <td class="px-4 py-2.5">
                <span :class="operationBadgeClass(r.operation)">{{ operationLabel(r.operation) }}</span>
              </td>
              <td class="px-4 py-2.5 text-slate-500">{{ r.target_type || '-' }}</td>
              <td class="px-4 py-2.5 text-slate-700 max-w-[200px] truncate">{{ r.target_name || '-' }}</td>
              <td class="px-4 py-2.5 text-slate-400 text-xs font-mono">{{ r.ip_address || '-' }}</td>
              <td class="px-4 py-2.5 text-slate-500 text-xs">{{ formatDateTime(r.created_at) }}</td>
              <td class="px-4 py-2.5 text-center">
                <button v-if="r.details" @click="showDetail(r)" class="text-blue-500 hover:text-blue-700">
                  <i class="fa-solid fa-eye"></i>
                </button>
                <span v-else class="text-slate-300">-</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="flex items-center justify-between px-4 py-3 border-t border-slate-200 bg-slate-50/50">
        <span class="text-sm text-slate-500">共 {{ total }} 条</span>
        <div class="flex items-center gap-2">
          <button @click="goToPage(1)" :disabled="page <= 1" class="px-3 py-1.5 text-sm border rounded-lg disabled:opacity-30 hover:bg-slate-100">首页</button>
          <button @click="goToPage(page - 1)" :disabled="page <= 1" class="px-3 py-1.5 text-sm border rounded-lg disabled:opacity-30 hover:bg-slate-100">上一页</button>
          <span class="text-sm text-slate-600 px-2">{{ page }} / {{ totalPages }}</span>
          <button @click="goToPage(page + 1)" :disabled="page >= totalPages" class="px-3 py-1.5 text-sm border rounded-lg disabled:opacity-30 hover:bg-slate-100">下一页</button>
          <button @click="goToPage(totalPages)" :disabled="page >= totalPages" class="px-3 py-1.5 text-sm border rounded-lg disabled:opacity-30 hover:bg-slate-100">末页</button>
        </div>
      </div>
    </div>

    <!-- Detail Modal -->
    <div v-if="detailVisible" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center" @click.self="detailVisible = false">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 max-h-[80vh] overflow-auto">
        <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200">
          <h3 class="text-lg font-bold text-slate-800">操作详情</h3>
          <button @click="detailVisible = false" class="text-slate-400 hover:text-slate-600"><i class="fa-solid fa-times text-lg"></i></button>
        </div>
        <div class="p-6 space-y-3">
          <div class="flex"><span class="w-20 text-slate-500 text-sm">操作人：</span><span class="font-medium">{{ detailRow?.operator_name || '-' }}</span></div>
          <div class="flex"><span class="w-20 text-slate-500 text-sm">模块：</span><span>{{ moduleLabel(detailRow?.module) }}</span></div>
          <div class="flex"><span class="w-20 text-slate-500 text-sm">操作：</span><span :class="operationBadgeClass(detailRow?.operation)">{{ operationLabel(detailRow?.operation) }}</span></div>
          <div class="flex"><span class="w-20 text-slate-500 text-sm">目标类型：</span><span>{{ detailRow?.target_type || '-' }}</span></div>
          <div class="flex"><span class="w-20 text-slate-500 text-sm">目标ID：</span><span>{{ detailRow?.target_id ?? '-' }}</span></div>
          <div class="flex"><span class="w-20 text-slate-500 text-sm">目标名称：</span><span>{{ detailRow?.target_name || '-' }}</span></div>
          <div class="flex"><span class="w-20 text-slate-500 text-sm">IP地址：</span><code class="text-xs">{{ detailRow?.ip_address || '-' }}</code></div>
          <div class="flex"><span class="w-20 text-slate-500 text-sm">时间：</span><span class="text-sm">{{ formatDateTime(detailRow?.created_at) }}</span></div>
          <div v-if="detailRow?.details" class="pt-2 border-t border-slate-100">
            <span class="text-slate-500 text-sm block mb-2">变更详情：</span>
            <pre class="bg-slate-50 rounded-lg p-3 text-xs overflow-auto max-h-60">{{ JSON.stringify(detailRow.details, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { getOperationLogs } from '@/api/system';
import { formatDateTime } from '@/utils/format';

const rows = ref([]);
const page = ref(1);
const total = ref(0);
const perPage = ref(20);
const loading = ref(false);

const filterModule = ref('');
const filterOperation = ref('');
const filterStartDate = ref('');
const filterEndDate = ref('');
const searchText = ref('');

const detailVisible = ref(false);
const detailRow = ref(null);

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / perPage.value)));

const moduleLabels = { product: '商品管理', supplier: '供应商管理', purchase: '采购管理', warehouse: '仓库管理', sales: '销售管理', member: '会员管理', employee: '员工管理', finance: '财务管理', system: '系统管理' };
const operationLabels = { create: '创建', update: '更新', delete: '删除', approve: '审批', cancel: '取消', post: '过账', login: '登录', logout: '登出', adjust: '调整', register: '注册' };

function moduleLabel(m) { return moduleLabels[m] || m || '-'; }
function operationLabel(o) { return operationLabels[o] || o || '-'; }
function moduleBadgeClass(m) {
  const m1 = { system: 'bg-purple-100 text-purple-700', product: 'bg-emerald-100 text-emerald-700', supplier: 'bg-amber-100 text-amber-700', purchase: 'bg-cyan-100 text-cyan-700', warehouse: 'bg-orange-100 text-orange-700', sales: 'bg-blue-100 text-blue-700', member: 'bg-pink-100 text-pink-700', employee: 'bg-teal-100 text-teal-700', finance: 'bg-indigo-100 text-indigo-700' };
  return `px-2 py-0.5 rounded-full text-xs font-medium ${m1[m] || 'bg-gray-100 text-gray-600'}`;
}
function operationBadgeClass(o) {
  const m2 = { create: 'bg-emerald-100 text-emerald-700', update: 'bg-blue-100 text-blue-700', delete: 'bg-red-100 text-red-700', approve: 'bg-indigo-100 text-indigo-700', cancel: 'bg-gray-100 text-gray-600', post: 'bg-teal-100 text-teal-700', login: 'bg-sky-100 text-sky-700', logout: 'bg-slate-100 text-slate-600', adjust: 'bg-amber-100 text-amber-700', register: 'bg-violet-100 text-violet-700' };
  return `px-2 py-0.5 rounded-full text-xs font-medium ${m2[o] || 'bg-gray-100 text-gray-600'}`;
}

async function fetchData() {
  loading.value = true;
  try {
    const params = { page: page.value, per_page: perPage.value };
    if (filterModule.value) params.module = filterModule.value;
    if (filterOperation.value) params.operation = filterOperation.value;
    if (filterStartDate.value) params.start_date = filterStartDate.value;
    if (filterEndDate.value) params.end_date = filterEndDate.value;
    if (searchText.value) params.search = searchText.value;
    const r = await getOperationLogs(params);
    rows.value = r.data || [];
    total.value = r.total || 0;
  } catch { rows.value = []; total.value = 0; }
  finally { loading.value = false; }
}

function goToPage(p) {
  page.value = Math.max(1, Math.min(p, totalPages.value));
  fetchData();
}

function resetFilters() {
  filterModule.value = '';
  filterOperation.value = '';
  filterStartDate.value = '';
  filterEndDate.value = '';
  searchText.value = '';
  page.value = 1;
  fetchData();
}

function showDetail(row) {
  detailRow.value = row;
  detailVisible.value = true;
}

onMounted(fetchData);
</script>
