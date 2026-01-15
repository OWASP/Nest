'use client'
import { useQuery } from '@apollo/client/react'
import { Pagination } from '@heroui/react'
import { useSearchParams, useRouter } from 'next/navigation'
import { FC, useState, useEffect } from 'react'
import type { IconType } from 'react-icons'
import { FaFilter, FaSort, FaSortUp, FaSortDown } from 'react-icons/fa6'
import { IconWrapper } from 'wrappers/IconWrapper'
import { handleAppError } from 'app/global-error'
import { Ordering } from 'types/__generated__/graphql'
import { GetProjectHealthMetricsDocument } from 'types/__generated__/projectsHealthDashboardQueries.generated'
import { DropDownSectionProps } from 'types/DropDownSectionProps'
import { HealthMetricsProps } from 'types/healthMetrics'
import { getKeysLabels } from 'utils/getKeysLabels'
import LoadingSpinner from 'components/LoadingSpinner'
import MetricsCard from 'components/MetricsCard'
import ProjectsDashboardDropDown from 'components/ProjectsDashboardDropDown'

interface HealthFilterStructure {
  score: {
    gte?: number
    lt?: number
  }
}

const PAGINATION_LIMIT = 10

const FIELD_MAPPING = {
  contributors: 'contributorsCount',
  createdAt: 'createdAt',
  forks: 'forksCount',
  score: 'score',
  stars: 'starsCount',
} as const

type OrderKey = keyof typeof FIELD_MAPPING

const healthFiltersMapping: Record<string, HealthFilterStructure> = {
  healthy: { score: { gte: 75 } },
  needsAttention: { score: { gte: 50, lt: 75 } },
  unhealthy: { score: { lt: 50 } },
} as const

const levelFiltersMapping: Record<string, { level: string }> = {
  incubator: { level: 'incubator' },
  lab: { level: 'lab' },
  production: { level: 'production' },
  flagship: { level: 'flagship' },
} as const

type FilterParams = Partial<HealthFilterStructure & { level: string }>

const getFiltersFromParams = (health: string | null, level: string | null): FilterParams => {
  let filters: FilterParams = {}

  if (health && health in healthFiltersMapping) {
    filters = { ...filters, ...healthFiltersMapping[health] }
  }
  if (level && level in levelFiltersMapping) {
    filters = { ...filters, ...levelFiltersMapping[level] }
  }
  return filters
}

