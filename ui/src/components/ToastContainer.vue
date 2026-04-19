<script setup lang="ts">
// ── ToastContainer ──
// Fixed top-right toast stack. Teleports to body, z-50 above all content.

import { useToast } from '../composables/useToast'

const { toasts, dismiss } = useToast()

function borderColor(type: string) {
  switch (type) {
    case 'success': return 'border-l-green-500'
    case 'error': return 'border-l-red-500'
    default: return 'border-l-indigo-500'
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      aria-live="polite"
      class="fixed top-4 right-4 z-50 flex flex-col gap-2"
      style="width: 360px;"
    >
      <TransitionGroup
        name="toast"
        tag="div"
        class="flex flex-col gap-2"
      >
        <div
          v-for="toast in toasts"
          :key="toast.id"
          class="border-l-4 rounded-lg bg-surface-raised shadow-lg overflow-hidden"
          :class="borderColor(toast.type)"
        >
          <div class="flex items-start gap-3 px-4 py-3">
            <p class="flex-1 text-sm text-text-primary">{{ toast.message }}</p>
            <button
              class="shrink-0 text-text-muted hover:text-text-primary transition-colors"
              @click="dismiss(toast.id)"
            >
              ✕
            </button>
          </div>
          <!-- Progress bar -->
          <div class="h-0.5 bg-border">
            <div
              class="h-full toast-progress"
              :style="{ '--duration': `${toast.duration}ms` }"
            />
          </div>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
/* Slide in from right */
.toast-enter-active {
  transition: transform 150ms ease-out, opacity 150ms ease-out;
}
.toast-leave-active {
  transition: opacity 200ms ease-in;
}
.toast-enter-from {
  transform: translateX(100%);
  opacity: 0;
}
.toast-leave-to {
  opacity: 0;
}

/* Progress bar animation */
.toast-progress {
  background: rgb(99 102 241 / 0.4);
  animation: shrink var(--duration) linear forwards;
}
@keyframes shrink {
  from { width: 100%; }
  to { width: 0%; }
}
</style>
