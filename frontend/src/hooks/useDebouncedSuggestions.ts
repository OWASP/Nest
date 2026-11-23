import { useApolloClient } from '@apollo/client/react'
import debounce from 'lodash/debounce'
import { useEffect, useMemo, useRef, useState } from 'react'

export function useDebouncedSuggestions<T>(
  query: string,
  fetcher: (trimmedQuery: string, client: ReturnType<typeof useApolloClient>) => Promise<T[]>,
  {
    minLength = 3,
    delayMs = 300,
  }: {
    minLength?: number
    delayMs?: number
  } = {}
): { items: T[]; isLoading: boolean } {
  const client = useApolloClient()
  const [items, setItems] = useState<T[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const requestIdRef = useRef(0)
  // Read the latest fetcher through a ref so a non-memoized fetcher does not
  // recreate the debounced function and refetch on every render.
  const fetcherRef = useRef(fetcher)

  useEffect(() => {
    fetcherRef.current = fetcher
  }, [fetcher])

  const fetchSuggestions = useMemo(
    () =>
      debounce(async (q: string, requestId: number) => {
        const trimmed = q.trim()
        if (trimmed.length < minLength || requestId !== requestIdRef.current) {
          setItems([])
          setIsLoading(false)
          return
        }
        setIsLoading(true)
        try {
          const results = await fetcherRef.current(trimmed, client)
          if (requestId === requestIdRef.current) {
            setItems(results)
          }
        } catch {
          if (requestId === requestIdRef.current) {
            setItems([])
          }
        } finally {
          if (requestId === requestIdRef.current) {
            setIsLoading(false)
          }
        }
      }, delayMs),
    [client, minLength, delayMs]
  )

  useEffect(() => {
    const currentId = ++requestIdRef.current
    const trimmed = query.trim()
    if (trimmed.length < minLength) {
      fetchSuggestions.cancel()
      setItems([])
      setIsLoading(false)
    } else {
      fetchSuggestions(query, currentId)
    }
    return () => {
      fetchSuggestions.cancel()
    }
  }, [query, minLength, fetchSuggestions])

  return { items, isLoading }
}
