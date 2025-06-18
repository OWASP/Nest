import { IconProp } from '@fortawesome/fontawesome-svg-core'
import dynamic from 'next/dynamic'
import React from 'react'
import type { ApexChartLabelSeries } from 'types/healthMetrics'
import SecondaryCard from 'components/SecondaryCard'

// Importing Chart dynamically to avoid SSR issues with ApexCharts
const Chart = dynamic(() => import('react-apexcharts'), {
  ssr: false,
})

const LineChart: React.FC<{
  title: string
  series: ApexChartLabelSeries[]
  labels?: string[]
  icon?: IconProp
}> = ({ title, series, labels, icon }) => {
  return (
    <SecondaryCard title={title} icon={icon}>
      <Chart
        options={{
          xaxis: {
            categories: labels,
          },
        }}
        series={series}
        height={450}
      />
    </SecondaryCard>
  )
}

const RadialChart: React.FC<{
  title: string
  icon?: IconProp
  labels: string[]
  series: number[]
}> = ({ title, series, icon, labels }) => {
  return (
    <SecondaryCard title={title} icon={icon}>
      <Chart
        options={{
          labels: labels,
          plotOptions: {
            radialBar: {
              dataLabels: {
                show: true,
                total: {
                  show: true,
                  label: 'Total',
                },
              },
            },
          },
        }}
        series={series}
        height={450}
        type="radialBar"
      />
    </SecondaryCard>
  )
}

export { RadialChart, LineChart }
