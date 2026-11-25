import dynamic from 'next/dynamic'
import { useTheme } from 'next-themes'
import React from 'react'
import type { IconType } from 'react-icons'
import { ApexBarChartDataSeries } from 'types/healthMetrics'
import { toApexTooltipTheme } from 'utils/toApexTooltipTheme'
import AnchorTitle from 'components/AnchorTitle'
import SecondaryCard from 'components/SecondaryCard'

// Importing Chart dynamically to avoid SSR issues with ApexCharts
const Chart = dynamic(() => import('react-apexcharts'), {
  ssr: false,
})

// Shown instead of a day count when the underlying date is missing (e.g. no release yet).
const NOT_AVAILABLE_LABEL = 'N/A'

const BarChart: React.FC<{
  title: string
  icon?: IconType
  labels: string[]
  // `null` means the date is missing and the bar is labeled N/A.
  days: Array<number | null>
  requirements: number[]
  reverseColors?: boolean[]
}> = ({ title, days, icon, requirements, labels, reverseColors }) => {
  const { theme, resolvedTheme } = useTheme()
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
    y: day,
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
            theme: toApexTooltipTheme(resolvedTheme),
            y: {
              // Also called with the requirement, which is never null.
              formatter: (val: number | null): string =>
                val === null ? NOT_AVAILABLE_LABEL : String(val),
            },
          },
          dataLabels: {
            formatter: (
              val: string | number | number[] | null,
              opts?: { dataPointIndex?: number }
            ): string => {
              const idx = opts?.dataPointIndex ?? 0
              const requirement = requirements[idx]
              const displayVal: string | number =
                (Array.isArray(val) ? val[0] : val) ?? NOT_AVAILABLE_LABEL
              if (requirement !== undefined) {
                return `${displayVal} / ${requirement}`
              }
              return String(displayVal)
            },
            style: {
              // N/A has no bar behind it, so white would be unreadable in light mode.
              colors: [
                ({ dataPointIndex }: { dataPointIndex: number }): string =>
                  days[dataPointIndex] === null ? themeColor : '#fff',
              ],
            },
          },
          colors: [
            function ({ value, dataPointIndex }: { value: number; dataPointIndex: number }) {
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
          yaxis: {
            // ApexCharts leaves a missing day's requirement out of the axis range.
            max: (max: number): number => Math.max(max, ...requirements),
          },
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
