import { sendGAEvent } from '@next/third-parties/google'
import { debounce } from 'lodash'
import { useRouter } from 'next/navigation'
import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react'
import { FaTimes, FaSearch } from 'react-icons/fa'
import {
  FaUser,
  FaCalendar,
  FaFolder,
  FaBuilding,
  FaLocationDot,
} from 'react-icons/fa6'

import { fetchAlgoliaData } from 'server/fetchAlgoliaData'

import type { Chapter } from 'types/chapter'
import type { Event } from 'types/event'
import type { Organization } from 'types/organization'
import type { Project } from 'types/project'
import type { MultiSearchBarProps, Suggestion } from 'types/search'
import type { User } from 'types/user'

import { SEARCH_DEBOUNCE_DELAY_MS } from 'utils/constants'

type SearchHit = Chapter | Event | Organization | Project | User

type HitMeta = {
  key?: string
  login?: string
  url?: string
  name?: string
}

const MultiSearchBar: React.FC<MultiSearchBarProps> = ({
  placeholder,
  indexes,
  initialValue = '',
}) => {
  const router = useRouter()

  const [searchQuery, setSearchQuery] = useState(initialValue)
  const [suggestions, setSuggestions] = useState<Suggestion[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)

  const inputRef = useRef<HTMLInputElement>(null)
  const searchBarRef = useRef<HTMLDivElement>(null)

  const activeRequest = useRef<AbortController | null>(null)

  const pageCount = 1
  const suggestionCount = 3

  const triggerSearch = useMemo(() => {
    return debounce(async (query: string) => {
      if (!query.trim()) {
        setSuggestions([])
        setShowSuggestions(false)
        return
      }

      sendGAEvent({
        event: 'homepageSearch',
        path: globalThis.location.pathname,
        value: query,
      })

      activeRequest.current?.abort()

      const controller = new AbortController()
      activeRequest.current = controller

      const results: Suggestion[] = await Promise.all(
        indexes.map(async (index) => {
          const data = await fetchAlgoliaData<SearchHit>(
            index,
            query,
            pageCount,
            suggestionCount,
            [],
            controller.signal
          )

          return {
            indexName: index,
            hits: data.hits as Suggestion['hits'],
            totalPages: data.totalPages ?? 0,
          }
        })
      )


      if (controller.signal.aborted) return

      setSuggestions(results.filter((r) => r.hits.length > 0))
      setShowSuggestions(true)
    }, SEARCH_DEBOUNCE_DELAY_MS)
  }, [indexes])

  useEffect(() => {
    return () => {
      triggerSearch.cancel()
      activeRequest.current?.abort()
    }
  }, [triggerSearch])

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setSearchQuery(value)
    triggerSearch(value)
  }

  const handleClearSearch = () => {
    setSearchQuery('')
    setSuggestions([])
    setShowSuggestions(false)
    inputRef.current?.focus()
  }

  const handleSuggestionClick = useCallback(
    (suggestion: SearchHit, indexName: string) => {
      setShowSuggestions(false)

      switch (indexName) {
        case 'chapters':
          router.push(`/chapters/${suggestion.key}`)
          break

        case 'events':
          window.open((suggestion as Event).url, '_blank')
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
        <FaSearch className="pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-gray-400" />

        <input
          ref={inputRef}
          type="text"
          value={searchQuery}
          onChange={handleSearchChange}
          placeholder={placeholder}
          className="h-12 w-full rounded-lg border border-gray-300 bg-white pl-10 pr-10 text-lg"
        />

        {searchQuery && (
          <button
            type="button"
            onClick={handleClearSearch}
            className="absolute right-2 top-1/2 -translate-y-1/2"
          >
            <FaTimes />
          </button>
        )}

        {showSuggestions && (
          <div className="absolute left-0 top-14 z-50 w-full overflow-hidden rounded-lg border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800">
            {suggestions.map((group) => (
              <div key={group.indexName}>
                {group.hits.map((hit) => {
                  const safeHit = hit as HitMeta

                  return (
                    <button
                      key={safeHit.key || safeHit.login || safeHit.url}
                      onClick={() =>
                        handleSuggestionClick(hit, group.indexName)
                      }
                      className="flex w-full items-center px-4 py-3 text-left text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700"
                    >
                      {getIconForIndex(group.indexName)}
                      <span className="truncate">
                        {safeHit.name || safeHit.login}
                      </span>
                    </button>
                  )
                })}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default MultiSearchBar
