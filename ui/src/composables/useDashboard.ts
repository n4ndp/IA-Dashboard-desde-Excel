// ── useDashboard ──
// State machine composable for the analysis tab.
// Manages 'empty' → 'loading' → 'generated' | 'error' lifecycle.
// Calls real API for dashboard generation.

import { ref } from 'vue'
import type { DashboardState, DashboardWidgetMap } from '../types'
import { chatDashboard } from '../services/endpoints'

export function useDashboard(userId: number, projectId: number, existingConfig?: { widgets: DashboardWidgetMap[] } | null) {
  const state = ref<DashboardState>('empty')
  const widgets = ref<DashboardWidgetMap[]>([])
  const errorMessage = ref<string>('')
  const resumenEjecutivo = ref<string>('')

  // Initialize from existing dashboard_config if present
  if (existingConfig?.widgets?.length) {
    widgets.value = existingConfig.widgets
    state.value = 'generated'
  }

  async function generate(): Promise<void> {
    if (state.value === 'loading') return

    state.value = 'loading'
    errorMessage.value = ''

    try {
      const response = await fetch(
        `/api/users/${userId}/projects/${projectId}/generate-dashboard`,
        { method: 'POST' },
      )

      if (!response.ok) {
        const body = await response.json().catch(() => ({}))
        const msg = body.detail || `Error ${response.status}: ${response.statusText}`

        if (response.status === 408) {
          errorMessage.value = 'La generación del dashboard tardó demasiado. Intentalo de nuevo.'
        } else {
          errorMessage.value = msg
        }

        state.value = 'error'
        return
      }

      const data = await response.json()
      widgets.value = data.widgets ?? []
      resumenEjecutivo.value = data.resumen_ejecutivo || ''
      state.value = 'generated'
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error de conexión al generar el dashboard'
      errorMessage.value = msg
      state.value = 'error'
    }
  }

  async function iterate(prompt: string): Promise<string | undefined> {
    if (state.value === 'loading') return undefined

    const previousWidgets = widgets.value
    errorMessage.value = ''

    try {
      const data = await chatDashboard(userId, projectId, prompt, { widgets: widgets.value })
      if (!Array.isArray(data.widgets)) {
        throw new Error('Respuesta inválida del servidor al iterar el dashboard')
      }

      widgets.value = data.widgets
      resumenEjecutivo.value = data.resumen_ejecutivo || ''
      return data.action_message || data.resumen_ejecutivo
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error de conexión al iterar el dashboard'
      errorMessage.value = msg
      widgets.value = previousWidgets
      return undefined
    }
  }

  return {
    state,
    widgets,
    errorMessage,
    resumenEjecutivo,
    generate,
    iterate,
  }
}
