import { IconProp } from '@fortawesome/fontawesome-svg-core'
import dynamic from 'next/dynamic'
import { useTheme } from 'next-themes'
import React from 'react'
import { ApexBarChartDataSeries } from 'types/healthMetrics'
import AnchorTitle from 'components/AnchorTitle'
import SecondaryCard from 'components/SecondaryCard'

// Importing Chart dynamically to avoid SSR issues with ApexCharts
const Chart = dynamic(() => import('react-apexcharts'), {
  ssr: false,
})

const BarChart: React.FC<{
  title: string
  icon?: IconProp
  labels?: string[]
  days: number[]
  requirements: number[]
}> = ({ title, days, icon, requirements, labels }) => {
  const { theme } = useTheme()
  let themeColor = '#1E1E2C'
  let redColor = '#ff7875'
  let greenColor = '#73d13d'
  let orangeColor = '#ffbb33'
  if (theme === 'dark') {
    themeColor = '#ececec'
    redColor = '#ff4d4f'
    greenColor = '#52c41a'
    orangeColor = '#faad14'
  }

  const seriesData: ApexBarChartDataSeries[] = days.map((day, index) => ({
    x: labels[index],
    y: days[index],
    goals: [
      {
        name: 'Requirement',
        value: requirements[index],
        strokeWidth: 5,
        strokeColor: redColor,
        strokeHeight: 15,
        strokeLineCap: 'round',
      },
    ],
  }))
  return (
    <SecondaryCard title={<AnchorTitle title={title} />} icon={icon}>
      <Chart
        key={theme}
        options={{
          chart: {
            animations: {
              enabled: true,
              speed: 1000,
            },
            toolbar: {
              show: false,
            },
            foreColor: themeColor,
          },
          plotOptions: {
            bar: {
              horizontal: true,
              columnWidth: '70%',
            },
          },
          tooltip: {
            theme: theme,
          },
          dataLabels: {
            formatter: (val: number, opts) => {
              const goal = opts.w.config.series[opts.seriesIndex].data[opts.dataPointIndex].goals[0]
              if (goal) {
                return `${val} / ${goal.value}`
              }
              return val.toString()
            },
          },
          colors: [
            function ({ value, seriesIndex, _ }) {
              const requirement = requirements[seriesIndex]
              if (value > requirement) {
                return redColor
              } else if (value > requirement * 0.8) {
                return orangeColor
              }
              return greenColor
            },
          ],
          legend: {
            show: true,
            showForSingleSeries: true,
            customLegendItems: ['Actual', 'Requirement'],
            markers: {
              fillColors: [greenColor, redColor],
            },
          },
        }}
        series={[
          {
            name: 'Actual',
            data: seriesData,
          },
        ]}
        height={300}
        type="bar"
      />
    </SecondaryCard>
  )
}

export default BarChart
