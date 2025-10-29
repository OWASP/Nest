'use client'
import { useQuery } from '@apollo/client/react'
import { faFilter } from '@fortawesome/free-solid-svg-icons'
import { Pagination } from '@heroui/react'
import { useSearchParams, useRouter } from 'next/navigation'
import { FC, useState, useEffect } from 'react'
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
  let currentOrdering = {
    score: Ordering.Desc,
  }
  const healthFilter = searchParams.get('health')
  const levelFilter = searchParams.get('level')
  const orderingParam = searchParams.get('order') as Ordering
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
  if (orderingParam) {
    currentOrdering = {
      score: orderingParam,
    }
  }

  const [metrics, setMetrics] = useState<HealthMetricsProps[]>([])
  const [metricsLength, setMetricsLength] = useState<number>(0)
  const [pagination, setPagination] = useState({ offset: 0, limit: PAGINATION_LIMIT })
  const [filters, setFilters] = useState(currentFilters)
  const [ordering, setOrdering] = useState(
    currentOrdering || {
      score: Ordering.Desc,
    }
  )
  const [activeFilters, setActiveFilters] = useState(currentFilterKeys)
  const [activeOrdering, setActiveOrdering] = useState(
    orderingParam ? [orderingParam] : [Ordering.Desc]
  )
  const {
    data,
    error: graphQLRequestError,
    loading,
    fetchMore,
  } = useQuery(GetProjectHealthMetricsDocument, {
    variables: {
      filters,
      pagination: { offset: 0, limit: PAGINATION_LIMIT },
      ordering: [
        ordering,
        {
          // eslint-disable-next-line @typescript-eslint/naming-convention
          project_Name: Ordering.Asc,
        },
      ],
    },
  })

  useEffect(() => {
    if (data) {
      setMetrics(data.projectHealthMetrics)
      setMetricsLength(data.projectHealthMetricsDistinctLength)
    }
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
    }
  }, [data, graphQLRequestError])

  const orderingSections: DropDownSectionProps[] = [
    {
      title: '',
      items: [
        { label: 'Descending', key: 'desc' },
        { label: 'Ascending', key: 'asc' },
      ],
    },
  ]
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

  return (
    <>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Project Health Metrics</h1>
        <div className="flex flex-row items-center gap-2">
          <ProjectsDashboardDropDown
            buttonDisplayName="Filter By"
            icon={faFilter}
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

          <ProjectsDashboardDropDown
            buttonDisplayName="Score"
            isOrdering
            sections={orderingSections}
            selectionMode="single"
            selectedKeys={activeOrdering}
            selectedLabels={getKeysLabels(orderingSections, activeOrdering)}
            onAction={(key: Ordering) => {
              // Reset pagination to the first page when changing ordering
              setPagination({ offset: 0, limit: PAGINATION_LIMIT })
              const newParams = new URLSearchParams(searchParams.toString())
              newParams.set('order', key)
              setOrdering({
                score: key,
              })
              setActiveOrdering([key])
              router.replace(`/projects/dashboard/metrics?${newParams.toString()}`)
            }}
          />
        </div>
      </div>
      <div className="grid grid-cols-[4fr_1fr_1fr_1fr_1.5fr_1fr] p-4">
        <div className="truncate font-semibold">Project Name</div>
        <div className="truncate text-center font-semibold">Stars</div>
        <div className="truncate text-center font-semibold">Forks</div>
        <div className="truncate text-center font-semibold">Contributors</div>
        <div className="truncate text-center font-semibold">Health Checked At</div>
        <div className="truncate text-center font-semibold">Score</div>
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
                    ordering: [
                      ordering,
                      {
                        // eslint-disable-next-line @typescript-eslint/naming-convention
                        project_Name: Ordering.Asc,
                      },
                    ],
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
