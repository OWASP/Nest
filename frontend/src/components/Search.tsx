import axios from 'axios'
import React, { useState, useEffect, useCallback } from 'react'

import { useDebounce } from '../lib/hooks'
import { ProjectDataType } from '../lib/types'

interface SearchBarProps {
  placeholder: string
  searchEndpoint: string
  // eslint-disable-next-line no-unused-vars
  onSearchResult: (results: ProjectDataType | null) => void
  defaultResults: ProjectDataType | null
}

const SearchBar: React.FC<SearchBarProps> = ({
  placeholder,
  searchEndpoint,
  onSearchResult,
  defaultResults,
}) => {
  const [query, setQuery] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  const debouncedQuery = useDebounce(query, 500)

  const performSearch = useCallback(
    async (searchQuery: string) => {
      if (!searchQuery.trim()) {
        onSearchResult(defaultResults)
        return
      }

      setLoading(true)
      setError(null)
      try {
        const response = await axios.get(searchEndpoint, {
          params: { q: searchQuery },
        })

        const defaultresults = response.data
        onSearchResult(defaultresults)
      } catch (err) {
        console.error('Search error:', err)
        setError('Failed to fetch search results. Please try again.')
        onSearchResult(defaultResults)
      } finally {
        setLoading(false)
      }
    },
    [defaultResults, onSearchResult, searchEndpoint]
  )

  useEffect(() => {
    performSearch(debouncedQuery)
  }, [debouncedQuery, performSearch])

  return (
    <div className="mx-auto mt-8 w-full max-w-md">
      <form
        onSubmit={(e) => {
          e.preventDefault()
          performSearch(query)
        }}
        className="relative"
      >
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder}
          className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 pr-12 text-gray-700 transition-all duration-300 ease-in-out focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:outline-none"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading}
          className="absolute right-2 top-1/2 -translate-y-1/2 transform rounded-lg bg-blue-600 px-4 py-2 text-white transition-colors duration-300 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-opacity-50 disabled:cursor-not-allowed disabled:opacity-50"
          aria-label="Search"
        >
          {loading ? (
            <svg
              className="h-5 w-5 animate-spin text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
          ) : (
            <svg
              className="h-5 w-5"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          )}
        </button>
      </form>
      {error && (
        <p className="mt-2 text-sm text-red-600" role="alert">
          {error}
        </p>
      )}
    </div>
  )
}

export default SearchBar
