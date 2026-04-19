<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { apiGet, apiDelete } from '../composables/useApi'
import ProjectCard from '../components/ProjectCard.vue'
import DeleteConfirmModal from '../components/DeleteConfirmModal.vue'

interface ProjectSummary {
  id: number
  nombre_archivo: string
  fecha_creacion: string
  tabla_count: number
}

const router = useRouter()
const route = useRoute()

const userId = computed(() => Number(route.params.userId))

const projects = ref<ProjectSummary[]>([])
const loading = ref(false)
const error = ref('')
const showDeleteModal = ref(false)
const deletingProject = ref<ProjectSummary | null>(null)

async function fetchProjects() {
  if (!userId.value) return
  loading.value = true
  error.value = ''
  try {
    const result = await apiGet<{ projects: ProjectSummary[] }>(
      `/users/${userId.value}/projects`
    )
    projects.value = result.projects
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : 'Error al cargar proyectos'
  } finally {
    loading.value = false
  }
}

onMounted(fetchProjects)

function goToNewProject() {
  router.push(`/u/${userId.value}/p/new`)
}

function requestDelete(projectId: number) {
  const found = projects.value.find((p) => p.id === projectId)
  if (!found) return
  deletingProject.value = found
  showDeleteModal.value = true
}

function cancelDelete() {
  showDeleteModal.value = false
  deletingProject.value = null
}

async function confirmDelete() {
  if (!deletingProject.value) return
  try {
    await apiDelete(`/users/${userId.value}/projects/${deletingProject.value.id}`)
    projects.value = projects.value.filter(
      (p) => p.id !== deletingProject.value!.id
    )
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : 'Error al eliminar proyecto'
  } finally {
    showDeleteModal.value = false
    deletingProject.value = null
  }
}
</script>

<template>
  <main class="mx-auto max-w-6xl px-6 py-8 animate-fade-in">
    <!-- Top actions -->
    <div class="mb-8 flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-bold text-slate-100">Tus proyectos</h2>
        <p class="mt-1 text-sm text-slate-400">
          Seleccioná un proyecto o creá uno nuevo
        </p>
      </div>
      <button
        class="btn-gradient inline-flex items-center gap-2 rounded-lg px-5 py-2.5 text-sm font-semibold text-white"
        @click="goToNewProject"
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
            d="M12 4.5v15m7.5-7.5h-15"
          />
        </svg>
        Nuevo proyecto
      </button>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="flex flex-col items-center gap-3 py-16">
      <div
        class="h-8 w-8 animate-spin rounded-full border-2 border-blue-500/30 border-t-blue-400"
      ></div>
      <p class="text-sm text-slate-400">Cargando proyectos...</p>
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
      v-else-if="projects.length === 0"
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
          No tenés proyectos todavía
        </p>
        <p class="mt-1 text-xs text-slate-500">
          Creá tu primer proyecto subiendo un archivo Excel
        </p>
      </div>
      <button
        class="btn-gradient mt-2 rounded-lg px-6 py-2.5 text-sm font-semibold text-white"
        @click="goToNewProject"
      >
        Crear proyecto
      </button>
    </div>

    <!-- Project grid -->
    <div
      v-else
      class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
    >
      <ProjectCard
        v-for="project in projects"
        :key="project.id"
        :id="project.id"
        :nombre-archivo="project.nombre_archivo"
        :fecha-creacion="project.fecha_creacion"
        :tabla-count="project.tabla_count"
        :user-id="userId"
        @delete="requestDelete"
      />
    </div>

    <!-- Delete confirmation modal -->
    <DeleteConfirmModal
      v-if="showDeleteModal && deletingProject"
      :project-name="deletingProject.nombre_archivo"
      @confirm="confirmDelete"
      @cancel="cancelDelete"
    />
  </main>
</template>
