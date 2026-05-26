<template>
  <div>
    <div class="mb-6"><h2 class="text-2xl font-bold text-slate-800">系统配置</h2><p class="text-sm text-slate-500 mt-0.5">管理系统配置与备份</p></div>
    <div class="flex gap-x-3 mb-4">
      <button @click="tab = 'config'" :class="tab === 'config' ? 'bg-blue-600 text-white' : 'bg-white text-slate-600 border'"
        class="px-4 py-2 rounded-xl text-sm font-medium transition-colors">系统配置</button>
      <button @click="tab = 'backup'" :class="tab === 'backup' ? 'bg-blue-600 text-white' : 'bg-white text-slate-600 border'"
        class="px-4 py-2 rounded-xl text-sm font-medium transition-colors">备份记录</button>
    </div>

    <div v-if="tab === 'config'">
      <div class="flex justify-end mb-4">
        <button @click="openConfig" class="btn-primary flex items-center gap-x-2 px-4 py-2 rounded-xl text-sm"><i class="fa-solid fa-plus"></i>添加配置</button>
      </div>
      <DataTable ref="configRef" :columns="configCols" apiUrl="/system-configs" :actions="configActions" />
      <FormModal :visible="configVisible" :title="editingConfig ? '编辑配置' : '添加配置'"
        :fields="configFields" :initialData="editingConfig" :loading="submitting"
        @submit="handleConfigSubmit" @cancel="configVisible = false; editingConfig = null" />
    </div>

    <div v-if="tab === 'backup'">
      <div class="flex justify-end mb-4">
        <button @click="createBackup" :disabled="backupLoading" class="btn-primary flex items-center gap-x-2 px-4 py-2 rounded-xl text-sm disabled:opacity-50">
          <i v-if="backupLoading" class="fa-solid fa-spinner fa-spin"></i>
          <i v-else class="fa-solid fa-floppy-disk"></i>创建备份
        </button>
      </div>
      <DataTable ref="backupRef" :columns="backupCols" apiUrl="/backup-records" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import DataTable from '@/components/DataTable.vue';
import FormModal from '@/components/FormModal.vue';
import StatusBadge from '@/components/StatusBadge.vue';
import { getSystemConfigs, createSystemConfig, updateSystemConfig, createBackupRecord } from '@/api/system';
import { formatDateTime } from '@/utils/format';
import { useToast } from '@/utils/toast';
const toast = useToast();

const tab = ref('config'); const submitting = ref(false);
const configVisible = ref(false); const editingConfig = ref(null);
const configRef = ref(null); const backupRef = ref(null); const backupLoading = ref(false);

const configCols = [
  { key: 'config_id', label: 'ID', width: '70px' },
  { key: 'config_key', label: '配置键' },
  { key: 'config_value', label: '配置值' },
  { key: 'config_type', label: '类型' },
  { key: 'description', label: '描述' }
];

const configActions = [
  { label: '编辑', icon: 'fa-edit', color: 'emerald', handler: (row) => { editingConfig.value = { ...row }; configVisible.value = true; } }
];

const configFields = [
  { key: 'config_key', label: '配置键', type: 'text', required: true },
  { key: 'config_value', label: '配置值', type: 'text', required: true },
  { key: 'config_type', label: '类型', type: 'select',
    options: [{ value: 'system', label: '系统' }, { value: 'ui', label: '界面' }, { value: 'business', label: '业务' }] },
  { key: 'description', label: '描述', type: 'textarea' }
];

const backupCols = [
  { key: 'backup_id', label: 'ID', width: '70px' },
  { key: 'backup_type', label: '备份类型' },
  { key: 'backup_path', label: '路径' },
  { key: 'backup_size', label: '大小' },
  { key: 'status', label: '状态', render: (v) => StatusBadge },
  { key: 'backup_time', label: '备份时间', render: (v) => formatDateTime(v) }
];

function openConfig() { editingConfig.value = null; configVisible.value = true; }

async function handleConfigSubmit(data) {
  submitting.value = true;
  try {
    if (editingConfig.value) { await updateSystemConfig(editingConfig.value.config_id, data); }
    else { await createSystemConfig(data); }
    configVisible.value = false; editingConfig.value = null; configRef.value?.fetchData();
  } catch (e) { toast.error(e.message); }
  finally { submitting.value = false; }
}

async function createBackup() {
  backupLoading.value = true;
  try { await createBackupRecord({ backup_type: 'full' }); backupRef.value?.fetchData(); }
  catch (e) { toast.error(e.message); }
  finally { backupLoading.value = false; }
}
</script>
