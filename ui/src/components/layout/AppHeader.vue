<script setup lang="ts">
// ── AppHeader ──
// Logo + user avatar with dropdown. Hidden on login page.

import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUser } from '../../composables/useUser'
import { LayoutGrid } from 'lucide-vue-next'

const router = useRouter()
const { userName, userId, clearUser } = useUser()

const dropdownOpen = ref(false)

function goToProjects() {
  if (userId.value) {
    router.push(`/u/${userId.value}/p`)
  }
}

function toggleDropdown() {
  dropdownOpen.value = !dropdownOpen.value
  if (dropdownOpen.value) {
    // Close on next click outside
    setTimeout(() => {
      document.addEventListener('click', closeDropdown, { once: true })
    }, 0)
  }
}

function closeDropdown() {
  dropdownOpen.value = false
}

function logout() {
  dropdownOpen.value = false
  clearUser()
  router.push('/')
}
</script>

<template>
  <header class="border-b border-border">
    <div class="mx-auto flex max-w-6xl items-center justify-between px-6 py-3.5">
      <button
        class="flex items-center gap-2.5 hover:opacity-80 transition-opacity"
        @click="goToProjects"
      >
        <LayoutGrid class="h-4 w-4 text-text-muted" />
        <span class="text-sm font-medium text-text-primary">Excel AI</span>
      </button>

      <div class="relative">
        <button
          class="flex items-center gap-2 hover:opacity-80 transition-opacity"
          @click.stop="toggleDropdown"
        >
          <span class="text-sm font-medium text-text-secondary">
            {{ userName }}
          </span>
          <div
            class="flex h-6 w-6 items-center justify-center rounded-full bg-surface-overlay text-[10px] font-medium text-text-secondary"
          >
            {{ userName?.charAt(0)?.toUpperCase() }}
          </div>
        </button>

        <div
          v-if="dropdownOpen"
          class="absolute right-0 top-full mt-2 z-50 min-w-40 rounded-lg border border-border bg-surface-raised shadow-lg py-1"
          @click.stop
        >
          <div class="px-3 py-2 text-xs text-text-muted">
            {{ userName }}
          </div>
          <div class="h-px bg-border mx-2" />
          <button
            class="w-full px-3 py-2 text-left text-sm text-text-secondary hover:bg-surface-overlay transition-colors"
            @click="logout"
          >
            Cerrar sesión
          </button>
        </div>
      </div>
    </div>
  </header>
</template>
