'use client'

import { useQuery } from '@apollo/client'
import { faFilter } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  Dropdown,
  DropdownItem,
  DropdownTrigger,
  DropdownMenu,
  Button,
  Select,
  SelectItem,
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
  const selectOptions = [
    { label: 'Score (High to Low)', key: 'score_DESC' },
    { label: 'Score (Low to High)', key: 'score_ASC' },
    { label: 'Stars (High to Low)', key: 'starsCount_DESC' },
    { label: 'Stars (Low to High)', key: 'starsCount_ASC' },
    { label: 'Forks (High to Low)', key: 'forksCount_DESC' },
    { label: 'Forks (Low to High)', key: 'forksCount_ASC' },
    { label: 'Contributors (High to Low)', key: 'contributorsCount_DESC' },
    { label: 'Contributors (Low to High)', key: 'contributorsCount_ASC' },
  ]
  return (
    <>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Project Health Metrics</h1>
        <div className="flex items-center space-x-2">
          <Dropdown>
            <DropdownTrigger>
              <Button variant="solid" color="primary">
                <FontAwesomeIcon icon={faFilter} className="mr-2" />
                Filter by Level
              </Button>
            </DropdownTrigger>
            <DropdownMenu
              onAction={async (key: string) => {
                const newFilters = { ...filters, level: key }
                setFilters(newFilters)
                await refetch({
                  filters: newFilters,
                  pagination: { offset: 0, limit: PAGINATION_LIMIT },
                })
              }}
            >
              <DropdownItem key="incubator">Incubator</DropdownItem>
              <DropdownItem key="lab">Lab</DropdownItem>
              <DropdownItem key="production">Production</DropdownItem>
              <DropdownItem key="flagship">Flagship</DropdownItem>
            </DropdownMenu>
          </Dropdown>
          <Select
            label="Sort By"
            placeholder="Select sorting option"
            selectionMode="multiple"
            className="w-64"
            color="primary"
          >
            {selectOptions.map((option) => (
              <SelectItem
                key={option.key}
                onPress={() => {
                  const [key, order] = option.key.split('_')
                  const newOrdering: HealthMetricsOrdering = {
                    ...ordering,
                  }
                  newOrdering[`${key}Ordering`] = { [key]: order }
                  setOrdering(newOrdering)
                  refetch({
                    filters,
                    pagination: { offset: 0, limit: PAGINATION_LIMIT },
                    ordering: Object.values(newOrdering),
                  })
                }}
              >
                {option.label}
              </SelectItem>
            ))}
          </Select>
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
