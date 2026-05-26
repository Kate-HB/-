<template>
  <Teleport to="body">
    <div v-if="visible" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="$emit('cancel')">
      <div class="bg-white rounded-2xl w-full max-w-lg mx-4 shadow-2xl max-h-[90vh] flex flex-col">
        <div class="px-6 pt-5 pb-3 border-b border-slate-100">
          <h3 class="text-lg font-bold text-slate-800">{{ title }}</h3>
        </div>
        <form @submit.prevent="handleSubmit" class="px-6 py-4 space-y-4 overflow-y-auto flex-1">
          <div v-for="field in visibleFields" :key="field.key" class="space-y-1.5">
            <label class="text-sm font-medium text-slate-700">
              {{ field.label }}
              <span v-if="field.required" class="text-red-500">*</span>
            </label>
            <input v-if="field.type === 'text' || field.type === 'number' || field.type === 'date'"
              v-model="formData[field.key]" :type="field.type"
              :placeholder="field.placeholder || ''"
              class="form-input" :required="field.required" />

            <!-- Single select -->
            <select v-else-if="field.type === 'select' && !field.multiple" v-model="formData[field.key]"
              class="form-input" :required="field.required">
              <option value="">请选择</option>
              <option v-for="opt in unwrap(field.options)" :key="opt.value ?? opt[field.optionValue || 'id']"
                :value="opt.value ?? opt[field.optionValue || 'id']">
                {{ opt.label ?? opt[field.optionLabel || 'name'] }}
              </option>
            </select>

            <!-- Multi-select with tags -->
            <div v-else-if="field.type === 'select' && field.multiple" class="relative multi-select-dropdown-container">
              <div @click="toggleDropdown(field.key)"
                class="form-input flex items-center flex-wrap gap-1 min-h-[42px] cursor-pointer">
                <span v-for="id in (formData[field.key] || [])" :key="id"
                  class="inline-flex items-center gap-x-1 px-2 py-0.5 bg-blue-50 text-blue-700 rounded-lg text-xs font-medium">
                  {{ getOptionLabel(field, id) }}
                  <button type="button" @click.stop="removeTag(field.key, id)" class="hover:text-red-500">&times;</button>
                </span>
                <span v-if="!(formData[field.key] || []).length" class="text-slate-400 text-sm">请选择</span>
              </div>
              <div v-if="openDropdown === field.key"
                class="absolute left-0 right-0 top-full mt-1 bg-white border border-slate-200 rounded-xl shadow-lg z-10 max-h-48 overflow-y-auto">
                <div v-for="opt in unwrap(field.options)" :key="opt.value ?? opt[field.optionValue || 'id']"
                  @click="toggleOption(field.key, opt.value ?? opt[field.optionValue || 'id'])"
                  :class="['px-4 py-2 text-sm cursor-pointer hover:bg-slate-50 flex items-center justify-between',
                    (formData[field.key] || []).includes(opt.value ?? opt[field.optionValue || 'id']) ? 'bg-blue-50 text-blue-700' : '']">
                  {{ opt.label ?? opt[field.optionLabel || 'name'] }}
                  <i v-if="(formData[field.key] || []).includes(opt.value ?? opt[field.optionValue || 'id'])" class="fa-solid fa-check text-xs text-blue-600"></i>
                </div>
              </div>
            </div>

            <textarea v-else-if="field.type === 'textarea'" v-model="formData[field.key]"
              :placeholder="field.placeholder || ''"
              class="form-input min-h-[80px]" :required="field.required"></textarea>
            <div v-else-if="field.type === 'table'" class="border border-slate-200 rounded-xl overflow-hidden">
              <table class="w-full text-sm">
                <thead class="bg-slate-50">
                  <tr>
                    <th v-for="sc in field.subColumns" :key="sc.key" class="px-3 py-2 text-left text-xs font-semibold text-slate-500">{{ sc.label }}</th>
                    <th class="w-10"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, i) in formData[field.key]" :key="i">
                    <td v-for="sc in field.subColumns" :key="sc.key" class="px-3 py-1">
                      <select v-if="sc.type === 'select'" v-model="item[sc.key]" class="form-input text-sm py-1">
                        <option value="">请选择</option>
                        <option v-for="opt in unwrap(sc.options)" :key="opt.value ?? opt[sc.optionValue || 'id']"
                          :value="opt.value ?? opt[sc.optionValue || 'id']">
                          {{ opt.label ?? opt[sc.optionLabel || 'name'] }}
                        </option>
                      </select>
                      <input v-else v-model="item[sc.key]" :type="sc.inputType || 'number'" class="form-input text-sm py-1" />
                    </td>
                    <td class="px-1 py-1 text-center">
                      <button type="button" @click="removeItem(field.key, i)" class="text-red-400 hover:text-red-600">
                        <i class="fa-solid fa-times"></i>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
              <button type="button" @click="addItem(field.key, field.defaultItem || {})"
                class="w-full py-2 text-sm text-blue-600 hover:bg-blue-50 transition-colors">
                <i class="fa-solid fa-plus mr-1"></i>添加行
              </button>
            </div>
          </div>
        </form>
        <div class="flex gap-x-3 justify-end px-6 py-4 border-t border-slate-100">
          <button type="button" @click="$emit('cancel')"
            class="px-5 py-2.5 rounded-xl border border-slate-200 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors">取消</button>
          <button type="button" @click="handleSubmit"
            :disabled="loading"
            class="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium transition-colors disabled:opacity-50">
            <i v-if="loading" class="fa-solid fa-spinner fa-spin mr-1"></i>保存
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { reactive, watch, isRef, ref, computed, onBeforeUnmount } from 'vue';

