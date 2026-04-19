<script setup lang="ts">
// ── LoginView ──
// Centered login: name input → createUser → localStorage → redirect.

import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUser } from '../composables/useUser'
import { createUser } from '../services/endpoints'
import AppInput from '../components/base/AppInput.vue'
import AppButton from '../components/base/AppButton.vue'
import { User } from 'lucide-vue-next'

const router = useRouter()
const { setUser } = useUser()

const inputName = ref('')
const nameError = ref('')
const submitting = ref(false)

onMounted(() => {
  const storedUserId = localStorage.getItem('user_id')
  if (storedUserId) {
    router.replace(`/u/${storedUserId}/p`)
  }
})

async function handleSubmit() {
  if (!inputName.value.trim()) {
    nameError.value = 'Por favor ingresa tu nombre.'
    return
  }
  nameError.value = ''
  submitting.value = true

  try {
    const result = await createUser(inputName.value.trim())
    setUser(result.id, result.nombre)
    router.push(`/u/${result.id}/p`)
  } catch {
    // Fallback: try using stored credentials if API failed
    const storedUserId = localStorage.getItem('user_id')
    if (storedUserId) {
      router.push(`/u/${storedUserId}/p`)
    } else {
      nameError.value = 'Error al conectar con el servidor. Intenta de nuevo.'
    }
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-surface-base px-4">
    <div class="card animate-fade-in w-full max-w-sm p-8">
      <!-- Icon -->
      <div class="mb-6 flex justify-center">
        <div
          class="flex h-14 w-14 items-center justify-center rounded-xl bg-primary/10 ring-1 ring-primary/20"
        >
          <User class="h-7 w-7 text-primary" />
        </div>
      </div>

      <h1 class="mb-2 text-center text-2xl font-bold tracking-tight text-text-primary">
        Bienvenido
      </h1>
      <p class="mb-6 text-center text-sm text-text-muted">
        Ingresa tu nombre para continuar al dashboard
      </p>

      <div class="space-y-4">
        <div>
          <label
            for="name-input"
            class="mb-1.5 block text-xs font-medium uppercase tracking-wider text-text-muted"
          >
            Nombre
          </label>
          <AppInput
            id="name-input"
            v-model="inputName"
            placeholder="Tu nombre..."
            :error="nameError"
            @keydown.enter="handleSubmit"
          />
        </div>

        <AppButton
          variant="primary"
          size="lg"
          :loading="submitting"
          :disabled="!inputName.trim()"
          class="w-full"
          @click="handleSubmit"
        >
          {{ submitting ? 'Cargando...' : 'Continuar' }}
        </AppButton>
      </div>
    </div>
  </div>
</template>
