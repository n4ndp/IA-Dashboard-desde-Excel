// ── useSkeleton ──
// Generates skeleton placeholder data for loading states.

export function useSkeleton() {
  function cardSkeletons(count = 6) {
    return Array.from({ length: count }, (_, i) => ({ id: i }))
  }

  function tableRowSkeletons(colCount: number, rowCount = 10) {
    return Array.from({ length: rowCount }, (_, rowIdx) => ({
      id: rowIdx,
      cells: Array.from({ length: colCount }, (_, colIdx) => ({
        id: colIdx,
        width: colIdx === 0 ? '40%' : `${30 + Math.random() * 40}%`,
      })),
    }))
  }

  function metricSkeletons(count = 4) {
    return Array.from({ length: count }, (_, i) => ({ id: i }))
  }

  return { cardSkeletons, tableRowSkeletons, metricSkeletons }
}
