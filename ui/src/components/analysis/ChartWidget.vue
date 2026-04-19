<script setup lang="ts">
// ── ChartWidget ──
// ECharts wrapper supporting bar, line, and pie chart types.
// Uses tree-shaken imports registered in main.ts.

import { computed } from 'vue'
import type { ChartWidgetData } from '../../types'
import VChart from 'vue-echarts'

const props = defineProps<{
  widget: ChartWidgetData
}>()

const chartOption = computed(() => {
  const { widget } = props
  const baseTextStyle = { color: '#a1a1aa' }
  const baseAxisLine = { lineStyle: { color: '#333' } }
  const baseSplitLine = { lineStyle: { color: '#222' } }

  if (widget.chartType === 'pie') {
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
          radius: ['40%', '70%'],
          center: ['50%', '45%'],
          data: widget.data.labels.map((name, i) => ({
            name,
            value: widget.data.values[i],
          })),
          label: { color: '#a1a1aa', fontSize: 11 },
          emphasis: {
            itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' },
          },
        },
      ],
    }
  }

  // bar or line
  return {
    textStyle: baseTextStyle,
    tooltip: { trigger: 'axis', confine: true },
    grid: { left: 50, right: 16, top: 16, bottom: 32 },
    xAxis: {
      type: 'category',
      data: widget.data.labels,
      axisLine: baseAxisLine,
      axisLabel: { color: '#71717a', fontSize: 11 },
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: baseSplitLine,
      axisLabel: { color: '#71717a', fontSize: 11 },
    },
    series: [
      {
        type: widget.chartType,
        data: widget.data.values,
        smooth: widget.chartType === 'line',
        areaStyle: widget.chartType === 'line' ? { opacity: 0.15 } : undefined,
        itemStyle: {
          color: widget.chartType === 'bar' ? '#6366f1' : undefined,
        },
        lineStyle:
          widget.chartType === 'line'
            ? { color: '#6366f1', width: 2 }
            : undefined,
      },
    ],
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
