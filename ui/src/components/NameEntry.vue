<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{
  'name-set': [name: string]
}>()

const inputName = ref('')
const error = ref('')

function handleSubmit() {
  if (!inputName.value.trim()) {
    error.value = 'Por favor ingresá tu nombre.'
    return
  }
  error.value = ''
  emit('name-set', inputName.value.trim())
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-midnight-950 px-4">
    <!-- Ambient background glow -->
    <div
      class="pointer-events-none fixed inset-0 overflow-hidden"
      aria-hidden="true"
    >
      <div
        class="absolute left-1/2 top-1/3 h-[500px] w-[500px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-glow-blue/5 blur-[120px]"
      ></div>
      <div
        class="absolute bottom-1/4 right-1/3 h-[400px] w-[400px] rounded-full bg-glow-violet/5 blur-[100px]"
      ></div>
    </div>

    <div
      class="glass glow-ring animate-fade-in relative w-full max-w-sm rounded-2xl p-8"
    >
      <!-- Top gradient line -->
      <div class="accent-bar absolute left-6 right-6 top-0 rounded-full"></div>

      <!-- Icon -->
      <div class="mb-6 flex justify-center">
        <div
          class="flex h-14 w-14 items-center justify-center rounded-xl bg-blue-500/10 ring-1 ring-blue-500/20"
        >
          <svg
            class="h-7 w-7 text-blue-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z"
            />
          </svg>
        </div>
      </div>

      <h1
        class="mb-2 text-center text-2xl font-bold tracking-tight text-slate-100"
      >
        Bienvenido
      </h1>
      <p class="mb-6 text-center text-sm text-slate-400">
        Ingresá tu nombre para continuar al dashboard
      </p>

      <div class="space-y-4">
        <div>
          <label
            for="name-input"
            class="mb-1.5 block text-xs font-medium uppercase tracking-wider text-slate-500"
          >
            Nombre
          </label>
          <input
            id="name-input"
            v-model="inputName"
            type="text"
            placeholder="Tu nombre..."
            class="w-full rounded-lg border border-slate-700/50 bg-midnight-800 px-4 py-2.5 text-sm text-slate-200 placeholder-slate-500 transition focus:border-blue-500/50 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
            @keydown.enter="handleSubmit"
          />
        </div>

        <p v-if="error" class="text-sm text-red-400">{{ error }}</p>

        <button
          class="btn-gradient w-full rounded-lg px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-40 disabled:hover:shadow-none"
          :disabled="!inputName.trim()"
          @click="handleSubmit"
        >
          Continuar
        </button>
      </div>
    </div>
  </div>
</template>
