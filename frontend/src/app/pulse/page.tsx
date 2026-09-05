'use client'

import { useApolloClient, useQuery } from '@apollo/client/react'
import { Skeleton } from '@heroui/skeleton'
import { debounce } from 'lodash'
import { useRouter, useSearchParams } from 'next/navigation'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { FaCodeBranch, FaWaveSquare } from 'react-icons/fa6'
import { SearchChapterNamesDocument } from 'types/__generated__/chapterQueries.generated'
import { SearchProjectNamesDocument } from 'types/__generated__/projectQueries.generated'
import {
  GetActivityEventsDocument,
  GetActivityEventStatsDocument,
} from 'types/__generated__/pulseQueries.generated'
import LoadingSpinner from 'components/LoadingSpinner'
import Pagination from 'components/Pagination'
import PulseFilters from 'components/pulse/PulseFilters'
import PulseMetricsCards from 'components/pulse/PulseMetricsCards'
import PulseTimelineItem from 'components/pulse/PulseTimelineItem'

const ITEMS_PER_PAGE = 20

const formatTimelineDate = (dateStr: string) => {
  try {
    const eventDate = new Date(dateStr)
    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)

    const isToday = eventDate.toDateString() === today.toDateString()
    const isYesterday = eventDate.toDateString() === yesterday.toDateString()

    const formattedDate = eventDate
      .toLocaleDateString('en-US', {
        month: 'long',
        day: 'numeric',
        year: 'numeric',
      })
      .toUpperCase()

    if (isToday) return `TODAY • ${formattedDate}`
    if (isYesterday) return `YESTERDAY • ${formattedDate}`
    return formattedDate
  } catch {
    return 'ACTIVITY STREAM'
  }
}

