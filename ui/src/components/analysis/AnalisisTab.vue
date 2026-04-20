<script setup lang="ts">
// ── AnalisisTab ──
// Analysis tab container with 4-state machine: empty → loading → generated | error.
// Uses useDashboard composable for state management with real API integration.
// Chat overlay: floating mini-chat for iterative dashboard modifications (Phase 1 mockup).

import { ref } from 'vue'
import { useDashboard } from '../../composables/useDashboard'
import DashboardRenderer from './DashboardRenderer.vue'
import { BarChart3, Loader2, AlertCircle, MessageSquare, Sparkles, Send, ChevronUp, ChevronDown } from 'lucide-vue-next'

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

// ── Chat state ──
const chatInput = ref('')
const chatLoading = ref(false)
const lastExchange = ref<{ user: string; ai: string } | null>(null)
const chatExpanded = ref(true)

const MOCK_AI_RESPONSE =
  'He actualizado el gráfico de ventas por categoría, ahora muestra los datos agrupados por región con una paleta de colores más representativa. También ajusté el KPI principal para reflejar el ticket promedio en vez del total. Los cambios ya se reflejan en tu dashboard.'

function handleChatSubmit() {
  if (!chatInput.value.trim() || chatLoading.value) return
  const userMsg = chatInput.value.trim()
  chatLoading.value = true
  chatInput.value = ''
  setTimeout(() => {
    chatLoading.value = false
    lastExchange.value = { user: userMsg, ai: MOCK_AI_RESPONSE }
  }, 2000)
}
</script>

<template>
  <div class="relative">
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

    <!-- Chat overlay — visible only when dashboard is generated -->
    <div
      v-if="state === 'generated'"
      class="fixed bottom-6 left-1/2 -translate-x-1/2 z-40 w-full max-w-xl px-4"
    >
      <!-- Exchange bubble (last user + AI exchange) — only when expanded -->
      <div
        v-if="lastExchange && chatExpanded"
        class="bg-surface-raised border border-border rounded-xl p-3 mb-2 animate-slide-up"
      >
        <!-- User message -->
        <div class="flex items-start gap-2 mb-2">
          <MessageSquare class="h-4 w-4 mt-0.5 shrink-0 text-text-secondary" />
          <p class="text-sm text-text-secondary">{{ lastExchange.user }}</p>
        </div>
        <!-- AI response -->
        <div class="flex items-start gap-2">
          <Sparkles class="h-4 w-4 mt-0.5 shrink-0 text-primary" />
          <p class="text-sm text-text-primary">{{ lastExchange.ai }}</p>
        </div>
      </div>

      <!-- Input row -->
      <div class="flex gap-2 bg-surface-raised border border-border rounded-xl p-2">
        <button
          class="text-text-muted hover:text-text-secondary transition-colors px-1"
          @click="chatExpanded = !chatExpanded"
          :title="chatExpanded ? 'Minimizar chat' : 'Expandir chat'"
        >
          <ChevronDown v-if="chatExpanded" class="h-5 w-5" />
          <ChevronUp v-else class="h-5 w-5" />
        </button>
        <input
          v-model="chatInput"
          type="text"
          class="input bg-surface-base text-text-primary placeholder-text-muted text-sm flex-1 px-3 py-2 rounded-lg outline-none"
          placeholder="Pide un cambio al dashboard..."
          :disabled="chatLoading"
          @keydown.enter="handleChatSubmit"
        />
        <div v-if="chatLoading" class="spinner-sm" />
        <button
          v-else
          class="bg-primary hover:bg-primary-hover text-white rounded-lg px-3 py-2 text-sm font-medium transition-all disabled:opacity-40"
          :disabled="chatLoading || !chatInput.trim()"
          @click="handleChatSubmit"
        >
          <Send class="h-4 w-4" />
        </button>
      </div>
    </div>
  </div>
</template>
