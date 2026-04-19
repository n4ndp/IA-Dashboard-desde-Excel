<script setup lang="ts">
// ── ChartWidget ──
// ECharts wrapper supporting bar, line, and pie chart types.
// Supports 6 variants: stacked, grouped, horizontal, multi, area, doughnut.
// Handles both simple data[] and series[] formats.

import { computed } from 'vue'
import type { ChartWidgetData, ChartDataItem, SeriesData } from '../../types'
import VChart from 'vue-echarts'

const props = defineProps<{
  widget: ChartWidgetData
}>()

// Color palette for multi-series charts
const SERIES_COLORS = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#06b6d4', '#a855f7']

/** Convert ChartDataItem[] to ECharts data format */
function toEchartsItems(data: ChartDataItem[]) {
  return data.map((item) => ({ name: item.name, value: item.value }))
}

/** Extract category labels from data or series */
function getCategories(): string[] {
  const { widget } = props
  if (widget.series && widget.series.length > 0) {
    // Use first series for category labels
    return widget.series[0].data.map((item) => item.name)
  }
  if (widget.data) {
    return widget.data.map((item) => item.name)
  }
  return []
}

const chartOption = computed(() => {
  const { widget } = props
  const baseTextStyle = { color: '#a1a1aa' }
  const baseAxisLine = { lineStyle: { color: '#333' } }
  const baseSplitLine = { lineStyle: { color: '#222' } }
  const variant = widget.variant

  // ── Pie / Doughnut ──
  if (widget.chartType === 'pie') {
    const pieData = widget.data ? toEchartsItems(widget.data) : []
    const isDoughnut = variant === 'doughnut'

    return {
      textStyle: baseTextStyle,
      tooltip: { trigger: 'item', confine: true },
      legend: {
        bottom: 0,
        textStyle: { color: '#a1a1aa', fontSize: 11 },
      },
      series: [
        {
          type: 'pie',
          radius: isDoughnut ? ['40%', '70%'] : ['0%', '70%'],
          center: ['50%', '45%'],
          data: pieData,
          label: { color: '#a1a1aa', fontSize: 11 },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)',
            },
          },
        },
      ],
    }
  }

  // ── Bar / Line with variants ──
  const categories = getCategories()
  const isHorizontal = variant === 'horizontal' || widget.orientation === 'horizontal'
  const isStacked = variant === 'stacked'
  const isArea = variant === 'area'

  // Build series array
  let seriesList: Array<Record<string, unknown>> = []

  if (widget.series && widget.series.length > 0) {
    // Multi-series (stacked, grouped, multi-line)
    widget.series.forEach((s: SeriesData, idx: number) => {
      const seriesEntry: Record<string, unknown> = {
        name: s.name,
        type: widget.chartType,
        data: s.data.map((item) => item.value),
        smooth: widget.chartType === 'line',
        itemStyle: { color: SERIES_COLORS[idx % SERIES_COLORS.length] },
      }

      if (widget.chartType === 'line') {
        seriesEntry.lineStyle = {
          color: SERIES_COLORS[idx % SERIES_COLORS.length],
          width: 2,
        }
        if (isArea) {
          seriesEntry.areaStyle = { opacity: 0.15 }
        }
      }

      if (isStacked && widget.chartType === 'bar') {
        seriesEntry.stack = 'total'
      }

      seriesList.push(seriesEntry)
    })
  } else if (widget.data) {
    // Single series from data array
    const seriesEntry: Record<string, unknown> = {
      type: widget.chartType,
      data: widget.data.map((item) => item.value),
      smooth: widget.chartType === 'line',
    }

    if (widget.chartType === 'bar') {
      seriesEntry.itemStyle = { color: '#6366f1' }
    }
    if (widget.chartType === 'line') {
      seriesEntry.lineStyle = { color: '#6366f1', width: 2 }
      if (isArea) {
        seriesEntry.areaStyle = { opacity: 0.15 }
      }
    }

    seriesList.push(seriesEntry)
  }

  // Build axis config
  const categoryAxis = {
    type: 'category' as const,
    data: categories,
    axisLine: baseAxisLine,
    axisLabel: { color: '#71717a', fontSize: 11 },
  }
  const valueAxis = {
    type: 'value' as const,
    axisLine: { show: false },
    splitLine: baseSplitLine,
    axisLabel: { color: '#71717a', fontSize: 11 },
  }

  return {
    textStyle: baseTextStyle,
    tooltip: { trigger: 'axis', confine: true },
    legend: seriesList.length > 1 ? {
      bottom: 0,
      textStyle: { color: '#a1a1aa', fontSize: 11 },
    } : undefined,
    grid: { left: 50, right: 16, top: 16, bottom: seriesList.length > 1 ? 40 : 32 },
    xAxis: isHorizontal ? valueAxis : categoryAxis,
    yAxis: isHorizontal ? categoryAxis : valueAxis,
    series: seriesList,
  }
})
</script>

<template>
  <div class="bg-surface-raised border border-border rounded-lg p-4">
    <h4 class="mb-3 text-sm font-medium text-text-primary">{{ widget.title }}</h4>
    <v-chart
      :option="chartOption"
      autoresize
      style="height: 300px; width: 100%"
    />
  </div>
</template>
