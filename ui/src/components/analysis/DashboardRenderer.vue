<script setup lang="ts">
// ── DashboardRenderer ──
// Iterates widget array and dispatches to correct component by type.
// KPIs rendered inline (top row), then charts and insights in grids.

import { computed } from 'vue'
import type { DashboardWidgetMap, KpiWidgetData, ChartWidgetData, InsightWidgetData } from '../../types'
import ChartWidget from './ChartWidget.vue'
import InsightWidget from './InsightWidget.vue'
import { TrendingUp, TrendingDown, Minus, FileText } from 'lucide-vue-next'

const props = defineProps<{
  widgets: DashboardWidgetMap[]
  resumen?: string
}>()

const kpiWidgets = computed(() =>
  props.widgets.filter((w) => w.type === 'kpi') as KpiWidgetData[],
)
const chartWidgets = computed(() =>
  props.widgets.filter((w) => w.type === 'chart') as ChartWidgetData[],
)
const insightWidgets = computed(() =>
  props.widgets.filter((w) => w.type === 'insight') as InsightWidgetData[],
)

function formatValue(value: number, format: string): string {
  switch (format) {
    case 'currency':
      return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS', maximumFractionDigits: 0 }).format(value)
    case 'percent':
      return `${value}%`
    default:
      return new Intl.NumberFormat('es-AR').format(value)
  }
}

function displayKpiValue(kpi: KpiWidgetData): string {
  const formatted = formatValue(kpi.value, kpi.format)
  const prefix = kpi.prefix ?? ''
  const suffix = kpi.suffix ?? ''
  return `${prefix}${formatted}${suffix}`
}

const trendIcon = {
  up: TrendingUp,
  down: TrendingDown,
  neutral: Minus,
}

const trendColor = {
  up: 'text-success',
  down: 'text-danger',
  neutral: 'text-text-muted',
}
</script>

<template>
  <div class="animate-fade-in">
    <!-- Resumen ejecutivo banner -->
    <div
      v-if="resumen"
      class="mb-6 rounded-xl border border-border bg-surface-raised p-4"
    >
      <div class="mb-2 flex items-center gap-2">
        <FileText class="h-4 w-4 text-primary" />
        <h3 class="text-sm font-semibold text-text-primary">Resumen Ejecutivo</h3>
      </div>
      <div class="text-sm leading-relaxed text-text-secondary whitespace-pre-line">{{ resumen }}</div>
    </div>

    <!-- KPI row -->
    <div v-if="kpiWidgets.length > 0" class="mb-6 grid grid-cols-2 gap-4">
      <div
        v-for="kpi in kpiWidgets"
        :key="kpi.id"
        class="bg-surface-raised border border-border rounded-lg p-5"
      >
        <p class="mb-1 text-xs font-medium uppercase tracking-wider text-text-muted">
          {{ kpi.label }}
        </p>
        <div class="flex items-end gap-3">
          <span class="text-2xl font-bold text-text-primary">
            {{ displayKpiValue(kpi) }}
          </span>
          <div v-if="kpi.trend && kpi.trend !== 'neutral'" class="flex items-center gap-1 pb-1">
            <component
              :is="trendIcon[kpi.trend]"
              class="h-4 w-4"
              :class="trendColor[kpi.trend]"
            />
            <span v-if="kpi.trendValue" class="text-xs font-medium" :class="trendColor[kpi.trend]">
              {{ kpi.trendValue }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts grid -->
    <div v-if="chartWidgets.length > 0" class="mb-6 grid grid-cols-2 gap-4">
      <ChartWidget
        v-for="chart in chartWidgets"
        :key="chart.id"
        :widget="chart"
      />
    </div>

    <!-- Insights grid -->
    <div v-if="insightWidgets.length > 0" class="grid grid-cols-2 gap-4">
      <InsightWidget
        v-for="insight in insightWidgets"
        :key="insight.id"
        :widget="insight"
      />
    </div>
  </div>
</template>
