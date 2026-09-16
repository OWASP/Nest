'use client'

import { useState, useEffect, useCallback } from 'react'

const useRecentSearches = () => {
  const [recentSearchResults, setRecentSearchResults] = useState<string[]>([])

  useEffect(() => {
    try {
      const savedResults = localStorage.getItem('recentSearchResults')
      if (savedResults) {
        const parseResults = JSON.parse(savedResults)
        if (Array.isArray(parseResults) && parseResults.every((item) => typeof item === 'string')) {
          setRecentSearchResults(parseResults)
        }
      }
    } catch {
      // Ignore errors related to localStorage access or JSON parsing
    }
  }, [])

  const setRecentSearch = useCallback((updater: string[] | ((prev: string[]) => string[])) => {
    setRecentSearchResults((prev) => {
      const next = typeof updater === 'function' ? updater(prev) : updater
      try {
        localStorage.setItem('recentSearchResults', JSON.stringify(next))
      } catch {
        // Ignore errors related to localStorage access
      }
      return next
    })
  }, [])

  const removeRecentSearch = useCallback((query: string) => {
    setRecentSearchResults((prev) => {
      const next = prev.filter((item) => item !== query)
      try {
        localStorage.setItem('recentSearchResults', JSON.stringify(next))
      } catch {
        // Ignore errors related to localStorage access
      }
      return next
    })
  }, [])

  return { recentSearchResults, setRecentSearch, removeRecentSearch }
}

export default useRecentSearches