function unwrap(o) { return isRef(o) ? o.value : o; }

const props = defineProps({
  visible: Boolean,
  title: { type: String, default: '表单' },
  fields: { type: Array, default: () => [] },
  initialData: { type: Object, default: null },
  loading: { type: Boolean, default: false }
});

const emit = defineEmits(['submit', 'cancel', 'update:visible']);

const formData = reactive({});
const openDropdown = ref(null);

const visibleFields = computed(() => props.fields.filter(f => {
  if (typeof f.visible === 'function') return f.visible(formData);
  return true;
}));

function onDocumentClick(e) {
  if (openDropdown.value) {
    const el = document.querySelector('.multi-select-dropdown-container');
    if (el && !el.contains(e.target)) {
      openDropdown.value = null;
    }
  }
}
watch(openDropdown, (v) => {
  if (v) document.addEventListener('click', onDocumentClick);
  else document.removeEventListener('click', onDocumentClick);
});
onBeforeUnmount(() => document.removeEventListener('click', onDocumentClick));

function getOptionLabel(field, id) {
  const opts = unwrap(field.options);
  const opt = opts.find(o => (o.value ?? o[field.optionValue || 'id']) === id);
  return opt ? (opt.label ?? opt[field.optionLabel || 'name']) : id;
}

function toggleDropdown(key) {
  openDropdown.value = openDropdown.value === key ? null : key;
}
function closeDropdown(key) {
  if (openDropdown.value === key) openDropdown.value = null;
}
function toggleOption(key, value) {
  if (!formData[key]) formData[key] = [];
  const idx = formData[key].indexOf(value);
  if (idx >= 0) formData[key].splice(idx, 1);
  else formData[key].push(value);
}
function removeTag(key, value) {
  if (!formData[key]) return;
  const idx = formData[key].indexOf(value);
  if (idx >= 0) formData[key].splice(idx, 1);
}

watch(() => props.visible, (v) => {
  if (v) {
    openDropdown.value = null;
    for (const field of props.fields) {
      if (field.type === 'table') {
        formData[field.key] = [];
      } else if (field.multiple) {
        formData[field.key] = props.initialData?.[field.key] ?? field.default ?? [];
      } else {
        formData[field.key] = props.initialData?.[field.key] ?? field.default ?? '';
      }
    }
    if (props.initialData) {
      for (const key of Object.keys(props.initialData)) {
        if (key in formData) formData[key] = props.initialData[key];
      }
    }
  }
}, { immediate: true });

function addItem(key, defaultItem) {
  if (!formData[key]) formData[key] = [];
  formData[key].push({ ...defaultItem });
}

function removeItem(key, index) {
  formData[key].splice(index, 1);
}

function handleSubmit() {
  const cleanData = {};
  for (const field of props.fields) {
    let val = formData[field.key];
    if (val === '') val = null;
    if (field.type === 'number' && val != null) val = Number(val);
    cleanData[field.key] = val;
  }
  emit('submit', cleanData);
}
</script>
