<script setup lang="ts">
// ── ChartCard ──
// Styled placeholder with "Charts coming soon" + default slot for future chart lib.

import { BarChart3 } from 'lucide-vue-next'

defineProps<{
  title: string
}>()
</script>

<template>
  <div class="card p-5">
    <div class="mb-3 flex items-center gap-2">
      <BarChart3 class="h-4 w-4 text-text-muted" />
      <h3 class="text-sm font-medium text-text-primary">{{ title }}</h3>
    </div>

    <!-- Default slot for future chart content -->
    <slot>
      <div class="flex flex-col items-center justify-center py-8 text-text-muted">
        <BarChart3 class="mb-2 h-8 w-8 opacity-30" />
        <p class="text-xs">Charts coming soon</p>
      </div>
    </slot>
  </div>
</template>
