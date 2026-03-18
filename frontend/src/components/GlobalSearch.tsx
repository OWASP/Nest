'use client'
import { sendGAEvent } from '@next/third-parties/google'
import { useShouldAutoFocusSearch } from 'hooks/useShouldAutoFocusSearch'
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

const INDEXES = ['chapters', 'events', 'organizations', 'projects', 'users']
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
  const [searchError, setSearchError] = useState(false)

  const router = useRouter()
  const inputRef = useRef<HTMLInputElement>(null)
  const panelRef = useRef<HTMLDivElement>(null)
  const searchVersionRef = useRef(0)
  const previousFocusRef = useRef<HTMLElement | null>(null)
  const shouldAutoFocus = useShouldAutoFocusSearch()

  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      if (e.key !== '/' || e.metaKey || e.ctrlKey || e.altKey) return
      const target = e.target as HTMLElement | null
      if (target?.closest('input, textarea, [contenteditable]')) return
      e.preventDefault()
      setIsOpen(true)
    }
    document.addEventListener('keydown', handleGlobalKeyDown)
    return () => document.removeEventListener('keydown', handleGlobalKeyDown)
  }, [])

  useEffect(() => {
    if (isOpen) {
      previousFocusRef.current = document.activeElement as HTMLElement
      const timer = shouldAutoFocus ? setTimeout(() => inputRef.current?.focus(), 50) : undefined
      document.body.style.overflow = 'hidden'
      return () => {
        if (timer !== undefined) clearTimeout(timer)
        document.body.style.overflow = ''
      }
    } else {
      document.body.style.overflow = ''
      previousFocusRef.current?.focus()
      previousFocusRef.current = null
    }
  }, [isOpen, shouldAutoFocus])

  useEffect(() => {
    if (!isOpen) {
      searchVersionRef.current++
      setSearchQuery('')
      setSuggestions([])
      setShowSuggestions(false)
      setHighlightedIndex(null)
      setSearchError(false)
    }
  }, [isOpen])

  const debouncedSearch = useMemo(
    () =>
      debounce(async (query: string) => {
        if (query && query.trim() !== '') {
          sendGAEvent({
            event: 'globalSearch',
            path: globalThis.location.pathname,
            value: query.length,
          })
        }
        if (query.length > 0) {
          const version = ++searchVersionRef.current
          setSearchError(false)
          let failedCount = 0
          const results = await Promise.all(
            INDEXES.map(async (index) => {
              try {
                const data = await fetchAlgoliaData(index, query, 1, SUGGESTION_COUNT)
                return {
                  indexName: index,
                  hits: data.hits as Chapter[] | Event[] | Organization[] | Project[] | User[],
                  totalPages: data.totalPages || 0,
                }
              } catch {
                failedCount++
                return { indexName: index, hits: [] as never[], totalPages: 0 }
              }
            })
          )
          if (version !== searchVersionRef.current) return
          if (failedCount === INDEXES.length) {
            setSuggestions([])
            setShowSuggestions(false)
            setSearchError(true)
          } else {
            setSuggestions(results.filter((result) => result.hits.length > 0) as Suggestion[])
            setShowSuggestions(true)
          }
        } else {
          searchVersionRef.current++
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
        case 'events': {
          const eventUrl = (suggestion as Event).url
          if (
            typeof eventUrl === 'string' &&
            (eventUrl.startsWith('https://') || eventUrl.startsWith('http://'))
          ) {
            globalThis.open(eventUrl, '_blank', 'noopener,noreferrer')
          }
          break
        }
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

  useEffect(() => {
    if (!isOpen || !panelRef.current) return

    const handleFocusTrap = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return

      const focusableElements = panelRef.current?.querySelectorAll<HTMLElement>(
        'input, button, a, [tabindex]:not([tabindex="-1"])'
      )
      if (!focusableElements || focusableElements.length === 0) return

      const firstElement = focusableElements[0]
      const lastElement = focusableElements[focusableElements.length - 1]

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault()
          lastElement.focus()
        }
      } else if (document.activeElement === lastElement) {
        e.preventDefault()
        firstElement.focus()
      }
    }

    document.addEventListener('keydown', handleFocusTrap)
    return () => document.removeEventListener('keydown', handleFocusTrap)
  }, [isOpen])

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newQuery = e.target.value
    setSearchQuery(newQuery)
    debouncedSearch(newQuery)
    setHighlightedIndex(null)
  }

  const handleClearSearch = () => {
    searchVersionRef.current++
    setSearchQuery('')
    setSuggestions([])
    setShowSuggestions(false)
    setHighlightedIndex(null)
    if (shouldAutoFocus) {
      inputRef.current?.focus()
    }
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

  const renderSuggestionItem = (
    hit: SearchHit,
    indexName: string,
    index: number,
    subIndex: number
  ) => {
    const hitRecord = hit as unknown as Record<string, string | undefined>
    const isHighlighted =
      highlightedIndex?.index === index && highlightedIndex?.subIndex === subIndex

    return (
      <li
        key={`global-search-${indexName}-${hitRecord.key || hitRecord.login || hitRecord.url}`}
        className={`mx-2 rounded-lg ${
          isHighlighted
            ? 'bg-blue-50 dark:bg-blue-900/30'
            : 'hover:bg-gray-50 dark:hover:bg-gray-700/50'
        }`}
      >
        <button
          type="button"
          onClick={() => handleSuggestionClick(hit, indexName)}
          onKeyDown={(e) => handleSuggestionKeyDown(e, hit, indexName)}
          className="flex w-full items-center overflow-hidden border-none bg-transparent px-3 py-2.5 text-left text-sm text-gray-700 focus:rounded-lg focus:outline-2 focus:outline-offset-2 focus:outline-blue-500 dark:text-gray-300"
        >
          {getIconForIndex(indexName)}
          <span className="block max-w-full truncate">{hitRecord.name || hitRecord.login}</span>
        </button>
      </li>
    )
  }

  const renderSuggestionGroup = (suggestion: Suggestion, index: number) => (
    <div key={suggestion.indexName}>
      <div className="px-4 pt-3 pb-1 text-xs font-semibold tracking-wider text-gray-500 uppercase dark:text-gray-400">
        {getIndexLabel(suggestion.indexName)}
      </div>
      <ul>
        {suggestion.hits.map((hit, subIndex) =>
          renderSuggestionItem(hit, suggestion.indexName, index, subIndex)
        )}
      </ul>
    </div>
  )

  const renderSearchContent = () => {
    if (showSuggestions && suggestions.length > 0) {
      return (
        <>
          {suggestions.map(renderSuggestionGroup)}
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
      )
    }

    if (searchError) {
      return (
        <div className="px-4 py-8 text-center text-sm text-red-500 dark:text-red-400">
          Search service is temporarily unavailable. Please try again later.
        </div>
      )
    }

    if (searchQuery && showSuggestions) {
      return (
        <div className="px-4 py-8 text-center text-sm text-gray-500 dark:text-gray-400">
          No results found for &ldquo;{searchQuery}&rdquo;
        </div>
      )
    }

    return (
      <div className="px-4 py-6 text-center text-sm text-gray-400 dark:text-gray-500">
        Start typing to search across projects, chapters, events, organizations, and members.
      </div>
    )
  }

  return (
    <>
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className="flex items-center gap-2 rounded-lg border border-slate-600/30 bg-transparent px-2.5 py-2 text-sm text-slate-600 transition-colors hover:border-slate-500/50 hover:bg-slate-200/50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-500 sm:w-60 sm:px-4 dark:border-slate-600/50 dark:bg-transparent dark:text-slate-300 dark:hover:border-slate-500/50 dark:hover:bg-slate-600/30 dark:hover:text-slate-100 dark:focus-visible:outline-slate-400"
        aria-label="Open search"
      >
        <FaSearch className="h-4 w-4 shrink-0" />
        <span className="hidden flex-1 text-left sm:inline">
          Type{' '}
          <kbd className="mx-1 rounded border border-slate-500/30 bg-transparent px-1.5 py-0.5 text-xs dark:border-slate-500/50 dark:bg-transparent">
            /
          </kbd>{' '}
          to search
        </span>
      </button>

      {isOpen && (
        <dialog
          open
          aria-modal="true"
          aria-label="Global search"
          className="fixed inset-0 z-[100] m-0 flex h-full max-h-full w-full max-w-full items-start justify-center border-none bg-transparent p-0 px-3 pt-[10vh] sm:px-0 sm:pt-[15vh]"
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
                aria-label="Search the OWASP community"
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

            <div className="max-h-[60vh] overflow-y-auto">{renderSearchContent()}</div>
          </div>
        </dialog>
      )}
    </>
  )
}
