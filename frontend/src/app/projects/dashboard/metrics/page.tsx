'use client'
import { useQuery } from '@apollo/client/react'
import { Pagination } from '@heroui/react'
import { useSearchParams, useRouter } from 'next/navigation'
import { FC, useState, useEffect } from 'react'
import type { IconType } from 'react-icons'
import {
  FaFilter,
  FaSort,
  FaSortUp,
  FaSortDown,
  FaArrowDownWideShort,
  FaArrowUpWideShort,
} from 'react-icons/fa6'
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

const PAGINATION_LIMIT = 10

type OrderKey = 'score' | 'stars' | 'forks' | 'contributors' | 'createdAt'

const MOBILE_ORDERING_MAP = {
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

type MobileOrderingKey = keyof typeof MOBILE_ORDERING_MAP

const MOBILE_SORT_FIELDS = [
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
  if (!orderParam || !(orderParam in MOBILE_ORDERING_MAP)) {
    return { field: 'score', direction: Ordering.Desc, urlKey: 'scoreDesc' }
  }

  const { field, direction } = MOBILE_ORDERING_MAP[orderParam as MobileOrderingKey]

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

const SortableColumnHeader: FC<{
  label: string
  fieldKey: OrderKey
  currentOrderKey: string
  onSort: (orderKey: string | null) => void
  align?: 'left' | 'center' | 'right'
}> = ({ label, fieldKey, currentOrderKey, onSort, align = 'left' }) => {
  const descOrderKey = `${fieldKey}Desc` as MobileOrderingKey
  const ascOrderKey = `${fieldKey}Asc` as MobileOrderingKey

  const isActiveSortDesc = currentOrderKey === descOrderKey
  const isActiveSortAsc = currentOrderKey === ascOrderKey
  const isActive = isActiveSortDesc || isActiveSortAsc

  const handleClick = () => {
    if (!isActive) {
      onSort(descOrderKey)
    } else if (isActiveSortDesc) {
      onSort(ascOrderKey)
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
      level: 'incubator',
    },
    lab: {
      level: 'lab',
    },
    production: {
      level: 'production',
    },
    flagship: {
      level: 'flagship',
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
          {/* Mobile Sort */}
          <div className="sm:hidden">
            <ProjectsDashboardDropDown
              buttonDisplayName="Sort By"
              icon={urlKey?.endsWith('Desc') ? FaArrowDownWideShort : FaArrowUpWideShort}
              sections={[
                {
                  title: 'Sort by',
                  items: MOBILE_SORT_FIELDS.map((field) => ({
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
                urlKey ? [MOBILE_SORT_FIELDS.find((f) => f.key === urlKey)?.label || ''] : []
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
      <div className="hidden grid-cols-[4fr_1fr_1fr_1fr_1.5fr_1fr] gap-2 border-b border-gray-200 p-4 sm:grid dark:border-gray-700">
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
