'use client'
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
import type { Suggestion } from 'types/search'
import type { User } from 'types/user'

type SearchHit = Chapter | Event | Organization | Project | User

const INDEXES = ['chapters', 'organizations', 'projects', 'users']
const SUGGESTION_COUNT = 3

export default function GlobalSearch() {
  const [isOpen, setIsOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [suggestions, setSuggestions] = useState<Suggestion[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [highlightedIndex, setHighlightedIndex] = useState<{
    index: number
    subIndex: number
  } | null>(null)

  const router = useRouter()
  const inputRef = useRef<HTMLInputElement>(null)
  const panelRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setIsOpen((prev) => !prev)
      }
    }
    document.addEventListener('keydown', handleGlobalKeyDown)
    return () => document.removeEventListener('keydown', handleGlobalKeyDown)
  }, [])

  useEffect(() => {
    if (isOpen) {
      const timer = setTimeout(() => inputRef.current?.focus(), 50)
      document.body.style.overflow = 'hidden'
      return () => {
        clearTimeout(timer)
        document.body.style.overflow = ''
      }
    } else {
      document.body.style.overflow = ''
    }
  }, [isOpen])

  useEffect(() => {
    if (!isOpen) {
      setSearchQuery('')
      setSuggestions([])
      setShowSuggestions(false)
      setHighlightedIndex(null)
    }
  }, [isOpen])

  const debouncedSearch = useMemo(
    () =>
      debounce(async (query: string) => {
        if (query && query.trim() !== '') {
          sendGAEvent({
            event: 'globalSearch',
            path: globalThis.location.pathname,
            value: query,
          })
        }
        if (query.length > 0) {
          const results = await Promise.all(
            INDEXES.map(async (index) => {
              const data = await fetchAlgoliaData(index, query, 1, SUGGESTION_COUNT)
              return {
                indexName: index,
                hits: data.hits as Chapter[] | Event[] | Organization[] | Project[] | User[],
                totalPages: data.totalPages || 0,
              }
            })
          )
          setSuggestions(results.filter((result) => result.hits.length > 0) as Suggestion[])
          setShowSuggestions(true)
        } else {
          setSuggestions([])
          setShowSuggestions(false)
        }
      }, 300),
    []
  )

  useEffect(() => {
    return () => {
      debouncedSearch.cancel()
    }
  }, [debouncedSearch])

  const handleSuggestionClick = useCallback(
    (suggestion: SearchHit, indexName: string) => {
      setIsOpen(false)

      switch (indexName) {
        case 'chapters':
          router.push(`/chapters/${suggestion.key}`)
          break
        case 'events':
          window.open((suggestion as Event).url, '_blank', 'noopener,noreferrer')
          break
        case 'organizations':
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
    if (!isOpen) return

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsOpen(false)
      } else if (event.key === 'Enter' && highlightedIndex !== null) {
        event.preventDefault()
        const { index, subIndex } = highlightedIndex
        const suggestion = suggestions[index].hits[subIndex]
        handleSuggestionClick(suggestion, suggestions[index].indexName)
      } else if (event.key === 'ArrowDown') {
        event.preventDefault()
        if (highlightedIndex === null) {
          if (suggestions.length > 0 && suggestions[0].hits.length > 0) {
            setHighlightedIndex({ index: 0, subIndex: 0 })
          }
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
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, suggestions, highlightedIndex, handleSuggestionClick])

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
    inputRef.current?.focus()
  }

  const handleSuggestionKeyDown = (e: React.KeyboardEvent, hit: SearchHit, indexName: string) => {
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

  const getIndexLabel = (indexName: string) => {
    switch (indexName) {
      case 'chapters':
        return 'Chapters'
      case 'events':
        return 'Events'
      case 'organizations':
        return 'Organizations'
      case 'projects':
        return 'Projects'
      case 'users':
        return 'Members'
      default:
        return indexName
    }
  }

  return (
    <>
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className="flex items-center gap-2 rounded-lg border border-slate-500/30 bg-slate-700/50 px-2.5 py-2 text-sm text-slate-300 transition-colors hover:border-slate-400/50 hover:bg-slate-600/50 hover:text-slate-200 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white sm:w-52 sm:px-4 dark:border-slate-600/50 dark:bg-slate-700/30 dark:hover:border-slate-500/50 dark:hover:bg-slate-600/30"
        aria-label="Open search"
      >
        <FaSearch className="h-4 w-4 shrink-0 sm:h-3.5 sm:w-3.5" />
        <span className="hidden flex-1 text-left sm:inline">Search...</span>
        <kbd className="hidden shrink-0 rounded border border-slate-500/50 bg-slate-600/50 px-1.5 py-0.5 text-xs text-slate-400 sm:inline">
          ⌘K
        </kbd>
      </button>

      {isOpen && (
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Global search"
          className="fixed inset-0 z-100 flex items-start justify-center px-3 pt-[10vh] sm:px-0 sm:pt-[15vh]"
        >
          {/* Backdrop */}
          <button
            type="button"
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={() => setIsOpen(false)}
            aria-label="Close search"
            tabIndex={-1}
          />
          <div
            ref={panelRef}
            className="relative mx-4 w-full max-w-xl overflow-hidden rounded-xl border border-gray-200 bg-white shadow-2xl dark:border-gray-700 dark:bg-gray-800"
          >
            <div className="relative flex items-center border-b border-gray-200 dark:border-gray-700">
              <FaSearch className="pointer-events-none absolute left-4 h-4 w-4 text-gray-400" />
              <input
                ref={inputRef}
                type="text"
                value={searchQuery}
                onChange={handleSearchChange}
                placeholder="Search the OWASP community..."
                className="h-14 w-full bg-transparent pr-10 pl-11 text-base text-gray-900 placeholder-gray-400 focus:outline-none dark:text-white dark:placeholder-gray-500"
              />
              {searchQuery ? (
                <button
                  type="button"
                  className="absolute right-3 rounded-md p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-700 dark:hover:text-gray-300"
                  onClick={handleClearSearch}
                  aria-label="Clear search"
                >
                  <FaTimes className="h-4 w-4" />
                </button>
              ) : (
                <kbd className="absolute right-3 rounded border border-gray-300 bg-gray-100 px-1.5 py-0.5 text-xs text-gray-400 dark:border-gray-600 dark:bg-gray-700">
                  ESC
                </kbd>
              )}
            </div>

            <div className="max-h-[60vh] overflow-y-auto">
              {showSuggestions && suggestions.length > 0 ? (
                <>
                  {suggestions.map((suggestion, index) => (
                    <div key={suggestion.indexName}>
                      <div className="px-4 pt-3 pb-1 text-xs font-semibold tracking-wider text-gray-500 uppercase dark:text-gray-400">
                        {getIndexLabel(suggestion.indexName)}
                      </div>
                      <ul>
                        {suggestion.hits.map((hit, subIndex) => (
                          <li
                            key={`global-search-${suggestion.indexName}-${(hit as unknown as Record<string, string | undefined>).key || (hit as unknown as Record<string, string | undefined>).login || (hit as unknown as Record<string, string | undefined>).url}`}
                            className={`mx-2 rounded-lg ${
                              highlightedIndex?.index === index &&
                              highlightedIndex?.subIndex === subIndex
                                ? 'bg-blue-50 dark:bg-blue-900/30'
                                : 'hover:bg-gray-50 dark:hover:bg-gray-700/50'
                            }`}
                          >
                            <button
                              type="button"
                              onClick={() => handleSuggestionClick(hit, suggestion.indexName)}
                              onKeyDown={(e) =>
                                handleSuggestionKeyDown(e, hit, suggestion.indexName)
                              }
                              className="flex w-full items-center overflow-hidden border-none bg-transparent px-3 py-2.5 text-left text-sm text-gray-700 focus:rounded-lg focus:outline-2 focus:outline-offset-2 focus:outline-blue-500 dark:text-gray-300"
                            >
                              {getIconForIndex(suggestion.indexName)}
                              <span className="block max-w-full truncate">
                                {(hit as unknown as Record<string, string | undefined>).name ||
                                  (hit as unknown as Record<string, string | undefined>).login}
                              </span>
                            </button>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                  <a
                    aria-label="Search by Algolia (opens in a new tab)"
                    className="flex items-center justify-center gap-2 border-t border-gray-200 py-2.5 text-gray-400 hover:text-gray-600 dark:border-gray-700 dark:text-gray-500 dark:hover:text-gray-300"
                    href="https://www.algolia.com"
                    rel="noopener noreferrer"
                    target="_blank"
                  >
                    <SiAlgolia className="h-3 w-3" aria-hidden="true" />
                    <span className="text-xs">Search by Algolia</span>
                  </a>
                </>
              ) : searchQuery && showSuggestions ? (
                <div className="px-4 py-8 text-center text-sm text-gray-500 dark:text-gray-400">
                  No results found for &ldquo;{searchQuery}&rdquo;
                </div>
              ) : (
                <div className="px-4 py-6 text-center text-sm text-gray-400 dark:text-gray-500">
                  Start typing to search across projects, chapters, organizations, and members.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  )
}