const parseOrderParam = (orderParam: string | null) => {
  if (!orderParam) {
    return { field: 'score', direction: Ordering.Desc, urlKey: '-score' }
  }

  const isDescending = orderParam.startsWith('-')
  const fieldKey = isDescending ? orderParam.slice(1) : orderParam
  const isValidKey = fieldKey in FIELD_MAPPING
  const normalizedKey = isValidKey ? fieldKey : 'score'
  const graphqlField = FIELD_MAPPING[normalizedKey as OrderKey]
  const direction = isDescending ? Ordering.Desc : Ordering.Asc
  const normalizedUrlKey = direction === Ordering.Desc ? `-${normalizedKey}` : normalizedKey

  return { field: graphqlField, direction, urlKey: normalizedUrlKey }
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
const SortableColumnHeader: FC<{
  label: string
  fieldKey: OrderKey
  currentOrderKey: string
  onSort: (orderKey: string | null) => void
  align?: 'left' | 'center' | 'right'
}> = ({ label, fieldKey, currentOrderKey, onSort, align = 'left' }) => {
  const isActiveSortDesc = currentOrderKey === `-${fieldKey}`
  const isActiveSortAsc = currentOrderKey === fieldKey
  const isActive = isActiveSortDesc || isActiveSortAsc

  const handleClick = () => {
    if (!isActive) {
      onSort(`-${fieldKey}`)
    } else if (isActiveSortDesc) {
      onSort(fieldKey)
    } else {
      onSort(null)
    }
  }

  const justifyMap = {
    left: 'justify-start',
    center: 'justify-center',
    right: 'justify-end',
  }

  const alignmentClass = justifyMap[align] || justifyMap.left

  const textAlignMap = {
    left: 'text-left',
    center: 'text-center',
    right: 'text-right',
  }

  const textAlignClass = textAlignMap[align] || textAlignMap.left

  let iconType: IconType
  if (isActiveSortDesc) {
    iconType = FaSortDown
  } else if (isActiveSortAsc) {
    iconType = FaSortUp
  } else {
    iconType = FaSort
  }

  return (
    <div className={`flex items-center gap-1 ${alignmentClass}`}>
      <button
        type="button"
        onClick={handleClick}
        className={`flex items-center gap-1 font-semibold transition-colors hover:text-blue-600 ${textAlignClass}`}
        title={`Sort by ${label}`}
        aria-label={`Sort by ${label}`}
        aria-pressed={isActive}
      >
        <span className="truncate">{label}</span>
        <IconWrapper
          icon={iconType}
          className={`h-3 w-3 ${isActive ? 'text-blue-600' : 'text-gray-400'}`}
        />
      </button>
    </div>
  )
}

const MetricsPage: FC = () => {
  const searchParams = useSearchParams()
  const router = useRouter()

  const orderingParam = searchParams.get('order')
  const { field, direction, urlKey } = parseOrderParam(orderingParam)
  const currentOrdering = buildGraphQLOrdering(field, direction)

  const healthParam = searchParams.get('health')
  const levelParam = searchParams.get('level')

  const currentFilters = getFiltersFromParams(healthParam, levelParam)
  const currentFilterKeys = [healthParam, levelParam].filter((k): k is string => !!k)

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
    const nextFilters = getFiltersFromParams(searchParams.get('health'), searchParams.get('level'))

    setFilters((prevFilters) => {
      if (JSON.stringify(nextFilters) !== JSON.stringify(prevFilters)) {
        return nextFilters
      }
      return prevFilters
    })

    const nextActiveFilters = [searchParams.get('health'), searchParams.get('level')].filter(
      Boolean
    ) as string[]

    setActiveFilters(nextActiveFilters)
  }, [searchParams])

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
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Project Health Metrics</h1>
        <div className="flex flex-row items-center gap-2">
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
              const newParams = new URLSearchParams(searchParams.toString())

              if (key === 'reset') {
                newParams.delete('health')
                newParams.delete('level')
              } else if (key in healthFiltersMapping) {
                newParams.set('health', key)
              } else if (key in levelFiltersMapping) {
                newParams.set('level', key)
              }

              const nextFilters = getFiltersFromParams(
                newParams.get('health'),
                newParams.get('level')
              )

              setFilters(nextFilters)
              setActiveFilters(
                [newParams.get('health'), newParams.get('level')].filter((k): k is string => !!k)
              )
              router.replace(`/projects/dashboard/metrics?${newParams.toString()}`)
            }}
          />
        </div>
      </div>
      <div className="grid grid-cols-[4fr_1fr_1fr_1fr_1.5fr_1fr] gap-2 border-b border-gray-200 p-4 dark:border-gray-700">
        <div className="truncate font-semibold">Project Name</div>
        <SortableColumnHeader
          label="Stars"
          fieldKey="stars"
          currentOrderKey={urlKey}
          onSort={handleSort}
          align="center"
        />
        <SortableColumnHeader
          label="Forks"
          fieldKey="forks"
          currentOrderKey={urlKey}
          onSort={handleSort}
          align="center"
        />
        <SortableColumnHeader
          label="Contributors"
          fieldKey="contributors"
          currentOrderKey={urlKey}
          onSort={handleSort}
          align="center"
        />
        <SortableColumnHeader
          label="Health Checked At"
          fieldKey="createdAt"
          currentOrderKey={urlKey}
          onSort={handleSort}
          align="center"
        />
        <SortableColumnHeader
          label="Score"
          fieldKey="score"
          currentOrderKey={urlKey}
          onSort={handleSort}
          align="center"
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
