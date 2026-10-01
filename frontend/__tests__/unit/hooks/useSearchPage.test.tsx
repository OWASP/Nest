import { renderHook, waitFor, act } from '@testing-library/react'
import { useSearchPage } from 'hooks/useSearchPage'
import { useRouter, useSearchParams } from 'next/navigation'
import React from 'react'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'

jest.mock('server/fetchAlgoliaData', () => ({
  fetchAlgoliaData: jest.fn(),
}))

jest.mock('app/global-error', () => ({
  handleAppError: jest.fn(),
}))

const mockFetchAlgoliaData = fetchAlgoliaData as jest.Mock
const mockHandleAppError = jest.requireMock('app/global-error').handleAppError as jest.Mock
const mockUseSearchParams = useSearchParams as jest.Mock
const mockUseRouter = useRouter as jest.Mock

const defaultOptions = {
  indexName: 'projects',
  pageTitle: 'OWASP Projects',
  defaultSortBy: 'default',
  defaultOrder: 'desc',
} as const

const programsOptions = {
  indexName: 'programs',
  pageTitle: 'OWASP Programs',
  defaultSortBy: 'default',
  defaultOrder: 'desc',
  hitsPerPage: 24,
} as const

describe('useSearchPage', () => {
  const push = jest.fn()

  const renderSearchPage = async (
    queryString = '',
    options: {
      facetFilters?: string[]
      indexName?: string
      pageTitle?: string
      wrapper?: React.ComponentType<{ children: React.ReactNode }>
    } = {}
  ) => {
    const { facetFilters, indexName, pageTitle, wrapper } = options
    mockUseSearchParams.mockReturnValue(new URLSearchParams(queryString))

    const rendered = renderHook(
      () =>
        useSearchPage({
          ...defaultOptions,
          ...(indexName ? { indexName } : {}),
          ...(pageTitle ? { pageTitle } : {}),
          ...(facetFilters ? { facetFilters } : {}),
        }),
      wrapper ? { wrapper } : undefined
    )

    await waitFor(() => {
      expect(rendered.result.current.isLoaded).toBe(true)
    })

    return rendered
  }

  beforeEach(() => {
    jest.clearAllMocks()
    mockUseRouter.mockReturnValue({ push })
    mockFetchAlgoliaData.mockResolvedValue({
      hits: [{ objectID: '1' }],
      totalPages: 5,
    })
    window.scrollTo = jest.fn()
  })

  it('preserves the page query param on initial load', async () => {
    const { result } = await renderSearchPage('page=3')

    expect(result.current.currentPage).toBe(3)
    expect(mockFetchAlgoliaData).toHaveBeenCalledWith('projects', '', 3, undefined, [])
    expect(push).not.toHaveBeenCalled()
  })

  it('preserves the page query param under Strict Mode double effects', async () => {
    const { result } = await renderSearchPage('page=3', { wrapper: React.StrictMode })

    expect(result.current.currentPage).toBe(3)
    expect(mockFetchAlgoliaData).toHaveBeenCalledWith('projects', '', 3, undefined, [])
    expect(push).not.toHaveBeenCalled()
  })

  it('resets to page 1 when facet filters change after mount', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams('page=3'))

    const { result, rerender } = renderHook(
      ({ facetFilters }) =>
        useSearchPage({
          indexName: 'chapters',
          pageTitle: 'OWASP Chapters',
          defaultSortBy: 'default',
          defaultOrder: 'desc',
          facetFilters,
        }),
      { initialProps: { facetFilters: [] as string[] } }
    )

    await waitFor(() => {
      expect(result.current.isLoaded).toBe(true)
      expect(result.current.currentPage).toBe(3)
    })

    mockUseSearchParams.mockReturnValue(new URLSearchParams())

    rerender({ facetFilters: ['idx_country:US'] })

    await waitFor(() => {
      expect(result.current.currentPage).toBe(1)
    })
  })

  it('resets to page 1 when the search query changes', async () => {
    const { result } = await renderSearchPage('page=3')

    act(() => {
      result.current.handleSearch('owasp')
    })

    expect(result.current.currentPage).toBe(1)

    await waitFor(() => {
      expect(result.current.isLoaded).toBe(true)
      expect(mockFetchAlgoliaData).toHaveBeenCalledWith('projects', 'owasp', 1, undefined, [])
    })
  })

  it('resets to page 1 when the sort option changes', async () => {
    const { result } = await renderSearchPage('page=3')

    act(() => {
      result.current.handleSortChange('stars_count')
    })

    expect(result.current.currentPage).toBe(1)
    expect(result.current.sortBy).toBe('stars_count')

    await waitFor(() => {
      expect(result.current.isLoaded).toBe(true)
      expect(mockFetchAlgoliaData).toHaveBeenCalledWith(
        'projects_stars_count_desc',
        '',
        1,
        undefined,
        []
      )
    })
  })

  it('resets to page 1 when the sort order changes', async () => {
    const { result } = await renderSearchPage('page=3&sortBy=stars_count&order=desc')

    expect(result.current.currentPage).toBe(3)
    expect(result.current.sortBy).toBe('stars_count')

    act(() => {
      result.current.handleOrderChange('asc')
    })

    expect(result.current.currentPage).toBe(1)
    expect(result.current.order).toBe('asc')

    await waitFor(() => {
      expect(result.current.isLoaded).toBe(true)
      expect(mockFetchAlgoliaData).toHaveBeenCalledWith(
        'projects_stars_count_asc',
        '',
        1,
        undefined,
        []
      )
    })
  })

  it('synchronizes state from URL on back/forward without pushing', async () => {
    const { result, rerender } = await renderSearchPage('page=3')

    push.mockClear()
    mockUseSearchParams.mockReturnValue(new URLSearchParams('page=2&q=nest'))
    rerender()

    await waitFor(() => {
      expect(result.current.currentPage).toBe(2)
      expect(result.current.searchQuery).toBe('nest')
    })

    expect(push).not.toHaveBeenCalled()
  })

  it('does not push when back/forward lands on an equivalent page=1 URL', async () => {
    const { result, rerender } = await renderSearchPage('page=2&q=foo')

    push.mockClear()
    mockUseSearchParams.mockReturnValue(new URLSearchParams('page=1&q=foo'))
    rerender()

    await waitFor(() => {
      expect(result.current.currentPage).toBe(1)
      expect(result.current.searchQuery).toBe('foo')
    })

    expect(push).not.toHaveBeenCalled()
  })

  it('falls back to page 1 for non-numeric or non-positive page params', async () => {
    const { result, rerender } = await renderSearchPage('page=abc')

    expect(result.current.currentPage).toBe(1)
    expect(mockFetchAlgoliaData).toHaveBeenCalledWith('projects', '', 1, undefined, [])

    mockUseSearchParams.mockReturnValue(new URLSearchParams('page=0'))
    rerender()

    await waitFor(() => {
      expect(result.current.currentPage).toBe(1)
    })

    mockUseSearchParams.mockReturnValue(new URLSearchParams('page=-2'))
    rerender()

    await waitFor(() => {
      expect(result.current.currentPage).toBe(1)
    })

    mockUseSearchParams.mockReturnValue(new URLSearchParams('page=2foo'))
    rerender()

    await waitFor(() => {
      expect(result.current.currentPage).toBe(1)
    })

    mockUseSearchParams.mockReturnValue(new URLSearchParams(`page=${'9'.repeat(400)}`))
    rerender()

    await waitFor(() => {
      expect(result.current.currentPage).toBe(1)
    })

    mockUseSearchParams.mockReturnValue(new URLSearchParams('page=12'))
    rerender()

    await waitFor(() => {
      expect(result.current.currentPage).toBe(12)
    })
  })

  it('still pushes URL updates for user-driven page changes after back/forward sync', async () => {
    const scrollTo = jest.spyOn(window, 'scrollTo').mockImplementation(() => undefined)

    try {
      const { result, rerender } = await renderSearchPage('page=3')

      push.mockClear()
      mockUseSearchParams.mockReturnValue(new URLSearchParams('page=2'))
      rerender()

      await waitFor(() => {
        expect(result.current.currentPage).toBe(2)
      })
      expect(push).not.toHaveBeenCalled()

      act(() => {
        result.current.handlePageChange(4)
      })

      expect(result.current.currentPage).toBe(4)
      expect(scrollTo).toHaveBeenCalled()
      await waitFor(() => {
        expect(push).toHaveBeenCalledWith('?page=4')
      })
    } finally {
      scrollTo.mockRestore()
    }
  })

  it('applies back/forward after a local navigation is acknowledged', async () => {
    const { result, rerender } = await renderSearchPage('page=2')

    act(() => {
      result.current.handleSearch('nest')
    })

    expect(result.current.searchQuery).toBe('nest')
    expect(result.current.currentPage).toBe(1)

    mockUseSearchParams.mockReturnValue(new URLSearchParams('q=nest'))
    rerender()

    push.mockClear()
    mockUseSearchParams.mockReturnValue(new URLSearchParams('page=2'))
    rerender()

    await waitFor(() => {
      expect(result.current.currentPage).toBe(2)
      expect(result.current.searchQuery).toBe('')
    })
    expect(push).not.toHaveBeenCalled()
  })

  it('applies back/forward when it happens before a local push is acknowledged', async () => {
    const scrollTo = jest.spyOn(window, 'scrollTo').mockImplementation(() => undefined)

    try {
      const { result, rerender } = await renderSearchPage('page=2')

      act(() => {
        result.current.handlePageChange(4)
      })
      expect(result.current.currentPage).toBe(4)
      expect(push).toHaveBeenCalledWith('?page=4')

      push.mockClear()
      mockUseSearchParams.mockReturnValue(new URLSearchParams('page=2'))
      rerender()

      await waitFor(() => {
        expect(result.current.currentPage).toBe(2)
      })
      expect(push).not.toHaveBeenCalled()
    } finally {
      scrollTo.mockRestore()
    }
  })

  it('still pushes after a no-op sync from noncanonical default sort params', async () => {
    const { result, rerender } = await renderSearchPage('')

    push.mockClear()
    mockUseSearchParams.mockReturnValue(new URLSearchParams('sortBy=default&order=desc'))
    rerender()

    expect(result.current.sortBy).toBe('default')
    expect(result.current.order).toBe('desc')
    expect(push).not.toHaveBeenCalled()

    act(() => {
      result.current.handleSearch('nest')
    })

    await waitFor(() => {
      expect(push).toHaveBeenCalledWith('?q=nest')
    })
  })

  it('resets to page 1 and fetches the replica index when sort changes on a later page', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams())

    const { result } = renderHook(() => useSearchPage<{ key: string }>(programsOptions))

    await waitFor(() => {
      expect(mockFetchAlgoliaData).toHaveBeenCalledTimes(1)
    })
    expect(push).not.toHaveBeenCalled()

    act(() => {
      result.current.handlePageChange(2)
    })

    await waitFor(() => {
      expect(mockFetchAlgoliaData).toHaveBeenLastCalledWith('programs', '', 2, 24, [])
    })
    expect(push).toHaveBeenLastCalledWith('?page=2')

    act(() => {
      result.current.handleSortChange('name')
    })

    await waitFor(() => {
      expect(mockFetchAlgoliaData).toHaveBeenLastCalledWith('programs_name_desc', '', 1, 24, [])
    })
    expect(mockFetchAlgoliaData).not.toHaveBeenCalledWith('programs_name_desc', '', 2, 24, [])
    expect(result.current.sortBy).toBe('name')
    expect(result.current.currentPage).toBe(1)
  })

  it('adopts sort and order params from the URL when it changes', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams('sortBy=name&order=desc'))

    const { result, rerender } = renderHook(() => useSearchPage<{ key: string }>(programsOptions))

    await waitFor(() => {
      expect(result.current.sortBy).toBe('name')
    })
    expect(result.current.order).toBe('desc')
    await waitFor(() => {
      expect(mockFetchAlgoliaData).toHaveBeenLastCalledWith('programs_name_desc', '', 1, 24, [])
    })
    expect(push).not.toHaveBeenCalled()

    mockUseSearchParams.mockReturnValue(new URLSearchParams())
    rerender()

    await waitFor(() => {
      expect(result.current.sortBy).toBe('default')
    })
    expect(result.current.order).toBe('desc')
    await waitFor(() => {
      expect(mockFetchAlgoliaData).toHaveBeenLastCalledWith('programs', '', 1, 24, [])
    })
    expect(push).not.toHaveBeenCalled()

    await act(async () => {
      result.current.handleSortChange('date_created')
    })
    expect(push).toHaveBeenCalledWith('?sortBy=date_created&order=desc')
    expect(result.current.sortBy).toBe('date_created')
  })

  it('ignores stale responses superseded by a newer request', async () => {
    let resolveInitial!: (value: { hits: { key: string }[]; totalPages: number }) => void
    let resolveNewer!: (value: { hits: { key: string }[]; totalPages: number }) => void
    const initial = new Promise<{ hits: { key: string }[]; totalPages: number }>((resolve) => {
      resolveInitial = resolve
    })
    const newer = new Promise<{ hits: { key: string }[]; totalPages: number }>((resolve) => {
      resolveNewer = resolve
    })

    mockFetchAlgoliaData.mockReturnValueOnce(initial).mockReturnValueOnce(newer)
    mockUseSearchParams.mockReturnValue(new URLSearchParams())

    const { result } = renderHook(() => useSearchPage<{ key: string }>(programsOptions))
    await waitFor(() => {
      expect(mockFetchAlgoliaData).toHaveBeenCalledTimes(1)
    })

    act(() => {
      result.current.handleSearch('owasp')
    })
    await waitFor(() => {
      expect(mockFetchAlgoliaData).toHaveBeenCalledTimes(2)
    })

    await act(async () => {
      resolveNewer({ hits: [{ key: 'new' }], totalPages: 1 })
    })
    await waitFor(() => {
      expect(result.current.items).toEqual([{ key: 'new' }])
    })

    await act(async () => {
      resolveInitial({ hits: [{ key: 'stale' }], totalPages: 1 })
    })
    await waitFor(() => {
      expect(result.current.items).toEqual([{ key: 'new' }])
    })
  })

  it('ignores stale failures superseded by a newer request', async () => {
    let rejectInitial!: (reason?: object) => void
    let resolveNewer!: (value: { hits: { key: string }[]; totalPages: number }) => void
    const initial = new Promise<{ hits: { key: string }[]; totalPages: number }>(
      (_resolve, reject) => {
        rejectInitial = reject
      }
    )
    const newer = new Promise<{ hits: { key: string }[]; totalPages: number }>((resolve) => {
      resolveNewer = resolve
    })

    mockFetchAlgoliaData.mockReturnValueOnce(initial).mockReturnValueOnce(newer)
    mockUseSearchParams.mockReturnValue(new URLSearchParams())

    const { result } = renderHook(() => useSearchPage<{ key: string }>(programsOptions))
    await waitFor(() => {
      expect(mockFetchAlgoliaData).toHaveBeenCalledTimes(1)
    })

    act(() => {
      result.current.handleSearch('owasp')
    })
    await waitFor(() => {
      expect(mockFetchAlgoliaData).toHaveBeenCalledTimes(2)
    })

    await act(async () => {
      resolveNewer({ hits: [{ key: 'new' }], totalPages: 1 })
    })
    await waitFor(() => {
      expect(result.current.items).toEqual([{ key: 'new' }])
    })
    expect(result.current.isLoaded).toBe(true)

    await act(async () => {
      rejectInitial(new Error('stale failure'))
    })
    expect(mockHandleAppError).not.toHaveBeenCalled()
    expect(result.current.items).toEqual([{ key: 'new' }])
    expect(result.current.isLoaded).toBe(true)
  })
})