export default function PulsePage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const client = useApolloClient()

  const [activityType, setActivityType] = useState<string>(searchParams.get('activityType') || '')
  const [projectKey, setProjectKey] = useState<string>(searchParams.get('project') || '')
  const [projectSearchInput, setProjectSearchInput] = useState<string>(
    searchParams.get('project') || ''
  )
  const [projectSuggestions, setProjectSuggestions] = useState<Array<{ id: string; name: string }>>(
    []
  )
  const [showProjectSuggestions, setShowProjectSuggestions] = useState<boolean>(false)
  const [isSearchingProjects, setIsSearchingProjects] = useState<boolean>(false)

  const [chapterKey, setChapterKey] = useState<string>(searchParams.get('chapter') || '')
  const [chapterSearchInput, setChapterSearchInput] = useState<string>(
    searchParams.get('chapter') || ''
  )
  const [chapterSuggestions, setChapterSuggestions] = useState<Array<{ id: string; name: string }>>(
    []
  )
  const [showChapterSuggestions, setShowChapterSuggestions] = useState<boolean>(false)
  const [isSearchingChapters, setIsSearchingChapters] = useState<boolean>(false)

  const [timeRange, setTimeRange] = useState<string>(searchParams.get('timeRange') || '')
  const [order, setOrder] = useState<string>(searchParams.get('order') || 'desc')
  const [searchQuery, setSearchQuery] = useState<string>(searchParams.get('search') || '')
  const [page, setPage] = useState<number>(
    Math.max(1, Number.parseInt(searchParams.get('page') || '1') || 1)
  )

  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState(searchQuery)
  const debouncedSetSearch = useMemo(
    () => debounce((v: string) => setDebouncedSearchQuery(v), 300),
    []
  )
  useEffect(() => {
    debouncedSetSearch(searchQuery)
  }, [searchQuery, debouncedSetSearch])
  useEffect(() => {
    return () => debouncedSetSearch.cancel()
  }, [debouncedSetSearch])

  const projectFetchGen = useRef(0)
  const chapterFetchGen = useRef(0)

  useEffect(() => {
    setActivityType(searchParams.get('activityType') || '')

    const project = searchParams.get('project') || ''
    setProjectKey(project)
    setProjectSearchInput(project)
    setProjectSuggestions([])
    setShowProjectSuggestions(false)
    setIsSearchingProjects(false)

    const chapter = searchParams.get('chapter') || ''
    setChapterKey(chapter)
    setChapterSearchInput(chapter)
    setChapterSuggestions([])
    setShowChapterSuggestions(false)
    setIsSearchingChapters(false)

    setTimeRange(searchParams.get('timeRange') || '')
    setOrder(searchParams.get('order') || 'desc')
    const search = searchParams.get('search') || ''
    debouncedSetSearch.cancel()
    setSearchQuery(search)
    setDebouncedSearchQuery(search)
    setPage(Math.max(1, Number.parseInt(searchParams.get('page') || '1') || 1))
  }, [searchParams, debouncedSetSearch])

  const fetchProjectSuggestions = useCallback(
    async (queryText: string) => {
      const cleanQuery = queryText.trim()
      const gen = ++projectFetchGen.current
      setIsSearchingProjects(true)
      try {
        const { data } = await client.query({
          query: SearchProjectNamesDocument,
          variables: { query: cleanQuery },
        })
        if (gen === projectFetchGen.current) {
          setProjectSuggestions((data?.searchProjects || []) as Array<{ id: string; name: string }>)
        }
      } catch {
        if (gen === projectFetchGen.current) {
          setProjectSuggestions([])
        }
      } finally {
        if (gen === projectFetchGen.current) {
          setIsSearchingProjects(false)
        }
      }
    },
    [client]
  )

  useEffect(() => {
    if (showProjectSuggestions) {
      fetchProjectSuggestions(projectSearchInput)
    }
  }, [projectSearchInput, showProjectSuggestions, fetchProjectSuggestions])

  const fetchChapterSuggestions = useCallback(
    async (queryText: string) => {
      const cleanQuery = queryText.trim()
      const gen = ++chapterFetchGen.current
      setIsSearchingChapters(true)
      try {
        const { data } = await client.query({
          query: SearchChapterNamesDocument,
          variables: { query: cleanQuery },
        })
        if (gen === chapterFetchGen.current) {
          setChapterSuggestions((data?.searchChapters || []) as Array<{ id: string; name: string }>)
        }
      } catch {
        if (gen === chapterFetchGen.current) {
          setChapterSuggestions([])
        }
      } finally {
        if (gen === chapterFetchGen.current) {
          setIsSearchingChapters(false)
        }
      }
    },
    [client]
  )

  useEffect(() => {
    if (showChapterSuggestions) {
      fetchChapterSuggestions(chapterSearchInput)
    }
  }, [chapterSearchInput, showChapterSuggestions, fetchChapterSuggestions])

  useEffect(() => {
    const params = new URLSearchParams()
    if (activityType) params.set('activityType', activityType)
    if (projectKey.trim()) params.set('project', projectKey.trim())
    if (chapterKey.trim()) params.set('chapter', chapterKey.trim())
    if (timeRange) params.set('timeRange', timeRange)
    if (order !== 'desc') params.set('order', order)
    if (debouncedSearchQuery.trim()) params.set('search', debouncedSearchQuery.trim())
    if (page > 1) params.set('page', page.toString())
    router.replace(`?${params.toString()}`)
  }, [activityType, projectKey, chapterKey, timeRange, order, debouncedSearchQuery, page, router])

  const {
    data: statsData,
    loading: statsLoading,
    error: statsError,
  } = useQuery(GetActivityEventStatsDocument)
  const stats = statsData?.activityEventStats

  const { data, loading, error } = useQuery(GetActivityEventsDocument, {
    variables: {
      activityType: activityType || undefined,
      githubUser: debouncedSearchQuery.trim() || undefined,
      projectKey: projectKey.trim() || undefined,
      chapterKey: chapterKey.trim() || undefined,
      timeRange: timeRange || undefined,
      order,
      page,
      limit: ITEMS_PER_PAGE,
    },
    fetchPolicy: 'network-only',
  })

  const events = data?.activityEvents?.events || []
  const currentPage = data?.activityEvents?.currentPage ?? page
  const totalPages = data?.activityEvents?.totalPages || 1
  const totalCount = data?.activityEvents?.totalCount ?? 0

  const groupedEvents: { [key: string]: typeof events } = {}
  events.forEach((event) => {
    const groupKey = formatTimelineDate(event.occurredAt)
    if (!groupedEvents[groupKey]) groupedEvents[groupKey] = []
    groupedEvents[groupKey].push(event)
  })

  const clearAllFilters = () => {
    setActivityType('')
    setProjectKey('')
    setProjectSearchInput('')
    setChapterKey('')
    setChapterSearchInput('')
    setTimeRange('')
    setSearchQuery('')
    setPage(1)
  }

  const handleSelectProject = (project: { id: string; name: string }) => {
    const filterValue = project.name || ''
    setProjectSearchInput(filterValue)
    setProjectKey(filterValue)
    setShowProjectSuggestions(false)
    setPage(1)
  }

  const handleSelectChapter = (chapter: { id: string; name: string }) => {
    const filterValue = chapter.name || ''
    setChapterSearchInput(filterValue)
    setChapterKey(filterValue)
    setShowChapterSuggestions(false)
    setPage(1)
  }

  return (
    <div className="min-h-screen p-4 font-sans text-gray-600 antialiased sm:p-6 lg:p-8 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-7xl space-y-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-3">
              <h1 className="flex items-center gap-2.5 text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
                OWASP Pulse
                <FaWaveSquare className="h-6 w-6 text-blue-500" />
              </h1>
            </div>
            <p className="mb-2 text-sm text-gray-600 dark:text-gray-400">
              A unified view of activity across the OWASP community.
            </p>
          </div>
        </div>

        <PulseMetricsCards stats={stats} loading={statsLoading} error={!!statsError} />

        <PulseFilters
          activityType={activityType}
          chapterKey={chapterKey}
          chapterSearchInput={chapterSearchInput}
          chapterSuggestions={chapterSuggestions}
          clearAllFilters={clearAllFilters}
          handleSelectChapter={handleSelectChapter}
          handleSelectProject={handleSelectProject}
          isSearchingChapters={isSearchingChapters}
          isSearchingProjects={isSearchingProjects}
          order={order}
          projectKey={projectKey}
          projectSearchInput={projectSearchInput}
          projectSuggestions={projectSuggestions}
          searchQuery={searchQuery}
          setActivityType={setActivityType}
          setChapterKey={setChapterKey}
          setChapterSearchInput={setChapterSearchInput}
          setOrder={setOrder}
          setPage={setPage}
          setProjectKey={setProjectKey}
          setProjectSearchInput={setProjectSearchInput}
          setSearchQuery={setSearchQuery}
          setShowChapterSuggestions={setShowChapterSuggestions}
          setShowProjectSuggestions={setShowProjectSuggestions}
          setTimeRange={setTimeRange}
          showChapterSuggestions={showChapterSuggestions}
          showProjectSuggestions={showProjectSuggestions}
          timeRange={timeRange}
        />

        <div className="flex items-center justify-between px-1 pt-4 pb-2 text-xs text-gray-500 dark:text-gray-400">
          {!loading ? (
            <>
              <div className="font-medium text-gray-700 dark:text-gray-300">
                <strong className="text-gray-900 dark:text-white">
                  {totalCount.toLocaleString()}
                </strong>{' '}
                activities found
              </div>
              <div className="flex items-center gap-3">
                <span>Showing {events.length} items</span>
              </div>
            </>
          ) : (
            <>
              <Skeleton className="h-4 w-28 rounded-md" />
              <Skeleton className="h-4 w-20 rounded-md" />
            </>
          )}
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-16">
            <LoadingSpinner />
            <p className="mt-4 text-sm text-gray-500 dark:text-gray-400">
              Loading OWASP activity stream...
            </p>
          </div>
        ) : error ? (
          <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-red-700 dark:border-red-900/50 dark:bg-red-950/30 dark:text-red-300">
            <h3 className="text-lg font-semibold">GraphQL Query Error</h3>
            <p className="mt-1 text-sm">{error.message}</p>
          </div>
        ) : events.length === 0 ? (
          <div className="rounded-xl border border-dashed border-gray-300 p-12 text-center text-gray-500 dark:border-gray-700 dark:text-gray-400">
            <FaCodeBranch className="mx-auto h-8 w-8 text-gray-400" />
            <h3 className="mt-3 text-base font-semibold text-gray-800 dark:text-gray-200">
              No activities found
            </h3>
            <p className="mt-1 text-sm">Try clearing or adjusting your search filters.</p>
          </div>
        ) : (
          <div className="space-y-8 pt-2">
            {Object.entries(groupedEvents).map(([dateHeader, dayEvents]) => (
              <div key={dateHeader} className="space-y-4">
                <div className="mb-1.5 pt-2 text-xs font-bold tracking-wider text-gray-500 uppercase dark:text-gray-400">
                  {dateHeader}
                </div>

                <div className="relative ml-4 space-y-4 border-l-2 border-gray-300 pl-6 dark:border-gray-700">
                  {dayEvents.map((event) => (
                    <PulseTimelineItem key={event.id} event={event} />
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={(newPage) => setPage(newPage)}
          isLoaded={!loading}
        />
      </div>
    </div>
  )
}
