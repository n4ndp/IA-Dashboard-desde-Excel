<script setup lang="ts">
// ── InsightWidget ──
// Styled text insight card with emoji, severity-based accent border and icon color.

import type { InsightWidgetData } from '../../types'

const props = defineProps<{
  widget: InsightWidgetData
}>()

const severityConfig: Record<string, { accent: string; iconColor: string }> = {
  positive: { accent: 'border-l-emerald-400', iconColor: 'text-emerald-400' },
  negative: { accent: 'border-l-red-400', iconColor: 'text-red-400' },
  warning: { accent: 'border-l-amber-400', iconColor: 'text-amber-400' },
  info: { accent: 'border-l-sky-400', iconColor: 'text-sky-400' },
}

const config = severityConfig[props.widget.severity] ?? severityConfig.info
</script>

<template>
  <div
    class="bg-surface-raised border border-border border-l-4 rounded-lg p-4 transition-colors"
    :class="config.accent"
  >
    <div class="flex items-start gap-3">
      <span class="text-2xl leading-none shrink-0">{{ widget.emoji }}</span>
      <p class="text-sm leading-relaxed text-text-secondary">
        {{ widget.content }}
      </p>
    </div>
  </div>
</template>
