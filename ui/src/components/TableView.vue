<script setup lang="ts">
// ── TableView ──
// TanStack table with type badges, collapsible, row truncation at 15.

import { ref, computed } from 'vue'
import {
  useVueTable,
  getCoreRowModel,
  type ColumnDef,
} from '@tanstack/vue-table'
import { ChevronDown } from 'lucide-vue-next'
import type { SingleTableResponse, RowOut } from '../types'

const props = defineProps<{
  table: SingleTableResponse
}>()

const isExpanded = ref(true)
const maxVisibleRows = 15
const showAll = ref(false)

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return '—'
  return String(value)
}

const colDefs = computed<ColumnDef<RowOut, string>[]>(() =>
  props.table.columns.map((col) => ({
    id: col.name,
    accessorFn: (row: RowOut) => formatValue(row.data[col.name]),
    header: col.name,
    cell: (info: { getValue: () => string }) => info.getValue(),
    size: 120,
    minSize: 80,
  })),
)

const rows = computed(() => props.table.rows)

const vueTable = useVueTable({
  get data() { return rows.value },
  get columns() { return colDefs.value },
  getCoreRowModel: getCoreRowModel(),
})

const isTruncated = computed(() => props.table.rows.length > maxVisibleRows)

const visibleRows = computed(() => {
  const allRows = vueTable.getRowModel().rows
  if (showAll.value || !isTruncated.value) return allRows
  return allRows.slice(0, maxVisibleRows)
})

// Template helpers — avoid repeating props.table in template
const sheetName = computed(() => props.table.sheet_name)
const columns = computed(() => props.table.columns)
const rowCount = computed(() => props.table.rows.length)
const colCount = computed(() => props.table.columns.length)
</script>

<template>
  <div class="rounded-lg border border-border transition-all">
    <!-- Header -->
    <button
      class="flex w-full items-center justify-between px-4 py-3 text-left transition-colors hover:bg-surface-overlay/40"
      @click="isExpanded = !isExpanded"
    >
      <div class="flex items-center gap-3">
        <h3 class="text-sm font-medium text-text-primary">{{ sheetName }}</h3>
        <span class="text-xs text-text-muted">{{ rowCount }} × {{ colCount }}</span>
      </div>
      <ChevronDown
        class="h-3.5 w-3.5 text-text-muted transition-transform duration-200"
        :class="isExpanded ? 'rotate-180' : ''"
      />
    </button>

    <!-- Table body -->
    <div v-show="isExpanded">
      <div class="overflow-x-auto border-t border-border">
        <table class="min-w-full">
          <thead>
            <tr>
              <th
                v-for="col in columns"
                :key="col.id"
                class="px-4 py-2 text-left text-xs font-medium text-text-muted"
                style="min-width: 80px"
              >
                {{ col.name }}
              </th>
            </tr>
            <tr class="border-t border-border">
              <td
                v-for="col in columns"
                :key="'t-' + col.id"
                class="px-4 py-1"
              >
                <span class="badge" :class="`badge-${col.type}`">{{ col.type }}</span>
              </td>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in visibleRows"
              :key="row.id"
              class="border-t border-border/60 hover:bg-surface-overlay/30"
            >
              <td
                v-for="col in columns"
                :key="col.id"
                class="px-4 py-2 text-sm text-text-secondary whitespace-nowrap"
              >
                {{ formatValue(row.original.data[col.name]) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="isTruncated" class="border-t border-border px-4 py-2">
        <button
          class="text-xs text-text-muted hover:text-text-secondary transition-colors"
          @click="showAll = !showAll"
        >
          {{ showAll ? 'Ver menos' : `Ver ${rowCount} filas` }}
        </button>
      </div>
    </div>
  </div>
</template>
