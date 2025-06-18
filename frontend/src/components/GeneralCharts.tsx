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
  const colors = series.map((days) => {
    if (days < 3)
      return '#00E396' // Green
    else if (days <= 20)
      return '#FFEA00' // Yellow
    else return '#FF4560' // Red
  })
  return (
    <SecondaryCard title={title} icon={icon}>
      <Chart
        options={{
          labels: labels,
          colors: colors,
          plotOptions: {
            radialBar: {
              dataLabels: {
                show: true,
                value: {
                  formatter: (val) => {
                    return `${val} days`
                  },
                },
                name: {
                  show: true,
                },
                total: {
                  show: true,
                  label: 'Average Days',
                  color: '#FF4560',
                  formatter: (w) => {
                    const total = w.globals.series.reduce((a, b) => a + b, 0)
                    return `${(total / w.globals.series.length).toFixed(0)} days`
                  },
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
