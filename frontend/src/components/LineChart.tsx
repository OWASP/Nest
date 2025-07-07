import { IconProp } from '@fortawesome/fontawesome-svg-core'
import dynamic from 'next/dynamic'
import { useTheme } from 'next-themes'
import React from 'react'
import type { ApexLineChartSeries } from 'types/healthMetrics'
import AnchorTitle from 'components/AnchorTitle'
import SecondaryCard from 'components/SecondaryCard'
// Importing Chart dynamically to avoid SSR issues with ApexCharts
const Chart = dynamic(() => import('react-apexcharts'), {
  ssr: false,
})

const LineChart: React.FC<{
  title: string
  series: ApexLineChartSeries[]
  labels?: string[]
  icon?: IconProp
}> = ({ title, series, labels, icon }) => {
  const { theme } = useTheme()
  const color = theme === 'dark' ? '#ECECEC' : '#1E1E2C'

  return (
    <SecondaryCard title={<AnchorTitle title={title} />} icon={icon}>
      <Chart
        key={theme}
        options={{
          chart: {
            toolbar: {
              show: false,
            },
            foreColor: color,
          },
          tooltip: {
            theme: theme,
          },
          xaxis: {
            categories: labels,
            tickAmount: 10,
          },
          yaxis: {
            labels: {
              formatter: (value: number) => {
                return value >= 1000 ? `${(value / 1000).toFixed(1)}K` : `${value.toFixed(0)}`
              },
            },
          },
          stroke: {
            curve: 'smooth',
          },
        }}
        series={series}
        height={200}
      />
    </SecondaryCard>
  )
}

export default LineChart
