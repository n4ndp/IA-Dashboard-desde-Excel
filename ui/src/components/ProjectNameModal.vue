<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  defaultName: string
}>()

const emit = defineEmits<{
  confirm: [name: string]
  cancel: []
}>()

const projectName = ref(props.defaultName)

function handleConfirm() {
  if (!projectName.value.trim()) return
  emit('confirm', projectName.value.trim())
}

function handleCancel() {
  emit('cancel')
}
</script>

<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      @click.self="handleCancel"
    >
      <div class="glass glow-ring animate-fade-in w-full max-w-sm rounded-2xl p-6">
        <!-- Top gradient line -->
        <div class="accent-bar absolute left-6 right-6 top-0 rounded-full"></div>

        <h2 class="mb-1 text-lg font-bold text-slate-100">Nombre del proyecto</h2>
        <p class="mb-4 text-sm text-slate-400">
          Elegí un nombre para tu proyecto
        </p>

        <div class="mb-5">
          <label
            for="project-name-input"
            class="mb-1.5 block text-xs font-medium uppercase tracking-wider text-slate-500"
          >
            Nombre
          </label>
          <input
            id="project-name-input"
            v-model="projectName"
            type="text"
            class="w-full rounded-lg border border-slate-700/50 bg-midnight-800 px-4 py-2.5 text-sm text-slate-200 placeholder-slate-500 transition focus:border-blue-500/50 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
            @keydown.enter="handleConfirm"
            @keydown.escape="handleCancel"
          />
        </div>

        <div class="flex gap-3">
          <button
            class="flex-1 rounded-lg border border-slate-700/50 bg-midnight-800 px-4 py-2.5 text-sm font-medium text-slate-300 transition hover:bg-midnight-700"
            @click="handleCancel"
          >
            Cancelar
          </button>
          <button
            class="btn-gradient flex-1 rounded-lg px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-40"
            :disabled="!projectName.trim()"
            @click="handleConfirm"
          >
            Crear
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
