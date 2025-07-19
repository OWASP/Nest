'use client'

import { useQuery } from '@apollo/client'
import {
  faPeopleGroup,
  faCodeFork,
  faDollar,
  faCodePullRequest,
  faChartArea,
  faExclamationCircle,
  faQuestionCircle,
  faFolderOpen,
  faHandshake,
  faTag,
  faRocket,
  faStar,
  faTags,
} from '@fortawesome/free-solid-svg-icons'
import millify from 'millify'
import { useParams } from 'next/navigation'
import { FC, useState, useEffect } from 'react'
import { handleAppError } from 'app/global-error'
import { GET_PROJECT_HEALTH_METRICS_DETAILS } from 'server/queries/projectsHealthDashboardQueries'
import { HealthMetricsProps } from 'types/healthMetrics'
import BarChart from 'components/BarChart'
import DashboardCard from 'components/DashboardCard'
import GeneralCompliantComponent from 'components/GeneralCompliantComponent'
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
      {metrics && (
        <>
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold">{metrics.projectName}</h1>
            <MetricsScoreCircle score={metrics.score} />
          </div>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <GeneralCompliantComponent
              title="Funding Requirements Compliant"
              icon={faDollar}
              compliant={metrics.isFundingRequirementsCompliant}
            />
            <GeneralCompliantComponent
              title="Leader Requirements Compliant"
              icon={faHandshake}
              compliant={metrics.isLeaderRequirementsCompliant}
            />
          </div>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <DashboardCard title="Stars" icon={faStar} stats={millify(metrics.starsCount)} />
            <DashboardCard title="Forks" icon={faCodeFork} stats={millify(metrics.forksCount)} />
            <DashboardCard
              title="Contributors"
              icon={faPeopleGroup}
              stats={millify(metrics.contributorsCount)}
            />
          </div>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3 lg:grid-cols-4">
            <DashboardCard
              title="Open Issues"
              icon={faExclamationCircle}
              stats={millify(metrics.openIssuesCount)}
            />
            <DashboardCard
              title="Total Issues"
              icon={faFolderOpen}
              stats={millify(metrics.totalIssuesCount)}
            />
            <DashboardCard
              title="Unassigned Issues"
              icon={faTag}
              stats={millify(metrics.unassignedIssuesCount)}
            />
            <DashboardCard
              title="Unanswered Issues"
              icon={faQuestionCircle}
              stats={millify(metrics.unansweredIssuesCount)}
            />
          </div>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <DashboardCard
              title="Open Pull Requests"
              icon={faCodePullRequest}
              stats={millify(metrics.openPullRequestsCount)}
            />
            <DashboardCard
              title="Recent Releases"
              icon={faRocket}
              stats={millify(metrics.recentReleasesCount)}
            />
            <DashboardCard
              title="Total Releases"
              icon={faTags}
              stats={millify(metrics.totalReleasesCount)}
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
              metrics.ageDays,
              metrics.lastCommitDays,
              metrics.lastReleaseDays,
              metrics.lastPullRequestDays,
              metrics.owaspPageLastUpdateDays,
            ]}
            requirements={[
              metrics.ageDaysRequirement,
              metrics.lastCommitDaysRequirement,
              metrics.lastReleaseDaysRequirement,
              metrics.lastPullRequestDaysRequirement,
              metrics.owaspPageLastUpdateDaysRequirement,
            ]}
            reverseColors={[true, false, false, false, false]}
          />
        </>
      )}
    </div>
  )
}

export default ProjectHealthMetricsDetails
