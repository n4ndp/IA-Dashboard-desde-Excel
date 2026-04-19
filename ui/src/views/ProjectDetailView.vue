<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiGet } from '../composables/useApi'
import TableView from '../components/TableView.vue'
import FileUpload from '../components/FileUpload.vue'

interface Column {
  id: number
  name: string
  type: string
}

interface Row {
  id: number
  data: Record<string, unknown>
}

interface TableFull {
  id: number
  sheet_name: string
  columns: Column[]
  rows: Row[]
}

interface TableSummary {
  id: number
  nombre_hoja: string
  row_count: number
  column_count: number
}

interface TableLoadState {
  loading: boolean
  error: string
  data: TableFull | null
}

interface ProjectInfo {
  id: number
  nombre_archivo: string
  fecha_creacion: string
  tables: TableSummary[]
}

const route = useRoute()
const router = useRouter()

const userId = computed(() => Number(route.params.userId))
const projectId = computed(() => Number(route.params.projectId))

const project = ref<ProjectInfo | null>(null)
const tableStates = ref<Map<number, TableLoadState>>(new Map())
const projectLoading = ref(false)
const error = ref('')
const uploadingMore = ref(false)

async function fetchProject() {
  projectLoading.value = true
  error.value = ''
  try {
    project.value = await apiGet<ProjectInfo>(
      `/users/${userId.value}/projects/${projectId.value}`
    )
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : 'Error al cargar proyecto'
  } finally {
    projectLoading.value = false
  }
}

async function fetchSingleTable(tableId: number, sheetName: string): Promise<void> {
  tableStates.value.set(tableId, { loading: true, error: '', data: null })

  try {
    const result = await apiGet<TableFull>(
      `/users/${userId.value}/projects/${projectId.value}/tables/${tableId}`
    )
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

  // Fire all table fetches in parallel using allSettled for individual error resilience
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

function goBack() {
  router.push(`/u/${userId.value}/p`)
}

async function onAdditionalUpload(_payload: { userId: number; projectId: number }) {
  uploadingMore.value = true
  try {
    await fetchProject()
    if (project.value) {
      await loadTablesParallel()
    }
  } finally {
    uploadingMore.value = false
  }
}
</script>

<template>
  <main class="mx-auto max-w-6xl px-6 py-8 animate-fade-in">
    <!-- Back button and title -->
    <div class="mb-8">
      <button
        class="mb-4 inline-flex items-center gap-1.5 text-sm text-slate-400 transition-colors hover:text-slate-200"
        @click="goBack"
      >
        <svg
          class="h-4 w-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="2"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18"
          />
        </svg>
        Volver a proyectos
      </button>

      <!-- Project title -->
      <template v-if="projectLoading && !project">
        <div class="h-8 w-48 animate-pulse rounded bg-slate-800"></div>
      </template>
      <template v-else-if="project">
        <h2 class="text-2xl font-bold text-slate-100">
          {{ project.nombre_archivo }}
        </h2>
        <p class="mt-1 text-sm text-slate-400">
          {{ project.tables.length }} tabla{{ project.tables.length !== 1 ? 's' : '' }}
        </p>
      </template>
    </div>

    <!-- Full-page error -->
    <div
      v-if="error"
      class="rounded-xl border border-red-500/20 bg-red-500/5 px-5 py-4 text-sm text-red-400"
    >
      <div class="flex items-center gap-2">
        <svg
          class="h-4 w-4 shrink-0"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="2"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z"
          />
        </svg>
        {{ error }}
      </div>
    </div>

    <!-- Content -->
    <template v-else-if="project">
      <!-- Upload additional Excel -->
      <section class="mb-10">
        <div class="mb-4 flex items-center gap-2">
          <div class="h-px flex-1 bg-slate-800"></div>
          <h3 class="text-xs font-medium uppercase tracking-widest text-slate-500">
            Agregar más datos
          </h3>
          <div class="h-px flex-1 bg-slate-800"></div>
        </div>
        <FileUpload
          :project-id="projectId"
          :user-id="userId"
          @upload-complete="onAdditionalUpload"
        />
      </section>

      <!-- Tables section — render each independently -->
      <section v-if="project.tables.length > 0">
        <div class="mb-5 flex items-center gap-2">
          <div class="h-px flex-1 bg-slate-800"></div>
          <h3 class="text-xs font-medium uppercase tracking-widest text-slate-500">
            Tablas del proyecto
          </h3>
          <div class="h-px flex-1 bg-slate-800"></div>
        </div>
        <div class="space-y-6">
          <template v-for="tableMeta in project.tables" :key="tableMeta.id">
            <!-- Loading state for this individual table -->
            <div
              v-if="getTableState(tableMeta.id).loading"
              class="flex flex-col items-center gap-3 py-8 rounded-xl border border-slate-800/60 bg-midnight-900/60"
            >
              <div
                class="h-8 w-8 animate-spin rounded-full border-2 border-blue-500/30 border-t-blue-400"
              ></div>
              <p class="text-sm text-slate-400">Cargando "{{ tableMeta.nombre_hoja }}"...</p>
            </div>

            <!-- Error state for this table -->
            <div
              v-else-if="getTableState(tableMeta.id).error"
              class="rounded-xl border border-red-500/20 bg-red-500/5 px-5 py-4 text-sm text-red-400"
            >
              <div class="flex items-center gap-2">
                <svg class="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
                </svg>
                {{ getTableState(tableMeta.id).error }}
              </div>
            </div>

            <!-- Loaded table -->
            <TableView
              v-else-if="getTableState(tableMeta.id).data"
              :sheet-name="getTableState(tableMeta.id).data!.sheet_name"
              :columns="getTableState(tableMeta.id).data!.columns"
              :rows="getTableState(tableMeta.id).data!.rows"
            />
          </template>
        </div>
      </section>

      <!-- No tables state -->
      <div
        v-else-if="!projectLoading"
        class="flex flex-col items-center gap-4 py-16"
      >
        <div
          class="flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-800/50 ring-1 ring-slate-700/50"
        >
          <svg
            class="h-8 w-8 text-slate-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m6.75 12H9.75m3 0h3m-3 0v3m0-3v-3m-6.75 9h13.5A2.25 2.25 0 0 0 21 16.5V7.5A2.25 2.25 0 0 0 18.75 5.25H5.25A2.25 2.25 0 0 0 3 7.5v9A2.25 2.25 0 0 0 5.25 18.75Z"
            />
          </svg>
        </div>
        <p class="text-sm text-slate-400">No hay tablas en este proyecto</p>
      </div>
    </template>
  </main>
</template>
