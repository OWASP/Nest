import { faSearch, faTimes } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Skeleton } from '@heroui/skeleton'
import { debounce } from 'lodash'
import React, { useEffect, useRef, useState, useMemo } from 'react'
import TagManager from 'react-gtm-module'

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

  useEffect(() => {
    setSearchQuery(initialValue)
  }, [initialValue])

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const debouncedSearch = useMemo(
    () => debounce((query: string) => onSearch(query), 750),
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

  useEffect(() => {
    TagManager.dataLayer({
      dataLayer: {
        event: 'search',
        search_term: searchQuery,
        page_path: window.location.pathname,
      },
    })
  }, [searchQuery])

  const handleClearSearch = () => {
    setSearchQuery('')
    onSearch('')
    inputRef.current?.focus()
  }

  return (
    <div className="w-full max-w-md p-4">
      <div className="relative">
        {!isLoaded ? (
          <>
            <FontAwesomeIcon
              icon={faSearch}
              className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400"
            />
            <input
              ref={inputRef}
              type="text"
              value={searchQuery}
              onChange={handleSearchChange}
              placeholder={placeholder}
              className="h-12 w-full rounded-lg border border-gray-300 pl-10 pr-10 text-lg text-black focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:focus:border-blue-300 dark:focus:ring-blue-300"
            />
            {searchQuery && (
              <button
                className="absolute right-2 top-1/2 -translate-y-1/2 rounded-full p-1 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-300"
                onClick={handleClearSearch}
              >
                <FontAwesomeIcon icon={faTimes} />
              </button>
            )}
          </>
        ) : (
          <Skeleton className="h-16 rounded-lg" />
        )}
      </div>
    </div>
  )
}

export default SearchBar
