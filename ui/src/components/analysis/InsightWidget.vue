<script setup lang="ts">
// ── InsightWidget ──
// Styled text insight card with severity-based accent and icon.

import type { InsightWidgetData } from '../../types'
import { Info, CheckCircle, AlertTriangle } from 'lucide-vue-next'

const props = defineProps<{
  widget: InsightWidgetData
}>()

const severityConfig: Record<string, { icon: typeof Info; accent: string; iconColor: string }> = {
  info: { icon: Info, accent: 'border-l-sky-400', iconColor: 'text-sky-400' },
  success: { icon: CheckCircle, accent: 'border-l-success', iconColor: 'text-success' },
  warning: { icon: AlertTriangle, accent: 'border-l-warning', iconColor: 'text-warning' },
}

const config = severityConfig[props.widget.severity] ?? severityConfig.info
</script>

<template>
  <div
    class="bg-surface-raised border border-border border-l-4 rounded-lg p-4 transition-colors"
    :class="config.accent"
  >
    <div class="mb-2 flex items-center gap-2">
      <component :is="config.icon" class="h-4 w-4 shrink-0" :class="config.iconColor" />
      <h4 class="text-sm font-medium text-text-primary">{{ widget.title }}</h4>
    </div>
    <p class="text-sm leading-relaxed text-text-secondary pl-6">
      {{ widget.text }}
    </p>
  </div>
</template>
