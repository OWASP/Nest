import { useState, useEffect, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'

import { fetchAlgoliaData } from 'lib/api'
import { useErrorHandler } from 'lib/hooks/useErrorHandler'
import { AlgoliaResponseType, ErrorConfig } from 'lib/types'

interface UseSearchPageOptions {
  indexName: string
  pageTitle: string
}

interface UseSearchPageReturn<T> {
  items: T[]
  isLoaded: boolean
  currentPage: number
  totalPages: number
  searchQuery: string
  /* eslint-disable-next-line */
  handleSearch: (query: string) => void
  /* eslint-disable-next-line */
  handlePageChange: (page: number) => void
  error: ErrorConfig | null
  retry: () => void
}

export function useSearchPage<T>({
  indexName,
  pageTitle,
}: UseSearchPageOptions): UseSearchPageReturn<T> {
  const [searchParams, setSearchParams] = useSearchParams()
  const [items, setItems] = useState<T[]>([])
  const [currentPage, setCurrentPage] = useState<number>(parseInt(searchParams.get('page') || '1'))
  const [searchQuery, setSearchQuery] = useState<string>(searchParams.get('q') || '')
  const [totalPages, setTotalPages] = useState<number>(0)
  const [isLoaded, setIsLoaded] = useState<boolean>(false)
  const { error, handleError, clearError, retry } = useErrorHandler('search')
  const [shouldFetch, setShouldFetch] = useState(false)

  const fetchData = useCallback(async (): Promise<void> => {
    try {
      const data: AlgoliaResponseType<T> = await fetchAlgoliaData<T>(
        indexName,
        searchQuery,
        currentPage
      )
      setItems(data.hits)
      setTotalPages(data.totalPages)
      clearError()
    } catch (error) {
      handleError(error)
    }
    setIsLoaded(true)
    setShouldFetch(false)
  }, [indexName, searchQuery, currentPage, clearError, handleError])

  useEffect(() => {
    const params = new URLSearchParams()
    if (searchQuery) params.set('q', searchQuery)
    if (currentPage > 1) params.set('page', currentPage.toString())
    setSearchParams(params)
  }, [searchQuery, currentPage, setSearchParams])

  useEffect(() => {
    document.title = pageTitle
    setIsLoaded(false)
    setShouldFetch(true)
  }, [pageTitle])

  useEffect(() => {
    if (!shouldFetch) return
    fetchData()
  }, [shouldFetch, fetchData])

  const handleSearch = (query: string) => {
    setSearchQuery(query)
    setCurrentPage(1)
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
    window.scrollTo({
      top: 0,
      behavior: 'auto',
    })
  }

  const retrySearch = useCallback(() => {
    retry(fetchData)
    setShouldFetch(true)
  }, [retry, fetchData])

  return {
    items,
    isLoaded,
    currentPage,
    totalPages,
    searchQuery,
    handleSearch,
    handlePageChange,
    error,
    retry: () => retrySearch,
  }
}
