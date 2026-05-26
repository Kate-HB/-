<template>
  <component :is="to ? 'router-link' : 'div'" :to="to"
    class="kpi-card card-hover block" :class="{ 'cursor-pointer': to }">
    <div class="kpi-icon" :style="{ background: bgColor }">
      <i :class="'fa-solid ' + icon" :style="{ color: color }"></i>
    </div>
    <div class="flex-1">
      <p class="text-xs text-slate-500 font-medium">{{ title }}</p>
      <p class="text-2xl font-bold text-slate-800 mt-0.5 tracking-tight">{{ value }}</p>
      <p v-if="change != null" class="text-xs mt-1" :class="change > 0 ? 'text-emerald-600' : 'text-red-500'">
        <i :class="'fa-solid fa-arrow-' + (change > 0 ? 'up' : 'down') + ' mr-0.5'"></i>
        {{ Math.abs(change) }}% {{ changeLabel }}
      </p>
    </div>
  </component>
</template>

<script setup>
defineProps({
  title: String,
  value: [String, Number],
  change: Number,
  changeLabel: { type: String, default: '较昨日' },
  icon: { type: String, default: 'fa-chart-line' },
  color: { type: String, default: '#2563eb' },
  bgColor: { type: String, default: '#eff6ff' },
  to: { type: [String, Object], default: '' }
});
</script>
