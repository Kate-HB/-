<template>
  <div class="flex flex-col items-center justify-center py-16 text-slate-400">
    <i class="fa-solid fa-inbox text-5xl mb-3"></i>
    <p class="text-sm">{{ message }}</p>
  </div>
</template>

<script setup>
defineProps({ message: { type: String, default: '暂无数据' } });
</script>
