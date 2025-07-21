'use client'

import { useQuery } from '@apollo/client'
import {
  faPeopleGroup,
  faCodeFork,
  faDollar,
  faCodePullRequest,
  faChartArea,
  faExclamationCircle,
  faHandshake,
  faStar,
  faTags,
} from '@fortawesome/free-solid-svg-icons'
import { useParams } from 'next/navigation'
import { FC, useState, useEffect } from 'react'
import { handleAppError } from 'app/global-error'
import { GET_PROJECT_HEALTH_METRICS_DETAILS } from 'server/queries/projectsHealthDashboardQueries'
import { HealthMetricsProps } from 'types/healthMetrics'
import BarChart from 'components/BarChart'
import GeneralCompliantComponent from 'components/GeneralCompliantComponent'
import LineChart from 'components/LineChart'
import LoadingSpinner from 'components/LoadingSpinner'
import MetricsScoreCircle from 'components/MetricsScoreCircle'
const ProjectHealthMetricsDetails: FC = () => {
  const { projectKey } = useParams()
  const [metricsList, setMetricsList] = useState<HealthMetricsProps[]>()
  const [metricsLatest, setMetricsLatest] = useState<HealthMetricsProps>()
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
      setMetricsLatest(data.project.healthMetricsLatest)
    }
    if (data?.project?.healthMetricsList) {
      setMetricsList(data.project.healthMetricsList)
    }
  }, [graphqlError, data])

  if (loading) {
    return <LoadingSpinner />
  }

  const labels =
    metricsList?.map((m) =>
      new Date(m.createdAt).toLocaleString('default', {
        month: 'short',
        day: 'numeric',
      })
    ) || []
  return (
    <div className="flex flex-col gap-4">
      {metricsList && metricsLatest ? (
        <>
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold">{metricsLatest.projectName}</h1>
            <div className="flex items-center gap-2">
              <MetricsScoreCircle score={metricsLatest.score} />
              <GeneralCompliantComponent
                title={
                  metricsLatest.isFundingRequirementsCompliant
                    ? 'Funding Requirements Compliant'
                    : 'Funding Requirements Not Compliant'
                }
                icon={faDollar}
                compliant={metricsLatest.isFundingRequirementsCompliant}
              />
              <GeneralCompliantComponent
                title={
                  metricsLatest.isLeaderRequirementsCompliant
                    ? 'Leader Requirements Compliant'
                    : 'Leader Requirements Not Compliant'
                }
                icon={faHandshake}
                compliant={metricsLatest.isLeaderRequirementsCompliant}
              />
            </div>
          </div>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <LineChart
              title="Stars"
              icon={faStar}
              series={[
                {
                  name: 'Stars',
                  data: metricsList.map((m) => m.starsCount),
                },
              ]}
              labels={labels}
              round
            />
            <LineChart
              title="Forks"
              icon={faCodeFork}
              series={[
                {
                  name: 'Forks',
                  data: metricsList.map((m) => m.forksCount),
                },
              ]}
              labels={labels}
              round
            />
          </div>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <LineChart
              title="Issues"
              icon={faExclamationCircle}
              series={[
                {
                  name: 'Open Issues',
                  data: metricsList.map((m) => m.openIssuesCount),
                },
                {
                  name: 'Unassigned Issues',
                  data: metricsList.map((m) => m.unassignedIssuesCount),
                },
                {
                  name: 'Unanswered Issues',
                  data: metricsList.map((m) => m.unansweredIssuesCount),
                },
                {
                  name: 'Total Issues',
                  data: metricsList.map((m) => m.totalIssuesCount),
                },
              ]}
              labels={labels}
              round
            />
            <LineChart
              title="Open Pull Requests"
              icon={faCodePullRequest}
              series={[
                {
                  name: 'Open Pull Requests',
                  data: metricsList.map((m) => m.openPullRequestsCount),
                },
              ]}
              labels={labels}
              round
            />
          </div>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <LineChart
              title="Releases"
              icon={faTags}
              series={[
                {
                  name: 'Recent Releases',
                  data: metricsList.map((m) => m.recentReleasesCount),
                },
                {
                  name: 'Total Releases',
                  data: metricsList.map((m) => m.totalReleasesCount),
                },
              ]}
              labels={labels}
              round
            />
            <LineChart
              title="Contributors"
              icon={faPeopleGroup}
              series={[
                {
                  name: 'Contributors',
                  data: metricsList.map((m) => m.contributorsCount),
                },
              ]}
              labels={labels}
              round
            />
          </div>
          <BarChart
            title="Days Metrics"
            icon={faChartArea}
            labels={[
              'Project Age',
              'Days Since Last Commit',
              'Days Since Last Release',
              'Days Since Last Pull Request',
              'Days Since OWASP Page Last Update',
            ]}
            days={[
              metricsLatest.ageDays,
              metricsLatest.lastCommitDays,
              metricsLatest.lastReleaseDays,
              metricsLatest.lastPullRequestDays,
              metricsLatest.owaspPageLastUpdateDays,
            ]}
            requirements={[
              metricsLatest.ageDaysRequirement,
              metricsLatest.lastCommitDaysRequirement,
              metricsLatest.lastReleaseDaysRequirement,
              metricsLatest.lastPullRequestDaysRequirement,
              metricsLatest.owaspPageLastUpdateDaysRequirement,
            ]}
            reverseColors={[true, false, false, false, false]}
          />
        </>
      ) : (
        <div className="text-center text-gray-500">No metrics data available for this project.</div>
      )}
    </div>
  )
}

export default ProjectHealthMetricsDetails
