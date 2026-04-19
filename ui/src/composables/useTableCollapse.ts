// ── useTableCollapse ──
// Singleton composable for Dashboard table collapse/expand state.

import { ref, readonly } from 'vue'

const expandedTableIds = ref(new Set<number>())

export function useTableCollapse() {
  function expandAll(ids: number[]) {
    ids.forEach(id => expandedTableIds.value.add(id))
  }

  function collapseAll() {
    expandedTableIds.value.clear()
  }

  function isExpanded(id: number): boolean {
    return expandedTableIds.value.has(id)
  }

  function toggle(id: number) {
    if (expandedTableIds.value.has(id)) {
      expandedTableIds.value.delete(id)
    } else {
      expandedTableIds.value.add(id)
    }
  }

  return { expandedTableIds: readonly(expandedTableIds), expandAll, collapseAll, isExpanded, toggle }
}
