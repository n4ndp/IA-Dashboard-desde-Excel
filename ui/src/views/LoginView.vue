<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUser } from '../composables/useUser'
import { apiPost } from '../composables/useApi'
import NameEntry from '../components/NameEntry.vue'

const router = useRouter()
const { setName, setUserId } = useUser()

// If returning user with userId in localStorage, redirect immediately
onMounted(() => {
  const storedUserId = localStorage.getItem('user_id')
  if (storedUserId) {
    router.replace(`/u/${storedUserId}/p`)
  }
})

async function onNameSet(name: string) {
  try {
    const result = await apiPost<{ id: number; nombre: string }>(
      '/users',
      { nombre: name },
    )
    setUserId(result.id)
    setName(result.nombre)
    router.push(`/u/${result.id}/p`)
  } catch {
    // Fallback: just store name locally (API may be down)
    setName(name)
  }
}
</script>

<template>
  <NameEntry @name-set="onNameSet" />
</template>
