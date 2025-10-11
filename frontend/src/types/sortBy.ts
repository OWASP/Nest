export type SortByProps = {
  sortOptions: { key: string; label: string }[]
  selectedSortOption: string
  selectedOrder: string
  onSortChange: (value: string) => void
  onOrderChange: (order: string) => void
}
