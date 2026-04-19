<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useUser } from '../../composables/useUser'

const router = useRouter()
const { name, userId } = useUser()

function goToProjects() {
  if (userId.value) {
    router.push(`/u/${userId.value}/p`)
  }
}
</script>

<template>
  <header class="relative border-b border-slate-800/60 bg-midnight-900/80">
    <div class="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
      <div class="flex items-center gap-3">
        <div
          class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-500/10 ring-1 ring-blue-500/20"
        >
          <svg
            class="h-4 w-4 text-blue-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="2"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M3.75 6A2.25 2.25 0 0 1 6 3.75h2.25A2.25 2.25 0 0 1 10.5 6v2.25a2.25 2.25 0 0 1-2.25 2.25H6a2.25 2.25 0 0 1-2.25-2.25V6ZM3.75 15.75A2.25 2.25 0 0 1 6 13.5h2.25a2.25 2.25 0 0 1 2.25 2.25V18a2.25 2.25 0 0 1-2.25 2.25H6A2.25 2.25 0 0 1 3.75 18v-2.25ZM13.5 6a2.25 2.25 0 0 1 2.25-2.25H18A2.25 2.25 0 0 1 20.25 6v2.25A2.25 2.25 0 0 1 18 10.5h-2.25a2.25 2.25 0 0 1-2.25-2.25V6ZM13.5 15.75a2.25 2.25 0 0 1 2.25-2.25H18a2.25 2.25 0 0 1 2.25 2.25V18A2.25 2.25 0 0 1 18 20.25h-2.25A2.25 2.25 0 0 1 13.5 18v-2.25Z"
            />
          </svg>
        </div>
        <h1 class="text-lg font-bold tracking-tight text-slate-100">
          Excel Dashboard
        </h1>
      </div>
      <button
        class="flex items-center gap-2 transition-opacity hover:opacity-80"
        @click="goToProjects"
      >
        <div
          class="flex h-7 w-7 items-center justify-center rounded-full bg-blue-500/10 text-xs font-semibold text-blue-400"
        >
          {{ name?.charAt(0)?.toUpperCase() }}
        </div>
        <span class="text-sm text-slate-400">{{ name }}</span>
      </button>
    </div>
    <!-- Signature gradient line -->
    <div class="accent-bar"></div>
  </header>
</template>
