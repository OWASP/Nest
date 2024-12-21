import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'

import logger from '../../utils/logger'
import { loadData } from '../api'

interface UseSearchPageOptions {
  endpoint: string
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
}

export function useSearchPage<T>({
  endpoint,
  pageTitle,
}: UseSearchPageOptions): UseSearchPageReturn<T> {
  const [searchParams, setSearchParams] = useSearchParams()
  const [items, setItems] = useState<T[]>([])
  const [currentPage, setCurrentPage] = useState<number>(parseInt(searchParams.get('page') || '1'))
  const [searchQuery, setSearchQuery] = useState<string>(searchParams.get('q') || '')
  const [totalPages, setTotalPages] = useState<number>(0)
  const [isLoaded, setIsLoaded] = useState<boolean>(false)

  useEffect(() => {
    const params = new URLSearchParams()
    if (searchQuery) params.set('q', searchQuery)
    if (currentPage > 1) params.set('page', currentPage.toString())
    setSearchParams(params)
  }, [searchQuery, currentPage, setSearchParams])

  useEffect(() => {
    document.title = pageTitle
    setIsLoaded(false)

    const fetchData = async () => {
      try {
        const data = await loadData<any>(endpoint, searchQuery, currentPage)
        const itemsKey = endpoint.split('/').pop() + 's'
        setItems(data[itemsKey])
        setTotalPages(data.total_pages)
      } catch (error) {
        logger.error(error)
      }
      setIsLoaded(true)
    }

    fetchData()
  }, [currentPage, searchQuery, endpoint, pageTitle])

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

  return {
    items,
    isLoaded,
    currentPage,
    totalPages,
    searchQuery,
    handleSearch,
    handlePageChange,
  }
}
