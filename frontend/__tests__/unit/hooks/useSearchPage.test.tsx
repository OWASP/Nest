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
const mockUseSearchParams = useSearchParams as jest.Mock
const mockUseRouter = useRouter as jest.Mock

describe('useSearchPage', () => {
  const push = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    mockUseRouter.mockReturnValue({ push })
    mockFetchAlgoliaData.mockResolvedValue({
      hits: [{ objectID: '1' }],
      totalPages: 5,
    })
  })

  it('preserves the page query param on initial load', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams('page=3'))

    const { result } = renderHook(() =>
      useSearchPage({
        indexName: 'projects',
        pageTitle: 'OWASP Projects',
        defaultSortBy: 'default',
        defaultOrder: 'desc',
      })
    )

    expect(result.current.currentPage).toBe(3)

    await waitFor(() => {
      expect(result.current.isLoaded).toBe(true)
      expect(mockFetchAlgoliaData).toHaveBeenCalledWith('projects', '', 3, undefined, [])
    })

    expect(result.current.currentPage).toBe(3)
    expect(push).not.toHaveBeenCalled()
  })

  it('preserves the page query param under Strict Mode double effects', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams('page=3'))

    const { result } = renderHook(
      () =>
        useSearchPage({
          indexName: 'projects',
          pageTitle: 'OWASP Projects',
          defaultSortBy: 'default',
          defaultOrder: 'desc',
        }),
      { wrapper: React.StrictMode }
    )

    await waitFor(() => {
      expect(result.current.isLoaded).toBe(true)
      expect(mockFetchAlgoliaData).toHaveBeenCalledWith('projects', '', 3, undefined, [])
    })

    expect(result.current.currentPage).toBe(3)
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
    mockUseSearchParams.mockReturnValue(new URLSearchParams('page=3'))

    const { result } = renderHook(() =>
      useSearchPage({
        indexName: 'projects',
        pageTitle: 'OWASP Projects',
        defaultSortBy: 'default',
        defaultOrder: 'desc',
      })
    )

    await waitFor(() => {
      expect(result.current.isLoaded).toBe(true)
      expect(result.current.currentPage).toBe(3)
    })

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
    mockUseSearchParams.mockReturnValue(new URLSearchParams('page=3'))

    const { result } = renderHook(() =>
      useSearchPage({
        indexName: 'projects',
        pageTitle: 'OWASP Projects',
        defaultSortBy: 'default',
        defaultOrder: 'desc',
      })
    )

    await waitFor(() => {
      expect(result.current.isLoaded).toBe(true)
      expect(result.current.currentPage).toBe(3)
    })

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
    mockUseSearchParams.mockReturnValue(new URLSearchParams('page=3&sortBy=stars_count&order=desc'))

    const { result } = renderHook(() =>
      useSearchPage({
        indexName: 'projects',
        pageTitle: 'OWASP Projects',
        defaultSortBy: 'default',
        defaultOrder: 'desc',
      })
    )

    await waitFor(() => {
      expect(result.current.isLoaded).toBe(true)
      expect(result.current.currentPage).toBe(3)
      expect(result.current.sortBy).toBe('stars_count')
    })

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

  it('synchronizes state from URL on back/forward without restoring the stale query', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams('page=3'))

    const { result, rerender } = renderHook(() =>
      useSearchPage({
        indexName: 'projects',
        pageTitle: 'OWASP Projects',
        defaultSortBy: 'default',
        defaultOrder: 'desc',
      })
    )

    await waitFor(() => {
      expect(result.current.isLoaded).toBe(true)
      expect(result.current.currentPage).toBe(3)
    })

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
    mockUseSearchParams.mockReturnValue(new URLSearchParams('page=2&q=foo'))

    const { result, rerender } = renderHook(() =>
      useSearchPage({
        indexName: 'projects',
        pageTitle: 'OWASP Projects',
        defaultSortBy: 'default',
        defaultOrder: 'desc',
      })
    )

    await waitFor(() => {
      expect(result.current.isLoaded).toBe(true)
      expect(result.current.currentPage).toBe(2)
    })

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
    mockUseSearchParams.mockReturnValue(new URLSearchParams('page=abc'))

    const { result, rerender } = renderHook(() =>
      useSearchPage({
        indexName: 'projects',
        pageTitle: 'OWASP Projects',
        defaultSortBy: 'default',
        defaultOrder: 'desc',
      })
    )

    await waitFor(() => {
      expect(result.current.isLoaded).toBe(true)
      expect(result.current.currentPage).toBe(1)
      expect(mockFetchAlgoliaData).toHaveBeenCalledWith('projects', '', 1, undefined, [])
    })

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
  })

  it('still pushes URL updates for user-driven page changes after back/forward sync', async () => {
    const scrollTo = jest.fn()
    window.scrollTo = scrollTo
    mockUseSearchParams.mockReturnValue(new URLSearchParams('page=3'))

    const { result, rerender } = renderHook(() =>
      useSearchPage({
        indexName: 'projects',
        pageTitle: 'OWASP Projects',
        defaultSortBy: 'default',
        defaultOrder: 'desc',
      })
    )

    await waitFor(() => {
      expect(result.current.isLoaded).toBe(true)
      expect(result.current.currentPage).toBe(3)
    })

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
  })

  it('keeps the latest search when a second change happens before searchParams update', async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams('page=3'))

    const { result, rerender } = renderHook(() =>
      useSearchPage({
        indexName: 'projects',
        pageTitle: 'OWASP Projects',
        defaultSortBy: 'default',
        defaultOrder: 'desc',
      })
    )

    await waitFor(() => {
      expect(result.current.isLoaded).toBe(true)
      expect(result.current.currentPage).toBe(3)
    })

    act(() => {
      result.current.handleSearch('foo')
    })
    act(() => {
      result.current.handleSearch('bar')
    })

    expect(result.current.searchQuery).toBe('bar')
    expect(result.current.currentPage).toBe(1)

    // Stale acknowledgment of the first push must not restore the older query.
    mockUseSearchParams.mockReturnValue(new URLSearchParams('q=foo'))
    rerender()

    expect(result.current.searchQuery).toBe('bar')

    mockUseSearchParams.mockReturnValue(new URLSearchParams('q=bar'))
    rerender()

    await waitFor(() => {
      expect(result.current.searchQuery).toBe('bar')
      expect(result.current.currentPage).toBe(1)
    })
  })
})
