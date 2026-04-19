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
