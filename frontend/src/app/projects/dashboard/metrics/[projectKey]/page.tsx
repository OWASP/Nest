'use client'
import { useQuery } from '@apollo/client/react'
import { useParams } from 'next/navigation'
import { FC, useState, useEffect } from 'react'
import { FaExclamationCircle } from 'react-icons/fa'
import {
  FaPeopleGroup,
  FaCodeFork,
  FaDollarSign,
  FaCodePullRequest,
  FaChartArea,
  FaHandshake,
  FaStar,
  FaTags,
} from 'react-icons/fa6'
import { handleAppError } from 'app/global-error'
import { GetProjectHealthMetricsDetailsDocument } from 'types/__generated__/projectsHealthDashboardQueries.generated'
import { HealthMetricsProps } from 'types/healthMetrics'
import BarChart from 'components/BarChart'
import GeneralCompliantComponent from 'components/GeneralCompliantComponent'
import LineChart from 'components/LineChart'
import LoadingSpinner from 'components/LoadingSpinner'
import MetricsPDFButton from 'components/MetricsPDFButton'
import MetricsScoreCircle from 'components/MetricsScoreCircle'

const ProjectHealthMetricsDetails: FC = () => {
  const { projectKey } = useParams<{ projectKey: string }>()
  const [metricsList, setMetricsList] = useState<HealthMetricsProps[]>()
  const [metricsLatest, setMetricsLatest] = useState<HealthMetricsProps>()
  const {
    loading,
    error: graphqlError,
    data,
  } = useQuery(GetProjectHealthMetricsDetailsDocument, {
    variables: { projectKey },
  })

  useEffect(() => {
    if (graphqlError) {
      handleAppError(graphqlError)
    }
    if (data?.project?.healthMetricsLatest) {
      setMetricsLatest(data.project.healthMetricsLatest as HealthMetricsProps)
    }
    if (data?.project?.healthMetricsList) {
      setMetricsList(data.project.healthMetricsList as HealthMetricsProps[])
    }
  }, [graphqlError, data])

  if (loading) {
    return <LoadingSpinner />
  }

  const labels =
    metricsList?.map((m) =>
      new Date(m.createdAt || '').toLocaleString('default', {
        month: 'short',
        day: 'numeric',
      })
    ) || []

  return (
    <div className="flex flex-col gap-4">
      {metricsList && metricsLatest ? (
        <>
          <div className="flex items-center justify-between">
            <div className="flex justify-start">
              <h1 className="text-2xl font-bold">{metricsLatest.projectName || ''}</h1>
              <MetricsPDFButton
                path={`${projectKey}/pdf`}
                fileName={`${projectKey}-health-metrics`}
              />
            </div>
            <div className="flex items-center gap-2">
              <MetricsScoreCircle score={metricsLatest.score ?? 0} clickable={false} />
              <GeneralCompliantComponent
                title={
                  metricsLatest.isFundingRequirementsCompliant
                    ? 'Funding Requirements Compliant'
                    : 'Funding Requirements Not Compliant'
                }
                icon={FaDollarSign}
                compliant={metricsLatest.isFundingRequirementsCompliant ?? false}
              />
              <GeneralCompliantComponent
                title={
                  metricsLatest.isLeaderRequirementsCompliant
                    ? 'Leader Requirements Compliant'
                    : 'Leader Requirements Not Compliant'
                }
                icon={FaHandshake}
                compliant={metricsLatest.isLeaderRequirementsCompliant ?? false}
              />
            </div>
          </div>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <LineChart
              title="Stars"
              icon={FaStar}
              series={[
                {
                  name: 'Stars',
                  data: metricsList.map((m) => m.starsCount ?? 0),
                },
              ]}
              labels={labels}
              round
            />
            <LineChart
              title="Forks"
              icon={FaCodeFork}
              series={[
                {
                  name: 'Forks',
                  data: metricsList.map((m) => m.forksCount ?? 0),
                },
              ]}
              labels={labels}
              round
            />
          </div>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <LineChart
              title="Issues"
              icon={FaExclamationCircle}
              series={[
                {
                  name: 'Open Issues',
                  data: metricsList.map((m) => m.openIssuesCount ?? 0),
                },
                {
                  name: 'Unassigned Issues',
                  data: metricsList.map((m) => m.unassignedIssuesCount ?? 0),
                },
                {
                  name: 'Unanswered Issues',
                  data: metricsList.map((m) => m.unansweredIssuesCount ?? 0),
                },
                {
                  name: 'Total Issues',
                  data: metricsList.map((m) => m.totalIssuesCount ?? 0),
                },
              ]}
              labels={labels}
              round
            />
            <LineChart
              title="Open Pull Requests"
              icon={FaCodePullRequest}
              series={[
                {
                  name: 'Open Pull Requests',
                  data: metricsList.map((m) => m.openPullRequestsCount ?? 0),
                },
              ]}
              labels={labels}
              round
            />
          </div>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <LineChart
              title="Releases"
              icon={FaTags}
              series={[
                {
                  name: 'Recent Releases',
                  data: metricsList.map((m) => m.recentReleasesCount ?? 0),
                },
                {
                  name: 'Total Releases',
                  data: metricsList.map((m) => m.totalReleasesCount ?? 0),
                },
              ]}
              labels={labels}
              round
            />
            <LineChart
              title="Contributors"
              icon={FaPeopleGroup}
              series={[
                {
                  name: 'Contributors',
                  data: metricsList.map((m) => m.contributorsCount ?? 0),
                },
              ]}
              labels={labels}
              round
            />
          </div>
          <BarChart
            title="Days Metrics"
            icon={FaChartArea}
            labels={[
              'Project Age',
              'Days Since Last Commit',
              'Days Since Last Release',
              'Days Since Last Pull Request',
              'Days Since OWASP Page Last Update',
            ]}
            days={[
              metricsLatest.ageDays ?? 0,
              metricsLatest.lastCommitDays ?? 0,
              metricsLatest.lastReleaseDays ?? 0,
              metricsLatest.lastPullRequestDays ?? 0,
              metricsLatest.owaspPageLastUpdateDays ?? 0,
            ]}
            requirements={[
              metricsLatest.ageDaysRequirement ?? 0,
              metricsLatest.lastCommitDaysRequirement ?? 0,
              metricsLatest.lastReleaseDaysRequirement ?? 0,
              metricsLatest.lastPullRequestDaysRequirement ?? 0,
              metricsLatest.owaspPageLastUpdateDaysRequirement ?? 0,
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