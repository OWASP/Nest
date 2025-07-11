'use client'

import { useQuery } from '@apollo/client'
import { faFilter, faSort } from '@fortawesome/free-solid-svg-icons'
import { Pagination } from '@heroui/react'
import { FC, useState, useEffect } from 'react'
import { handleAppError } from 'app/global-error'
import { GET_PROJECT_HEALTH_METRICS_LIST } from 'server/queries/projectsHealthDashboardQueries'
import { DropDownSectionProps } from 'types/DropDownSectionProps'
import { HealthMetricsProps, HealthMetricsFilter, HealthMetricsOrdering } from 'types/healthMetrics'
import LoadingSpinner from 'components/LoadingSpinner'
import MetricsCard from 'components/MetricsCard'
import ProjectsDashboardDropDown from 'components/ProjectsDashboardDropDown'

const PAGINATION_LIMIT = 10

const MetricsPage: FC = () => {
  const [metrics, setMetrics] = useState<HealthMetricsProps[]>([])
  const [metricsLength, setMetricsLength] = useState<number>(0)
  const [filters, setFilters] = useState<HealthMetricsFilter>({})
  const [pagination, setPagination] = useState({ offset: 0, limit: PAGINATION_LIMIT })
  const [ordering, setOrdering] = useState<HealthMetricsOrdering>({
    scoreOrdering: { score: 'DESC' },
  })
  const [activeFilterKey, setActiveFilterKey] = useState<string>('reset')
  const [activeOrderingKey, setActiveOrderingKey] = useState<string>('scoreDESC')
  const {
    data,
    error: graphQLRequestError,
    refetch,
    loading,
    fetchMore,
  } = useQuery(GET_PROJECT_HEALTH_METRICS_LIST, {
    variables: {
      filters,
      pagination: { offset: 0, limit: PAGINATION_LIMIT },
      ordering: Object.values(ordering),
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
      title: 'Score',
      items: [
        { label: 'High to Low', key: 'scoreDESC' },
        { label: 'Low to High', key: 'scoreASC' },
      ],
    },
    {
      title: 'Stars',
      items: [
        { label: 'High to Low', key: 'starsCountDESC' },
        { label: 'Low to High', key: 'starsCountASC' },
      ],
    },
    {
      title: 'Forks',
      items: [
        { label: 'High to Low', key: 'forksCountDESC' },
        { label: 'Low to High', key: 'forksCountASC' },
      ],
    },
    {
      title: 'Contributors',
      items: [
        { label: 'High to Low', key: 'contributorsCountDESC' },
        { label: 'Low to High', key: 'contributorsCountASC' },
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
        { label: 'Healthy Projects', key: 'healthy' },
        { label: 'Projects Needing Attention', key: 'warning' },
        { label: 'Unhealthy Projects', key: 'critical' },
      ],
    },
    {
      title: 'Reset Filters',
      items: [{ label: 'Reset All Filters', key: 'reset' }],
    },
  ]
  const filtersMapping = {
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
    healthy: {
      score: {
        gte: 75,
      },
    },
    warning: {
      score: {
        gte: 50,
        lt: 75,
      },
    },
    critical: {
      score: {
        lt: 50,
      },
    },
    reset: {},
  }
  const orderingMapping = {
    scoreDESC: {
      scoreOrdering: { score: 'DESC' },
    },
    scoreASC: {
      scoreOrdering: { score: 'ASC' },
    },
    starsCountDESC: {
      starsOrdering: { starsCount: 'DESC' },
    },
    starsCountASC: {
      starsOrdering: { starsCount: 'ASC' },
    },
    forksCountDESC: {
      forksOrdering: { forksCount: 'DESC' },
    },
    forksCountASC: {
      forksOrdering: { forksCount: 'ASC' },
    },
    contributorsCountDESC: {
      contributorsOrdering: { contributorsCount: 'DESC' },
    },
    contributorsCountASC: {
      contributorsOrdering: { contributorsCount: 'ASC' },
    },
  }

  const getCurrentPage = () => {
    return Math.floor(pagination.offset / PAGINATION_LIMIT) + 1
  }

  return (
    <>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Project Health Metrics</h1>
        <div className="flex items-center space-x-2">
          <ProjectsDashboardDropDown
            buttonDisplayName="Filter By"
            icon={faFilter}
            sections={filteringSections}
            selectionMode="single"
            selectedKeys={[activeFilterKey]}
            onAction={async (key: string) => {
              // Because how apollo caches pagination, we need to reset the pagination.
              const newPagination = { offset: 0, limit: PAGINATION_LIMIT }
              setPagination(newPagination)
              setFilters(filtersMapping[key])
              setActiveFilterKey(key)
              await refetch({
                filters: filtersMapping[key],
                pagination: newPagination,
                ordering: Object.values(ordering),
              })
            }}
          />

          <ProjectsDashboardDropDown
            buttonDisplayName="Sort By"
            icon={faSort}
            sections={orderingSections}
            selectionMode="single"
            selectedKeys={[activeOrderingKey]}
            onAction={async (key: string) => {
              // Reset pagination to the first page when changing ordering
              const newPagination = { offset: 0, limit: PAGINATION_LIMIT }
              setPagination(newPagination)
              setOrdering(orderingMapping[key])
              setActiveOrderingKey(key)
              await refetch({
                filters,
                pagination: newPagination,
                ordering: Object.values(orderingMapping[key]),
              })
            }}
          />
        </div>
      </div>
      <div className="grid grid-cols-[4fr_1fr_1fr_1fr_1.5fr_1fr] p-4">
        <div className="truncate font-semibold">Project Name</div>
        <div className="truncate font-semibold">Stars</div>
        <div className="truncate font-semibold">Forks</div>
        <div className="truncate font-semibold">Contributors</div>
        <div className="truncate text-center font-semibold">Created At</div>
        <div className="truncate text-center font-semibold">Score</div>
      </div>
      {loading ? (
        <LoadingSpinner />
      ) : (
        <div className="grid grid-cols-1 gap-2">
          {metrics.length === 0 ? (
            <div className="py-8 text-center text-gray-500">
              No metrics found. Try adjusting your filters.
            </div>
          ) : (
            metrics.map((metric) => <MetricsCard key={metric.id} metric={metric} />)
          )}
        </div>
      )}
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
                ordering: Object.values(ordering),
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
  )
}

export default MetricsPage
