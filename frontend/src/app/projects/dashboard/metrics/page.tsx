'use client'
import { useQuery } from '@apollo/client/react'
import { Pagination } from '@heroui/react'
import { useSearchParams, useRouter } from 'next/navigation'
import { FC, useState, useEffect } from 'react'
import { FaFilter, FaArrowDownWideShort, FaArrowUpWideShort } from 'react-icons/fa6'
import { handleAppError } from 'app/global-error'
import { Ordering } from 'types/__generated__/graphql'
import { GetProjectHealthMetricsDocument } from 'types/__generated__/projectsHealthDashboardQueries.generated'
import { DropDownSectionProps } from 'types/DropDownSectionProps'
import { HealthMetricsProps } from 'types/healthMetrics'
import { getKeysLabels } from 'utils/getKeysLabels'
import LoadingSpinner from 'components/LoadingSpinner'
import MetricsCard from 'components/MetricsCard'
import ProjectsDashboardDropDown from 'components/ProjectsDashboardDropDown'

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

const SORT_FIELDS = [
  { label: 'Score (High → Low)', key: 'scoreDesc' },
  { label: 'Score (Low → High)', key: 'scoreAsc' },
  { label: 'Stars (High → Low)', key: 'starsDesc' },
  { label: 'Stars (Low → High)', key: 'starsAsc' },
  { label: 'Forks (High → Low)', key: 'forksDesc' },
  { label: 'Forks (Low → High)', key: 'forksAsc' },
  { label: 'Contributors (High → Low)', key: 'contributorsDesc' },
  { label: 'Contributors (Low → High)', key: 'contributorsAsc' },
  { label: 'Last checked (Newest)', key: 'createdAtDesc' },
  { label: 'Last checked (Oldest)', key: 'createdAtAsc' },
] as const

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
      level: 'INCUBATOR',
    },
    lab: {
      level: 'LAB',
    },
    production: {
      level: 'INCUBATOR',
    },
    flagship: {
      level: 'FLAGSHIP',
    },
  }

  let currentFilters = {}
  const orderingParam = searchParams.get('order')
  const { field, direction, urlKey } = parseOrderParam(orderingParam)
  const currentOrdering = buildGraphQLOrdering(field, direction)

  const healthFilter = searchParams.get('health')
  const levelFilter = searchParams.get('level')
  const currentFilterKeys = []
  if (healthFilter) {
    currentFilters = {
      ...healthFiltersMapping[healthFilter],
    }
    currentFilterKeys.push(healthFilter)
  }
  if (levelFilter) {
    currentFilters = {
      ...currentFilters,
      ...levelFiltersMapping[levelFilter],
    }
    currentFilterKeys.push(levelFilter)
  }

  const [metrics, setMetrics] = useState<HealthMetricsProps[]>([])
  const [metricsLength, setMetricsLength] = useState<number>(0)
  const [pagination, setPagination] = useState({ offset: 0, limit: PAGINATION_LIMIT })
  const [filters, setFilters] = useState(currentFilters)
  const [ordering, setOrdering] = useState(currentOrdering)
  const [activeFilters, setActiveFilters] = useState(currentFilterKeys)
  const {
    data,
    error: graphQLRequestError,
    loading,
    fetchMore,
  } = useQuery(GetProjectHealthMetricsDocument, {
    variables: {
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
      setMetrics(data.projectHealthMetrics)
      setMetricsLength(data.projectHealthMetricsDistinctLength)
    }
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
    }
  }, [data, graphQLRequestError])

  const filteringSections: DropDownSectionProps[] = [
    {
      title: 'Project Level',
      items: [
        { label: 'Incubator', key: 'incubator' },
        { label: 'Lab', key: 'lab' },
        { label: 'Production', key: 'production' },
        { label: 'Flagship', key: 'flagship' },
      ],
    },
    {
      title: 'Project Health',
      items: [
        { label: 'Healthy', key: 'healthy' },
        { label: 'Need Attention', key: 'needsAttention' },
        { label: 'Unhealthy', key: 'unhealthy' },
      ],
    },
    {
      title: 'Reset Filters',
      items: [{ label: 'Reset All Filters', key: 'reset' }],
    },
  ]

  const getCurrentPage = () => {
    return Math.floor(pagination.offset / PAGINATION_LIMIT) + 1
  }

  const handleSort = (orderKey: string | null) => {
    setPagination({ offset: 0, limit: PAGINATION_LIMIT })
    const newParams = new URLSearchParams(searchParams.toString())

    if (orderKey === null) {
      newParams.delete('order')
      const defaultOrdering = buildGraphQLOrdering('score', Ordering.Desc)
      setOrdering(defaultOrdering)
    } else {
      newParams.set('order', orderKey)
      const { field: newField, direction: newDirection } = parseOrderParam(orderKey)
      const newOrdering = buildGraphQLOrdering(newField, newDirection)
      setOrdering(newOrdering)
    }

    router.replace(`/projects/dashboard/metrics?${newParams.toString()}`)
  }

  return (
    <>
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="mb-2 text-2xl font-bold">Project Health Metrics</h1>
        <div className="flex flex-row items-center gap-2 self-end">
          <div>
            <ProjectsDashboardDropDown
              buttonDisplayName="Sort By"
              icon={urlKey?.endsWith('Desc') ? FaArrowDownWideShort : FaArrowUpWideShort}
              sections={[
                {
                  title: 'Sort by',
                  items: SORT_FIELDS.map((field) => ({
                    label: field.label,
                    key: field.key,
                  })),
                },
                {
                  title: 'Reset',
                  items: [{ label: 'Reset Sorting', key: 'reset-sort' }],
                },
              ]}
              selectionMode="single"
              selectedKeys={urlKey ? [urlKey] : []}
              selectedLabels={
                urlKey ? [SORT_FIELDS.find((f) => f.key === urlKey)?.label || ''] : []
              }
              onAction={(key: string) => {
                if (key === 'reset-sort') {
                  handleSort(null)
                  return
                }

                handleSort(key)
              }}
            />
          </div>
          <ProjectsDashboardDropDown
            buttonDisplayName="Filter By"
            icon={FaFilter}
            sections={filteringSections}
            selectionMode="multiple"
            selectedKeys={activeFilters}
            selectedLabels={getKeysLabels(filteringSections, activeFilters)}
            onAction={(key: string) => {
              // Because how apollo caches pagination, we need to reset the pagination.
              setPagination({ offset: 0, limit: PAGINATION_LIMIT })
              let newFilters = { ...currentFilters }
              const newParams = new URLSearchParams(searchParams.toString())
              if (key in healthFiltersMapping) {
                newParams.set('health', key)
                newFilters = { ...newFilters, ...healthFiltersMapping[key] }
              } else if (key in levelFiltersMapping) {
                newParams.set('level', key)
                newFilters = { ...newFilters, ...levelFiltersMapping[key] }
              } else {
                newParams.delete('health')
                newParams.delete('level')
                newFilters = {}
              }
              setFilters(newFilters)
              setActiveFilters(
                Array.from(
                  newParams
                    .entries()
                    .filter(([key]) => key != 'order')
                    .map(([, value]) => value)
                )
              )
              router.replace(`/projects/dashboard/metrics?${newParams.toString()}`)
            }}
          />
        </div>
      </div>
      {loading ? (
        <LoadingSpinner />
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-4 sm:gap-4 md:gap-6">
            {metrics.length === 0 ? (
              <div className="col-span-full py-8 text-center text-gray-500">
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
