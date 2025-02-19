export interface MultiSearchBarProps {
  isLoaded: boolean
  placeholder: string
  indexes: string[]
  initialValue?: string
}

export interface Suggestion {
  indexName: string
  hits: any[]
  totalPages: number
}
