<script setup lang="ts">
// ── InsightCard ──
// AI Insights section with accent border and insight list.

import { Lightbulb } from 'lucide-vue-next'

defineProps<{
  title: string
  insights: string[]
}>()
</script>

<template>
  <div class="rounded-lg border-l-2 border-l-primary border border-border bg-surface-raised">
    <div class="px-5 py-4">
      <div class="mb-3 flex items-center gap-2">
        <Lightbulb class="h-4 w-4 text-primary" />
        <h3 class="text-sm font-medium text-text-primary">{{ title }}</h3>
        <span class="rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-primary">
          AI Insights
        </span>
      </div>

      <ul v-if="insights.length > 0" class="space-y-2">
        <li
          v-for="(insight, i) in insights"
          :key="i"
          class="flex items-start gap-2 text-sm text-text-secondary"
        >
          <span class="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
          {{ insight }}
        </li>
      </ul>

      <p v-else class="text-sm text-text-muted">
        AI insights will appear here
      </p>
    </div>
  </div>
</template>
