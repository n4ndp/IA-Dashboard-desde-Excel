<script setup lang="ts">
// ── DashboardView ──
// Dashboard: tab system (Datos | Análisis), title + table count, upload section, tables with collapse/expand.
// Uses useToast for error notifications and useTableCollapse for table visibility.

import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProject, getTable } from '../services/endpoints'
import type { ProjectDetail, SingleTableResponse, TableSummaryOut } from '../types'
import TableView from '../components/TableView.vue'
import AppFileUpload from '../components/base/AppFileUpload.vue'
import AppButton from '../components/base/AppButton.vue'
import AnalisisTab from '../components/analysis/AnalisisTab.vue'
import { useSkeleton } from '../composables/useSkeleton'
import { useToast } from '../composables/useToast'
import { useTableCollapse } from '../composables/useTableCollapse'
import { AlertCircle, ArrowLeft } from 'lucide-vue-next'

const activeTab = ref<'datos' | 'analisis'>('datos')

interface TableLoadState {
  loading: boolean
  error: string
  data: SingleTableResponse | null
}

const route = useRoute()
const router = useRouter()
const toast = useToast()
const { expandedTableIds, expandAll, collapseAll, isExpanded, toggle } = useTableCollapse()

const userId = computed(() => Number(route.params.userId))
const projectId = computed(() => Number(route.params.projectId))

const project = ref<ProjectDetail | null>(null)
const tableStates = ref<Map<number, TableLoadState>>(new Map())
const projectLoading = ref(false)
const error = ref('')

const { tableRowSkeletons } = useSkeleton()

async function fetchProject() {
  projectLoading.value = true
  error.value = ''
  try {
    project.value = await getProject(userId.value, projectId.value)
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : 'Error al cargar proyecto'
    error.value = msg
    toast.show(msg, 'error')
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
    toast.show(msg, 'error')
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
    // Bug 1 fix: clear stale IDs from previous projects before expanding
    collapseAll()
    expandAll(project.value.tables.map(t => t.id))
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
  toast.show('Datos agregados correctamente', 'success')
  await fetchProject()
  if (project.value) {
    // Bug 2 fix: expand newly added tables so user sees them
    expandAll(project.value.tables.map(t => t.id))
    await loadTablesParallel()
  }
}

// Bug 3 fix: check only current project IDs, not stale ones from other projects
function allCurrentTablesExpanded(): boolean {
  if (!project.value) return false
  const currentIds = project.value.tables.map(t => t.id)
  return currentIds.every(id => expandedTableIds.value.has(id))
}

const collapseLabel = computed(() => {
  return allCurrentTablesExpanded() ? 'Compactar todo' : 'Expandir todo'
})

function handleCollapseToggle() {
  if (allCurrentTablesExpanded()) {
    collapseAll()
  } else if (project.value) {
    expandAll(project.value.tables.map(t => t.id))
  }
}
</script>

<template>
  <div class="min-h-screen bg-surface-base">
    <!-- Main content -->
    <div class="overflow-auto">
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
          <!-- Project title + table count badge -->
          <div class="mb-6 flex items-center gap-3">
            <h2 class="text-2xl font-bold text-text-primary">
              {{ project.nombre_archivo }}
            </h2>
            <span class="bg-surface-overlay px-2.5 py-0.5 text-xs font-medium text-text-secondary">
              {{ project.tables.length }} tabla{{ project.tables.length !== 1 ? 's' : '' }}
            </span>
          </div>

          <!-- Tab system -->
          <div class="mb-6 flex border-b border-border">
            <button
              class="px-4 py-2.5 text-sm font-medium transition-colors"
              :class="
                activeTab === 'datos'
                  ? 'border-b-2 border-primary text-text-primary'
                  : 'text-text-muted hover:text-text-secondary'
              "
              @click="activeTab = 'datos'"
            >
              Datos
            </button>
            <button
              class="px-4 py-2.5 text-sm font-medium transition-colors"
              :class="
                activeTab === 'analisis'
                  ? 'border-b-2 border-primary text-text-primary'
                  : 'text-text-muted hover:text-text-secondary'
              "
              @click="activeTab = 'analisis'"
            >
              Análisis
            </button>
          </div>

          <!-- Tab: Datos (existing content) -->
          <template v-if="activeTab === 'datos'">
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

          <!-- Tables section -->
          <section id="tables" class="mb-8">
            <div class="mb-4 flex items-center gap-2">
              <div class="h-px flex-1 bg-border" />
              <h3 class="text-xs font-medium uppercase tracking-widest text-text-muted">
                Tablas del proyecto
              </h3>
              <div class="h-px flex-1 bg-border" />
            </div>
            <div v-if="project.tables.length > 0" class="mb-4 flex justify-end">
              <AppButton
                variant="secondary"
                size="sm"
                @click="handleCollapseToggle"
              >
                {{ collapseLabel }}
              </AppButton>
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
                  :collapsed="!isExpanded(tableMeta.id)"
                  @toggle="toggle(tableMeta.id)"
                />
              </template>
            </div>

            <div v-else class="flex flex-col items-center gap-4 py-16">
              <div class="flex h-16 w-16 items-center justify-center rounded-2xl bg-surface-overlay ring-1 ring-border">
                <AlertCircle class="h-8 w-8 text-text-muted" />
              </div>
              <p class="text-sm text-text-muted">No hay tablas en este proyecto</p>
            </div>
          </section>
          </template>

          <!-- Tab: Análisis -->
          <AnalisisTab
            v-if="activeTab === 'analisis'"
            :user-id="userId"
            :project-id="projectId"
            :existing-dashboard="project?.dashboard_config ?? null"
          />
        </template>
      </main>
    </div>
  </div>
</template>
