import dynamic from 'next/dynamic'
import React from 'react'
import type { HealthMetricsProps } from 'types/project'

const Chart = dynamic(() => import('react-apexcharts'), {
  ssr: false,
})

const HealthMetricsCharts: React.FC<{ data: HealthMetricsProps[] }> = ({ data }) => {
  return (
    <div>
      <h2>Health Metrics Charts</h2>
      <Chart
        options={{
          chart: {
            type: 'line',
          },
          xaxis: {
            categories: ['Open Issues', 'Unassigned Issues'],
          },
        }}
        series={[
          {
            name: 'Health Metrics',
            data: [data[0].openIssuesCount, data[0].unassignedIssuesCount],
          },
        ]}
      />
    </div>
  )
}

export default HealthMetricsCharts
