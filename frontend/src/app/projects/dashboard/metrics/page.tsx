'use client'

import { useQuery } from '@apollo/client'
import { FC, useState, useEffect } from 'react'
import { handleAppError } from 'app/global-error'
import { GET_PROJECT_HEALTH_METRICS_LIST } from 'server/queries/projectsHealthDashboardQueries'
import { HealthMetricsProps, HealthMetricsFilter } from 'types/healthMetrics'
import LoadingSpinner from 'components/LoadingSpinner'

const MetricsPage: FC = () => {
  const [metrics, setMetrics] = useState<HealthMetricsProps[]>([])
  const [filters] = useState<HealthMetricsFilter>({})
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const { data, error: graphQLRequestError } = useQuery(GET_PROJECT_HEALTH_METRICS_LIST, {
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
    <div>
      <h1>Metrics Page</h1>
      {metrics.length > 0 ? (
        <ul>
          {metrics.map((metric) => (
            <li key={metric.id}>
              <h2>{metric.projectName}</h2>
              <p>Score: {metric.score}</p>
              <p>Created At: {new Date(metric.createdAt).toLocaleDateString()}</p>
              <p>Contributors Count: {metric.contributorsCount}</p>
            </li>
          ))}
        </ul>
      ) : (
        <p>No metrics available.</p>
      )}
    </div>
  )
}

export default MetricsPage
