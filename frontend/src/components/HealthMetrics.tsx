import React from 'react'
import { FaExclamationCircle } from 'react-icons/fa'
import { FaCodeCommit, FaCodeFork, FaCodePullRequest, FaStar } from 'react-icons/fa6'
import type { HealthMetricsProps } from 'types/healthMetrics'
import BarChart from 'components/BarChart'
import LineChart from 'components/LineChart'

const HealthMetrics: React.FC<{ data: HealthMetricsProps[] }> = ({ data }) => {
  const chronological = [...data].reverse()
  const openIssuesCountArray = chronological.map((item) => item.openIssuesCount)
  const labels = chronological.map((item) => {
    return new Date(item.createdAt).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    })
  })
  const length = chronological.length
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
              data: chronological.map((item) => item.unassignedIssuesCount),
            },
            {
              name: 'Unanswered Issues',
              data: chronological.map((item) => item.unansweredIssuesCount),
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
              data: chronological.map((item) => item.openPullRequestsCount),
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
              data: chronological.map((item) => item.starsCount),
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
              data: chronological.map((item) => item.forksCount),
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
        days={[
          chronological[length - 1]?.lastCommitDays ?? 0,
          chronological[length - 1]?.lastReleaseDays ?? 0,
        ]}
        requirements={[
          chronological[length - 1]?.lastCommitDaysRequirement ?? 0,
          chronological[length - 1]?.lastReleaseDaysRequirement ?? 0,
        ]}
      />
    </>
  )
}

export default HealthMetrics
