import {
  faExclamationCircle,
  faCodeCommit,
  faCodeFork,
  faCodePullRequest,
  faQuestionCircle,
  faStar,
  faTag,
} from '@fortawesome/free-solid-svg-icons'
import React from 'react'
import type { HealthMetricsProps } from 'types/healthMetrics'
import { LineChart, RadialChart } from 'components/GeneralCharts'

const HealthMetricsCharts: React.FC<{ data: HealthMetricsProps[] }> = ({ data }) => {
  const openIssuesCountArray = data.map((item) => item.openIssuesCount)
  const labels = data.map((item, index) => `Day ${index + 1}`)
  return (
    <>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <LineChart
          title="Issues Health Trend"
          series={[
            {
              name: 'Open Issues',
              data: openIssuesCountArray,
            },
            {
              name: 'Unassigned Issues',
              data: data.map((item) => item.unassignedIssuesCount),
            },
          ]}
          labels={labels}
          icon={faExclamationCircle}
        />
        <LineChart
          title="Unanswered Issues Trend"
          series={[
            {
              name: 'Open Issues',
              data: openIssuesCountArray,
            },
            {
              name: 'Unanswered Issues',
              data: data.map((item) => item.unansweredIssuesCount),
            },
          ]}
          labels={labels}
          icon={faQuestionCircle}
        />
      </div>
      <LineChart
        title="Activity Trend"
        series={[
          {
            name: 'Open Pull Requests',
            data: data.map((item) => item.openPullRequestsCount),
          },
        ]}
        labels={labels}
        icon={faCodePullRequest}
      />
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
        <RadialChart
          title="Days Since Last Commit"
          icon={faCodeCommit}
          series={data.map((item) => item.lastCommitDays)}
          labels={labels}
        />
        <RadialChart
          title="Days Since Last Release"
          icon={faTag}
          series={data.map((item) => item.lastReleaseDays)}
          labels={labels}
        />
      </div>
    </>
  )
}

export default HealthMetricsCharts
