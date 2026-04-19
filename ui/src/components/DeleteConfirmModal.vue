<script setup lang="ts">
defineProps<{
  projectName: string
}>()

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()
</script>

<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      @click.self="$emit('cancel')"
    >
      <div class="glass glow-ring animate-fade-in w-full max-w-sm rounded-2xl p-6">
        <!-- Top gradient line -->
        <div class="accent-bar absolute left-6 right-6 top-0 rounded-full"></div>

        <div class="mb-5 flex justify-center">
          <div
            class="flex h-12 w-12 items-center justify-center rounded-xl bg-red-500/10 ring-1 ring-red-500/20"
          >
            <svg
              class="h-6 w-6 text-red-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="1.5"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"
              />
            </svg>
          </div>
        </div>

        <h2 class="mb-1 text-center text-lg font-bold text-slate-100">
          Eliminar proyecto
        </h2>
        <p class="mb-6 text-center text-sm text-slate-400">
          ¿Estás seguro de que querés eliminar
          <span class="font-medium text-slate-300">"{{ projectName }}"</span>?
          Esta acción no se puede deshacer.
        </p>

        <div class="flex gap-3">
          <button
            class="flex-1 rounded-lg border border-slate-700/50 bg-midnight-800 px-4 py-2.5 text-sm font-medium text-slate-300 transition hover:bg-midnight-700"
            @click="$emit('cancel')"
          >
            Cancelar
          </button>
          <button
            class="flex-1 rounded-lg bg-red-500/80 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-red-500"
            @click="$emit('confirm')"
          >
            Eliminar
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
