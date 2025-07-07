'use client'

import { useQuery } from '@apollo/client'
import { faFilter } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Dropdown, DropdownItem, DropdownTrigger, DropdownMenu, Button } from '@heroui/react'
import { FC, useState, useEffect } from 'react'
import { handleAppError } from 'app/global-error'
import { GET_PROJECT_HEALTH_METRICS_LIST } from 'server/queries/projectsHealthDashboardQueries'
import { HealthMetricsProps, HealthMetricsFilter } from 'types/healthMetrics'
import LoadingSpinner from 'components/LoadingSpinner'
import MetricsCard from 'components/MetricsCard'

const MetricsPage: FC = () => {
  const [metrics, setMetrics] = useState<HealthMetricsProps[]>([])
  const [filters, setFilters] = useState<HealthMetricsFilter>({})
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const { data, error: graphQLRequestError, refetch } = useQuery(GET_PROJECT_HEALTH_METRICS_LIST, {
    variables: {
      filters,
      pagination: { offset: 0, limit: 10 },
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
  return (
    <>
      <div className='flex justify-between items-center mb-4'>
        <h1 className="text-2xl font-bold">Project Health Metrics</h1>
        <Dropdown>
          <DropdownTrigger>
            <Button variant="solid" color="primary">
              <FontAwesomeIcon icon={faFilter} className="mr-2" />
              Filter by Level
            </Button>
          </DropdownTrigger>
          <DropdownMenu onAction={async (key: string) =>{
            setFilters((prev) => ({ ...prev, level: key }))
            await refetch({
              filters: { ...filters, level: key },
              pagination: { offset: 0, limit: 10 },
            })
          }}>
            <DropdownItem key="incubator">
              Incubator
            </DropdownItem>
            <DropdownItem key="lab">
              Lab
            </DropdownItem>
            <DropdownItem key="production">
              Production
            </DropdownItem>
            <DropdownItem key="flagship">
              Flagship
            </DropdownItem>
          </DropdownMenu>
        </Dropdown>
      </div>
      <div className="grid grid-cols-8 p-4">
        <div className="font-semibold col-span-3 truncate">Project Name</div>
        <div className="font-semibold col-span-1 truncate">Score</div>
        <div className="font-semibold col-span-1 truncate">Stars</div>
        <div className="font-semibold col-span-1 truncate">Forks</div>
        <div className="font-semibold col-span-1 truncate">Contributors</div>
        <div className="font-semibold col-span-1 truncate">Created At</div>
      </div>
      <div className="grid grid-cols-1 gap-2">
        {metrics.map((metric) => (
          <MetricsCard key={metric.id} metric={metric} />
        ))}
      </div>
    </>
  )
}

export default MetricsPage
