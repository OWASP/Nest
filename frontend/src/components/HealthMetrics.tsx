import {
  faExclamationCircle,
  faCodeCommit,
  faCodeFork,
  faCodePullRequest,
  faStar,
  faTag,
} from '@fortawesome/free-solid-svg-icons'
import React from 'react'
import type { HealthMetricsProps } from 'types/healthMetrics'
import GradientRadialChart from 'components/GradientRadialChart'
import LineChart from 'components/LineChart'

const HealthMetrics: React.FC<{ data: HealthMetricsProps[] }> = ({ data }) => {
  const openIssuesCountArray = data.map((item) => item.openIssuesCount)
  const labels = data.map((item) => {
    return new Date(item.createdAt).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    })
  })
  const length = data.length
  return (
    <>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <LineChart
          title="Issues Trend"
          series={[
            {
              name: 'Open Issues',
              data: openIssuesCountArray,
            },
            {
              name: 'Unassigned Issues',
              data: data.map((item) => item.unassignedIssuesCount),
            },
            {
              name: 'Unanswered Issues',
              data: data.map((item) => item.unansweredIssuesCount),
            },
          ]}
          labels={labels}
          icon={faExclamationCircle}
        />
        <LineChart
          title="Pull Requests Trend"
          series={[
            {
              name: 'Open Pull Requests',
              data: data.map((item) => item.openPullRequestsCount),
            },
          ]}
          labels={labels}
          icon={faCodePullRequest}
        />
      </div>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <LineChart
          title="Stars Trend"
          series={[
            {
              name: 'Stars',
              data: data.map((item) => item.starsCount),
            },
          ]}
          labels={labels}
          icon={faStar}
        />
        <LineChart
          title="Forks Trend"
          series={[
            {
              name: 'Forks',
              data: data.map((item) => item.forksCount),
            },
          ]}
          labels={labels}
          icon={faCodeFork}
        />
      </div>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <GradientRadialChart
          title="Days Since Last Commit"
          icon={faCodeCommit}
          days={data[length - 1]?.lastCommitDays ?? 0}
          requirement={data[length - 1]?.lastCommitDaysRequirement ?? 0}
        />
        <GradientRadialChart
          title="Days Since Last Release"
          icon={faTag}
          days={data[length - 1]?.lastReleaseDays ?? 0}
          requirement={data[length - 1]?.lastReleaseDaysRequirement ?? 0}
        />
      </div>
    </>
  )
}

export default HealthMetrics
