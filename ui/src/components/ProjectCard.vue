<script setup lang="ts">
// ── ProjectCard ──
// Project grid card showing metadata, open and delete actions.

import { useRouter } from 'vue-router'
import { Trash2 } from 'lucide-vue-next'
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
      <!-- Card content: title, date, badge -->
      <div class="mb-4">
        <h3 class="truncate text-sm font-semibold text-text-primary">
          {{ nombre_archivo }}
        </h3>
        <p class="text-xs text-text-muted">
          {{ formatDate(fecha_creacion) }}
        </p>
        <span class="mt-1 inline-block bg-surface-overlay px-2 py-0.5 text-text-secondary text-xs font-medium">
          {{ tabla_count }} tabla{{ tabla_count !== 1 ? 's' : '' }}
        </span>
      </div>

      <!-- Buttons at bottom right -->
      <div class="flex items-center justify-end gap-2">
        <AppButton variant="danger" size="md" class="h-9 w-9 !p-0" @click="handleDelete">
          <Trash2 class="h-4 w-4" />
        </AppButton>
        <AppButton variant="primary" size="md" class="h-9" @click="openProject">
          Abrir
        </AppButton>
      </div>
    </div>
  </div>
</template>
