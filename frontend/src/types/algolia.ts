export type AlgoliaResponse<T> = {
  hits: T[]
  totalPages?: number
}

export type AlgoliaRequest = {
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
