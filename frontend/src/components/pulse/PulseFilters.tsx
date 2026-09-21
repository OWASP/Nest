'use client'

import { Button } from '@heroui/button'
import { type ReactNode, useRef } from 'react'
import { FaFolder, FaGlobe, FaMagnifyingGlass, FaXmark } from 'react-icons/fa6'
import type { PulseFiltersProps } from 'types/pulse'
import { sortOptionsPulse } from 'utils/sortingOptions'
import SortBy from 'components/SortBy'

export const ACTIVITY_TYPES = [
  { label: 'All Activity Types', value: '' },
  { label: 'Issue Opened', value: 'issue_opened' },
  { label: 'Issue Closed', value: 'issue_closed' },
  { label: 'PR Opened', value: 'pr_opened' },
  { label: 'PR Closed', value: 'pr_closed' },
  { label: 'PR Merged', value: 'pr_merged' },
  { label: 'Release Published', value: 'release_published' },
]

export const TIME_RANGES = [
  { label: 'All Time', value: '' },
  { label: 'Last 24 Hours', value: '24h' },
  { label: 'Last 7 Days', value: '7d' },
  { label: 'Last 30 Days', value: '30d' },
  { label: 'Last 90 Days', value: '90d' },
]

const FilterDismissButton = ({ onPress, label }: { onPress: () => void; label: string }) => (
  <Button
    size="sm"
    isIconOnly
    variant="light"
    onPress={onPress}
    aria-label={label}
    className="h-4 w-4 min-w-0 p-0 text-gray-400 hover:text-gray-900 dark:hover:text-white"
  >
    <FaXmark className="h-3 w-3" />
  </Button>
)

