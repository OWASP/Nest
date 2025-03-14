import {
  faSearch,
  faTimes,
  faUser,
  faCalendarAlt,
  faLocationPin,
  faFolder,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { fetchTypesenseData } from 'api/fetchTypesenseData'
import { debounce } from 'lodash'
import type React from 'react'
import { useState, useEffect, useMemo, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { ChapterTypeAlgolia } from 'types/chapter'
import { EventType } from 'types/event'
import { ProjectTypeAlgolia } from 'types/project'
import { MultiSearchBarProps, Suggestion } from 'types/search'
import { User } from 'types/user'

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
  const navigate = useNavigate()
  const pageCount = 1
  const suggestionCount = 5
  const searchBarRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const debouncedSearch = useMemo(
    () =>
      debounce(async (query: string) => {
        if (query.length > 0) {
          const results = await Promise.all(
            indexes.map(async (index) => {
              const data = await fetchTypesenseData(index, query, pageCount, suggestionCount)
              return {
                indexName: index,
                hits: data.hits as
                  | ChapterTypeAlgolia[]
                  | EventType[]
                  | ProjectTypeAlgolia[]
                  | User[],
                totalPages: data.totalPages,
              }
            })
          )
          const filteredEvents =
            eventData?.filter((event) => event.name.toLowerCase().includes(query.toLowerCase())) ||
            []
          if (filteredEvents.length > 0) {
            results.push({
              indexName: 'events',
              hits: filteredEvents.slice(0, suggestionCount),
              totalPages: 1,
            })
          }
          setSuggestions(results.filter((result) => result.hits.length > 0))
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
    (suggestion: ChapterTypeAlgolia | ProjectTypeAlgolia | User | EventType, indexName: string) => {
      setSearchQuery(suggestion.name)
      setShowSuggestions(false)

      switch (indexName) {
        case 'chapter':
          navigate(`/chapters/${suggestion.key}`)
          break
        case 'events':
          window.open((suggestion as EventType).url, '_blank')
          break
        case 'project':
          navigate(`/projects/${suggestion.key}`)
          break
        case 'user':
          navigate(`/community/users/${suggestion.key}`)
          break
      }
    },
    [navigate]
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
          suggestion as ChapterTypeAlgolia | ProjectTypeAlgolia | User | EventType,
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

  const getIconForIndex = (indexName: string) => {
    switch (indexName) {
      case 'chapter':
        return faLocationPin
      case 'events':
        return faCalendarAlt
      case 'project':
        return faFolder
      case 'user':
        return faUser
      default:
        return faSearch
    }
  }

  return (
    <div className="w-full max-w-md p-4" ref={searchBarRef}>
      <div className="relative">
        {isLoaded ? (
          <>
            <FontAwesomeIcon
              icon={faSearch}
              className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400"
            />
            <input
              type="text"
              value={searchQuery}
              ref={inputRef}
              onChange={handleSearchChange}
              onFocus={handleFocusSearch}
              placeholder={placeholder}
              className="h-12 w-full rounded-lg border border-gray-300 pl-10 pr-10 text-lg text-black focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:focus:border-blue-300 dark:focus:ring-blue-300"
            />
            {searchQuery && (
              <button
                className="absolute right-2 top-1/2 -translate-y-1/2 rounded-full p-1 text-gray-400 hover:text-gray-600"
                onClick={handleClearSearch}
              >
                <FontAwesomeIcon icon={faTimes} />
              </button>
            )}
          </>
        ) : (
          <div className="animate-pulse h-12 w-full rounded-lg bg-gray-200 dark:bg-gray-700"></div>
        )}
        {showSuggestions && suggestions.length > 0 && (
          <div className="absolute z-10 mt-1 w-full overflow-hidden rounded-md border bg-white shadow-lg dark:border-gray-700 dark:bg-gray-800">
            {suggestions.map((suggestion, index) => (
              <div
                key={suggestion.indexName}
                className="border-b text-gray-600 last:border-b-0 dark:border-gray-700 dark:text-gray-300"
              >
                <ul>
                  {suggestion.hits.map((hit, subIndex) => (
                    <li
                      key={subIndex}
                      className={`flex items-center px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 ${
                        highlightedIndex &&
                        highlightedIndex.index === index &&
                        highlightedIndex.subIndex === subIndex
                          ? 'bg-gray-100 dark:bg-gray-700'
                          : ''
                      }`}
                    >
                      <button
                        onClick={() => handleSuggestionClick(hit, suggestion.indexName)}
                        className="flex w-full cursor-pointer items-center overflow-hidden border-none bg-transparent p-0 text-left"
                      >
                        <FontAwesomeIcon
                          icon={getIconForIndex(suggestion.indexName)}
                          className="mr-2 flex-shrink-0 text-gray-400"
                        />
                        <span className="block max-w-full truncate">{hit.name || hit.login}</span>
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default MultiSearchBar
