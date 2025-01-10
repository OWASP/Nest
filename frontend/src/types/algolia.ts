export interface AlgoliaResponseType<T> {
  hits: T[]
  totalPages: number
}

export interface AlgoliaRequestType {
  aroundLatLngViaIP?: boolean
  attributesToHighlight: string[]
  attributesToRetrieve: string[]
  distinct?: number
  filters?: string
  hitsPerPage: number
  indexName: string
  minProximity?: number
  page: number
  query: string
  removeWordsIfNoResults: 'none' | 'lastWords' | 'firstWords' | 'allOptional'
  typoTolerance?: string
}