export default function PulseFilters({
  activityType,
  chapterKey,
  chapterSearchInput,
  chapterSuggestions,
  clearAllFilters,
  handleSelectChapter,
  handleSelectProject,
  isSearchingChapters,
  isSearchingProjects,
  order,
  projectKey,
  projectSearchInput,
  projectSuggestions,
  searchQuery,
  setActivityType,
  setChapterKey,
  setChapterSearchInput,
  setOrder,
  setPage,
  setProjectKey,
  setProjectSearchInput,
  setSearchQuery,
  setShowChapterSuggestions,
  setShowProjectSuggestions,
  setTimeRange,
  showChapterSuggestions,
  showProjectSuggestions,
  timeRange,
}: Readonly<PulseFiltersProps>) {
  const projectBlurTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const chapterBlurTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  let projectSuggestionsContent: ReactNode

  if (isSearchingProjects) {
    projectSuggestionsContent = (
      <div className="px-3.5 py-2 text-xs text-gray-400">Searching projects...</div>
    )
  } else if (projectSuggestions.length === 0) {
    projectSuggestionsContent = (
      <div className="px-3.5 py-2 text-xs text-gray-400">No project suggestions found</div>
    )
  } else {
    projectSuggestionsContent = projectSuggestions.map((proj) => (
      <button
        key={proj.id || proj.name}
        type="button"
        onMouseDown={(e) => {
          e.preventDefault()
          handleSelectProject(proj)
        }}
        onClick={() => handleSelectProject(proj)}
        className="flex w-full items-center justify-between px-3.5 py-2 text-left text-xs font-medium text-gray-700 hover:bg-blue-50 dark:text-gray-200 dark:hover:bg-gray-700"
      >
        <span className="font-semibold text-gray-900 dark:text-white">{proj.name}</span>
      </button>
    ))
  }

  let chapterSuggestionsContent: ReactNode

  if (isSearchingChapters) {
    chapterSuggestionsContent = (
      <div className="px-3.5 py-2 text-xs text-gray-400">Searching chapters...</div>
    )
  } else if (chapterSuggestions.length === 0) {
    chapterSuggestionsContent = (
      <div className="px-3.5 py-2 text-xs text-gray-400">No chapter suggestions found</div>
    )
  } else {
    chapterSuggestionsContent = chapterSuggestions.map((chap) => (
      <button
        key={chap.id || chap.name}
        type="button"
        onMouseDown={(e) => {
          e.preventDefault()
          handleSelectChapter(chap)
        }}
        onClick={() => handleSelectChapter(chap)}
        className="flex w-full items-center justify-between px-3.5 py-2 text-left text-xs font-medium text-gray-700 hover:bg-blue-50 dark:text-gray-200 dark:hover:bg-gray-700"
      >
        <span className="font-semibold text-gray-900 dark:text-white">{chap.name}</span>
      </button>
    ))
  }

  const hasActiveFilters = Boolean(
    searchQuery || activityType || projectKey || chapterKey || timeRange
  )

  return (
    <div className="space-y-4 rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-800">
      <div className="relative">
        <FaMagnifyingGlass className="absolute top-3.5 left-3.5 h-4 w-4 text-gray-400" />
        <input
          aria-label="Search activity"
          type="text"
          placeholder="Search activity..."
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value)
          }}
          className="w-full rounded-lg border border-gray-300 bg-gray-50 py-2.5 pr-4 pl-10 text-sm text-gray-900 placeholder:text-gray-400 focus:border-blue-500 focus:outline-none dark:border-gray-700 dark:bg-gray-800 dark:text-white dark:placeholder:text-gray-400"
        />
      </div>

      <div className="mt-2 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <SortBy
          id="pulse-activity-type-select"
          sortOptions={ACTIVITY_TYPES.map((t) => ({ key: t.value, label: t.label }))}
          selectedSortOption={activityType}
          selectedOrder="desc"
          onSortChange={(value) => {
            setActivityType(value)
            setPage(1)
          }}
          hideOrderButton
          containerClassName="h-[42px] bg-gray-50 dark:bg-gray-800 border-gray-300 dark:border-gray-700"
          triggerClassName="w-full"
        />

        <div className="relative">
          <input
            aria-label="Filter by project"
            type="text"
            placeholder="All Projects"
            value={projectSearchInput}
            onFocus={() => {
              clearTimeout(projectBlurTimer.current ?? undefined)
              setShowProjectSuggestions(true)
            }}
            onBlur={() => {
              projectBlurTimer.current = setTimeout(() => setShowProjectSuggestions(false), 200)
            }}
            onChange={(e) => {
              setProjectSearchInput(e.target.value)
              setShowProjectSuggestions(true)
              setProjectKey('')
              setPage(1)
            }}
            className="w-full rounded-lg border border-gray-300 bg-gray-50 px-3.5 py-2.5 pr-8 text-sm font-medium text-gray-800 placeholder:text-gray-400 focus:border-blue-500 focus:outline-none dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200 dark:placeholder:text-gray-400"
          />
          <FaFolder className="pointer-events-none absolute top-3.5 right-3 h-3.5 w-3.5 text-gray-400" />

          {showProjectSuggestions && (
            <div className="absolute top-full right-0 left-0 z-50 mt-1 max-h-60 overflow-y-auto rounded-lg border border-gray-200 bg-white py-1 shadow-lg dark:border-gray-700 dark:bg-gray-800">
              {projectSuggestionsContent}
            </div>
          )}
        </div>

        <div className="relative">
          <input
            aria-label="Filter by chapter"
            type="text"
            placeholder="All Chapters"
            value={chapterSearchInput}
            onFocus={() => {
              clearTimeout(chapterBlurTimer.current ?? undefined)
              setShowChapterSuggestions(true)
            }}
            onBlur={() => {
              chapterBlurTimer.current = setTimeout(() => setShowChapterSuggestions(false), 200)
            }}
            onChange={(e) => {
              setChapterSearchInput(e.target.value)
              setShowChapterSuggestions(true)
              setChapterKey('')
              setPage(1)
            }}
            className="w-full rounded-lg border border-gray-300 bg-gray-50 px-3.5 py-2.5 pr-8 text-sm font-medium text-gray-800 placeholder:text-gray-400 focus:border-blue-500 focus:outline-none dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200 dark:placeholder:text-gray-400"
          />
          <FaGlobe className="pointer-events-none absolute top-3.5 right-3 h-3.5 w-3.5 text-gray-400" />

          {showChapterSuggestions && (
            <div className="absolute top-full right-0 left-0 z-50 mt-1 max-h-60 overflow-y-auto rounded-lg border border-gray-200 bg-white py-1 shadow-lg dark:border-gray-700 dark:bg-gray-800">
              {chapterSuggestionsContent}
            </div>
          )}
        </div>

        <SortBy
          id="pulse-time-range-select"
          aria-label="Time range"
          sortOptions={TIME_RANGES.map((tr) => ({ key: tr.value, label: tr.label }))}
          selectedSortOption={timeRange}
          selectedOrder="desc"
          onSortChange={(value) => {
            setTimeRange(value)
            setPage(1)
          }}
          hideOrderButton
          containerClassName="h-[42px] bg-gray-50 dark:bg-gray-800 border-gray-300 dark:border-gray-700"
          triggerClassName="w-full"
        />

        <SortBy
          id="pulse-sort-order-select"
          sortOptions={sortOptionsPulse}
          selectedSortOption={order}
          selectedOrder={order}
          onSortChange={(newOrder) => {
            setOrder(newOrder)
            setPage(1)
          }}
          onOrderChange={(newOrder) => {
            setOrder(newOrder)
            setPage(1)
          }}
          containerClassName="h-[42px] bg-gray-50 dark:bg-gray-800 border-gray-300 dark:border-gray-700"
          triggerClassName="w-full"
          buttonClassName="h-[42px] bg-gray-50 dark:bg-gray-800 border-gray-300 dark:border-gray-700"
        />
      </div>

      {hasActiveFilters && (
        <div className="mt-2 flex flex-wrap items-center gap-2 border-t border-gray-200 pt-4 text-xs dark:border-gray-700">
          <span className="font-medium text-gray-500 dark:text-gray-400">Active filters:</span>

          {searchQuery && (
            <span className="inline-flex items-center gap-1.5 rounded-md border border-gray-300 bg-gray-100 px-2.5 py-1 text-gray-700 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200">
              Search: {searchQuery}
              <FilterDismissButton
                label="Clear search filter"
                onPress={() => {
                  setSearchQuery('')
                  setPage(1)
                }}
              />
            </span>
          )}

          {activityType && (
            <span className="inline-flex items-center gap-1.5 rounded-md border border-gray-300 bg-gray-100 px-2.5 py-1 text-gray-700 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200">
              Type: {ACTIVITY_TYPES.find((t) => t.value === activityType)?.label || activityType}
              <FilterDismissButton
                label="Clear activity type filter"
                onPress={() => {
                  setActivityType('')
                  setPage(1)
                }}
              />
            </span>
          )}

          {projectKey && (
            <span className="inline-flex items-center gap-1.5 rounded-md border border-gray-300 bg-gray-100 px-2.5 py-1 text-gray-700 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200">
              Project: {projectKey}
              <FilterDismissButton
                label="Clear project filter"
                onPress={() => {
                  setProjectKey('')
                  setProjectSearchInput('')
                  setPage(1)
                }}
              />
            </span>
          )}

          {chapterKey && (
            <span className="inline-flex items-center gap-1.5 rounded-md border border-gray-300 bg-gray-100 px-2.5 py-1 text-gray-700 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200">
              Chapter: {chapterKey}
              <FilterDismissButton
                label="Clear chapter filter"
                onPress={() => {
                  setChapterKey('')
                  setChapterSearchInput('')
                  setPage(1)
                }}
              />
            </span>
          )}

          {timeRange && (
            <span className="inline-flex items-center gap-1.5 rounded-md border border-gray-300 bg-gray-100 px-2.5 py-1 text-gray-700 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200">
              Time: {TIME_RANGES.find((tr) => tr.value === timeRange)?.label || timeRange}
              <FilterDismissButton
                label="Clear time range filter"
                onPress={() => {
                  setTimeRange('')
                  setPage(1)
                }}
              />
            </span>
          )}

          <Button
            size="sm"
            variant="light"
            onPress={clearAllFilters}
            className="ml-2 h-auto min-w-0 bg-transparent p-0 font-semibold text-blue-600 hover:underline dark:text-blue-400"
          >
            Clear all
          </Button>
        </div>
      )}
    </div>
  )
}
