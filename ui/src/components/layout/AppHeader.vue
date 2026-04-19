<script setup lang="ts">
// ── AppHeader ──
// Logo + user avatar initial. Hidden on login page. Navigates to projects.

import { useRouter } from 'vue-router'
import { useUser } from '../../composables/useUser'
import { LayoutGrid } from 'lucide-vue-next'

const router = useRouter()
const { userName, userId } = useUser()

function goToProjects() {
  if (userId.value) {
    router.push(`/u/${userId.value}/p`)
  }
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

      <button
        class="flex items-center gap-2 hover:opacity-80 transition-opacity"
        @click="goToProjects"
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
    </div>
  </header>
</template>
