<template>
  <Teleport to="body">
    <div v-if="visible" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="$emit('cancel')">
      <div class="bg-white rounded-2xl w-full max-w-sm mx-4 shadow-2xl p-6">
        <div class="text-center">
          <div class="w-12 h-12 rounded-full mx-auto mb-4 flex items-center justify-center"
            :class="danger ? 'bg-red-100' : 'bg-amber-100'">
            <i :class="'fa-solid ' + (danger ? 'fa-triangle-exclamation text-red-500' : 'fa-circle-question text-amber-500') + ' text-xl'"></i>
          </div>
          <h3 class="text-lg font-bold text-slate-800 mb-1">{{ title }}</h3>
          <p class="text-sm text-slate-500">{{ message }}</p>
        </div>
        <div class="flex gap-x-3 mt-6">
          <button @click="$emit('cancel')" class="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors">取消</button>
          <button @click="$emit('confirm')" class="flex-1 px-4 py-2.5 rounded-xl text-sm font-medium text-white transition-colors"
            :class="danger ? 'bg-red-500 hover:bg-red-600' : 'bg-blue-600 hover:bg-blue-700'">{{ confirmText }}</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  visible: Boolean,
  title: { type: String, default: '确认操作' },
  message: { type: String, default: '确定要执行此操作吗？' },
  confirmText: { type: String, default: '确认' },
  danger: { type: Boolean, default: false }
});
defineEmits(['confirm', 'cancel']);
</script>
