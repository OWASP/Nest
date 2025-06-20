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

const HealthMetricsCharts: React.FC<{ data: HealthMetricsProps[] }> = ({ data }) => {
  const openIssuesCountArray = data.map((item) => item.openIssuesCount)
  const labels = data.map((item, index) => `Day ${index + 1}`)
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
          series={[data.map((item) => item.lastCommitDays)[0]]}
          requirements={[data.map((item) => item.lastCommitDaysRequirement)[0]]}
          labels={['Last Commit Days']}
        />
        <GradientRadialChart
          title="Days Since Last Release"
          icon={faTag}
          series={[data.map((item) => item.lastReleaseDays)[0]]}
          requirements={[data.map((item) => item.lastReleaseDaysRequirement)[0]]}
          labels={['Last Release Days']}
        />
      </div>
    </>
  )
}

export default HealthMetricsCharts
