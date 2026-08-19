import { useApolloClient } from '@apollo/client/react'
import debounce from 'lodash/debounce'
import { useCallback, useEffect, useRef, useState } from 'react'

/**
 * Generic debounced suggestion hook.
 *
 * @param query        - The current input value to search on.
 * @param minLength    - Minimum query length before fetching (default: 3).
 * @param delayMs      - Debounce delay in milliseconds (default: 300).
 * @param fetcher      - Async function that receives the trimmed query and the Apollo
 *                       client, and resolves to the suggestions array.
 */
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

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const fetchSuggestions = useCallback(
    debounce(async (q: string, requestId: number) => {
      const trimmed = q.trim()
      if (trimmed.length < minLength || requestId !== requestIdRef.current) {
        setItems([])
        setIsLoading(false)
        return
      }
      setIsLoading(true)
      try {
        const results = await fetcher(trimmed, client)
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
    // fetcher identity changes only when the caller passes a new ref; keep it stable with useCallback at call-site.
    [client, minLength, delayMs, fetcher]
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
