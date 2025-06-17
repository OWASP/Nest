import dynamic from 'next/dynamic'
import React from 'react'
import type { ApexChartSeries } from 'types/healthMetrics'
import SecondaryCard from 'components/SecondaryCard'

// Importing Chart dynamically to avoid SSR issues with ApexCharts
const Chart = dynamic(() => import('react-apexcharts'), {
  ssr: false,
})

const GeneralChart: React.FC<{
  title: string
  series: ApexChartSeries[]
  xAxis?: string[]
}> = ({ title, series, xAxis }) => {
  return (
    <SecondaryCard title={title}>
      <Chart
        options={{
          chart: {
            type: 'line',
          },
          xaxis: {
            categories: xAxis.map((dayNum) => `Day ${dayNum}`),
          },
        }}
        series={series}
        height={450}
      />
    </SecondaryCard>
  )
}

export default GeneralChart
