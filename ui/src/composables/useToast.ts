// ── useToast ──
// Singleton toast notification system. Module-level state shared across all callers.

import { ref, readonly } from 'vue'

export interface Toast {
  id: number
  message: string
  type: 'success' | 'error' | 'info'
  duration: number
  createdAt: Date
}

// Module-level state — singleton across the app
const toasts = ref<Toast[]>([])
const MAX_TOASTS = 5
const timeouts = new Map<number, ReturnType<typeof setTimeout>>()

let nextId = 0

export function useToast() {
  function show(message: string, type: Toast['type'] = 'info', duration = 4000) {
    // Stagger: if at MAX, dismiss oldest first
    if (toasts.value.length >= MAX_TOASTS) {
      const oldest = toasts.value[0]
      dismiss(oldest.id)
    }
    const id = nextId++
    toasts.value.push({ id, message, type, duration, createdAt: new Date() })
    // Auto-dismiss
    const timeout = setTimeout(() => dismiss(id), duration)
    timeouts.set(id, timeout)
  }

  function dismiss(id: number) {
    const idx = toasts.value.findIndex(t => t.id === id)
    if (idx === -1) return
    toasts.value.splice(idx, 1)
    const t = timeouts.get(id)
    if (t) {
      clearTimeout(t)
      timeouts.delete(id)
    }
  }

  return { toasts: readonly(toasts), show, dismiss }
}
