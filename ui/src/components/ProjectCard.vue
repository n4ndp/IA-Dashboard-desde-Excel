<script setup lang="ts">
import { useRouter } from 'vue-router'

interface Props {
  id: number
  nombreArchivo: string
  fechaCreacion: string
  tablaCount: number
  userId: number
}

const props = defineProps<Props>()

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
  <div
    class="group overflow-hidden rounded-xl border border-slate-800/60 bg-midnight-900/60 transition-all hover:border-blue-500/20 hover:bg-midnight-800/40"
  >
    <div class="p-5">
      <div class="mb-3 flex items-start justify-between">
        <div class="flex items-center gap-3">
          <div
            class="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-500/10 ring-1 ring-blue-500/20"
          >
            <svg
              class="h-5 w-5 text-blue-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="1.5"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z"
              />
            </svg>
          </div>
          <div>
            <h3 class="text-sm font-semibold text-slate-200">
              {{ nombreArchivo }}
            </h3>
            <p class="mt-0.5 text-xs text-slate-500">
              {{ formatDate(fechaCreacion) }}
            </p>
          </div>
        </div>
      </div>

      <div class="mb-4 flex items-center gap-2">
        <span
          class="inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset bg-slate-500/10 text-slate-400 ring-slate-500/20"
        >
          {{ tablaCount }} tabla{{ tablaCount !== 1 ? 's' : '' }}
        </span>
      </div>

      <div class="flex gap-2">
        <button
          class="btn-gradient flex-1 rounded-lg px-4 py-2 text-sm font-semibold text-white"
          @click="openProject"
        >
          Abrir
        </button>
        <button
          class="flex-1 rounded-lg border border-red-500/20 bg-red-500/5 px-4 py-2 text-sm font-medium text-red-400 transition-colors hover:bg-red-500/10"
          @click="handleDelete"
        >
          Eliminar
        </button>
      </div>
    </div>
  </div>
</template>
