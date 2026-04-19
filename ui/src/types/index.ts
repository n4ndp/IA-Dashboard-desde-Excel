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

export type DashboardState = 'empty' | 'loading' | 'generated'
export type WidgetType = 'kpi' | 'chart' | 'insight'
export type ChartType = 'bar' | 'line' | 'pie'
export type ValueFormat = 'currency' | 'number' | 'percent'
export type TrendDirection = 'up' | 'down' | 'neutral'
export type InsightSeverity = 'info' | 'success' | 'warning'

export interface DashboardWidget {
  id: string
  type: WidgetType
  title: string
}

export interface ChartWidgetData extends DashboardWidget {
  type: 'chart'
  chartType: ChartType
  data: {
    labels: string[]
    values: number[]
  }
}

export interface KpiWidgetData extends DashboardWidget {
  type: 'kpi'
  value: number
  format: ValueFormat
  trend: TrendDirection
  trendValue?: string
}

export interface InsightWidgetData extends DashboardWidget {
  type: 'insight'
  text: string
  severity: InsightSeverity
}

export type DashboardWidgetMap = ChartWidgetData | KpiWidgetData | InsightWidgetData

export interface DashboardConfig {
  widgets: DashboardWidgetMap[]
  generatedAt?: string
}
