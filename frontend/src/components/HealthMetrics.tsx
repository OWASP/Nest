import {
  faExclamationCircle,
  faCodeCommit,
  faCodeFork,
  faCodePullRequest,
  faHeart,
  faStar,
  faTag,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import React from 'react'
import type { HealthMetricsProps } from 'types/healthMetrics'
import GradientRadialChart from 'components/GradientRadialChart'
import LineChart from 'components/LineChart'

const HealthMetrics: React.FC<{ data: HealthMetricsProps[] }> = ({ data }) => {
  const openIssuesCountArray = data.map((item) => item.openIssuesCount)
  const labels = data.map((item, index) => `Day ${index + 1}`)
  return (
    <>
      <div className="relative mt-4 flex w-full items-center">
        <div className="flex-grow border-t border-gray-300"></div>
        <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-700 dark:text-gray-200">
          <FontAwesomeIcon icon={faHeart} />
          Health Metrics
        </h3>
        <div className="flex-grow border-t border-gray-300"></div>
      </div>
      <h4 className="mb-4 text-center text-lg font-semibold text-gray-700 dark:text-gray-200">
        Score: {data[0].score}
      </h4>
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
          days={data[0]?.lastCommitDays ?? 0}
          requirement={data[0]?.lastCommitDaysRequirement ?? 0}
        />
        <GradientRadialChart
          title="Days Since Last Release"
          icon={faTag}
          days={data[0]?.lastReleaseDays ?? 0}
          requirement={data[0]?.lastReleaseDaysRequirement ?? 0}
        />
      </div>
    </>
  )
}

export default HealthMetrics
