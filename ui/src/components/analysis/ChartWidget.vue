<script setup lang="ts">
// ── ChartWidget ──
// ECharts wrapper supporting bar, line, pie, and scatter chart types.
// Supports 7 variants: stacked, grouped, horizontal, multi, area, doughnut, histogram.
// Handles colorPalette from widget data (falls back to SERIES_COLORS).
// Handles both simple data[] and series[] formats.

import { computed } from 'vue'
import type { ChartWidgetData, ChartDataItem, SeriesData } from '../../types'
import VChart from 'vue-echarts'

const props = defineProps<{
  widget: ChartWidgetData
}>()

// Color palette for multi-series charts (fallback when widget has no colorPalette)
const SERIES_COLORS = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#06b6d4', '#a855f7']

/** Resolve effective color array: widget.colorPalette or fallback SERIES_COLORS */
function resolveColors(): string[] {
  return props.widget.colorPalette?.length ? props.widget.colorPalette : SERIES_COLORS
}

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
  const colors = resolveColors()
  const baseTextStyle = { color: '#a1a1aa' }
  const baseAxisLine = { lineStyle: { color: '#333' } }
  const baseSplitLine = { lineStyle: { color: '#222' } }
  const variant = widget.variant

  // ── Pie / Doughnut ──
  if (widget.chartType === 'pie') {
    const pieData = widget.data ? toEchartsItems(widget.data) : []
    const isDoughnut = variant === 'doughnut'

    return {
      color: colors,
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

  // ── Scatter ──
  if (widget.chartType === 'scatter') {
    const scatterData = (widget.data || [])
      .filter((item) => item.x != null && item.y != null)
      .map((item) => [item.x, item.y])

    return {
      color: colors,
      textStyle: baseTextStyle,
      tooltip: {
        trigger: 'item',
        confine: true,
        formatter: (params: { data: number[] }) => {
          return `${widget.x_label || 'X'}: ${params.data[0]}<br/>${widget.y_label || 'Y'}: ${params.data[1]}`
        },
      },
      grid: { left: 50, right: 16, top: 16, bottom: 32 },
      xAxis: {
        type: 'value' as const,
        axisLine: { show: false },
        splitLine: baseSplitLine,
        axisLabel: { color: '#71717a', fontSize: 11 },
        name: widget.x_label || '',
        nameTextStyle: { color: '#71717a', fontSize: 11 },
      },
      yAxis: {
        type: 'value' as const,
        axisLine: { show: false },
        splitLine: baseSplitLine,
        axisLabel: { color: '#71717a', fontSize: 11 },
        name: widget.y_label || '',
        nameTextStyle: { color: '#71717a', fontSize: 11 },
      },
      series: [
        {
          type: 'scatter',
          data: scatterData,
          symbolSize: 8,
        },
      ],
    }
  }

  // ── Histogram (bar chart with range labels) ──
  if (variant === 'histogram') {
    const categories = getCategories()
    const dataValues = widget.data ? widget.data.map((item) => item.value) : []

    return {
      color: colors,
      textStyle: baseTextStyle,
      tooltip: { trigger: 'axis', confine: true },
      grid: { left: 50, right: 16, top: 16, bottom: 32 },
      xAxis: {
        type: 'category' as const,
        data: categories,
        axisLine: baseAxisLine,
        axisLabel: { color: '#71717a', fontSize: 10, rotate: 20 },
        name: widget.x_label || '',
        nameTextStyle: { color: '#71717a', fontSize: 11 },
      },
      yAxis: {
        type: 'value' as const,
        axisLine: { show: false },
        splitLine: baseSplitLine,
        axisLabel: { color: '#71717a', fontSize: 11 },
        name: widget.y_label || 'Count',
        nameTextStyle: { color: '#71717a', fontSize: 11 },
      },
      series: [
        {
          type: 'bar',
          data: dataValues,
          barWidth: '90%',
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
        itemStyle: { color: colors[idx % colors.length] },
      }

      if (widget.chartType === 'line') {
        seriesEntry.lineStyle = {
          color: colors[idx % colors.length],
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
      seriesEntry.itemStyle = { color: colors[0] }
    }
    if (widget.chartType === 'line') {
      seriesEntry.lineStyle = { color: colors[0], width: 2 }
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
    color: colors,
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
