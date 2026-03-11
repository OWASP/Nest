import type { ProjectCategoryOption } from 'hooks/useProjectCategories'
import type { ReactNode } from 'react'

export type UnifiedSearchBarProps = {
  searchQuery: string
  sortBy: string
  order: string
  category: string
  isLoaded: boolean
  sortOptions: { key: string; label: string }[]
  categoryOptions: { key: string; label: string }[]
  categories?: ProjectCategoryOption[]
  filterOptions?: { key: string; label: string }[]
  searchPlaceholder?: string
  onSearch: (query: string) => void
  onSortChange: (value: string) => void
  onOrderChange: (order: string) => void
  onCategoryChange: (category: string) => void
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
  indexName: string
  empty?: string
  children?: ReactNode
}
