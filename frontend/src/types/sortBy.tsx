import { ListCollection } from '@chakra-ui/react'
export interface SortByProps {
  sortOptions: ListCollection
  selectedSortOption: string
  selectedOrder: string
  onSortChange: (value: string) => void
  onOrderChange: (order: string) => void
}
