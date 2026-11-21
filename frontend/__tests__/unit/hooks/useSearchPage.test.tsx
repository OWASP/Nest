import { renderHook, waitFor, act } from '@testing-library/react'
import { useSearchPage } from 'hooks/useSearchPage'
import { useRouter, useSearchParams } from 'next/navigation'
import React from 'react'
import { handleAppError } from 'app/global-error'
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

const defaultOptions = {
  indexName: 'projects',
  pageTitle: 'OWASP Projects',
  defaultSortBy: 'default',
  defaultOrder: 'desc',
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
  })

  it('preserves the page query param on initial load', async () => {
    const { result } = await renderSearchPage('page=3')

    expect(result.current.currentPage).toBe(3)
    expect(mockFetchAlgoliaData).toHaveBeenCalledWith(
      'projects',
      '',
      3,
      undefined,
      [],
      expect.any(AbortSignal)
    )
    expect(push).not.toHaveBeenCalled()
  })

  it('preserves the page query param under Strict Mode double effects', async () => {
    const { result } = await renderSearchPage('page=3', { wrapper: React.StrictMode })

    expect(result.current.currentPage).toBe(3)
    expect(mockFetchAlgoliaData).toHaveBeenCalledWith(
      'projects',
      '',
      3,
      undefined,
      [],
      expect.any(AbortSignal)
    )
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
      expect(mockFetchAlgoliaData).toHaveBeenCalledWith(
        'projects',
        'owasp',
        1,
        undefined,
        [],
        expect.any(AbortSignal)
      )
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
        [],
        expect.any(AbortSignal)
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
        [],
        expect.any(AbortSignal)
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
    expect(mockFetchAlgoliaData).toHaveBeenCalledWith(
      'projects',
      '',
      1,
      undefined,
      [],
      expect.any(AbortSignal)
    )

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

  describe('request cancellation', () => {
    type SearchResult = { hits: { objectID: string }[]; totalPages: number }

    const createDeferred = () => {
      let resolve!: (value: SearchResult) => void
      let reject!: (reason: unknown) => void
      const promise = new Promise<SearchResult>((res, rej) => {
        resolve = res
        reject = rej
      })
      return { promise, resolve, reject }
    }

    // Mimics fetch(): rejects with an AbortError as soon as the signal is aborted.
    const abortable = (promise: Promise<SearchResult>, signal?: AbortSignal) =>
      new Promise<SearchResult>((resolve, reject) => {
        signal?.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')))
        promise.then(resolve, reject)
      })

    const signalOfCall = (call: number) => mockFetchAlgoliaData.mock.calls[call][5] as AbortSignal

    const renderPending = () => {
      mockUseSearchParams.mockReturnValue(new URLSearchParams(''))
      return renderHook(() => useSearchPage<{ objectID: string }>(defaultOptions))
    }

    it('aborts the in-flight request when the query changes', async () => {
      const first = createDeferred()
      const second = createDeferred()
      mockFetchAlgoliaData
        .mockImplementationOnce((...args) => abortable(first.promise, args[5]))
        .mockImplementationOnce((...args) => abortable(second.promise, args[5]))

      const { result } = renderPending()
      await waitFor(() => expect(mockFetchAlgoliaData).toHaveBeenCalledTimes(1))

      act(() => {
        result.current.handleSearch('nest')
      })
      await waitFor(() => expect(mockFetchAlgoliaData).toHaveBeenCalledTimes(2))

      expect(signalOfCall(0).aborted).toBe(true)
      expect(signalOfCall(1).aborted).toBe(false)

      await act(async () => {
        second.resolve({ hits: [{ objectID: 'nest' }], totalPages: 1 })
      })

      await waitFor(() => expect(result.current.isLoaded).toBe(true))
      expect(result.current.items).toEqual([{ objectID: 'nest' }])
      expect(handleAppError).not.toHaveBeenCalled()
    })

    it('aborts the in-flight request when the page changes', async () => {
      const first = createDeferred()
      const second = createDeferred()
      mockFetchAlgoliaData
        .mockImplementationOnce((...args) => abortable(first.promise, args[5]))
        .mockImplementationOnce((...args) => abortable(second.promise, args[5]))

      const { result } = renderPending()
      await waitFor(() => expect(mockFetchAlgoliaData).toHaveBeenCalledTimes(1))

      const scrollTo = jest.spyOn(window, 'scrollTo').mockImplementation(() => {})
      try {
        act(() => {
          result.current.handlePageChange(3)
        })
        await waitFor(() => expect(mockFetchAlgoliaData).toHaveBeenCalledTimes(2))
      } finally {
        scrollTo.mockRestore()
      }

      expect(signalOfCall(0).aborted).toBe(true)
      expect(signalOfCall(1).aborted).toBe(false)
    })

    it('keeps the latest results even if a stale request ignores the abort and settles last', async () => {
      const stale = createDeferred()
      const latest = createDeferred()
      // These fakes deliberately ignore the signal, so only the post-await guard can protect state.
      mockFetchAlgoliaData
        .mockImplementationOnce(() => stale.promise)
        .mockImplementationOnce(() => latest.promise)

      const { result } = renderPending()
      await waitFor(() => expect(mockFetchAlgoliaData).toHaveBeenCalledTimes(1))

      act(() => {
        result.current.handleSearch('nest')
      })
      await waitFor(() => expect(mockFetchAlgoliaData).toHaveBeenCalledTimes(2))

      await act(async () => {
        latest.resolve({ hits: [{ objectID: 'nest' }], totalPages: 1 })
      })
      await waitFor(() => expect(result.current.isLoaded).toBe(true))

      await act(async () => {
        stale.resolve({ hits: [{ objectID: 'owasp' }], totalPages: 9 })
      })

      expect(result.current.items).toEqual([{ objectID: 'nest' }])
      expect(result.current.totalPages).toBe(1)
      expect(result.current.isLoaded).toBe(true)
    })

    it('does not mark the page as loaded while only a stale request has settled', async () => {
      const stale = createDeferred()
      const latest = createDeferred()
      mockFetchAlgoliaData
        .mockImplementationOnce(() => stale.promise)
        .mockImplementationOnce(() => latest.promise)

      const { result } = renderPending()
      await waitFor(() => expect(mockFetchAlgoliaData).toHaveBeenCalledTimes(1))

      act(() => {
        result.current.handleSearch('nest')
      })
      await waitFor(() => expect(mockFetchAlgoliaData).toHaveBeenCalledTimes(2))

      await act(async () => {
        stale.resolve({ hits: [{ objectID: 'owasp' }], totalPages: 9 })
      })

      expect(result.current.isLoaded).toBe(false)
      expect(result.current.items).toEqual([])
    })

    it('does not report an error for an aborted request', async () => {
      const first = createDeferred()
      mockFetchAlgoliaData.mockImplementationOnce((...args) => abortable(first.promise, args[5]))

      const { unmount } = renderPending()
      await waitFor(() => expect(mockFetchAlgoliaData).toHaveBeenCalledTimes(1))

      unmount()
      await act(async () => {
        await Promise.resolve()
      })

      expect(signalOfCall(0).aborted).toBe(true)
      expect(handleAppError).not.toHaveBeenCalled()
    })

    it('still reports an error from the latest request', async () => {
      const failure = new Error('Search service error')
      mockFetchAlgoliaData.mockRejectedValueOnce(failure)

      const { result } = renderPending()

      await waitFor(() => expect(result.current.isLoaded).toBe(true))
      expect(handleAppError).toHaveBeenCalledWith(failure)
    })
  })
})
