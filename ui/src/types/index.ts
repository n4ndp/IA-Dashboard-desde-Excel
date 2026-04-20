// ── Shared API Types ──
// Single source of truth for all API response interfaces.

export interface User {
  id: number
  nombre: string
}

export interface ProjectSummary {
  id: number
  nombre_archivo: string
  fecha_creacion: string
  tabla_count: number
}

export interface TableSummaryOut {
  id: number
  nombre_hoja: string
  row_count: number
  column_count: number
}

export interface ProjectDetail {
  id: number
  nombre_archivo: string
  fecha_creacion: string
  tables: TableSummaryOut[]
  dashboard_config: DashboardConfig | null
}

export interface ColumnOut {
  id: number
  name: string
  type: string
}

export interface RowOut {
  id: number
  data: Record<string, unknown>
}

export interface SingleTableResponse {
  id: number
  sheet_name: string
  columns: ColumnOut[]
  rows: RowOut[]
}

export interface CreateProjectResponse {
  user_id: number
  project_id: number
  tables: TableSummaryOut[]
}

export interface UploadResponse {
  user_id: number
  project_id: number
  tables: TableSummaryOut[]
}

// ── Dashboard / Analysis Types ──

export type DashboardState = 'empty' | 'loading' | 'error' | 'generated'
export type WidgetType = 'kpi' | 'chart' | 'insight'
export type ChartType = 'bar' | 'line' | 'pie' | 'scatter'
export type ChartVariant = 'stacked' | 'grouped' | 'horizontal' | 'multi' | 'area' | 'doughnut' | 'histogram'
export type ValueFormat = 'currency' | 'number' | 'percent'
export type TrendDirection = 'up' | 'down' | 'neutral'
export type InsightSeverity = 'positive' | 'negative' | 'warning' | 'info'

// ── Chart data types ──

export interface ChartDataItem {
  name: string
  value: number
  x?: number
  y?: number
}

export interface SeriesData {
  name: string
  data: ChartDataItem[]
}

// ── Widget types (each independently typed) ──

export interface KpiWidgetData {
  id: string
  type: 'kpi'
  label: string
  value: number
  format: ValueFormat
  prefix?: string
  suffix?: string
  trend?: TrendDirection
  trendValue?: string
}

export interface ChartWidgetData {
  id: string
  type: 'chart'
  chartType: ChartType
  variant?: ChartVariant
  title: string
  x?: string
  y?: string
  x_label?: string
  y_label?: string
  data?: ChartDataItem[]
  series?: SeriesData[]
  orientation?: string
  areaStyle?: Record<string, unknown>
  colorPalette?: string[]
}

export interface InsightWidgetData {
  id: string
  type: 'insight'
  emoji: string
  content: string
  severity: InsightSeverity
}

export type DashboardWidgetMap = ChartWidgetData | KpiWidgetData | InsightWidgetData

export interface DashboardConfig {
  widgets: DashboardWidgetMap[]
  generated_at?: string
  resumen_ejecutivo?: string
}
