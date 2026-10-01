'use client'

import { useRouter, useSearchParams } from 'next/navigation'
import { useMemo, useState, useEffect, useRef } from 'react'
import { handleAppError } from 'app/global-error'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'

interface UseSearchPageOptions {
  indexName: string
  pageTitle: string
  defaultSortBy?: string
  defaultOrder?: string
  hitsPerPage?: number
  facetFilters?: string[]
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

interface SearchUrlState {
  currentPage: number
  searchQuery: string
  sortBy: string
  order: string
}

const parsePageParam = (value: string | null): number => {
  const page = (value || '').trim()
  const parsed = Number(page)
  return /^[1-9]\d*$/.test(page) && Number.isFinite(parsed) ? parsed : 1
}

const normalizedPageParam = (params: URLSearchParams): string => {
  const page = params.get('page')
  return !page || page === '1' ? '' : page
}

const buildSearchQueryString = ({
  currentPage,
  searchQuery,
  sortBy,
  order,
}: SearchUrlState): string => {
  const params = new URLSearchParams()
  if (searchQuery) params.set('q', searchQuery)
  if (currentPage > 1) params.set('page', currentPage.toString())

  if (sortBy && sortBy !== 'default' && sortBy !== '') {
    params.set('sortBy', sortBy)
  }

  if (sortBy !== 'default' && order && order !== '') {
    params.set('order', order)
  }

  return params.toString()
}

const isSameSearchQuery = (left: string, right: string): boolean => {
  const leftParams = new URLSearchParams(left)
  const rightParams = new URLSearchParams(right)

  return (
    (leftParams.get('q') || '') === (rightParams.get('q') || '') &&
    normalizedPageParam(leftParams) === normalizedPageParam(rightParams) &&
    (leftParams.get('sortBy') || '') === (rightParams.get('sortBy') || '') &&
    (leftParams.get('order') || '') === (rightParams.get('order') || '')
  )
}

export function useSearchPage<T>({
  indexName,
  pageTitle,
  defaultSortBy = '',
  defaultOrder = '',
  hitsPerPage,
  facetFilters = [],
}: UseSearchPageOptions): UseSearchPageReturn<T> {
  const router = useRouter()
  const searchParams = useSearchParams()

  const [items, setItems] = useState<T[]>([])
  const [currentPage, setCurrentPage] = useState<number>(parsePageParam(searchParams.get('page')))
  const [searchQuery, setSearchQuery] = useState<string>(searchParams.get('q') || '')
  const [sortBy, setSortBy] = useState<string>(searchParams.get('sortBy') || defaultSortBy)
  const [order, setOrder] = useState<string>(searchParams.get('order') || defaultOrder)
  const [totalPages, setTotalPages] = useState<number>(0)
  const [isLoaded, setIsLoaded] = useState<boolean>(false)

  const facetFiltersKey = JSON.stringify(facetFilters)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const stableFacetFilters = useMemo(() => facetFilters, [facetFiltersKey])
  const prevFacetFiltersKeyRef = useRef(facetFiltersKey)
  const prevSearchParamsRef = useRef(searchParams.toString())
  const skipNextUrlPushRef = useRef(false)
  const stateRef = useRef<SearchUrlState>({
    currentPage,
    searchQuery,
    sortBy,
    order,
  })
  stateRef.current = { currentPage, searchQuery, sortBy, order }
  const fetchVersion = useRef(0)

  useEffect(() => {
    // Only reset when filters actually change (Strict Mode safe — skips mount / re-invoke).
    if (prevFacetFiltersKeyRef.current === facetFiltersKey) {
      return
    }
    prevFacetFiltersKeyRef.current = facetFiltersKey
    setCurrentPage(1)
  }, [facetFiltersKey])

  // Sync state from URL when searchParams change (back/forward or push acknowledgment).
  useEffect(() => {
    const query = searchParams.toString()
    if (query === prevSearchParamsRef.current) {
      return
    }

    // Local push already updated prev optimistically — treat matching URLs as acks.
    if (isSameSearchQuery(query, buildSearchQueryString(stateRef.current))) {
      prevSearchParamsRef.current = query
      return
    }

    prevSearchParamsRef.current = query

    const nextPage = parsePageParam(searchParams.get('page'))
    const nextSearchQuery = searchParams.get('q') || ''
    const nextSortBy = searchParams.get('sortBy') || defaultSortBy
    const nextOrder = searchParams.get('order') || defaultOrder

    const {
      currentPage: page,
      searchQuery: queryText,
      sortBy: sort,
      order: sortOrder,
    } = stateRef.current
    const stateChanged =
      nextPage !== page ||
      nextSearchQuery !== queryText ||
      nextSortBy !== sort ||
      nextOrder !== sortOrder

    // Avoid a stale skip flag when the URL is non-canonical but state is unchanged.
    if (!stateChanged) {
      return
    }

    skipNextUrlPushRef.current = true
    setCurrentPage(nextPage)
    setSearchQuery(nextSearchQuery)
    setSortBy(nextSortBy)
    setOrder(nextOrder)
  }, [searchParams, defaultSortBy, defaultOrder])

  // Sync URL with state changes (do not depend on searchParams — avoids clobbering back/forward).
  useEffect(() => {
    if (skipNextUrlPushRef.current) {
      skipNextUrlPushRef.current = false
      return
    }

    const nextQuery = buildSearchQueryString({
      currentPage,
      searchQuery,
      sortBy,
      order,
    })

    if (isSameSearchQuery(nextQuery, prevSearchParamsRef.current)) {
      return
    }

    prevSearchParamsRef.current = nextQuery
    router.push(nextQuery ? `?${nextQuery}` : '?')
  }, [searchQuery, order, currentPage, sortBy, router])

  // Fetch data when state changes
  useEffect(() => {
    const requestVersion = ++fetchVersion.current
    setIsLoaded(false)

    const fetchData = async () => {
      try {
        let computedIndexName = indexName

        // Check if valid sort option is selected
        const hasValidSort = sortBy && sortBy !== 'default'

        if (hasValidSort) {
          // if sorting is active then appends the sort field and order to the base index name.
          const orderSuffix = order && order !== '' ? `_${order}` : ''
          computedIndexName = `${indexName}_${sortBy}${orderSuffix}`
        }

        const response = await fetchAlgoliaData<T>(
          computedIndexName,
          searchQuery,
          currentPage,
          hitsPerPage,
          [...stableFacetFilters]
        )

        if (requestVersion !== fetchVersion.current) return

        if ('hits' in response) {
          setItems(response.hits)
          setTotalPages(response.totalPages ?? 0)
        } else {
          handleAppError(response)
        }
      } catch (error) {
        if (requestVersion !== fetchVersion.current) return
        handleAppError(error)
      }
      setIsLoaded(true)
    }

    fetchData()
  }, [
    currentPage,
    searchQuery,
    order,
    sortBy,
    hitsPerPage,
    indexName,
    pageTitle,
    stableFacetFilters,
  ])

  const handleSearch = (query: string) => {
    setSearchQuery(query)
    setCurrentPage(1)
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
    window.scrollTo({ top: 0, behavior: 'auto' })
  }

  const handleSortChange = (sort: string) => {
    if (sort === sortBy) {
      return
    }
    setSortBy(sort)
    setCurrentPage(1)
  }

  const handleOrderChange = (nextOrder: string) => {
    if (nextOrder === order) {
      return
    }
    setOrder(nextOrder)
    setCurrentPage(1)
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
