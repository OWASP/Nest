import { IconProp } from '@fortawesome/fontawesome-svg-core'
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
  icon?: IconProp
  type: 'line' | 'radialBar'
}> = ({ title, series, xAxis, icon, type }) => {
  let plotOptions = {}
  if (type == 'radialBar') {
    plotOptions = {
      radialBar: {
        size: 150,
        hollow: {
          margin: 5,
          size: '70%',
          background: 'transparent',
        },
        track: {
          background: '#f2f2f2',
        },
        dataLabels: {
          show: true,
        },
      },
    }
  }
  return (
    <SecondaryCard title={title} icon={icon}>
      <Chart
        options={{
          plotOptions: plotOptions,
          labels: series.map((s) => s.name),
          xaxis: {
            categories: xAxis.map((dayNum) => `Day ${dayNum}`),
          },
        }}
        series={series}
        height={450}
        type={type}
      />
    </SecondaryCard>
  )
}

export default GeneralChart
