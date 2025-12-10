import dynamic from 'next/dynamic'
import { useTheme } from 'next-themes'
import React from 'react'
import { IconType } from 'react-icons'
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
  icon?: IconType
  round?: boolean
}> = ({ title, series, labels, icon, round }) => {
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
                if (value >= 1000) {
                  return `${(value / 1000).toFixed(1)}K`
                }
                return `${value.toFixed(round ? 0 : 2)}`
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
