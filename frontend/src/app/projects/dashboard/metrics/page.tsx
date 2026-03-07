'use client'

import { useQuery } from '@apollo/client/react'
import { Pagination } from '@heroui/react'
import { useSearchParams, useRouter } from 'next/navigation'
import { FC, useState, useEffect } from 'react'
import { handleAppError } from 'app/global-error'
import { Ordering, ProjectLevel } from 'types/__generated__/graphql'
import { GetProjectHealthMetricsDocument } from 'types/__generated__/projectsHealthDashboardQueries.generated'
import { HealthMetricsProps } from 'types/healthMetrics'
import LoadingSpinner from 'components/LoadingSpinner'
import MetricsCard from 'components/MetricsCard'
import SearchWithFilters from 'components/SearchWithFilters'

const PAGINATION_LIMIT = 10

const ORDERING_MAP = {
  scoreDesc: { field: 'score', direction: Ordering.Desc },
  scoreAsc: { field: 'score', direction: Ordering.Asc },
  starsDesc: { field: 'starsCount', direction: Ordering.Desc },
  starsAsc: { field: 'starsCount', direction: Ordering.Asc },
  forksDesc: { field: 'forksCount', direction: Ordering.Desc },
  forksAsc: { field: 'forksCount', direction: Ordering.Asc },
  contributorsDesc: { field: 'contributorsCount', direction: Ordering.Desc },
  contributorsAsc: { field: 'contributorsCount', direction: Ordering.Asc },
  createdAtDesc: { field: 'createdAt', direction: Ordering.Desc },
  createdAtAsc: { field: 'createdAt', direction: Ordering.Asc },
} as const

type OrderingKey = keyof typeof ORDERING_MAP

const SORT_OPTIONS = [
  { label: 'Score', key: 'score' },
  { label: 'Stars', key: 'stars' },
  { label: 'Forks', key: 'forks' },
  { label: 'Contributors', key: 'contributors' },
  { label: 'Last Checked', key: 'createdAt' },
]

const FILTER_CATEGORY_OPTIONS = [
  { label: 'All Projects', key: '' },
  { label: 'Incubator', key: 'level:incubator' },
  { label: 'Lab', key: 'level:lab' },
  { label: 'Production', key: 'level:production' },
  { label: 'Flagship', key: 'level:flagship' },
  { label: 'Healthy', key: 'health:healthy' },
  { label: 'Needs Attention', key: 'health:needsAttention' },
  { label: 'Unhealthy', key: 'health:unhealthy' },
]

const parseOrderParam = (orderParam: string | null) => {
  if (!orderParam || !Object.hasOwn(ORDERING_MAP, orderParam)) {
    return { field: 'score', direction: Ordering.Desc, urlKey: 'scoreDesc' }
  }

  const { field, direction } = ORDERING_MAP[orderParam as OrderingKey]

  return { field, direction, urlKey: orderParam }
}

const buildGraphQLOrdering = (field: string, direction: Ordering) => {
  return {
    [field]: direction,
  }
}

const buildOrderingWithTieBreaker = (primaryOrdering: Record<string, Ordering>) => [
  primaryOrdering,
  {
    // eslint-disable-next-line @typescript-eslint/naming-convention
    project_Name: Ordering.Asc,
  },
]

const sortFieldToOrderingKey = (sortField: string, order: string): string => {
  const dirSuffix = order === 'asc' ? 'Asc' : 'Desc'

  const fieldMap: Record<string, string> = {
    score: 'score',
    stars: 'stars',
    forks: 'forks',
    contributors: 'contributors',
    createdAt: 'createdAt',
  }

  const mappedField = fieldMap[sortField] || 'score'
  return `${mappedField}${dirSuffix}`
}

