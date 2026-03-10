export type CategoryOption = {
  key: string
  label: string
}

export type SearchWithFiltersProps = {
  isLoaded: boolean
  searchQuery: string
  sortBy: string
  order: string
  category: string
  sortOptions: { key: string; label: string }[]
  categoryOptions?: CategoryOption[]
  searchPlaceholder?: string
  onSearch: (query: string) => void
  onSortChange: (value: string) => void
  onOrderChange: (order: string) => void
  onCategoryChange: (category: string) => void
}
