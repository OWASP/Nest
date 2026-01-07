import React from 'react'
import { FaExclamationCircle } from 'react-icons/fa'
import { FaCodeCommit, FaCodeFork, FaCodePullRequest, FaStar } from 'react-icons/fa6'
import type { HealthMetricsProps } from 'types/healthMetrics'
import BarChart from 'components/BarChart'
import LineChart from 'components/LineChart'

const HealthMetrics: React.FC<{ data: HealthMetricsProps[] }> = ({ data }) => {
  const openIssuesCountArray = data.map((item) => item.openIssuesCount ?? 0)
  const labels = data.map((item) => {
    return new Date(item.createdAt || '').toLocaleDateString('en-US', {
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
          round={true}
          series={[
            {
              name: 'Open Issues',
              data: openIssuesCountArray,
            },
            {
              name: 'Unassigned Issues',
              data: data.map((item) => item.unassignedIssuesCount ?? 0),
            },
            {
              name: 'Unanswered Issues',
              data: data.map((item) => item.unansweredIssuesCount ?? 0),
            },
          ]}
          labels={labels}
          icon={FaExclamationCircle}
        />
        <LineChart
          title="Pull Requests Trend"
          round={true}
          series={[
            {
              name: 'Open Pull Requests',
              data: data.map((item) => item.openPullRequestsCount ?? 0),
            },
          ]}
          labels={labels}
          icon={FaCodePullRequest}
        />
      </div>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <LineChart
          title="Stars Trend"
          round={true}
          series={[
            {
              name: 'Stars',
              data: data.map((item) => item.starsCount ?? 0),
            },
          ]}
          labels={labels}
          icon={FaStar}
        />
        <LineChart
          title="Forks Trend"
          round={true}
          series={[
            {
              name: 'Forks',
              data: data.map((item) => item.forksCount ?? 0),
            },
          ]}
          labels={labels}
          icon={FaCodeFork}
        />
      </div>

      <BarChart
        title="Days Since Last Commit and Release"
        icon={FaCodeCommit}
        labels={['Days Since Last Commit', 'Days Since Last Release']}
        days={[data[length - 1]?.lastCommitDays ?? 0, data[length - 1]?.lastReleaseDays ?? 0]}
        requirements={[
          data[length - 1]?.lastCommitDaysRequirement ?? 0,
          data[length - 1]?.lastReleaseDaysRequirement ?? 0,
        ]}
      />
    </>
  )
}

export default HealthMetrics