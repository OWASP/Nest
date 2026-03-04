'use client'

import { useQuery } from '@apollo/client/react'
import { useSearchParams, useRouter } from 'next/navigation'
import { FC, useState, useEffect } from 'react'
import { handleAppError } from 'app/global-error'
import { Ordering, ProjectLevel } from 'types/__generated__/graphql'
import { GetProjectHealthMetricsDocument } from 'types/__generated__/projectsHealthDashboardQueries.generated'
import { HealthMetricsProps } from 'types/healthMetrics'
import LoadingSpinner from 'components/LoadingSpinner'
import MetricsCard from 'components/MetricsCard'
import UnifiedSearchBar from 'components/UnifiedSearchBar'

const PAGINATION_LIMIT = 10

const FILTER_OPTIONS = [
  { label: 'All Filters', key: '' },
  // Health Filters
  { label: 'Healthy', key: 'healthy' },
  { label: 'Need Attention', key: 'needsAttention' },
  { label: 'Unhealthy', key: 'unhealthy' },
  // Level Filters
  { label: 'Incubator', key: 'incubator' },
  { label: 'Lab', key: 'lab' },
  { label: 'Production', key: 'production' },
  { label: 'Flagship', key: 'flagship' },
]

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

const SORT_FIELDS = [
  { label: 'Score', key: 'scoreDesc' },
  { label: 'Stars', key: 'starsDesc' },
  { label: 'Forks', key: 'forksDesc' },
  { label: 'Contributors', key: 'contributorsDesc' },
  { label: 'Last Checked', key: 'createdAtDesc' },
]

const healthFiltersMapping = {
  healthy: {
    score: {
      gte: 75,
    },
  },
  needsAttention: {
    score: {
      gte: 50,
      lt: 75,
    },
  },
  unhealthy: {
    score: {
      lt: 50,
    },
  },
}

const levelFiltersMapping = {
  incubator: {
    level: ProjectLevel.Incubator,
  },
  lab: {
    level: ProjectLevel.Lab,
  },
  production: {
    level: ProjectLevel.Production,
  },
  flagship: {
    level: ProjectLevel.Flagship,
  },
}

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

