import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { useDebounce } from '../lib/hooks'


interface SearchBarProps {
  placeholder: string
  searchEndpoint: string
  onSearchResult: (results: any[]) => void
  defaultResults: any[]
}

const SearchBar: React.FC<SearchBarProps> = ({
  placeholder,
  searchEndpoint,
  onSearchResult,
  defaultResults
}) => {
  const [query, setQuery] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  const debouncedQuery = useDebounce(query, 500)

  const performSearch = async (searchQuery: string) => {
    console.log("searched query",searchQuery)
    if (!searchQuery.trim()) {
      console.log("entered",defaultResults)
      onSearchResult(defaultResults)
      return;
    }

    setLoading(true)
    setError(null)
    try {
      const response = await axios.get(searchEndpoint, {
        params: { q: searchQuery },
      })
      console.log(response.data)
      onSearchResult(response.data)
    } catch (err) {
      setError('Failed to fetch search results. Please try again.')
      onSearchResult(defaultResults)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    performSearch(debouncedQuery)
  }, [debouncedQuery])

  return (
    <div className="w-full max-w-md mx-auto mt-8">
      <form onSubmit={(e) => {
        e.preventDefault()
        performSearch(query)
      }} className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder}
          className="w-full px-4 py-2 pr-12 text-gray-700 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all duration-300 ease-in-out"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading}
          className="absolute right-2 top-1/2 transform -translate-y-1/2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-opacity-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-300"
          aria-label="Search"
        >
          {loading ? (
            <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          ) : (
            <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
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
