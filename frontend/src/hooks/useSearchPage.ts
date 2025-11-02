'use client'

import { useRouter, useSearchParams } from 'next/navigation'
import { useState, useEffect } from 'react'
import { handleAppError } from 'app/global-error'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'
interface UseSearchPageOptions {
  indexName: string
  pageTitle: string
  defaultSortBy?: string
  defaultOrder?: string
  hitsPerPage?: number
}

interface UseSearchPageReturn<T> {
  items: T[]
  isLoaded: boolean
  currentPage: number
  totalPages: number
  searchQuery: string
  sortBy: string
  order: string
  handleSearch: (query: string) => void
  handlePageChange: (page: number) => void
  handleSortChange: (sort: string) => void
  handleOrderChange: (order: string) => void
}

/**
 * Provides search state, synchronizes that state with the URL, and fetches paginated results from Algolia.
 *
 * @param indexName - Base Algolia index name used to fetch results; a computed variant may be used when sorting/order are applied
 * @param pageTitle - Page title used as a dependency for data refreshes
 * @param defaultSortBy - Optional default sort key applied when no `sortBy` parameter is present
 * @param defaultOrder - Optional default order ('asc' or 'desc') applied when no `order` parameter is present
 * @param hitsPerPage - Optional number of results to fetch per page
 * @returns An object containing:
 *  - `items`: the current page of results of type `T[]`
 *  - `isLoaded`: `true` when a fetch has completed, `false` while loading
 *  - `currentPage`: the active page number
 *  - `totalPages`: total number of available pages
 *  - `searchQuery`: current query string
 *  - `sortBy`: current sort key
 *  - `order`: current sort order
 *  - `handleSearch(query: string)`: updates the search query
 *  - `handlePageChange(page: number)`: updates the current page and scrolls to top
 *  - `handleSortChange(sort: string)`: updates the sort key
 *  - `handleOrderChange(order: string)`: updates the sort order
 */
export function useSearchPage<T>({
  indexName,
  pageTitle,
  defaultSortBy = '',
  defaultOrder = '',
  hitsPerPage,
}: UseSearchPageOptions): UseSearchPageReturn<T> {
  const router = useRouter()
  const searchParams = useSearchParams()

  const [items, setItems] = useState<T[]>([])
  const [currentPage, setCurrentPage] = useState<number>(parseInt(searchParams.get('page') || '1'))
  const [searchQuery, setSearchQuery] = useState<string>(searchParams.get('q') || '')
  const [sortBy, setSortBy] = useState<string>(searchParams.get('sortBy') || defaultSortBy)
  const [order, setOrder] = useState<string>(searchParams.get('order') || defaultOrder)
  const [totalPages, setTotalPages] = useState<number>(0)
  const [isLoaded, setIsLoaded] = useState<boolean>(false)

  // Sync state with URL changes
  useEffect(() => {
    if (searchParams) {
      const searchQueryParam = searchParams.get('q') || ''
      const sortByParam = searchParams.get('sortBy') || 'default'
      const orderParam = searchParams.get('order') || 'desc'
      if (
        indexName === 'projects' &&
        (searchQuery !== searchQueryParam || sortBy !== sortByParam || order !== orderParam)
      ) {
        setCurrentPage(1)
      } else if (searchQuery !== searchQueryParam) {
        setCurrentPage(1)
      }
    }
  }, [searchParams, order, searchQuery, sortBy, indexName])
  // Sync URL with state changes
  useEffect(() => {
    const params = new URLSearchParams()
    if (searchQuery) params.set('q', searchQuery)
    if (currentPage > 1) params.set('page', currentPage.toString())

    if (sortBy && sortBy !== 'default' && sortBy[0] !== 'default' && sortBy !== '') {
      params.set('sortBy', sortBy)
    }

    if (sortBy !== 'default' && sortBy[0] !== 'default' && order && order !== '') {
      params.set('order', order)
    }

    router.push(`?${params.toString()}`)
  }, [searchQuery, order, currentPage, sortBy, router])
  // Update URL when state changes
  useEffect(() => {
    setIsLoaded(false)

    const fetchData = async () => {
      try {
        let computedIndexName = indexName

        const hasValidSort = sortBy && sortBy !== 'default' && sortBy[0] !== 'default'

        if (hasValidSort) {
          const orderSuffix = order && order !== '' ? `_${order}` : ''
          computedIndexName = `${indexName}_${sortBy}${orderSuffix}`
        }

        const response = await fetchAlgoliaData<T>(
          computedIndexName,
          searchQuery,
          currentPage,
          hitsPerPage
        )

        if ('hits' in response) {
          setItems(response.hits)
          setTotalPages(response.totalPages as number)
        } else {
          handleAppError(response)
        }
      } catch (error) {
        handleAppError(error)
      }
      setIsLoaded(true)
    }

    fetchData()
  }, [currentPage, searchQuery, order, sortBy, hitsPerPage, indexName, pageTitle])

  const handleSearch = (query: string) => {
    setSearchQuery(query)
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
    window.scrollTo({ top: 0, behavior: 'auto' })
  }

  const handleSortChange = (sort: string) => {
    setSortBy(sort)
  }

  const handleOrderChange = (order: string) => {
    setOrder(order)
  }

  return {
    items,
    isLoaded,
    currentPage,
    totalPages,
    searchQuery,
    sortBy,
    order,
    handleSearch,
    handlePageChange,
    handleSortChange,
    handleOrderChange,
  }
}