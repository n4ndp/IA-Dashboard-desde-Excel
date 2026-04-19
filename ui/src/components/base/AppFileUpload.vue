<script setup lang="ts">
// ── AppFileUpload ──
// Drag-drop file upload: standalone (API call) or emit-only (parent handles).
// Validates .xlsx + 10MB limit.

import { ref } from 'vue'
import { uploadToProject } from '../../services/endpoints'
import AppButton from './AppButton.vue'
import { Upload, AlertCircle, CheckCircle } from 'lucide-vue-next'

interface Props {
  mode?: 'standalone' | 'emit-only'
  projectId?: number
}

const props = withDefaults(defineProps<Props>(), {
  mode: 'standalone',
})

const emit = defineEmits<{
  'file-selected': [file: File]
  'upload-complete': [payload: { userId: number; projectId: number }]
  error: [message: string]
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const uploading = ref(false)
const uploadProgress = ref(0)
const errorMsg = ref('')
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

function validateFile(file: File): string | null {
  if (!file.name.endsWith('.xlsx')) return 'Solo se aceptan archivos .xlsx'
  if (file.size > 10 * 1024 * 1024) return 'El archivo supera el límite de 10MB'
  return null
}

async function processFile(file: File) {
  const validationError = validateFile(file)
  if (validationError) {
    errorMsg.value = validationError
    emit('error', validationError)
    return
  }

  // Emit-only mode: just pass the file to parent
  if (props.mode === 'emit-only') {
    emit('file-selected', file)
    return
  }

  // Standalone mode: call API directly
  if (!props.projectId) {
    errorMsg.value = 'Se requiere projectId en modo standalone'
    emit('error', errorMsg.value)
    return
  }

  errorMsg.value = ''
  uploading.value = true
  uploadProgress.value = 0
  success.value = false

  const storedUserId = Number(localStorage.getItem('user_id'))
  const formData = new FormData()
  formData.append('file', file)

  try {
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += Math.random() * 15
      }
    }, 200)

    const result = await uploadToProject(storedUserId, props.projectId, formData)

    clearInterval(progressInterval)
    uploadProgress.value = 100
    success.value = true
    emit('upload-complete', { userId: result.user_id, projectId: result.project_id })
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : 'Error al subir archivo'
    errorMsg.value = msg
    emit('error', msg)
  } finally {
    uploading.value = false
  }
}

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  processFile(file)
  target.value = ''
}

function handleDrop(e: DragEvent) {
  isDragOver.value = false
  const file = e.dataTransfer?.files?.[0]
  if (!file) return
  processFile(file)
}
</script>

<template>
  <div
    class="relative overflow-hidden rounded-xl border border-dashed transition-all duration-300"
    :class="[
      isDragOver
        ? 'border-primary/60 bg-primary/5'
        : 'border-border bg-surface-raised hover:border-primary/30',
    ]"
    @dragover="onDragOver"
    @dragleave="onDragLeave"
    @drop="handleDrop"
  >
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
              ? 'bg-primary/10 ring-1 ring-primary/20'
              : 'bg-surface-overlay ring-1 ring-border'
          "
        >
          <Upload
            class="h-5 w-5 transition-colors"
            :class="isDragOver ? 'text-primary' : 'text-text-muted'"
          />
        </div>
      </div>

      <p class="mb-1 text-sm text-text-primary">
        <span class="font-medium">Arrastra</span> tu archivo Excel aquí o
      </p>

      <AppButton
        variant="primary"
        size="md"
        class="mt-3"
        :disabled="uploading"
        @click="triggerUpload"
      >
        <span v-if="uploading" class="spinner-sm" />
        {{ uploading ? 'Procesando...' : 'Seleccionar archivo' }}
      </AppButton>

      <p class="mt-3 text-xs text-text-muted">Solo archivos .xlsx (máx. 10MB)</p>

      <!-- Progress bar -->
      <div v-if="uploading || uploadProgress > 0" class="progress-track mt-4">
        <div
          class="progress-bar"
          :style="{ width: `${uploadProgress}%` }"
        />
      </div>

      <!-- Error -->
      <div v-if="errorMsg" class="mt-4 text-sm text-danger">
        <div class="flex items-center justify-center gap-1.5">
          <AlertCircle class="h-3.5 w-3.5" />
          {{ errorMsg }}
        </div>
      </div>

      <!-- Success -->
      <div
        v-if="success"
        class="mt-4 flex items-center justify-center gap-1.5 text-sm text-success"
      >
        <CheckCircle class="h-3.5 w-3.5" />
        Archivo procesado correctamente
      </div>
    </div>
  </div>
</template>
