<script setup lang="ts">
// ── ProjectNewView ──
// FileUpload (emit-only) + ProjectNameModal → createProject → redirect.

import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { createProject } from '../services/endpoints'
import AppFileUpload from '../components/base/AppFileUpload.vue'
import ProjectNameModal from '../components/ProjectNameModal.vue'
import { AlertCircle } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()

const userId = computed(() => Number(route.params.userId))

const uploadedFile = ref<File | null>(null)
const showModal = ref(false)
const uploading = ref(false)
const error = ref('')

function onFileSelected(file: File) {
  uploadedFile.value = file
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
    const result = await createProject(userId.value, formData)
    showModal.value = false
    router.push(`/u/${userId.value}/p/${result.project_id}`)
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : 'Error al crear proyecto'
  } finally {
    uploading.value = false
  }
}

function onUploadError(msg: string) {
  error.value = msg
}
</script>

<template>
  <main class="mx-auto max-w-6xl px-6 py-8 animate-fade-in">
    <div class="mb-8">
      <h2 class="text-2xl font-bold text-text-primary">Nuevo proyecto</h2>
      <p class="mt-1 text-sm text-text-muted">
        Subí un archivo Excel para crear tu proyecto
      </p>
    </div>

    <div v-if="error" class="mb-6 rounded-xl border border-danger/20 bg-danger/5 px-5 py-4 text-sm text-danger">
      <div class="flex items-center gap-2">
        <AlertCircle class="h-4 w-4 shrink-0" />
        {{ error }}
      </div>
    </div>

    <AppFileUpload
      mode="emit-only"
      @file-selected="onFileSelected"
      @error="onUploadError"
    />

    <ProjectNameModal
      v-if="showModal && uploadedFile"
      :default-name="uploadedFile.name.replace(/\.[^.]+$/, '')"
      @confirm="confirmProjectName"
      @cancel="cancelModal"
    />
  </main>
</template>
