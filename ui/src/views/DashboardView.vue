<script setup lang="ts">
// ── DashboardView ──
// Sidebar + content layout. Fetches project, parallel table loading.
// Metrics cards, TableViews, ChartCards, InsightCard, FileUpload.

import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProject, getTable } from '../services/endpoints'
import type { ProjectDetail, SingleTableResponse, TableSummaryOut } from '../types'
import TableView from '../components/TableView.vue'
import ChartCard from '../components/ChartCard.vue'
import InsightCard from '../components/InsightCard.vue'
import AppFileUpload from '../components/base/AppFileUpload.vue'
import AppSidebar from '../components/layout/AppSidebar.vue'
import AppButton from '../components/base/AppButton.vue'
import { useSkeleton } from '../composables/useSkeleton'
import { AlertCircle, ArrowLeft, FileSpreadsheet, Rows3, Columns3 } from 'lucide-vue-next'

interface TableLoadState {
  loading: boolean
  error: string
  data: SingleTableResponse | null
}

const route = useRoute()
const router = useRouter()

const userId = computed(() => Number(route.params.userId))
const projectId = computed(() => Number(route.params.projectId))

const project = ref<ProjectDetail | null>(null)
const tableStates = ref<Map<number, TableLoadState>>(new Map())
const projectLoading = ref(false)
const error = ref('')
const sidebarCollapsed = ref(false)

const { tableRowSkeletons } = useSkeleton()

async function fetchProject() {
  projectLoading.value = true
  error.value = ''
  try {
    project.value = await getProject(userId.value, projectId.value)
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : 'Error al cargar proyecto'
  } finally {
    projectLoading.value = false
  }
}

async function fetchSingleTable(tableId: number, sheetName: string): Promise<void> {
  tableStates.value.set(tableId, { loading: true, error: '', data: null })
  try {
    const result = await getTable(userId.value, projectId.value, tableId)
    tableStates.value.set(tableId, { loading: false, error: '', data: result })
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : `Error al cargar tabla "${sheetName}"`
    tableStates.value.set(tableId, { loading: false, error: msg, data: null })
  }
}

async function loadTablesParallel() {
  if (!project.value) return
  const tables = project.value.tables
  if (tables.length === 0) return

  const promises = tables.map((t) => fetchSingleTable(t.id, t.nombre_hoja))
  await Promise.allSettled(promises)
}

onMounted(async () => {
  await fetchProject()
  if (project.value) {
    await loadTablesParallel()
  }
})

function getTableState(tableId: number): TableLoadState {
  return tableStates.value.get(tableId) ?? { loading: false, error: 'No cargada', data: null }
}

function retryTable(table: TableSummaryOut) {
  fetchSingleTable(table.id, table.nombre_hoja)
}

function goBack() {
  router.push(`/u/${userId.value}/p`)
}

async function onAdditionalUpload(_payload: { userId: number; projectId: number }) {
  await fetchProject()
  if (project.value) {
    await loadTablesParallel()
  }
}

// Computed metrics
const totalRows = computed(() => {
  if (!project.value) return 0
  return project.value.tables.reduce((sum, t) => sum + t.row_count, 0)
})

const totalColumns = computed(() => {
  if (!project.value) return 0
  return project.value.tables.reduce((sum, t) => sum + t.column_count, 0)
})
</script>

