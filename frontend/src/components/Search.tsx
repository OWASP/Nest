import { Skeleton } from '@heroui/skeleton'
import { sendGTMEvent } from '@next/third-parties/google'
import { debounce } from 'lodash'
import { usePathname } from 'next/navigation'
import React, { useEffect, useRef, useState, useMemo } from 'react'
import { FaSearch, FaTimes } from 'react-icons/fa'

interface SearchProps {
  isLoaded: boolean
  onSearch: (query: string) => void
  placeholder: string
  initialValue?: string
}

const SearchBar: React.FC<SearchProps> = ({
  isLoaded,
  onSearch,
  placeholder,
  initialValue = '',
}) => {
  const [searchQuery, setSearchQuery] = useState(initialValue)
  const inputRef = useRef<HTMLInputElement>(null)
  const pathname = usePathname()

  useEffect(() => {
    setSearchQuery(initialValue)
  }, [initialValue])

  useEffect(() => {
    if (isLoaded && inputRef.current) {
      inputRef.current.focus()
    }
  }, [pathname, isLoaded])

  const debouncedSearch = useMemo(
    () =>
      debounce((query: string) => {
        onSearch(query)
        if (query && query.trim() !== '') {
          sendGTMEvent({
            event: 'search',
            path: globalThis.location.pathname,
            value: query,
          })
        }
      }, 750),
    [onSearch]
  )

  useEffect(() => {
    return () => {
      debouncedSearch.cancel()
    }
  }, [debouncedSearch])

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newQuery = e.target.value
    setSearchQuery(newQuery)
    debouncedSearch(newQuery)
  }

  const handleClearSearch = () => {
    debouncedSearch.cancel()
    setSearchQuery('')
    onSearch('')
    inputRef.current?.focus()
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      handleClearSearch()
    }
  }

  return (
    <div className="w-full max-w-md p-4">
      <div className="relative">
        {isLoaded ? (
          <>
            <FaSearch
              className="pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-gray-400"
              aria-hidden="true"
            />
            <input
              ref={inputRef}
              type="text"
              value={searchQuery}
              onChange={handleSearchChange}
              placeholder={placeholder}
              className="h-12 w-full rounded-lg border-1 border-gray-300 bg-white pr-10 pl-10 text-lg text-black focus:ring-1 focus:ring-blue-500 focus:outline-hidden dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:focus:ring-blue-300"
            />
            {searchQuery && (
              <button
                type="button"
                className="absolute top-1/2 right-2 h-8 w-8 -translate-y-1/2 rounded-md p-1 text-gray-400 hover:bg-gray-400 hover:text-gray-200 focus:ring-2 focus:ring-gray-300 focus:outline-hidden dark:hover:bg-gray-600"
                onClick={handleClearSearch}
                onKeyDown={handleKeyDown}
                aria-label="Clear search"
              >
                <FaTimes className="h-4 w-4" aria-hidden="true" />
              </button>
            )}
          </>
        ) : (
          <Skeleton className="h-12 rounded-lg" />
        )}
      </div>
    </div>
  )
}

export default SearchBar
