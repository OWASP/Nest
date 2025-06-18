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
import GeneralChart from 'components/GeneralChart'

const HealthMetricsCharts: React.FC<{ data: HealthMetricsProps[] }> = ({ data }) => {
  const openIssuesCountArray = data.map((item) => item.openIssuesCount)
  const xAxisArray = data.map((item, index) => (index + 1).toString())
  return (
    <>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <GeneralChart
          title="Issues Health Trend"
          type="line"
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
          xAxis={xAxisArray}
          icon={faExclamationCircle}
        />
        <GeneralChart
          title="Unanswered Issues Trend"
          type="line"
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
          xAxis={xAxisArray}
          icon={faQuestionCircle}
        />
      </div>
      <div className="grid grid-cols-1">
        <GeneralChart
          title="Activity Trend"
          type="line"
          series={[
            {
              name: 'Open Pull Requests',
              data: data.map((item) => item.openPullRequestsCount),
            },
          ]}
          xAxis={xAxisArray}
          icon={faCodePullRequest}
        />
      </div>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <GeneralChart
          title="Stars Trend"
          type="line"
          series={[
            {
              name: 'Stars',
              data: data.map((item) => item.starsCount),
            },
          ]}
          xAxis={xAxisArray}
          icon={faStar}
        />
        <GeneralChart
          title="Forks Trend"
          type="line"
          series={[
            {
              name: 'Forks',
              data: data.map((item) => item.forksCount),
            },
          ]}
          xAxis={xAxisArray}
          icon={faCodeFork}
        />
      </div>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <GeneralChart
          title="Days Since Last Commit"
          type="radialBar"
          series={[
            {
              name: 'Last Commit Days',
              data: data.map((item) => item.lastCommitDays),
            },
          ]}
          xAxis={xAxisArray}
          icon={faCodeCommit}
        />
        <GeneralChart
          title="Days Since Last Release"
          type="radialBar"
          series={[
            {
              name: 'Last Release Days',
              data: data.map((item) => item.lastReleaseDays),
            },
          ]}
          xAxis={xAxisArray}
          icon={faTag}
        />
      </div>
    </>
  )
}

export default HealthMetricsCharts