const MetricsPage: FC = () => {
  const searchParams = useSearchParams()
  const router = useRouter()

  const orderingParam = searchParams.get('order')
  const { field, direction, urlKey } = parseOrderParam(orderingParam)
  const currentOrdering = buildGraphQLOrdering(field, direction)

  const healthFilter = searchParams.get('health')
  const levelFilter = searchParams.get('level')

  let currentFilters = {}
  const currentCategory = levelFilter || healthFilter || ''
  const searchQueryParam = searchParams.get('search') || ''

  if (currentCategory && currentCategory in healthFiltersMapping) {
    currentFilters = healthFiltersMapping[currentCategory as keyof typeof healthFiltersMapping]
  } else if (currentCategory && currentCategory in levelFiltersMapping) {
    currentFilters = levelFiltersMapping[currentCategory as keyof typeof levelFiltersMapping]
  }

  const [metrics, setMetrics] = useState<HealthMetricsProps[]>([])
  const [metricsLength, setMetricsLength] = useState<number>(0)
  const [pagination, setPagination] = useState({ offset: 0, limit: PAGINATION_LIMIT })
  const [filters, setFilters] = useState(currentFilters)
  const [ordering, setOrdering] = useState(currentOrdering)
  const [searchQuery, setSearchQuery] = useState(searchQueryParam)

  const handleSearchChange = (query: string) => {
    setSearchQuery(query)
    setPagination({ offset: 0, limit: PAGINATION_LIMIT })
    const newParams = new URLSearchParams(searchParams.toString())
    if (query) {
      newParams.set('search', query)
    } else {
      newParams.delete('search')
    }
    router.replace(`/projects/dashboard/metrics?${newParams.toString()}`)
  }

  const {
    data,
    error: graphQLRequestError,
    loading,
    fetchMore,
  } = useQuery(GetProjectHealthMetricsDocument, {
    variables: {
      query: searchQuery || '',
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

  const getCurrentPage = () => {
    return Math.floor(pagination.offset / PAGINATION_LIMIT) + 1
  }

  const handleSortChange = (sortKey: string) => {
    setPagination({ offset: 0, limit: PAGINATION_LIMIT })
    const newParams = new URLSearchParams(searchParams.toString())
    newParams.set('order', sortKey)
    const { field: newField, direction: newDirection } = parseOrderParam(sortKey)
    setOrdering(buildGraphQLOrdering(newField, newDirection))
    router.replace(`/projects/dashboard/metrics?${newParams.toString()}`)
  }

  const handleOrderChange = (newOrder: string) => {
    setPagination({ offset: 0, limit: PAGINATION_LIMIT })
    const newParams = new URLSearchParams(searchParams.toString())
    const currentOrderKey = searchParams.get('order') || 'scoreDesc'
    const { field } = parseOrderParam(currentOrderKey)

    const newOrderKey =
      newOrder === 'asc'
        ? Object.entries(ORDERING_MAP).find(
            ([_, v]) => v.field === field && v.direction === Ordering.Asc
          )?.[0]
        : Object.entries(ORDERING_MAP).find(
            ([_, v]) => v.field === field && v.direction === Ordering.Desc
          )?.[0]

    if (newOrderKey) {
      newParams.set('order', newOrderKey)
      const { field: f, direction: d } = ORDERING_MAP[newOrderKey as OrderingKey]
      setOrdering(buildGraphQLOrdering(f, d))
      router.replace(`/projects/dashboard/metrics?${newParams.toString()}`)
    }
  }

  const handleCategoryChange = (category: string) => {
    setPagination({ offset: 0, limit: PAGINATION_LIMIT })
    const newParams = new URLSearchParams(searchParams.toString())
    let newFilters = {}

    // Single-select behavior: clear both scopes, then apply one.
    newParams.delete('health')
    newParams.delete('level')

    if (category in healthFiltersMapping) {
      newParams.set('health', category)
      newFilters = healthFiltersMapping[category as keyof typeof healthFiltersMapping]
    } else if (category in levelFiltersMapping) {
      newParams.set('level', category)
      newFilters = levelFiltersMapping[category as keyof typeof levelFiltersMapping]
    }

    setFilters(newFilters)
    router.replace(`/projects/dashboard/metrics?${newParams.toString()}`)
  }

  const getSortFieldKey = () => {
    if (!urlKey) return 'scoreDesc'
    const field = urlKey.replace(/(?:Asc|Desc)$/, '')
    return `${field}Desc`
  }

  return (
    <div className="w-full">
      <div className="mb-6">
        <h1 className="mb-4 text-2xl font-bold">Project Health Metrics</h1>

        <UnifiedSearchBar
          searchQuery={searchQuery}
          sortBy={getSortFieldKey()}
          order={urlKey?.endsWith('Desc') ? 'desc' : 'asc'}
          category={currentCategory}
          isLoaded={!loading}
          sortOptions={SORT_FIELDS}
          categoryOptions={FILTER_OPTIONS}
          searchPlaceholder="Search metrics..."
          onSearch={handleSearchChange}
          onSortChange={handleSortChange}
          onOrderChange={handleOrderChange}
          onCategoryChange={handleCategoryChange}
          currentPage={getCurrentPage()}
          totalPages={Math.ceil(metricsLength / PAGINATION_LIMIT)}
          onPageChange={async (page) => {
            const newOffset = (page - 1) * PAGINATION_LIMIT
            const newPagination = { offset: newOffset, limit: PAGINATION_LIMIT }
            setPagination(newPagination)
            await fetchMore({
              variables: {
                query: searchQuery || '',
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
          indexName="health-metrics"
          empty="No metrics found. Try adjusting your filters."
        >
          {loading ? (
            <LoadingSpinner />
          ) : (
            <div className="grid grid-cols-1 gap-2">
              {metrics.length === 0 ? (
                <div className="py-8 text-center text-gray-500">
                  {searchQuery
                    ? 'No metrics found matching your search.'
                    : 'No metrics found. Try adjusting your filters.'}
                </div>
              ) : (
                metrics.map((metric) => <MetricsCard key={metric.id} metric={metric} />)
              )}
            </div>
          )}
        </UnifiedSearchBar>
      </div>
    </div>
  )
}

export default MetricsPage
