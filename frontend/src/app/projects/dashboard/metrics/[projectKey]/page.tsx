'use client'

import { useQuery } from '@apollo/client'
import { faChartBar } from '@fortawesome/free-regular-svg-icons'
import { useParams } from 'next/navigation'
import { FC, useState, useEffect } from 'react'
import { handleAppError } from 'app/global-error'
import { GET_PROJECT_HEALTH_METRICS_DETAILS } from 'server/queries/projectsHealthDashboardQueries'
import { HealthMetricsProps } from 'types/healthMetrics'
import DashboardCard from 'components/DashboardCard'
import LoadingSpinner from 'components/LoadingSpinner'
import MetricsScoreCircle from 'components/MetricsScoreCircle'

const ProjectHealthMetricsDetails: FC = () => {
  const { projectKey } = useParams()
  const [metrics, setMetrics] = useState<HealthMetricsProps>()
  const {
    loading,
    error: graphqlError,
    data,
  } = useQuery(GET_PROJECT_HEALTH_METRICS_DETAILS, {
    variables: { projectKey },
  })

  useEffect(() => {
    if (graphqlError) {
      handleAppError(graphqlError)
    }
    if (data?.project?.healthMetricsLatest) {
      setMetrics(data.project.healthMetricsLatest)
    }
  }, [graphqlError, data])
  if (loading) {
    return <LoadingSpinner />
  }
  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{metrics ? metrics.projectName : ''}</h1>
        <MetricsScoreCircle score={metrics ? metrics.score : 0} />
      </div>
      {metrics && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3 lg:grid-cols-5">
          <DashboardCard title="Score" icon={faChartBar} stats={metrics.score.toString()} />
          <DashboardCard title="Stars" icon={faChartBar} stats={metrics.starsCount.toString()} />
          <DashboardCard title="Forks" icon={faChartBar} stats={metrics.forksCount.toString()} />
          <DashboardCard
            title="Contributors"
            icon={faChartBar}
            stats={metrics.contributorsCount.toString()}
          />
          <DashboardCard
            title="Open Issues"
            icon={faChartBar}
            stats={metrics.openIssuesCount.toString()}
          />
        </div>
      )}
    </div>
  )
}

export default ProjectHealthMetricsDetails
