<template>
  <div>
    <div class="flex items-center gap-x-3 mb-4">
      <div class="relative flex-1 max-w-sm">
        <i class="fa-solid fa-search absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
        <input v-model="searchText" @input="onSearch" :placeholder="searchPlaceholder"
          class="form-input pl-9" />
      </div>
      <select v-if="filters.length" v-model="activeFilter" @change="fetchData"
        class="form-input w-40">
        <option value="">全部</option>
        <option v-for="f in filters" :key="f.value" :value="f.value">{{ f.label }}</option>
      </select>
      <slot name="actions" />
    </div>

    <div class="bg-white rounded-2xl border border-slate-100 overflow-hidden">
      <table class="w-full modern-table">
        <thead>
          <tr>
            <th v-for="col in columns" :key="col.key" :style="{ width: col.width }"
              class="cursor-pointer select-none" @click="col.sortable !== false && toggleSort(col.key)">
              {{ col.label }}
              <i v-if="col.sortable !== false && sortKey === col.key"
                :class="'fa-solid fa-sort-' + (sortDir === 'asc' ? 'up' : 'down') + ' ml-1 text-xs'"></i>
            </th>
            <th v-if="visibleActions.length" class="w-32">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td :colspan="columns.length + (visibleActions.length ? 1 : 0)" class="text-center py-12">
              <i class="fa-solid fa-spinner fa-spin text-slate-400 text-xl"></i>
            </td>
          </tr>
          <tr v-else-if="!data.length">
            <td :colspan="columns.length + (visibleActions.length ? 1 : 0)">
              <EmptyState />
            </td>
          </tr>
          <tr v-for="(row, i) in data" :key="row[columns[0].key] != null ? row[columns[0].key] : '_' + i" @click="$emit('row-click', row)"
            class="cursor-pointer">
            <td v-for="col in columns" :key="col.key">
              <template v-if="col.render">
                <template v-if="typeof col.render === 'function'">
                  <component v-if="isComponent(col.render(row[col.key], row))" :is="col.render(row[col.key], row)" :status="row[col.key]" />
                  <span v-else>{{ col.render(row[col.key], row) }}</span>
                </template>
                <component v-else :is="col.render" :status="row[col.key]" />
              </template>
              <span v-else>{{ row[col.key] ?? '-' }}</span>
            </td>
            <td v-if="visibleActions.length" @click.stop>
              <div class="flex gap-x-1">
                <template v-for="(act, ai) in visibleActions" :key="ai">
                  <button v-if="!act.visible || act.visible(row)" @click="act.handler(row)"
                    class="w-8 h-8 rounded-lg flex items-center justify-center text-xs transition-colors"
                    :class="actionColor(act.color)">
                    <i :class="'fa-solid ' + act.icon"></i>
                  </button>
                </template>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="flex items-center justify-between mt-4 text-xs text-slate-500">
      <span>显示 {{ data.length ? (page - 1) * perPage + 1 : 0 }}-{{ Math.min(page * perPage, total) }} 共 {{ total }} 条</span>
      <div class="flex items-center gap-x-2">
        <select v-model="perPage" @change="onPerPageChange" class="form-input w-20 text-xs py-1">
          <option v-for="s in pageSizes" :key="s" :value="s">{{ s }}/页</option>
        </select>
        <button @click="page--; fetchData()" :disabled="page <= 1"
          class="px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
          <i class="fa-solid fa-chevron-left"></i>
        </button>
        <span class="font-medium">{{ page }} / {{ Math.ceil(total / perPage) || 1 }}</span>
        <button @click="page++; fetchData()" :disabled="page * perPage >= total"
          class="px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
          <i class="fa-solid fa-chevron-right"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue';
import { get } from '@/api/index.js';
import EmptyState from './EmptyState.vue';
import { useAuthStore } from '@/stores/auth.js';

const auth = useAuthStore();

const props = defineProps({
  columns: { type: Array, required: true },
  apiUrl: { type: String, required: true },
  searchPlaceholder: { type: String, default: '搜索...' },
  filters: { type: Array, default: () => [] },
  actions: { type: Array, default: () => [] },
  extraParams: { type: Object, default: () => ({}) },
  perPageDefault: { type: Number, default: 20 }
});

defineEmits(['row-click']);

const data = ref([]);
const loading = ref(false);
const searchText = ref('');
const activeFilter = ref('');
const page = ref(1);
const perPage = ref(props.perPageDefault);
const total = ref(0);
const sortKey = ref('');
const sortDir = ref('asc');
const pageSizes = [10, 20, 50, 100];

function isComponent(v) { return typeof v === 'object' && v !== null; }

const visibleActions = computed(() =>
  props.actions.filter(a => !a.requiredPermission || auth.hasPermission(a.requiredPermission))
);

let searchTimer;

function onSearch() {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => { page.value = 1; fetchData(); }, 300);
}

function toggleSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortKey.value = key;
    sortDir.value = 'asc';
  }
  fetchData();
}

function onPerPageChange() {
  page.value = 1;
  fetchData();
}

function actionColor(color) {
  const map = {
    emerald: 'text-emerald-600 hover:bg-emerald-50',
    red: 'text-red-500 hover:bg-red-50',
    blue: 'text-blue-600 hover:bg-blue-50',
    amber: 'text-amber-600 hover:bg-amber-50',
    slate: 'text-slate-500 hover:bg-slate-50'
  };
  return map[color] || map.slate;
}

async function fetchData() {
  loading.value = true;
  try {
    const params = {
      page: page.value,
      per_page: perPage.value,
      search: searchText.value,
      sort_key: sortKey.value,
      sort_dir: sortDir.value,
      ...props.extraParams
    };
    if (activeFilter.value) {
      const filterKey = props.filters[0]?.key || 'status';
      params[filterKey] = activeFilter.value;
    }
    const res = await get(props.apiUrl, params);
    data.value = res.data || [];
    total.value = res.total || 0;
  } catch (e) {
    data.value = [];
    total.value = 0;
  } finally {
    loading.value = false;
  }
}

watch(() => props.extraParams, () => {
  page.value = 1;
  fetchData();
}, { deep: true });

onMounted(fetchData);
defineExpose({ fetchData });
</script>
