export interface MultiSearchBarProps {
  isLoaded: boolean
  placeholder: string
  indexes: string[]
  initialValue?: string
}

export interface Suggestion {
  indexName: string
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  hits: any[]
  totalPages: number
}
