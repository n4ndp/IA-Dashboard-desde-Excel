<script setup lang="ts">
// ── ProjectCard ──
// Project grid card showing metadata, open and delete actions.

import { useRouter } from 'vue-router'
import { FileSpreadsheet, Trash2 } from 'lucide-vue-next'
import AppButton from './base/AppButton.vue'

const props = defineProps<{
  id: number
  nombre_archivo: string
  fecha_creacion: string
  tabla_count: number
  userId: number
}>()

const emit = defineEmits<{
  delete: [id: number]
}>()

const router = useRouter()

function openProject() {
  router.push(`/u/${props.userId}/p/${props.id}`)
}

function handleDelete() {
  emit('delete', props.id)
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('es-AR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}
</script>

<template>
  <div class="card group transition-all">
    <div class="p-5">
      <div class="mb-3 flex items-center gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-surface-overlay ring-1 ring-border">
          <FileSpreadsheet class="h-5 w-5 text-text-muted" />
        </div>
        <div class="min-w-0 flex-1">
          <h3 class="truncate text-sm font-semibold text-text-primary">
            {{ nombre_archivo }}
          </h3>
          <p class="text-xs text-text-muted">
            {{ formatDate(fecha_creacion) }}
          </p>
        </div>
      </div>

      <div class="mb-4">
        <span class="badge rounded-full bg-surface-overlay px-2 py-0.5 text-text-secondary">
          {{ tabla_count }} tabla{{ tabla_count !== 1 ? 's' : '' }}
        </span>
      </div>

      <div class="flex gap-2">
        <AppButton variant="primary" size="sm" class="flex-1" @click="openProject">
          Abrir
        </AppButton>
        <AppButton variant="danger" size="sm" @click="handleDelete">
          <Trash2 class="h-3.5 w-3.5" />
        </AppButton>
      </div>
    </div>
  </div>
</template>
