export type SortByProps = {
  id?: string
  'aria-label'?: string
  sortOptions: { key: string; label: string }[]
  selectedSortOption: string
  selectedOrder: string
  onSortChange: (value: string) => void
  onOrderChange: (order: string) => void
  showLabel?: boolean
  hideOrderButton?: boolean
  className?: string
  containerClassName?: string
  triggerClassName?: string
  buttonClassName?: string
}
