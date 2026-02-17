import { useSearchParams, useRouter, usePathname } from 'next/navigation'
import { useState, useEffect, useCallback } from 'react'
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
  pageTitle: _pageTitle,
  defaultSortBy = '',
  defaultOrder = '',
  hitsPerPage,
}: UseSearchPageOptions): UseSearchPageReturn<T> {
  const searchParams = useSearchParams()
  const router = useRouter()
  const pathname = usePathname()

  const [items, setItems] = useState<T[]>([])
  const [currentPage, setCurrentPage] = useState<number>(
    Number.parseInt(searchParams.get('page') || '1')
  )
  const [searchQuery, setSearchQuery] = useState<string>(searchParams.get('q') || '')
  const [sortBy, setSortBy] = useState<string>(searchParams.get('sortBy') || defaultSortBy)
  const [order, setOrder] = useState<string>(searchParams.get('order') || defaultOrder)
  const [totalPages, setTotalPages] = useState<number>(0)
  const [isLoaded, setIsLoaded] = useState<boolean>(false)

  const updateUrl = useCallback(
    (params: Record<string, string | number | undefined>) => {
      const current = new URLSearchParams(Array.from(searchParams.entries()))

      Object.entries(params).forEach(([key, value]) => {
        if (value === undefined || value === null || value === '') {
          current.delete(key)
          return
        }

        if (key === 'page' && (value === 1 || value === '1')) {
          current.delete(key)
          return
        }

        current.set(key, String(value))
      })

      const search = current.toString()
      const query = search ? `?${search}` : ''

      router.push(`${pathname}${query}`)
    },
    [router, pathname, searchParams]
  )

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
  }, [currentPage, searchQuery, order, sortBy, hitsPerPage, indexName])

  const handleSearch = (query: string) => {
    setSearchQuery(query)
    setCurrentPage(1)
    updateUrl({ q: query, page: 1 })
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
    window.scrollTo({ top: 0, behavior: 'auto' })
    updateUrl({ page })
  }

  const handleSortChange = (sort: string) => {
    setSortBy(sort)
    setCurrentPage(1)
    updateUrl({ sortBy: sort, page: 1 })
  }

  const handleOrderChange = (newOrder: string) => {
    setOrder(newOrder)
    setCurrentPage(1)
    updateUrl({ order: newOrder, page: 1 })
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
