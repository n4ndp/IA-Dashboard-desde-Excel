<script setup lang="ts">
// ── ProjectsView ──
// Grid of ProjectCard + dashed new card. Fetch on mount, delete with modal.

import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getProjects, deleteProject } from '../services/endpoints'
import type { ProjectSummary } from '../types'
import ProjectCard from '../components/ProjectCard.vue'
import DeleteConfirmModal from '../components/DeleteConfirmModal.vue'
import AppButton from '../components/base/AppButton.vue'
import { useSkeleton } from '../composables/useSkeleton'
import { useToast } from '../composables/useToast'
import { Plus, AlertCircle } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const toast = useToast()

const userId = computed(() => Number(route.params.userId))

const projects = ref<ProjectSummary[]>([])
const loading = ref(false)
const error = ref('')
const showDeleteModal = ref(false)
const deletingProject = ref<ProjectSummary | null>(null)

const { cardSkeletons } = useSkeleton()
const skeletons = computed(() => cardSkeletons(6))

interface GridItem {
  id: number
  isNewProject: boolean
  nombre_archivo: string
  fecha_creacion: string
  tabla_count: number
}

const allItems = computed<GridItem[]>(() => [
  { id: -1, isNewProject: true, nombre_archivo: '', fecha_creacion: '', tabla_count: 0 },
  ...projects.value.map((p) => ({ ...p, isNewProject: false })),
])

async function fetchProjects() {
  if (!userId.value) return
  loading.value = true
  error.value = ''
  try {
    const result = await getProjects(userId.value)
    projects.value = result.projects
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : 'Error al cargar proyectos'
    error.value = msg
    toast.show(msg, 'error')
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
      await deleteProject(userId.value, deletingProject.value.id)
      projects.value = projects.value.filter(
        (p) => p.id !== deletingProject.value!.id,
      )
      toast.show('Proyecto eliminado correctamente', 'success')
    } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : 'Error al eliminar proyecto'
    error.value = msg
    toast.show(msg, 'error')
  } finally {
    showDeleteModal.value = false
    deletingProject.value = null
  }
}
</script>

<template>
  <main class="mx-auto max-w-6xl px-6 py-8 animate-fade-in">
    <!-- Header -->
    <div class="mb-8">
      <h2 class="text-2xl font-bold text-text-primary">Tus proyectos</h2>
      <p class="mt-1 text-sm text-text-muted">
        Selecciona un proyecto o crea uno nuevo
      </p>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="s in skeletons"
        :key="s.id"
        class="card p-5"
      >
        <div class="mb-3 flex items-center gap-3">
          <div class="skeleton h-10 w-10 rounded-lg" />
          <div class="flex-1 space-y-2">
            <div class="skeleton h-4 w-3/4" />
            <div class="skeleton h-3 w-1/2" />
          </div>
        </div>
        <div class="mb-4">
          <div class="skeleton h-5 w-20 rounded-full" />
        </div>
        <div class="flex gap-2">
          <div class="skeleton h-9 flex-1 rounded-lg" />
          <div class="skeleton h-9 flex-1 rounded-lg" />
        </div>
      </div>
    </div>

    <!-- Error -->
    <div
      v-else-if="error"
      class="rounded-xl border border-danger/20 bg-danger/5 px-5 py-4 text-sm text-danger"
    >
      <div class="flex items-center gap-2">
        <AlertCircle class="h-4 w-4 shrink-0" />
        {{ error }}
      </div>
    </div>

    <!-- Empty state -->
    <div
      v-else-if="projects.length === 0"
      class="flex flex-col items-center gap-4 py-20"
    >
      <div class="flex h-16 w-16 items-center justify-center rounded-2xl bg-surface-overlay ring-1 ring-border">
        <Plus class="h-8 w-8 text-text-muted" />
      </div>
      <div class="text-center">
        <p class="text-sm font-medium text-text-secondary">No tienes proyectos todavía</p>
        <p class="mt-1 text-xs text-text-muted">Crea tu primer proyecto subiendo un archivo Excel</p>
      </div>
      <AppButton variant="primary" size="md" class="mt-2" @click="goToNewProject">
        Crear proyecto
      </AppButton>
    </div>

    <!-- Project grid -->
    <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <template v-for="project in allItems" :key="project.id">
        <!-- New project card -->
        <div
          v-if="project.isNewProject"
          class="flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-border p-8 transition-all duration-150 ease-out hover:scale-[1.01] hover:bg-[#1c1c1c] hover:border-border/80"
          @click="goToNewProject"
        >
          <Plus class="h-8 w-8 text-text-secondary" />
          <span class="text-sm font-medium text-text-secondary">Nuevo Proyecto</span>
        </div>

        <ProjectCard
          v-else
          :id="project.id"
          :nombre_archivo="project.nombre_archivo"
          :fecha_creacion="project.fecha_creacion"
          :tabla_count="project.tabla_count"
          :user-id="userId"
          @delete="requestDelete"
        />
      </template>
    </div>

    <!-- Delete modal -->
    <DeleteConfirmModal
      v-if="showDeleteModal && deletingProject"
      :project-name="deletingProject.nombre_archivo"
      @confirm="confirmDelete"
      @cancel="cancelDelete"
    />
  </main>
</template>
