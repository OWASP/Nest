'use client'

import { useSearchProjectsGraphQL } from 'hooks/useSearchProjectsGraphQL'
import { useRouter, useSearchParams } from 'next/navigation'
import { useState, useEffect } from 'react'
import { handleAppError } from 'app/global-error'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'
import type { SearchBackend } from 'utils/backendConfig'
interface UseSearchPageOptions {
  indexName: string
  pageTitle: string
  defaultSortBy?: string
  defaultOrder?: string
  defaultCategory?: string
  hitsPerPage?: number
  useBackend?: SearchBackend
}

interface UseSearchPageReturn<T> {
  items: T[]
  isLoaded: boolean
  currentPage: number
  totalPages: number
  searchQuery: string
  sortBy: string
  order: string
  category: string
  handleSearch: (query: string) => void
  handlePageChange: (page: number) => void
  handleSortChange: (sort: string) => void
  handleOrderChange: (order: string) => void
  handleCategoryChange: (category: string) => void
}

export function useSearchPage<T>({
  indexName,
  pageTitle,
  defaultSortBy = '',
  defaultOrder = '',
  defaultCategory = '',
  hitsPerPage = 25,
  useBackend = 'algolia',
}: UseSearchPageOptions): UseSearchPageReturn<T> {
  const router = useRouter()
  const searchParams = useSearchParams()

  const [items, setItems] = useState<T[]>([])
  const [currentPage, setCurrentPage] = useState<number>(
    Number.parseInt(searchParams.get('page') || '1')
  )
  const [searchQuery, setSearchQuery] = useState<string>(searchParams.get('q') || '')
  const [sortBy, setSortBy] = useState<string>(searchParams.get('sortBy') || defaultSortBy)
  const [order, setOrder] = useState<string>(searchParams.get('order') || defaultOrder)
  const [category, setCategory] = useState<string>(searchParams.get('category') || defaultCategory)
  const [totalPages, setTotalPages] = useState<number>(0)
  const [isLoaded, setIsLoaded] = useState<boolean>(false)

  useEffect(() => {
    if (searchParams) {
      const searchQueryParam = searchParams.get('q') || ''
      const sortByParam = searchParams.get('sortBy') || 'default'
      const orderParam = searchParams.get('order') || 'desc'
      const categoryParam = searchParams.get('category') || defaultCategory

      const searchQueryChanged = searchQuery !== searchQueryParam
      const sortOrOrderChanged = sortBy !== sortByParam || order !== orderParam

      if (categoryParam !== category) {
        setCategory(categoryParam)
      }

      // Reset page if search query changes (all indices) or if sort/order changes (projects only)
      if (searchQueryChanged || (indexName === 'projects' && sortOrOrderChanged)) {
        setCurrentPage(1)
      }
    }
  }, [searchParams, order, searchQuery, sortBy, category, indexName, defaultCategory])
  // Sync URL with state changes
  useEffect(() => {
    const params = new URLSearchParams()
    if (searchQuery) params.set('q', searchQuery)
    if (currentPage > 1) params.set('page', currentPage.toString())

    if (sortBy && sortBy !== 'default' && sortBy !== '') {
      params.set('sortBy', sortBy)
    }

    if (sortBy && sortBy !== 'default' && order && order !== '') {
      params.set('order', order)
    }

    if (category && category !== '') {
      params.set('category', category)
    }

    router.push(`?${params.toString()}`)
  }, [searchQuery, order, currentPage, sortBy, category, router])

  // GraphQL backend support
  const isGraphQLBackend = useBackend === 'graphql'
  const {
    items: graphqlItems,
    isLoaded: graphqlIsLoaded,
    totalCount: graphqlTotalCount,
    error: graphqlError,
  } = useSearchProjectsGraphQL(searchQuery, category, sortBy, order, currentPage, hitsPerPage, {
    enabled: isGraphQLBackend,
  })

  // Fetch data via Algolia
  useEffect(() => {
    if (useBackend !== 'algolia') return
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
          category ? [category] : []
        )

        if ('hits' in response) {
          setItems(response.hits)
          setTotalPages(response.totalPages ?? 0)
        } else {
          handleAppError(response)
        }
      } catch (error) {
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
    category,
    hitsPerPage,
    indexName,
    pageTitle,
    useBackend,
  ])

  // Use GraphQL data when backend is graphql
  useEffect(() => {
    if (useBackend !== 'graphql') return
    if (graphqlError) {
      handleAppError(graphqlError)
    }
    setItems((prev) => {
      const newItems = graphqlItems as T[]
      if (JSON.stringify(prev) === JSON.stringify(newItems)) return prev
      return newItems
    })
    const calculatedTotalPages = Math.ceil(graphqlTotalCount / hitsPerPage)
    setTotalPages((prev) => (prev === calculatedTotalPages ? prev : calculatedTotalPages))
    setIsLoaded((prev) => (prev === graphqlIsLoaded ? prev : graphqlIsLoaded))
  }, [graphqlItems, graphqlIsLoaded, graphqlError, graphqlTotalCount, hitsPerPage, useBackend])

  const handleSearch = (query: string) => {
    setSearchQuery(query)
    setCurrentPage(1)
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
    window.scrollTo({ top: 0, behavior: 'auto' })
  }

  const handleSortChange = (sort: string) => {
    setSortBy(sort)
    setCurrentPage(1)
  }

  const handleOrderChange = (newOrder: string) => {
    setOrder(newOrder)
    setCurrentPage(1)
  }

  const handleCategoryChange = (cat: string) => {
    setCategory(cat)
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
    category,
    handleSearch,
    handlePageChange,
    handleSortChange,
    handleOrderChange,
    handleCategoryChange,
  }
}
