<script setup lang="ts">
// ── AppSidebar ──
// Dashboard-only collapsible sidebar with project name and nav links.

import { Table2, Lightbulb, PanelLeftClose, PanelLeft } from 'lucide-vue-next'

defineProps<{
  projectName: string
}>()

const collapsed = defineModel<boolean>('collapsed', { default: false })
</script>

<template>
  <aside
    class="flex flex-col border-r border-border bg-surface-raised transition-all duration-300"
    :class="collapsed ? 'w-14' : 'w-56'"
  >
    <!-- Toggle button -->
    <div class="flex items-center justify-end px-2 py-3">
      <button
        class="flex h-7 w-7 items-center justify-center rounded-md text-text-muted hover:text-text-primary hover:bg-surface-overlay transition-colors"
        @click="collapsed = !collapsed"
      >
        <PanelLeftClose v-if="!collapsed" class="h-4 w-4" />
        <PanelLeft v-else class="h-4 w-4" />
      </button>
    </div>

    <!-- Project name -->
    <div v-if="!collapsed" class="px-4 pb-4">
      <h3 class="text-sm font-semibold text-text-primary truncate">
        {{ projectName }}
      </h3>
    </div>

    <!-- Nav links -->
    <nav class="flex-1 px-2 space-y-1">
      <a
        href="#tables"
        class="flex items-center gap-2.5 rounded-md px-2 py-1.5 text-sm text-text-secondary hover:text-text-primary hover:bg-surface-overlay transition-colors"
        :class="collapsed && 'justify-center'"
      >
        <Table2 class="h-4 w-4 shrink-0" />
        <span v-if="!collapsed">Tablas</span>
      </a>
      <a
        href="#insights"
        class="flex items-center gap-2.5 rounded-md px-2 py-1.5 text-sm text-text-secondary hover:text-text-primary hover:bg-surface-overlay transition-colors"
        :class="collapsed && 'justify-center'"
      >
        <Lightbulb class="h-4 w-4 shrink-0" />
        <span v-if="!collapsed">Insights</span>
      </a>
    </nav>
  </aside>
</template>
