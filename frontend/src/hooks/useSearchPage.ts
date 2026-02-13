'use client'

import { useSearchParams } from 'next/navigation'
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

export function useSearchPage<T>({
  indexName,
  pageTitle,
  defaultSortBy = '',
  defaultOrder = '',
  hitsPerPage,
}: UseSearchPageOptions): UseSearchPageReturn<T> {
  const searchParams = useSearchParams()

  const [items, setItems] = useState<T[]>([])
  const [currentPage, setCurrentPage] = useState<number>(
    Number.parseInt(searchParams.get('page') || '1')
  )
  const [searchQuery, setSearchQuery] = useState<string>(searchParams.get('q') || '')
  const [sortBy, setSortBy] = useState<string>(searchParams.get('sortBy') || defaultSortBy)
  const [order, setOrder] = useState<string>(searchParams.get('order') || defaultOrder)
  const [totalPages, setTotalPages] = useState<number>(0)
  const [isLoaded, setIsLoaded] = useState<boolean>(false)

  useEffect(() => {
    setIsLoaded(false)

    const controller = new AbortController()

    const fetchData = async () => {
      try {
        let computedIndexName = indexName
        const hasValidSort = sortBy && sortBy !== 'default'

        if (hasValidSort) {
          const orderSuffix = order && order !== '' ? `_${order}` : ''
          computedIndexName = `${indexName}_${sortBy}${orderSuffix}`
        }

        const response = await fetchAlgoliaData<T>(
          computedIndexName,
          searchQuery,
          currentPage,
          hitsPerPage,
          [],
          controller.signal
        )

        if (controller.signal.aborted) return

        if ('hits' in response) {
          setItems(response.hits)
          setTotalPages(response.totalPages ?? 0)
        } else {
          handleAppError(response)
        }
      } catch (error) {
        if ((error as Error).name !== 'AbortError') {
          handleAppError(error)
        }
      }

      if (!controller.signal.aborted) {
        setIsLoaded(true)
      }
    }

    fetchData()

    return () => {
      controller.abort()
    }
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
