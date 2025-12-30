import { sendGAEvent } from '@next/third-parties/google'
import { debounce } from 'lodash'
import { useRouter } from 'next/navigation'
import type React from 'react'
import { useState, useEffect, useMemo, useCallback, useRef } from 'react'
import { FaTimes, FaSearch } from 'react-icons/fa'
import { FaUser, FaCalendar, FaFolder, FaBuilding, FaLocationDot } from 'react-icons/fa6'
import { SiAlgolia } from 'react-icons/si'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'
import type { Chapter } from 'types/chapter'
import type { Event } from 'types/event'
import type { Organization } from 'types/organization'
import type { Project } from 'types/project'
import type { MultiSearchBarProps, Suggestion } from 'types/search'
import type { User } from 'types/user'

const MultiSearchBar: React.FC<MultiSearchBarProps> = ({
  isLoaded,
  placeholder,
  indexes,
  initialValue = '',
  eventData,
}) => {
  const [searchQuery, setSearchQuery] = useState(initialValue)
  const [suggestions, setSuggestions] = useState<Suggestion[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [highlightedIndex, setHighlightedIndex] = useState<{
    index: number
    subIndex: number
  } | null>(null)
  const router = useRouter()
  const pageCount = 1
  const suggestionCount = 3
  const searchBarRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const debouncedSearch = useMemo(
    () =>
      debounce(async (query: string) => {
        if (query && query.trim() !== '') {
          sendGAEvent({
            event: 'homepageSearch',
            path: globalThis.location.pathname,
            value: query,
          })
        }
        if (query.length > 0) {
          const results = await Promise.all(
            indexes.map(async (index) => {
              const data = await fetchAlgoliaData(index, query, pageCount, suggestionCount)
              return {
                indexName: index,
                hits: data.hits as Chapter[] | Event[] | Organization[] | Project[] | User[],
                totalPages: data.totalPages || 0,
              }
            })
          )
          const filteredEvents =
            eventData?.filter((event) => event.name.toLowerCase().includes(query.toLowerCase())) ||
            []

          if (filteredEvents.length > 0) {
            results.push({
              indexName: 'events',
              hits: filteredEvents.slice(0, suggestionCount) as Event[],
              totalPages: 1,
            })
          }
          setSuggestions(results.filter((result) => result.hits.length > 0) as Suggestion[])
          setShowSuggestions(true)
        } else {
          setSuggestions([])
          setShowSuggestions(false)
        }
      }, 300),
    [eventData, indexes]
  )

  useEffect(() => {
    return () => {
      debouncedSearch.cancel()
    }
  }, [debouncedSearch])

  const handleSuggestionClick = useCallback(
    (suggestion: Chapter | Project | User | Event | Organization, indexName: string) => {
      setSearchQuery(suggestion.name ?? '')
      setShowSuggestions(false)

      switch (indexName) {
        case 'chapters':
          router.push(`/chapters/${suggestion.key}`)
          break
        case 'events':
          globalThis.open((suggestion as Event).url, '_blank')
          break
        case 'organizations':
          // Use type guard to safely access login property
          if ('login' in suggestion && suggestion.login) {
            router.push(`/organizations/${suggestion.login}`)
          }
          break
        case 'projects':
          router.push(`/projects/${suggestion.key}`)
          break
        case 'users':
          router.push(`/members/${suggestion.key}`)
          break
      }
    },
    [router]
  )

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setShowSuggestions(false)
        inputRef.current?.blur()
      } else if (event.key === 'Enter' && highlightedIndex !== null) {
        const { index, subIndex } = highlightedIndex
        const suggestion = suggestions[index].hits[subIndex]
        handleSuggestionClick(
          suggestion as Chapter | Organization | Project | User | Event,
          suggestions[index].indexName
        )
      } else if (event.key === 'ArrowDown') {
        event.preventDefault()
        if (highlightedIndex === null) {
          setHighlightedIndex({ index: 0, subIndex: 0 })
        } else {
          const { index, subIndex } = highlightedIndex
          if (subIndex < suggestions[index].hits.length - 1) {
            setHighlightedIndex({ index, subIndex: subIndex + 1 })
          } else if (index < suggestions.length - 1) {
            setHighlightedIndex({ index: index + 1, subIndex: 0 })
          }
        }
      } else if (event.key === 'ArrowUp') {
        event.preventDefault()
        if (highlightedIndex !== null) {
          const { index, subIndex } = highlightedIndex
          if (subIndex > 0) {
            setHighlightedIndex({ index, subIndex: subIndex - 1 })
          } else if (index > 0) {
            setHighlightedIndex({
              index: index - 1,
              subIndex: suggestions[index - 1].hits.length - 1,
            })
          }
        }
      }
    }

    document.addEventListener('keydown', handleKeyDown)

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [searchQuery, suggestions, highlightedIndex, handleSuggestionClick])

  useEffect(() => {
    inputRef.current?.focus()

    const handleClickOutside = (event: MouseEvent) => {
      if (searchBarRef.current && !searchBarRef.current.contains(event.target as Node)) {
        setShowSuggestions(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newQuery = e.target.value
    setSearchQuery(newQuery)
    debouncedSearch(newQuery)
    setHighlightedIndex(null)
  }

  const handleClearSearch = () => {
    setSearchQuery('')
    setSuggestions([])
    setShowSuggestions(false)
    setHighlightedIndex(null)
  }

  const handleFocusSearch = () => {
    if (searchQuery.trim().length > 0 && !showSuggestions) {
      setShowSuggestions(true)
    } else {
      setHighlightedIndex(null)
    }
  }

  const handleSuggestionKeyDown = (
    e: React.KeyboardEvent,
    hit: Chapter | Project | User | Event | Organization,
    indexName: string
  ) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      e.stopPropagation()
      handleSuggestionClick(hit, indexName)
    }
  }

  const getIconForIndex = (indexName: string) => {
    switch (indexName) {
      case 'chapters':
        return <FaLocationDot className="mr-2 shrink-0 text-gray-400" />
      case 'events':
        return <FaCalendar className="mr-2 shrink-0 text-gray-400" />
      case 'organizations':
        return <FaBuilding className="mr-2 shrink-0 text-gray-400" />
      case 'projects':
        return <FaFolder className="mr-2 shrink-0 text-gray-400" />
      case 'users':
        return <FaUser className="mr-2 shrink-0 text-gray-400" />
      default:
        return <FaSearch className="mr-2 shrink-0 text-gray-400" />
    }
  }

  return (
    <div className="w-full max-w-md p-4" ref={searchBarRef}>
      <div className="relative">
        {isLoaded ? (
          <>
            <FaSearch
              className="pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-gray-400"
              aria-hidden="true"
            />
            <input
              type="text"
              value={searchQuery}
              ref={inputRef}
              onChange={handleSearchChange}
              onFocus={handleFocusSearch}
              placeholder={placeholder}
              className="h-12 w-full rounded-lg border-1 border-gray-300 bg-white pr-10 pl-10 text-lg text-black focus:ring-1 focus:ring-blue-500 focus:outline-hidden dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:focus:ring-blue-300"
            />
            {searchQuery && (
              <button
                type="button"
                className="absolute top-1/2 right-2 h-8 w-8 -translate-y-1/2 rounded-md p-1 text-gray-400 hover:bg-gray-400 hover:text-gray-200 focus:ring-2 focus:ring-gray-300 focus:outline-hidden dark:hover:bg-gray-600"
                onClick={handleClearSearch}
                aria-label="Clear search"
              >
                <FaTimes />
              </button>
            )}
          </>
        ) : (
          <div className="h-12 w-full animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700"></div>
        )}
        {showSuggestions && suggestions.length > 0 && (
          <div className="absolute z-10 mt-1 w-full overflow-hidden rounded-md border-1 border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-800">
            {suggestions.map((suggestion, index) => (
              <div
                key={suggestion.indexName}
                className="border-b-1 border-b-gray-200 text-gray-600 last:border-b-0 dark:border-b-gray-700 dark:text-gray-300"
              >
                <ul>
                  {suggestion.hits.map((hit, subIndex) => (
                    <li
                      key={`${hit.key || hit.login || hit.url}-${subIndex}`}
                      className={`flex items-center px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 ${highlightedIndex?.index === index && highlightedIndex?.subIndex === subIndex
                          ? 'bg-gray-100 dark:bg-gray-700'
                          : ''
                        }`}
                    >
                      <button
                        type="button"
                        onClick={() => handleSuggestionClick(hit, suggestion.indexName)}
                        onKeyDown={(e) =>
                          handleSuggestionKeyDown(
                            e,
                            hit as Chapter | Organization | Project | User | Event,
                            suggestion.indexName
                          )
                        }
                        className="flex w-full cursor-pointer items-center overflow-hidden border-none bg-transparent p-0 text-left focus:rounded focus:outline-2 focus:outline-offset-2 focus:outline-blue-500"
                      >
                        {getIconForIndex(suggestion.indexName)}
                        <span className="block max-w-full truncate">{hit.name || hit.login}</span>
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
            <a
              aria-label="Search by Algolia (opens in a new tab)"
              className="flex items-center justify-center gap-2 bg-white py-2 text-gray-500 hover:text-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
              href="https://www.algolia.com"
              rel="noopener noreferrer"
              target="_blank"
            >
              <SiAlgolia className="h-3 w-3" aria-hidden="true" />
              <span className="text-xs">Search by Algolia</span>
            </a>
          </div>
        )}
      </div>
    </div>
  )
}

export default MultiSearchBar