const MetricsPage: FC = () => {
  const searchParams = useSearchParams()
  const router = useRouter()

  const healthFiltersMapping: Record<string, Record<string, unknown>> = {
    healthy: {
      score: { gte: 75 },
    },
    needsAttention: {
      score: { gte: 50, lt: 75 },
    },
    unhealthy: {
      score: { lt: 50 },
    },
  }
  const levelFiltersMapping: Record<string, Record<string, unknown>> = {
    incubator: { level: ProjectLevel.Incubator },
    lab: { level: ProjectLevel.Lab },
    production: { level: ProjectLevel.Production },
    flagship: { level: ProjectLevel.Flagship },
  }

  const orderingParam = searchParams.get('order')
  const { field, direction } = parseOrderParam(orderingParam)
  const currentOrdering = buildGraphQLOrdering(field, direction)

  const healthFilter = searchParams.get('health') || ''
  const levelFilter = searchParams.get('level') || ''
  const searchQueryParam = searchParams.get('q') || ''
  const sortByParam = searchParams.get('sortBy') || 'score'
  const orderParam = searchParams.get('orderDir') || 'desc'

  let currentFilters: Record<string, unknown> = {}
  if (healthFilter && healthFiltersMapping[healthFilter]) {
    currentFilters = { ...currentFilters, ...healthFiltersMapping[healthFilter] }
  }
  if (levelFilter && levelFiltersMapping[levelFilter]) {
    currentFilters = { ...currentFilters, ...levelFiltersMapping[levelFilter] }
  }

  const [metrics, setMetrics] = useState<HealthMetricsProps[]>([])
  const [metricsLength, setMetricsLength] = useState<number>(0)
  const [pagination, setPagination] = useState({ offset: 0, limit: PAGINATION_LIMIT })
  const [filters, setFilters] = useState(currentFilters)
  const [ordering, setOrdering] = useState(currentOrdering)
  const [searchQuery, setSearchQuery] = useState(searchQueryParam)
  const [sortBy, setSortBy] = useState(sortByParam)
  const [order, setOrder] = useState(orderParam)
  const initialCategory = healthFilter
    ? `health:${healthFilter}`
    : levelFilter
      ? `level:${levelFilter}`
      : ''
  const [category, setCategory] = useState(initialCategory)

  const {
    data,
    error: graphQLRequestError,
    loading,
    fetchMore,
  } = useQuery(GetProjectHealthMetricsDocument, {
    variables: {
      query: searchQuery,
      filters,
      pagination: { offset: 0, limit: PAGINATION_LIMIT },
      ordering: buildOrderingWithTieBreaker(ordering),
    },
  })

  useEffect(() => {
    const { field: f, direction: d } = parseOrderParam(searchParams.get('order'))
    const nextOrdering = buildGraphQLOrdering(f, d)
    if (JSON.stringify(nextOrdering) !== JSON.stringify(ordering)) {
      setOrdering(nextOrdering)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams])

  useEffect(() => {
    if (data) {
      setMetrics(data.projectHealthMetrics as unknown as HealthMetricsProps[])
      setMetricsLength(data.projectHealthMetricsDistinctLength)
    }
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
    }
  }, [data, graphQLRequestError])

  const updateUrlParams = (params: Record<string, string | null>) => {
    const newParams = new URLSearchParams(searchParams.toString())
    for (const [key, value] of Object.entries(params)) {
      if (value === null || value === '') {
        newParams.delete(key)
      } else {
        newParams.set(key, value)
      }
    }
    router.replace(`/projects/dashboard/metrics?${newParams.toString()}`)
  }

  const getCurrentPage = () => {
    return Math.floor(pagination.offset / PAGINATION_LIMIT) + 1
  }

  const handleSearch = (query: string) => {
    setSearchQuery(query)
    setPagination({ offset: 0, limit: PAGINATION_LIMIT })
    updateUrlParams({ q: query || null })
  }

  const handleSortChange = (newSort: string) => {
    setSortBy(newSort)
    const orderingKey = sortFieldToOrderingKey(newSort === 'default' ? 'score' : newSort, order)
    const parsed = parseOrderParam(orderingKey)
    const newOrdering = buildGraphQLOrdering(parsed.field, parsed.direction)
    setOrdering(newOrdering)
    setPagination({ offset: 0, limit: PAGINATION_LIMIT })
    updateUrlParams({ sortBy: newSort, order: orderingKey })
  }

  const handleOrderChange = (newOrder: string) => {
    setOrder(newOrder)
    const orderingKey = sortFieldToOrderingKey(sortBy === 'default' ? 'score' : sortBy, newOrder)
    const parsed = parseOrderParam(orderingKey)
    const newOrdering = buildGraphQLOrdering(parsed.field, parsed.direction)
    setOrdering(newOrdering)
    setPagination({ offset: 0, limit: PAGINATION_LIMIT })
    updateUrlParams({ orderDir: newOrder, order: orderingKey })
  }

  const handleCategoryChange = (newCategory: string) => {
    setCategory(newCategory)
    let newFilters: Record<string, unknown> = {}
    const urlUpdates: Record<string, string | null> = { health: null, level: null }

    if (newCategory.startsWith('health:')) {
      const healthKey = newCategory.replace('health:', '')
      if (healthFiltersMapping[healthKey]) {
        newFilters = { ...healthFiltersMapping[healthKey] }
        urlUpdates.health = healthKey
      }
    } else if (newCategory.startsWith('level:')) {
      const levelKey = newCategory.replace('level:', '')
      if (levelFiltersMapping[levelKey]) {
        newFilters = { ...levelFiltersMapping[levelKey] }
        urlUpdates.level = levelKey
      }
    }

    setFilters(newFilters)
    setPagination({ offset: 0, limit: PAGINATION_LIMIT })
    updateUrlParams(urlUpdates)
  }

  return (
    <>
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="mb-2 text-2xl font-bold">Project Health Metrics</h1>
      </div>
      <div className="mb-4 flex w-full justify-center">
        <SearchWithFilters
          isLoaded={!loading}
          searchQuery={searchQuery}
          sortBy={sortBy}
          order={order}
          category={category}
          sortOptions={SORT_OPTIONS}
          categoryOptions={FILTER_CATEGORY_OPTIONS}
          searchPlaceholder="Search health metrics..."
          onSearch={handleSearch}
          onSortChange={handleSortChange}
          onOrderChange={handleOrderChange}
          onCategoryChange={handleCategoryChange}
        />
      </div>
      {loading ? (
        <LoadingSpinner />
      ) : (
        <>
          <div className="grid grid-cols-1 gap-2">
            {metrics.length === 0 ? (
              <div className="py-8 text-center text-gray-500">
                No metrics found. Try adjusting your filters.
              </div>
            ) : (
              metrics.map((metric) => <MetricsCard key={metric.id} metric={metric} />)
            )}
          </div>
          <div className="mt-4 flex items-center justify-center">
            <Pagination
              initialPage={getCurrentPage()}
              page={getCurrentPage()}
              total={Math.ceil(metricsLength / PAGINATION_LIMIT)}
              onChange={async (page) => {
                const newOffset = (page - 1) * PAGINATION_LIMIT
                const newPagination = { offset: newOffset, limit: PAGINATION_LIMIT }
                setPagination(newPagination)
                await fetchMore({
                  variables: {
                    query: searchQuery,
                    filters,
                    pagination: newPagination,
                    ordering: buildOrderingWithTieBreaker(ordering),
                  },
                  updateQuery: (prev, { fetchMoreResult }) => {
                    if (!fetchMoreResult) return prev
                    return {
                      ...prev,
                      projectHealthMetrics: fetchMoreResult.projectHealthMetrics,
                    }
                  },
                })
              }}
              showControls
              color="warning"
              className="mt-4"
            />
          </div>
        </>
      )}
    </>
  )
}

export default MetricsPage
