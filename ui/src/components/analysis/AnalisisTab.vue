<script setup lang="ts">
// ── AnalisisTab ──
// Analysis tab container with 4-state machine: empty → loading → generated | error.
// Uses useDashboard composable for state management with real API integration.

import { useDashboard } from '../../composables/useDashboard'
import DashboardRenderer from './DashboardRenderer.vue'
import { BarChart3, Loader2, AlertCircle } from 'lucide-vue-next'

const props = defineProps<{
  userId: number
  projectId: number
  existingDashboard?: { widgets: unknown[] } | null
}>()

const { state, widgets, errorMessage, generate } = useDashboard(
  props.userId,
  props.projectId,
  props.existingDashboard as { widgets: import('../../types').DashboardWidgetMap[] } | null | undefined,
)
</script>

<template>
  <div>
    <!-- Empty state -->
    <div
      v-if="state === 'empty'"
      class="flex flex-col items-center justify-center gap-4 py-24"
    >
      <div class="flex h-16 w-16 items-center justify-center rounded-2xl bg-surface-overlay ring-1 ring-border">
        <BarChart3 class="h-8 w-8 text-text-muted" />
      </div>
      <p class="text-sm text-text-muted">No hay dashboard generado</p>
      <button
        class="btn btn-primary btn-md"
        @click="generate"
      >
        Generar dashboard
      </button>
    </div>

    <!-- Loading state -->
    <div
      v-else-if="state === 'loading'"
      class="flex flex-col items-center justify-center gap-4 py-24"
    >
      <Loader2 class="h-8 w-8 animate-spin text-primary" />
      <p class="text-sm text-text-muted">Generando dashboard...</p>
    </div>

    <!-- Error state -->
    <div
      v-else-if="state === 'error'"
      class="flex flex-col items-center justify-center gap-4 py-24"
    >
      <div class="flex h-16 w-16 items-center justify-center rounded-2xl bg-surface-overlay ring-1 ring-border">
        <AlertCircle class="h-8 w-8 text-danger" />
      </div>
      <p class="text-sm text-danger">{{ errorMessage }}</p>
      <button
        class="btn btn-primary btn-md"
        @click="generate"
      >
        Reintentar
      </button>
    </div>

    <!-- Generated state -->
    <DashboardRenderer
      v-else-if="state === 'generated'"
      :widgets="widgets"
    />
  </div>
</template>
