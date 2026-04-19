<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { apiPost } from '../composables/useApi'
import FileUpload from '../components/FileUpload.vue'
import ProjectNameModal from '../components/ProjectNameModal.vue'

const router = useRouter()
const route = useRoute()

const userId = computed(() => Number(route.params.userId))

const uploadedFile = ref<File | null>(null)
const showModal = ref(false)
const uploading = ref(false)
const error = ref('')

function onFileReady(payload: { file: File }) {
  uploadedFile.value = payload.file
  showModal.value = true
}

function cancelModal() {
  showModal.value = false
  uploadedFile.value = null
}

async function confirmProjectName(projectName: string) {
  if (!uploadedFile.value) return
  uploading.value = true
  error.value = ''

  const formData = new FormData()
  formData.append('file', uploadedFile.value)
  formData.append('project_name', projectName)

  try {
    const result = await apiPost<{
      user_id: number
      project_id: number
    }>(`/users/${userId.value}/projects`, formData)

    showModal.value = false
    router.push(`/u/${userId.value}/p/${result.project_id}`)
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : 'Error al crear proyecto'
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <main class="mx-auto max-w-6xl px-6 py-8 animate-fade-in">
    <div class="mb-8">
      <h2 class="text-2xl font-bold text-slate-100">Nuevo proyecto</h2>
      <p class="mt-1 text-sm text-slate-400">
        Subí un archivo Excel para crear tu proyecto
      </p>
    </div>

    <div v-if="error" class="mb-6 rounded-xl border border-red-500/20 bg-red-500/5 px-5 py-4 text-sm text-red-400">
      <div class="flex items-center gap-2">
        <svg class="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
        </svg>
        {{ error }}
      </div>
    </div>

    <FileUpload
      :hide-success="true"
      @upload-ready="onFileReady"
    />

    <ProjectNameModal
      v-if="showModal && uploadedFile"
      :default-name="uploadedFile.name.replace(/\.[^.]+$/, '')"
      @confirm="confirmProjectName"
      @cancel="cancelModal"
    />
  </main>
</template>
