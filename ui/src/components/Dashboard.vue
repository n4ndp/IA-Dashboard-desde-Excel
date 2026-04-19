<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUser } from '../composables/useUser'
import { apiGet } from '../composables/useApi'
import FileUpload from './FileUpload.vue'
import TableView from './TableView.vue'

interface Column {
  id: number
  name: string
  type: string
}

interface Row {
  id: number
  data: Record<string, unknown>
}

interface TableDetail {
  id: number
  sheet_name: string
  columns: Column[]
  rows: Row[]
}

const { name, userId, setUserId } = useUser()
const tables = ref<TableDetail[]>([])
const loading = ref(false)
const error = ref('')

async function fetchTables() {
  if (!userId.value) return
  loading.value = true
  error.value = ''
  try {
    const result = await apiGet<{ tables: TableDetail[] }>(
      `/users/${userId.value}/tables`
    )
    tables.value = result.tables
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : 'Error al cargar tablas'
  } finally {
    loading.value = false
  }
}

onMounted(fetchTables)

function onUploadComplete(payload: { userId: number; projectId: number }) {
  setUserId(payload.userId)
  setTimeout(fetchTables, 0)
}
</script>

<template>
  <div class="min-h-screen bg-midnight-950">
    <!-- ── Header ── -->
    <header class="relative border-b border-slate-800/60 bg-midnight-900/80">
      <div
        class="mx-auto flex max-w-6xl items-center justify-between px-6 py-4"
      >
        <div class="flex items-center gap-3">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-500/10 ring-1 ring-blue-500/20"
          >
            <svg
              class="h-4 w-4 text-blue-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="2"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M3.75 6A2.25 2.25 0 0 1 6 3.75h2.25A2.25 2.25 0 0 1 10.5 6v2.25a2.25 2.25 0 0 1-2.25 2.25H6a2.25 2.25 0 0 1-2.25-2.25V6ZM3.75 15.75A2.25 2.25 0 0 1 6 13.5h2.25a2.25 2.25 0 0 1 2.25 2.25V18a2.25 2.25 0 0 1-2.25 2.25H6A2.25 2.25 0 0 1 3.75 18v-2.25ZM13.5 6a2.25 2.25 0 0 1 2.25-2.25H18A2.25 2.25 0 0 1 20.25 6v2.25A2.25 2.25 0 0 1 18 10.5h-2.25a2.25 2.25 0 0 1-2.25-2.25V6ZM13.5 15.75a2.25 2.25 0 0 1 2.25-2.25H18a2.25 2.25 0 0 1 2.25 2.25V18A2.25 2.25 0 0 1 18 20.25h-2.25A2.25 2.25 0 0 1 13.5 18v-2.25Z"
              />
            </svg>
          </div>
          <h1
            class="text-lg font-bold tracking-tight text-slate-100"
          >
            Excel Dashboard
          </h1>
        </div>
        <div class="flex items-center gap-2">
          <div
            class="flex h-7 w-7 items-center justify-center rounded-full bg-blue-500/10 text-xs font-semibold text-blue-400"
          >
            {{ name?.charAt(0)?.toUpperCase() }}
          </div>
          <span class="text-sm text-slate-400">{{ name }}</span>
        </div>
      </div>
      <!-- Signature gradient line -->
      <div class="accent-bar"></div>
    </header>

    <!-- ── Main content ── -->
    <main class="mx-auto max-w-6xl px-6 py-8 animate-fade-in">
      <!-- Upload section -->
      <section class="mb-10">
        <div class="mb-4 flex items-center gap-2">
          <div class="h-px flex-1 bg-slate-800"></div>
          <h2 class="text-xs font-medium uppercase tracking-widest text-slate-500">
            Cargar archivo
          </h2>
          <div class="h-px flex-1 bg-slate-800"></div>
        </div>
        <FileUpload @upload-complete="onUploadComplete" />
      </section>

      <!-- Loading state -->
      <div v-if="loading" class="flex flex-col items-center gap-3 py-16">
        <div
          class="h-8 w-8 animate-spin rounded-full border-2 border-blue-500/30 border-t-blue-400"
        ></div>
        <p class="text-sm text-slate-400">Cargando tablas...</p>
      </div>

      <!-- Error state -->
      <div
        v-else-if="error"
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

      <!-- Empty state -->
      <div
        v-else-if="tables.length === 0"
        class="flex flex-col items-center gap-4 py-20"
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
        <div class="text-center">
          <p class="text-sm font-medium text-slate-400">
            No hay tablas cargadas todavía
          </p>
          <p class="mt-1 text-xs text-slate-500">
            Subí un archivo Excel para comenzar
          </p>
        </div>
      </div>

      <!-- Tables section -->
      <section v-else>
        <div class="mb-5 flex items-center gap-2">
          <div class="h-px flex-1 bg-slate-800"></div>
          <h2 class="text-xs font-medium uppercase tracking-widest text-slate-500">
            Tus tablas
          </h2>
          <div class="h-px flex-1 bg-slate-800"></div>
        </div>
        <div class="space-y-6">
          <TableView
            v-for="table in tables"
            :key="table.id"
            :sheet-name="table.sheet_name"
            :columns="table.columns"
            :rows="table.rows"
          />
        </div>
      </section>
    </main>
  </div>
</template>
