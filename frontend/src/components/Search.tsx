import { Skeleton } from '@heroui/skeleton'
import { sendGTMEvent } from '@next/third-parties/google'
import { useShouldAutoFocusSearch } from 'hooks/useShouldAutoFocusSearch'
import { debounce } from 'lodash'
import { usePathname } from 'next/navigation'
import React, { useEffect, useRef, useState, useMemo } from 'react'
import { FaSearch, FaTimes } from 'react-icons/fa'

interface SearchProps {
  isLoaded: boolean
  onSearch: (query: string) => void
  placeholder: string
  initialValue?: string
  className?: string
}

/** True when search is visually joined to filter/sort (tighter outer padding). */
function joinedToolbarInputClass(className: string): boolean {
  return (
    /(?:^|\s)rounded-none(?:\s|$)/.test(className) ||
    /(?:^|\s)rounded-r-none(?:\s|$)/.test(className) ||
    /\bmd:rounded-none\b/.test(className) ||
    /\bmd:rounded-r-none\b/.test(className)
  )
}

const SearchBar: React.FC<SearchProps> = ({
  isLoaded,
  onSearch,
  placeholder,
  initialValue = '',
  className = '',
}) => {
  const [searchQuery, setSearchQuery] = useState(initialValue)
  const inputRef = useRef<HTMLInputElement>(null)
  const onSearchRef = useRef(onSearch)
  const pathname = usePathname()
  const shouldAutoFocus = useShouldAutoFocusSearch()

  useEffect(() => {
    onSearchRef.current = onSearch
  }, [onSearch])

  const debouncedSearch = useMemo(
    () =>
      debounce((query: string) => {
        onSearchRef.current(query)
        if (query.trim()) {
          sendGTMEvent({
            event: 'search',
            path: globalThis.location.pathname,
            value: query,
          })
        }
      }, 750),
    []
  )

  useEffect(() => {
    return () => debouncedSearch.cancel()
  }, [debouncedSearch])

  useEffect(() => {
    debouncedSearch.cancel()
    setSearchQuery(initialValue)
  }, [initialValue, debouncedSearch])

  useEffect(() => {
    if (isLoaded && shouldAutoFocus) {
      inputRef.current?.focus()
    }
  }, [isLoaded, shouldAutoFocus])

  useEffect(() => {
    if (shouldAutoFocus && document.activeElement !== inputRef.current) {
      inputRef.current?.focus()
    }
  }, [pathname, shouldAutoFocus])

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newQuery = e.target.value
    setSearchQuery(newQuery)
    debouncedSearch(newQuery)
  }

  const handleClearSearch = () => {
    debouncedSearch.cancel()
    setSearchQuery('')
    onSearch('')
    if (shouldAutoFocus) {
      inputRef.current?.focus()
    }
  }

  return (
    <div
      className={`w-full max-w-md md:py-4 ${joinedToolbarInputClass(className) ? 'p-0' : 'md:p-4'}`}
    >
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
              className={`box-border h-12 w-full rounded-lg border-1 border-gray-300 bg-white py-0 pr-10 pl-10 text-sm leading-12 text-black placeholder:leading-12 placeholder:text-gray-500 focus:ring-1 focus:ring-blue-500 focus:outline-hidden dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:placeholder:text-gray-400 dark:focus:ring-blue-300 ${className}`}
            />
            {searchQuery && (
              <button
                type="button"
                className="absolute top-1/2 right-2 h-8 w-8 -translate-y-1/2 rounded-md p-1 text-gray-400 hover:bg-gray-400 hover:text-gray-200 focus:ring-2 focus:ring-gray-300 focus:outline-hidden dark:hover:bg-gray-600"
                onClick={handleClearSearch}
                aria-label="Clear search"
              >
                <FaTimes className="h-4 w-4" aria-hidden="true" />
              </button>
            )}
          </>
        ) : (
          <Skeleton className={`h-12 rounded-lg ${className}`} />
        )}
      </div>
    </div>
  )
}

export default SearchBar
