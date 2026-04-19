<script setup lang="ts">
import { ref } from 'vue'
import { apiPost } from '../composables/useApi'

const props = defineProps<{
  projectId?: number
  userId?: number
  hideSuccess?: boolean
}>()

const emit = defineEmits<{
  'upload-complete': [payload: { userId: number; projectId: number }]
  'upload-ready': [payload: { file: File }]
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const uploading = ref(false)
const error = ref('')
const success = ref(false)
const isDragOver = ref(false)

function triggerUpload() {
  fileInput.value?.click()
}

function onDragOver(e: DragEvent) {
  e.preventDefault()
  isDragOver.value = true
}

function onDragLeave() {
  isDragOver.value = false
}

async function processFile(file: File) {
  if (!file.name.endsWith('.xlsx')) {
    error.value = 'Solo se aceptan archivos .xlsx'
    return
  }

  if (file.size > 10 * 1024 * 1024) {
    error.value = 'El archivo supera el límite de 10MB'
    return
  }

  // For ProjectNewView: emit the file for the parent to handle (ProjectNameModal flow)
  if (props.projectId === undefined && props.hideSuccess) {
    emit('upload-ready', { file })
    return
  }

  error.value = ''
  uploading.value = true
  success.value = false

  const formData = new FormData()
  formData.append('file', file)

  try {
    let endpoint = '/upload'
    if (props.projectId && props.userId) {
      endpoint = `/users/${props.userId}/projects/${props.projectId}/upload`
    }

    const result = await apiPost<{
      user_id: number
      project_id: number
      tables: unknown[]
    }>(endpoint, formData)

    success.value = true
    emit('upload-complete', {
      userId: result.user_id,
      projectId: result.project_id,
    })
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : 'Error al subir archivo'
  } finally {
    uploading.value = false
  }
}

async function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  await processFile(file)
  target.value = ''
}

async function handleDrop(e: DragEvent) {
  isDragOver.value = false
  const file = e.dataTransfer?.files?.[0]
  if (!file) return
  await processFile(file)
}
</script>

<template>
  <div
    class="relative overflow-hidden rounded-xl border border-dashed transition-all duration-300"
    :class="[
      isDragOver
        ? 'border-blue-400/60 bg-blue-500/5'
        : 'border-slate-700/40 bg-midnight-900/40 hover:border-blue-500/30 hover:bg-midnight-800/40',
    ]"
    @dragover="onDragOver"
    @dragleave="onDragLeave"
    @drop="handleDrop"
  >
    <!-- Ambient glow on drag -->
    <div
      v-if="isDragOver"
      class="pointer-events-none absolute inset-0 bg-blue-500/5 blur-xl"
    ></div>

    <div class="relative p-8 text-center">
      <input
        ref="fileInput"
        type="file"
        accept=".xlsx"
        class="hidden"
        @change="handleFileChange"
      />

      <!-- Upload icon -->
      <div class="mb-4 flex justify-center">
        <div
          class="flex h-12 w-12 items-center justify-center rounded-xl transition-colors"
          :class="
            isDragOver
              ? 'bg-blue-500/15 ring-1 ring-blue-500/30'
              : 'bg-slate-800/50 ring-1 ring-slate-700/50'
          "
        >
          <svg
            class="h-5 w-5 transition-colors"
            :class="isDragOver ? 'text-blue-400' : 'text-slate-500'"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5"
            />
          </svg>
        </div>
      </div>

      <p class="mb-1 text-sm text-slate-300">
        <span class="font-medium">Arrastrá</span> tu archivo Excel acá o
      </p>

      <button
        class="btn-gradient mt-3 inline-flex items-center gap-2 rounded-lg px-6 py-2.5 text-sm font-semibold text-white disabled:opacity-40 disabled:hover:shadow-none"
        :disabled="uploading"
        @click="triggerUpload"
      >
        <span
          v-if="uploading"
          class="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white"
        ></span>
        {{ uploading ? 'Procesando...' : 'Seleccionar archivo' }}
      </button>

      <p class="mt-3 text-xs text-slate-600">Solo archivos .xlsx (máx. 10MB)</p>

      <!-- Feedback messages -->
      <div v-if="error" class="mt-4 text-sm text-red-400">
        <div class="flex items-center justify-center gap-1.5">
          <svg
            class="h-3.5 w-3.5"
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
      <div
        v-if="success && !hideSuccess"
        class="mt-4 flex items-center justify-center gap-1.5 text-sm text-emerald-400"
      >
        <svg
          class="h-3.5 w-3.5"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="2"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
          />
        </svg>
        ¡Archivo procesado correctamente!
      </div>
    </div>
  </div>
</template>
