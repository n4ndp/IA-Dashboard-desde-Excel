<script setup lang="ts">
import { ref, computed } from 'vue'

interface Column {
  id: number
  name: string
  type: string
}

interface Row {
  id: number
  data: Record<string, unknown>
}

const props = defineProps<{
  sheetName: string
  columns: Column[]
  rows: Row[]
}>()

const isExpanded = ref(true)
const maxVisibleRows = 15

const isTruncated = computed(() => props.rows.length > maxVisibleRows)
const showAll = ref(false)

const visibleRows = computed(() => {
  if (showAll.value || !isTruncated.value) return props.rows
  return props.rows.slice(0, maxVisibleRows)
})

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return '—'
  return String(value)
}

function toggleExpand() {
  isExpanded.value = !isExpanded.value
}

function toggleShowAll() {
  showAll.value = !showAll.value
}

function typeColor(type: string): string {
  switch (type) {
    case 'number':
      return 'text-sky-400 bg-sky-500/10 ring-sky-500/20'
    case 'date':
      return 'text-violet-400 bg-violet-500/10 ring-violet-500/20'
    case 'string':
    default:
      return 'text-slate-400 bg-slate-500/10 ring-slate-500/20'
  }
}
</script>

<template>
  <div
    class="overflow-hidden rounded-xl border border-slate-800/60 bg-midnight-900/60 transition-all"
  >
    <!-- Card header -->
    <button
      class="flex w-full items-center justify-between px-5 py-4 text-left transition-colors hover:bg-midnight-800/40"
      @click="toggleExpand"
    >
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
              d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 0 1-1.125-1.125M3.375 19.5h1.5C5.496 19.5 6 18.996 6 18.375m-2.625 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-1.5A1.125 1.125 0 0 1 18 18.375M20.625 4.5H3.375m17.25 0c.621 0 1.125.504 1.125 1.125M20.625 4.5h-1.5C18.504 4.5 18 5.004 18 5.625m3.75 0v1.5c0 .621-.504 1.125-1.125 1.125M3.375 4.5c-.621 0-1.125.504-1.125 1.125M3.375 4.5h1.5C5.496 4.5 6 5.004 6 5.625m-3.75 0v1.5c0 .621.504 1.125 1.125 1.125m0 0h1.5m-1.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125m1.5-3.75C5.496 8.25 6 7.746 6 7.125v-1.5M4.875 8.25C5.496 8.25 6 8.754 6 9.375v1.5c0 .621-.504 1.125-1.125 1.125m1.5 0h12m-12 0c-.621 0-1.125.504-1.125 1.125M18 12h1.5m-1.5 0c.621 0 1.125.504 1.125 1.125m0 0v1.5c0 .621-.504 1.125-1.125 1.125M18 12c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h1.5m-1.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125"
            />
          </svg>
        </div>
        <div>
          <h3 class="text-sm font-semibold text-slate-200">{{ sheetName }}</h3>
          <p class="mt-0.5 text-xs text-slate-500">
            {{ rows.length }} filas · {{ columns.length }} columnas
          </p>
        </div>
      </div>

      <svg
        class="h-4 w-4 text-slate-500 transition-transform"
        :class="isExpanded ? 'rotate-180' : ''"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="2"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="m19.5 8.25-7.5 7.5-7.5-7.5"
        />
      </svg>
    </button>

    <!-- Table content (collapsible) -->
    <div v-show="isExpanded">
      <div class="overflow-x-auto">
        <table class="min-w-full">
          <thead>
            <tr class="border-y border-slate-800/60">
              <th
                v-for="col in columns"
                :key="col.id"
                class="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500"
              >
                <div class="flex items-center gap-1.5">
                  {{ col.name }}
                  <span
                    class="inline-flex items-center rounded-md px-1.5 py-0.5 text-[10px] font-medium ring-1 ring-inset"
                    :class="typeColor(col.type)"
                  >
                    {{ col.type }}
                  </span>
                </div>
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/40">
            <tr
              v-for="(row, idx) in visibleRows"
              :key="row.id"
              class="transition-colors hover:bg-blue-500/[0.03]"
              :class="idx % 2 === 0 ? 'bg-transparent' : 'bg-slate-900/30'"
            >
              <td
                v-for="col in columns"
                :key="col.id"
                class="whitespace-nowrap px-5 py-2.5 text-sm text-slate-300"
              >
                {{ formatValue(row.data[col.name]) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Show more / less -->
      <div
        v-if="isTruncated"
        class="border-t border-slate-800/60 px-5 py-3"
      >
        <button
          class="text-xs font-medium text-blue-400 transition hover:text-blue-300"
          @click="toggleShowAll"
        >
          {{ showAll ? 'Ver menos' : `Ver todas las ${rows.length} filas` }}
        </button>
      </div>
    </div>
  </div>
</template>
