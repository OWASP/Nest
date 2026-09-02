'use client'

import { Button } from '@heroui/button'
import {
  FaArrowUpWideShort,
  FaCalendarDays,
  FaChevronDown,
  FaFolder,
  FaGlobe,
  FaMagnifyingGlass,
  FaXmark,
} from 'react-icons/fa6'
import type { PulseFiltersProps } from 'types/pulse'

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

const FilterDismissButton = ({ onPress }: { onPress: () => void }) => (
  <Button
    size="sm"
    isIconOnly
    variant="light"
    onPress={onPress}
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
}: PulseFiltersProps) {
  return (
    <div className="space-y-4 rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-800">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <FaMagnifyingGlass className="absolute top-3.5 left-3.5 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search activity..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value)
              setPage(1)
            }}
            className="w-full rounded-lg border border-gray-300 bg-gray-50 py-2.5 pr-4 pl-10 text-sm text-gray-900 placeholder:text-gray-400 focus:border-blue-500 focus:outline-none dark:border-gray-700 dark:bg-gray-800 dark:text-white dark:placeholder:text-gray-400"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <div className="relative">
          <select
            value={activityType}
            onChange={(e) => {
              setActivityType(e.target.value)
              setPage(1)
            }}
            className="w-full appearance-none rounded-lg border border-gray-300 bg-gray-50 px-3.5 py-2.5 text-sm font-medium text-gray-800 focus:border-blue-500 focus:outline-none dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200"
          >
            {ACTIVITY_TYPES.map((t) => (
              <option
                key={t.value}
                value={t.value}
                className="bg-white text-gray-900 dark:bg-gray-800 dark:text-white"
              >
                {t.label}
              </option>
            ))}
          </select>
          <FaChevronDown className="pointer-events-none absolute top-3.5 right-3 h-3 w-3 text-gray-400" />
        </div>

        <div className="relative">
          <input
            type="text"
            placeholder="All Projects"
            value={projectSearchInput}
            onFocus={() => setShowProjectSuggestions(true)}
            onBlur={() => setTimeout(() => setShowProjectSuggestions(false), 200)}
            onChange={(e) => {
              setProjectSearchInput(e.target.value)
              setShowProjectSuggestions(true)
              if (!e.target.value.trim()) {
                setProjectKey('')
              }
            }}
            className="w-full rounded-lg border border-gray-300 bg-gray-50 px-3.5 py-2.5 pr-8 text-sm font-medium text-gray-800 placeholder:text-gray-400 focus:border-blue-500 focus:outline-none dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200 dark:placeholder:text-gray-400"
          />
          <FaFolder className="pointer-events-none absolute top-3.5 right-3 h-3.5 w-3.5 text-gray-400" />

          {showProjectSuggestions && (
            <div className="absolute top-full right-0 left-0 z-50 mt-1 max-h-60 overflow-y-auto rounded-lg border border-gray-200 bg-white py-1 shadow-lg dark:border-gray-700 dark:bg-gray-800">
              {isSearchingProjects ? (
                <div className="px-3.5 py-2 text-xs text-gray-400">Searching projects...</div>
              ) : projectSuggestions.length === 0 ? (
                <div className="px-3.5 py-2 text-xs text-gray-400">
                  No project suggestions found
                </div>
              ) : (
                projectSuggestions.map((proj) => (
                  <button
                    key={proj.id || proj.name}
                    type="button"
                    onMouseDown={(e) => {
                      e.preventDefault()
                      handleSelectProject(proj)
                    }}
                    className="flex w-full items-center justify-between px-3.5 py-2 text-left text-xs font-medium text-gray-700 hover:bg-blue-50 dark:text-gray-200 dark:hover:bg-gray-700"
                  >
                    <span className="font-semibold text-gray-900 dark:text-white">{proj.name}</span>
                  </button>
                ))
              )}
            </div>
          )}
        </div>

        <div className="relative">
          <input
            type="text"
            placeholder="All Chapters"
            value={chapterSearchInput}
            onFocus={() => setShowChapterSuggestions(true)}
            onBlur={() => setTimeout(() => setShowChapterSuggestions(false), 200)}
            onChange={(e) => {
              setChapterSearchInput(e.target.value)
              setShowChapterSuggestions(true)
              if (!e.target.value.trim()) {
                setChapterKey('')
              }
            }}
            className="w-full rounded-lg border border-gray-300 bg-gray-50 px-3.5 py-2.5 pr-8 text-sm font-medium text-gray-800 placeholder:text-gray-400 focus:border-blue-500 focus:outline-none dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200 dark:placeholder:text-gray-400"
          />
          <FaGlobe className="pointer-events-none absolute top-3.5 right-3 h-3.5 w-3.5 text-gray-400" />

          {showChapterSuggestions && (
            <div className="absolute top-full right-0 left-0 z-50 mt-1 max-h-60 overflow-y-auto rounded-lg border border-gray-200 bg-white py-1 shadow-lg dark:border-gray-700 dark:bg-gray-800">
              {isSearchingChapters ? (
                <div className="px-3.5 py-2 text-xs text-gray-400">Searching chapters...</div>
              ) : chapterSuggestions.length === 0 ? (
                <div className="px-3.5 py-2 text-xs text-gray-400">
                  No chapter suggestions found
                </div>
              ) : (
                chapterSuggestions.map((chap) => (
                  <button
                    key={chap.id || chap.name}
                    type="button"
                    onMouseDown={(e) => {
                      e.preventDefault()
                      handleSelectChapter(chap)
                    }}
                    className="flex w-full items-center justify-between px-3.5 py-2 text-left text-xs font-medium text-gray-700 hover:bg-blue-50 dark:text-gray-200 dark:hover:bg-gray-700"
                  >
                    <span className="font-semibold text-gray-900 dark:text-white">{chap.name}</span>
                  </button>
                ))
              )}
            </div>
          )}
        </div>

        <div className="relative">
          <select
            value={timeRange}
            onChange={(e) => {
              setTimeRange(e.target.value)
              setPage(1)
            }}
            className="w-full appearance-none rounded-lg border border-gray-300 bg-gray-50 px-3.5 py-2.5 text-sm font-medium text-gray-800 focus:border-blue-500 focus:outline-none dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200"
          >
            {TIME_RANGES.map((tr) => (
              <option
                key={tr.value}
                value={tr.value}
                className="bg-white text-gray-900 dark:bg-gray-800 dark:text-white"
              >
                {tr.label}
              </option>
            ))}
          </select>
          <FaCalendarDays className="pointer-events-none absolute top-3.5 right-3 h-3.5 w-3.5 text-gray-400" />
        </div>

        <div className="relative">
          <select
            value={order}
            onChange={(e) => {
              setOrder(e.target.value)
              setPage(1)
            }}
            className="w-full appearance-none rounded-lg border border-gray-300 bg-gray-50 px-3.5 py-2.5 text-sm font-medium text-gray-800 focus:border-blue-500 focus:outline-none dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200"
          >
            <option value="desc" className="bg-white dark:bg-gray-800">
              Sort: Newest First
            </option>
            <option value="asc" className="bg-white dark:bg-gray-800">
              Sort: Oldest First
            </option>
          </select>
          <FaArrowUpWideShort className="pointer-events-none absolute top-3.5 right-3 h-3.5 w-3.5 text-gray-400" />
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
        <span className="font-medium text-gray-500 dark:text-gray-400">Active filters:</span>
        <span className="inline-flex items-center gap-1.5 rounded-md border border-gray-300 bg-gray-100 px-2.5 py-1 text-gray-700 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200">
          {activityType
            ? ACTIVITY_TYPES.find((t) => t.value === activityType)?.label
            : 'All Activity Types'}
          <FilterDismissButton onPress={() => setActivityType('')} />
        </span>

        {projectKey && (
          <span className="inline-flex items-center gap-1.5 rounded-md border border-gray-300 bg-gray-100 px-2.5 py-1 text-gray-700 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200">
            Project: {projectKey}
            <FilterDismissButton
              onPress={() => {
                setProjectKey('')
                setProjectSearchInput('')
              }}
            />
          </span>
        )}

        {chapterKey && (
          <span className="inline-flex items-center gap-1.5 rounded-md border border-gray-300 bg-gray-100 px-2.5 py-1 text-gray-700 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200">
            Chapter: {chapterKey}
            <FilterDismissButton
              onPress={() => {
                setChapterKey('')
                setChapterSearchInput('')
              }}
            />
          </span>
        )}

        <span className="inline-flex items-center gap-1.5 rounded-md border border-gray-300 bg-gray-100 px-2.5 py-1 text-gray-700 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200">
          {TIME_RANGES.find((tr) => tr.value === timeRange)?.label || 'All Time'}
          <FilterDismissButton onPress={() => setTimeRange('')} />
        </span>

        <Button
          size="sm"
          variant="light"
          onPress={clearAllFilters}
          className="ml-2 h-auto min-w-0 bg-transparent p-0 font-semibold text-blue-600 hover:underline dark:text-blue-400"
        >
          Clear all
        </Button>
      </div>
    </div>
  )
}
