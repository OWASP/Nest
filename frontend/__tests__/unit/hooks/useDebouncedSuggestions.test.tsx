import { act, renderHook } from '@testing-library/react'
import { useDebouncedSuggestions } from 'hooks/useDebouncedSuggestions'

const mockApolloClient = { query: jest.fn() }

jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useApolloClient: () => mockApolloClient,
}))

type Item = { id: string }

const flushPromises = async () => {
  await act(async () => {
    await Promise.resolve()
    await Promise.resolve()
  })
}

describe('useDebouncedSuggestions', () => {
  beforeEach(() => {
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.useRealTimers()
    jest.clearAllMocks()
  })

  it('does not fetch for queries shorter than minLength', () => {
    const fetcher = jest.fn().mockResolvedValue([{ id: '1' }])

    const { result } = renderHook(() =>
      useDebouncedSuggestions<Item>('ab', fetcher, { minLength: 3 })
    )
    act(() => {
      jest.advanceTimersByTime(500)
    })

    expect(fetcher).not.toHaveBeenCalled()
    expect(result.current).toEqual({ items: [], isLoading: false })
  })

  it('fetches with the trimmed query after the debounce delay', async () => {
    const fetcher = jest.fn().mockResolvedValue([{ id: '1' }])

    const { result } = renderHook(() =>
      useDebouncedSuggestions<Item>('  nest  ', fetcher, { delayMs: 300 })
    )

    act(() => {
      jest.advanceTimersByTime(299)
    })
    expect(fetcher).not.toHaveBeenCalled()

    act(() => {
      jest.advanceTimersByTime(1)
    })
    await flushPromises()

    expect(fetcher).toHaveBeenCalledTimes(1)
    expect(fetcher).toHaveBeenCalledWith('nest', mockApolloClient)
    expect(result.current).toEqual({ items: [{ id: '1' }], isLoading: false })
  })

  it('debounces rapid query changes into a single request', async () => {
    const fetcher = jest.fn().mockResolvedValue([{ id: '1' }])

    const { rerender } = renderHook(
      ({ query }) => useDebouncedSuggestions<Item>(query, fetcher, { delayMs: 300 }),
      { initialProps: { query: 'own' } }
    )
    act(() => {
      jest.advanceTimersByTime(100)
    })
    rerender({ query: 'nest' })
    act(() => {
      jest.advanceTimersByTime(300)
    })
    await flushPromises()

    expect(fetcher).toHaveBeenCalledTimes(1)
    expect(fetcher).toHaveBeenCalledWith('nest', mockApolloClient)
  })

  it('discards a stale response once the query has changed', async () => {
    let resolveStale: (items: Item[]) => void = () => {}
    const fetcher = jest
      .fn()
      .mockImplementationOnce(
        () =>
          new Promise<Item[]>((resolve) => {
            resolveStale = resolve
          })
      )
      .mockResolvedValueOnce([{ id: 'fresh' }])

    const { result, rerender } = renderHook(
      ({ query }) => useDebouncedSuggestions<Item>(query, fetcher),
      { initialProps: { query: 'old' } }
    )
    act(() => {
      jest.advanceTimersByTime(300)
    })

    rerender({ query: 'new' })
    act(() => {
      jest.advanceTimersByTime(300)
    })
    await flushPromises()

    await act(async () => {
      resolveStale([{ id: 'stale' }])
    })

    expect(result.current.items).toEqual([{ id: 'fresh' }])
  })

  it('clears previous suggestions when the next request rejects', async () => {
    const fetcher = jest
      .fn()
      .mockResolvedValueOnce([{ id: 'previous' }])
      .mockRejectedValueOnce(new Error('boom'))

    const { result, rerender } = renderHook(
      ({ query }) => useDebouncedSuggestions<Item>(query, fetcher),
      { initialProps: { query: 'nest' } }
    )
    act(() => {
      jest.advanceTimersByTime(300)
    })
    await flushPromises()
    expect(result.current.items).toEqual([{ id: 'previous' }])

    rerender({ query: 'owasp' })
    act(() => {
      jest.advanceTimersByTime(300)
    })
    await flushPromises()

    expect(fetcher).toHaveBeenLastCalledWith('owasp', mockApolloClient)
    expect(result.current).toEqual({ items: [], isLoading: false })
  })

  it('clears items when the query drops below minLength', async () => {
    const fetcher = jest.fn().mockResolvedValue([{ id: '1' }])

    const { result, rerender } = renderHook(
      ({ query }) => useDebouncedSuggestions<Item>(query, fetcher),
      { initialProps: { query: 'nest' } }
    )
    act(() => {
      jest.advanceTimersByTime(300)
    })
    await flushPromises()
    expect(result.current.items).toEqual([{ id: '1' }])

    rerender({ query: 'ne' })

    expect(result.current).toEqual({ items: [], isLoading: false })
  })

  it('cancels the pending request on unmount', () => {
    const fetcher = jest.fn().mockResolvedValue([])

    const { unmount } = renderHook(() => useDebouncedSuggestions<Item>('nest', fetcher))
    unmount()
    act(() => {
      jest.advanceTimersByTime(500)
    })

    expect(fetcher).not.toHaveBeenCalled()
  })

  it('does not refetch when a non-memoized fetcher changes identity', async () => {
    const calls: string[] = []

    const { rerender } = renderHook(() =>
      useDebouncedSuggestions<Item>('nest', async (q) => {
        calls.push(q)
        return []
      })
    )
    act(() => {
      jest.advanceTimersByTime(300)
    })
    await flushPromises()

    rerender()
    rerender()
    act(() => {
      jest.advanceTimersByTime(300)
    })
    await flushPromises()

    expect(calls).toEqual(['nest'])
  })

  it('uses the latest fetcher for the next request', async () => {
    const first = jest.fn().mockResolvedValue([{ id: 'first' }])
    const second = jest.fn().mockResolvedValue([{ id: 'second' }])

    const { result, rerender } = renderHook(
      ({ query, fetcher }) => useDebouncedSuggestions<Item>(query, fetcher),
      { initialProps: { query: 'nest', fetcher: first } }
    )
    act(() => {
      jest.advanceTimersByTime(300)
    })
    await flushPromises()

    rerender({ query: 'owasp', fetcher: second })
    act(() => {
      jest.advanceTimersByTime(300)
    })
    await flushPromises()

    expect(first).toHaveBeenCalledTimes(1)
    expect(second).toHaveBeenCalledWith('owasp', mockApolloClient)
    expect(result.current.items).toEqual([{ id: 'second' }])
  })
})
