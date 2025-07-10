'use client'

import { useQuery } from '@apollo/client'
import { faFilter, faSort } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  Dropdown,
  DropdownItem,
  DropdownTrigger,
  DropdownMenu,
  DropdownSection,
  Button,
} from '@heroui/react'
import { FC, useState, useEffect } from 'react'
import { handleAppError } from 'app/global-error'
import { GET_PROJECT_HEALTH_METRICS_LIST } from 'server/queries/projectsHealthDashboardQueries'
import { HealthMetricsProps, HealthMetricsFilter, HealthMetricsOrdering } from 'types/healthMetrics'
import LoadingSpinner from 'components/LoadingSpinner'
import MetricsCard from 'components/MetricsCard'

const PAGINATION_LIMIT = 10

const MetricsPage: FC = () => {
  const [metrics, setMetrics] = useState<HealthMetricsProps[]>([])
  const [filters, setFilters] = useState<HealthMetricsFilter>({})
  const [ordering, setOrdering] = useState<HealthMetricsOrdering>({
    scoreOrdering: { score: 'DESC' },
  })
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const {
    data,
    error: graphQLRequestError,
    refetch,
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
      setIsLoading(false)
    }
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
      setIsLoading(false)
    }
  }, [data, graphQLRequestError])
  if (isLoading) {
    return <LoadingSpinner />
  }
  const orderingItems = [
    { label: 'Score (High to Low)', key: 'scoreDESC' },
    { label: 'Score (Low to High)', key: 'scoreASC' },
    { label: 'Stars (High to Low)', key: 'starsCountDESC' },
    { label: 'Stars (Low to High)', key: 'starsCountASC' },
    { label: 'Forks (High to Low)', key: 'forksCountDESC' },
    { label: 'Forks (Low to High)', key: 'forksCountASC' },
    { label: 'Contributors (High to Low)', key: 'contributorsCountDESC' },
    { label: 'Contributors (Low to High)', key: 'contributorsCountASC' },
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
      scoreOrdering: { starsCount: 'DESC' },
    },
    starsCountASC: {
      scoreOrdering: { starsCount: 'ASC' },
    },
    forksCountDESC: {
      scoreOrdering: { forksCount: 'DESC' },
    },
    forksCountASC: {
      scoreOrdering: { forksCount: 'ASC' },
    },
    contributorsCountDESC: {
      scoreOrdering: { contributorsCount: 'DESC' },
    },
    contributorsCountASC: {
      scoreOrdering: { contributorsCount: 'ASC' },
    },
  }
  return (
    <>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Project Health Metrics</h1>
        <div className="flex items-center space-x-2">
          <Dropdown>
            <DropdownTrigger>
              <Button variant="solid" color="success">
                <FontAwesomeIcon icon={faFilter} className="mr-2" />
                Filters
              </Button>
            </DropdownTrigger>
            <DropdownMenu
              selectionMode="single"
              selectedKeys={Object.keys(filtersMapping).filter(
                (key) => JSON.stringify(filtersMapping[key]) === JSON.stringify(filters)
              )}
              onAction={async (key: string) => {
                setFilters(filtersMapping[key])
                await refetch({
                  filters: filtersMapping[key],
                  pagination: { offset: 0, limit: PAGINATION_LIMIT },
                })
              }}
            >
              <DropdownSection title="Project Level">
                <DropdownItem key="incubator">Incubator</DropdownItem>
                <DropdownItem key="lab">Lab</DropdownItem>
                <DropdownItem key="production">Production</DropdownItem>
                <DropdownItem key="flagship">Flagship</DropdownItem>
              </DropdownSection>
              <DropdownSection title="Project Health">
                <DropdownItem key="healthy">Healthy Projects</DropdownItem>
                <DropdownItem key="warning">Projects Needing Attention</DropdownItem>
                <DropdownItem key="critical">Unhealthy Projects</DropdownItem>
              </DropdownSection>
              <DropdownSection title="Reset Filters">
                <DropdownItem key="reset">Reset All Filters</DropdownItem>
              </DropdownSection>
            </DropdownMenu>
          </Dropdown>
          <Dropdown>
            <DropdownTrigger>
              <Button variant="solid" color="success">
                <FontAwesomeIcon icon={faSort} className="mr-2" />
                Sort By
              </Button>
            </DropdownTrigger>
            <DropdownMenu
              selectionMode="single"
              selectedKeys={Object.keys(orderingMapping).filter(
                (key) => JSON.stringify(ordering) === JSON.stringify(orderingMapping[key])
              )}
              onAction={async (key: string) => {
                setOrdering(orderingMapping[key])
                await refetch({
                  filters,
                  pagination: { offset: 0, limit: PAGINATION_LIMIT },
                  ordering: Object.values(orderingMapping[key]),
                })
              }}
            >
              {orderingItems.map((option) => (
                <DropdownItem key={option.key}>{option.label}</DropdownItem>
              ))}
            </DropdownMenu>
          </Dropdown>
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
      <div className="grid grid-cols-1 gap-2">
        {metrics.length === 0 ? (
          <div className="py-8 text-center text-gray-500">
            No metrics found. Try adjusting your filters.
          </div>
        ) : (
          metrics.map((metric) => <MetricsCard key={metric.id} metric={metric} />)
        )}
      </div>
    </>
  )
}

export default MetricsPage
