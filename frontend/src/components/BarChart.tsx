import dynamic from 'next/dynamic'
import { useTheme } from 'next-themes'
import React from 'react'
import type { IconType } from 'react-icons'
import { ApexBarChartDataSeries } from 'types/healthMetrics'
import AnchorTitle from 'components/AnchorTitle'
import SecondaryCard from 'components/SecondaryCard'

// Importing Chart dynamically to avoid SSR issues with ApexCharts
const Chart = dynamic(() => import('react-apexcharts'), {
  ssr: false,
})

const BarChart: React.FC<{
  title: string
  icon?: IconType
  labels: string[]
  days: number[]
  requirements: number[]
  reverseColors?: boolean[]
}> = ({ title, days, icon, requirements, labels, reverseColors }) => {
  const { theme } = useTheme()
  let themeColor = '#1E1E2C'
  let redColor = '#FF7875'
  let greenColor = '#73D13D'
  let orangeColor = '#FFBB33'
  if (theme === 'dark') {
    themeColor = '#ECECEC'
    redColor = '#FF4D4F'
    greenColor = '#52C41A'
    orangeColor = '#FAAD14'
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
            formatter: (
              val: string | number | number[],
              opts?: { dataPointIndex?: number }
            ): string => {
              const idx = opts?.dataPointIndex ?? 0
              const requirement = requirements[idx]
              if (requirement !== undefined) {
                const displayVal = typeof val === 'number' ? val : Array.isArray(val) ? val[0] : val
                return `${displayVal} / ${requirement}`
              }
              return typeof val === 'number'
                ? String(val)
                : Array.isArray(val)
                  ? String(val[0])
                  : String(val)
            },
          },
          colors: [
            function ({
              value,
              dataPointIndex,
              _,
            }: {
              value: number
              dataPointIndex: number
              _: unknown
            }) {
              const requirement = requirements[dataPointIndex]
              if (reverseColors?.[dataPointIndex]) {
                if (value < requirement * 0.75) {
                  return orangeColor
                } else if (value < requirement) {
                  return redColor
                }
                return greenColor
              }
              if (value > requirement) {
                return redColor
              } else if (value > requirement * 0.75) {
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
