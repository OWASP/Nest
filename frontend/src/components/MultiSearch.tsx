import { faSearch, faTimes, faProjectDiagram, faBook } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { debounce } from 'lodash'
import type React from 'react'
import { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'

interface MultiSearchBarProps {
  isLoaded: boolean
  placeholder: string
  indexes: string[]
  initialValue?: string
}

interface Suggestion {
  indexName: string
  hits: any[]
  totalPages: number
}

const MultiSearchBar: React.FC<MultiSearchBarProps> = ({
  isLoaded,
  placeholder,
  indexes,
  initialValue = '',
}) => {
  const [searchQuery, setSearchQuery] = useState(initialValue)
  const [suggestions, setSuggestions] = useState<Suggestion[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const navigate = useNavigate()
  const pageCount = 1
  const suggestionCount = 3

  useEffect(() => {
    setSearchQuery(initialValue)
  }, [initialValue])

  const debouncedSearch = useMemo(
    () =>
      debounce(async (query: string) => {
        if (query.length > 0) {
          const results = await Promise.all(
            indexes.map(async (index) => {
              const data = await fetchAlgoliaData(index, query, pageCount, suggestionCount)
              return {
                indexName: index,
                hits: data.hits,
                totalPages: data.totalPages,
              }
            })
          )
          setSuggestions(results.filter((result) => result.hits.length > 0))
          setShowSuggestions(true)
        } else {
          setSuggestions([])
          setShowSuggestions(false)
        }
      }, 300),
    [indexes]
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
    setSearchQuery('')
    setSuggestions([])
    setShowSuggestions(false)
  }

  const handleSuggestionClick = (suggestion: any, indexName: string) => {
    setSearchQuery(suggestion.idx_name || suggestion.name)
    setShowSuggestions(false)

    switch (indexName) {
      case 'projects':
        navigate(`/projects/${suggestion.key}`)
        break
      case 'chapters':
        navigate(`/chapters/${suggestion.key}`)
        break
      default:
        throw new Error(`Unknown index name: ${indexName}`)
    }
  }

  const getIconForIndex = (indexName: string) => {
    switch (indexName) {
      case 'projects':
        return faProjectDiagram
      case 'chapters':
        return faBook
      default:
        return faSearch
    }
  }

  return (
    <div className="w-full max-w-md p-4">
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
              onChange={handleSearchChange}
              placeholder={placeholder}
              className="h-12 w-full rounded-lg border border-gray-300 pl-10 pr-10 text-lg text-black transition duration-300 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:focus:border-blue-300 dark:focus:ring-blue-300"
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
          <div className="h-12 w-full animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700"></div>
        )}
        {showSuggestions && suggestions.length > 0 && (
          <div className="absolute z-10 mt-1 w-full overflow-hidden rounded-md border bg-white shadow-lg dark:border-gray-700 dark:bg-gray-800">
            {suggestions.map((suggestion) => (
              <div
                key={suggestion.indexName}
                className="border-b text-gray-600 last:border-b-0 dark:border-gray-700 dark:text-gray-300"
              >
                <h3 className="border-b p-2 text-start font-semibold">
                  {suggestion.indexName.charAt(0).toUpperCase() + suggestion.indexName.slice(1)}
                </h3>
                <ul>
                  {suggestion.hits.map((hit, index) => (
                    <li
                      key={index}
                      className="flex cursor-pointer items-center px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700"
                      onClick={() => handleSuggestionClick(hit, suggestion.indexName)}
                    >
                      <FontAwesomeIcon
                        icon={getIconForIndex(suggestion.indexName)}
                        className="mr-2 text-gray-400"
                      />
                      <span className="whitespace-nowrap">{hit.name || 'Untitled'}</span>
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
