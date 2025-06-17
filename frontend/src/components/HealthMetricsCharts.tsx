import React from 'react'
import type { HealthMetricsProps } from 'types/healthMetrics'
import GeneralChart from 'components/GeneralChart'

const HealthMetricsCharts: React.FC<{ data: HealthMetricsProps[] }> = ({ data }) => {
  const openIssuesCountArray = data.map((item) => item.openIssuesCount)
  const xAxisArray = data.map((item, index) => (data.length - index).toString())
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      <GeneralChart
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
        xAxis={xAxisArray}
      />
      <GeneralChart
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
        xAxis={xAxisArray}
      />
    </div>
  )
}

export default HealthMetricsCharts
