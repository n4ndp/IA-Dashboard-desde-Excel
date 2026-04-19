// ── mockDashboard ──
// Hardcoded 7-widget mock payload for Fase 1 analysis tab.
// Replaced by AI-generated data in Fase 2.

import type { DashboardConfig, DashboardWidgetMap } from '../types'

const widgets: DashboardWidgetMap[] = [
  // 2 KPIs
  {
    id: 'kpi-1',
    type: 'kpi',
    title: 'Total Ventas',
    value: 150000,
    format: 'currency',
    trend: 'up',
    trendValue: '+12.5%',
  },
  {
    id: 'kpi-2',
    type: 'kpi',
    title: 'Usuarios Activos',
    value: 2340,
    format: 'number',
    trend: 'down',
    trendValue: '-3.2%',
  },

  // 1 bar chart: Ventas por mes
  {
    id: 'chart-1',
    type: 'chart',
    title: 'Ventas por mes',
    chartType: 'bar',
    data: {
      labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
      values: [18500, 22300, 19800, 25400, 28100, 31200],
    },
  },

  // 1 line chart: Tendencia de ingresos
  {
    id: 'chart-2',
    type: 'chart',
    title: 'Tendencia de ingresos',
    chartType: 'line',
    data: {
      labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
      values: [42000, 45000, 43500, 48200, 51000, 55000],
    },
  },

  // 1 pie chart: Distribución por categoría
  {
    id: 'chart-3',
    type: 'chart',
    title: 'Distribución por categoría',
    chartType: 'pie',
    data: {
      labels: ['Electrónica', 'Ropa', 'Hogar', 'Alimentos'],
      values: [35, 25, 22, 18],
    },
  },

  // 2 insights
  {
    id: 'insight-1',
    type: 'insight',
    title: 'Tendencia positiva',
    text: 'Las ventas muestran un crecimiento sostenido del 12.5% en el último trimestre, impulsado principalmente por la categoría de Electrónica.',
    severity: 'success',
  },
  {
    id: 'insight-2',
    type: 'insight',
    title: 'Oportunidad de mejora',
    text: 'La categoría de Alimentos representa solo el 18% del total. Considerar estrategias de promoción para aumentar su participación en el portafolio.',
    severity: 'info',
  },
]

export const mockDashboard: DashboardConfig = {
  widgets,
  generatedAt: new Date().toISOString(),
}
