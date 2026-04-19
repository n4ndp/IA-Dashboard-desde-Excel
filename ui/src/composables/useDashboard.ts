// ── useDashboard ──
// State machine composable for the analysis tab.
// Manages 'empty' → 'loading' → 'generated' lifecycle with mock data (Fase 1).

import { ref } from 'vue'
import type { DashboardState, DashboardWidgetMap } from '../types'
import { mockDashboard } from './mockDashboard'

export function useDashboard() {
  const state = ref<DashboardState>('empty')
  const widgets = ref<DashboardWidgetMap[]>([])

  async function generate(): Promise<void> {
    if (state.value !== 'empty') return

    state.value = 'loading'

    // Simulated AI generation delay (Fase 1 — replaced by API call in Fase 2)
    await new Promise((resolve) => setTimeout(resolve, 1500))

    widgets.value = mockDashboard.widgets
    state.value = 'generated'
  }

  return {
    state,
    widgets,
    generate,
  }
}