<template>
  <div class="flex min-h-screen bg-surface-base">
    <!-- Sidebar -->
    <AppSidebar
      v-if="project"
      :project-name="project.nombre_archivo"
      v-model:collapsed="sidebarCollapsed"
    />

    <!-- Main content -->
    <div class="flex-1 overflow-auto">
      <main class="mx-auto max-w-6xl px-6 py-8 animate-fade-in">
        <!-- Back button -->
        <button
          class="mb-4 inline-flex items-center gap-1.5 text-sm text-text-muted transition-colors hover:text-text-primary"
          @click="goBack"
        >
          <ArrowLeft class="h-4 w-4" />
          Volver a proyectos
        </button>

        <!-- Full-page error -->
        <div
          v-if="error"
          class="rounded-xl border border-danger/20 bg-danger/5 px-5 py-4 text-sm text-danger"
        >
          <div class="flex items-center gap-2">
            <AlertCircle class="h-4 w-4 shrink-0" />
            {{ error }}
          </div>
        </div>

        <template v-else-if="project">
          <!-- Project title -->
          <div class="mb-6">
            <h2 class="text-2xl font-bold text-text-primary">
              {{ project.nombre_archivo }}
            </h2>
            <p class="mt-1 text-sm text-text-muted">
              {{ project.tables.length }} tabla{{ project.tables.length !== 1 ? 's' : '' }}
            </p>
          </div>

          <!-- Metrics cards -->
          <div class="mb-8 grid gap-4 sm:grid-cols-3">
            <div class="card p-4">
              <div class="flex items-center gap-3">
                <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
                  <FileSpreadsheet class="h-4 w-4 text-primary" />
                </div>
                <div>
                  <p class="text-2xl font-bold text-text-primary">{{ project.tables.length }}</p>
                  <p class="text-xs text-text-muted">Tablas</p>
                </div>
              </div>
            </div>
            <div class="card p-4">
              <div class="flex items-center gap-3">
                <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-500/10">
                  <Rows3 class="h-4 w-4 text-emerald-400" />
                </div>
                <div>
                  <p class="text-2xl font-bold text-text-primary">{{ totalRows }}</p>
                  <p class="text-xs text-text-muted">Filas</p>
                </div>
              </div>
            </div>
            <div class="card p-4">
              <div class="flex items-center gap-3">
                <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-sky-500/10">
                  <Columns3 class="h-4 w-4 text-sky-400" />
                </div>
                <div>
                  <p class="text-2xl font-bold text-text-primary">{{ totalColumns }}</p>
                  <p class="text-xs text-text-muted">Columnas</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Charts placeholder -->
          <section class="mb-8">
            <div class="mb-4 flex items-center gap-2">
              <div class="h-px flex-1 bg-border" />
              <h3 class="text-xs font-medium uppercase tracking-widest text-text-muted">Gráficos</h3>
              <div class="h-px flex-1 bg-border" />
            </div>
            <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <ChartCard title="Distribución de datos" />
              <ChartCard title="Tendencias" />
              <ChartCard title="Resumen estadístico" />
            </div>
          </section>

          <!-- Tables section -->
          <section id="tables" class="mb-8">
            <div class="mb-4 flex items-center gap-2">
              <div class="h-px flex-1 bg-border" />
              <h3 class="text-xs font-medium uppercase tracking-widest text-text-muted">
                Tablas del proyecto
              </h3>
              <div class="h-px flex-1 bg-border" />
            </div>

            <div v-if="project.tables.length > 0" class="space-y-6">
              <template v-for="tableMeta in project.tables" :key="tableMeta.id">
                <!-- Loading skeleton -->
                <div
                  v-if="getTableState(tableMeta.id).loading"
                  class="overflow-hidden rounded-xl border border-border"
                >
                  <div class="flex items-center justify-between px-5 py-4">
                    <div class="flex items-center gap-3">
                      <div class="skeleton h-8 w-8 rounded-lg" />
                      <div class="space-y-2">
                        <div class="skeleton h-4 w-32" />
                        <div class="skeleton h-3 w-24" />
                      </div>
                    </div>
                  </div>
                  <div class="border-t border-border px-5 py-3 space-y-2">
                    <div
                      v-for="row in tableRowSkeletons(tableMeta.column_count, 8)"
                      :key="row.id"
                      class="flex gap-3"
                    >
                      <div
                        v-for="cell in row.cells"
                        :key="cell.id"
                        class="skeleton h-4"
                        :style="{ width: cell.width }"
                      />
                    </div>
                  </div>
                </div>

                <!-- Error per table -->
                <div
                  v-else-if="getTableState(tableMeta.id).error"
                  class="rounded-xl border border-danger/20 bg-danger/5 px-5 py-4"
                >
                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-2 text-sm text-danger">
                      <AlertCircle class="h-4 w-4 shrink-0" />
                      {{ getTableState(tableMeta.id).error }}
                    </div>
                    <AppButton variant="secondary" size="sm" @click="retryTable(tableMeta)">
                      Reintentar
                    </AppButton>
                  </div>
                </div>

                <!-- Loaded table -->
                <TableView
                  v-else-if="getTableState(tableMeta.id).data"
                  :table="getTableState(tableMeta.id).data!"
                />
              </template>
            </div>

            <div v-else class="flex flex-col items-center gap-4 py-16">
              <div class="flex h-16 w-16 items-center justify-center rounded-2xl bg-surface-overlay ring-1 ring-border">
                <FileSpreadsheet class="h-8 w-8 text-text-muted" />
              </div>
              <p class="text-sm text-text-muted">No hay tablas en este proyecto</p>
            </div>
          </section>

          <!-- AI Insights -->
          <section id="insights" class="mb-8">
            <InsightCard title="AI Insights" :insights="[]" />
          </section>

          <!-- Upload additional data -->
          <section class="mb-8">
            <div class="mb-4 flex items-center gap-2">
              <div class="h-px flex-1 bg-border" />
              <h3 class="text-xs font-medium uppercase tracking-widest text-text-muted">
                Agregar más datos
              </h3>
              <div class="h-px flex-1 bg-border" />
            </div>
            <AppFileUpload
              mode="standalone"
              :project-id="projectId"
              @upload-complete="onAdditionalUpload"
            />
          </section>
        </template>
      </main>
    </div>
  </div>
</template>
