import type { ApexTooltipCustomOpts } from 'apexcharts'
import dynamic from 'next/dynamic'
import { useTheme } from 'next-themes'
import React, { useMemo } from 'react'
import {
  buildContributionCalendar,
  type ContributionHeatmapSeries,
} from 'utils/contributionHeatmap'
import { pluralize } from 'utils/pluralize'

const Chart = dynamic(() => import('react-apexcharts'), {
  ssr: false,
})

const getChartOptions = (isDarkMode: boolean, unit: string) => ({
  chart: {
    type: 'heatmap' as const,
    toolbar: {
      show: false,
    },
    background: 'transparent',
  },
  dataLabels: {
    enabled: false,
  },
  legend: {
    show: false,
  },
  colors: ['#008FFB'],
  plotOptions: {
    heatmap: {
      colorScale: {
        ranges: [
          {
            from: 0,
            to: 0,
            color: isDarkMode ? '#2C3A4D' : '#E7E7E6',
            name: 'No activity',
          },
          {
            from: 1,
            to: 4,
            color: isDarkMode ? '#4A5F7A' : '#7BA3C0',
            name: 'Low',
          },
          {
            from: 5,
            to: 8,
            color: isDarkMode ? '#5A6F8A' : '#6C8EAB',
            name: 'Medium',
          },
          {
            from: 9,
            to: 12,
            color: isDarkMode ? '#6A7F9A' : '#5C7BA2',
            name: 'High',
          },
          {
            from: 13,
            to: 1000,
            color: isDarkMode ? '#7A8FAA' : '#567498',
            name: 'Very High',
          },
        ],
      },
      radius: 2,
      distributed: false,
      useFillColorAsStroke: false,
      enableShades: false,
    },
  },
  states: {
    hover: {
      filter: {
        type: 'none' as const,
      },
    },
    active: {
      filter: {
        type: 'none' as const,
      },
    },
  },
  stroke: {
    show: true,
    width: 2,
    colors: [isDarkMode ? '#1F2937' : '#FFFFFF'],
  },
  grid: {
    show: false,
    padding: {
      top: 0,
      right: 0,
      bottom: 0,
      left: 0,
    },
  },
  tooltip: {
    enabled: true,
    shared: false,
    intersect: true,
    followCursor: true,
    offsetY: -10,
    style: {
      fontSize: '12px',
    },
    custom: ({ seriesIndex, dataPointIndex, w }: ApexTooltipCustomOpts) => {
      const series = w.config.series as ContributionHeatmapSeries
      const data = series?.[seriesIndex]?.data?.[dataPointIndex]
      if (!data || data.y === null) return ''

      const count = data.y
      const date = data.date
      const parsedDate = new Date(date + 'T00:00:00Z')
      const formattedDate = parsedDate.toLocaleDateString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        timeZone: 'UTC',
      })

      const bgColor = isDarkMode ? '#1F2937' : '#FFFFFF'
      const textColor = isDarkMode ? '#F3F4F6' : '#111827'
      const secondaryColor = isDarkMode ? '#9CA3AF' : '#6B7280'
      const unitLabel = pluralize(count, unit)

      return `
        <div style="
          background: ${bgColor} !important;
          border: 1px solid ${isDarkMode ? '#374151' : '#E5E7EB'} !important;
          border-radius: 8px !important;
          padding: 10px 14px !important;
          box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.3), 0 4px 6px -4px rgb(0 0 0 / 0.2) !important;
        ">
          <div style="color: ${textColor} !important; font-weight: 600; margin-bottom: 4px; font-size: 14px;">${formattedDate}</div>
          <div style="color: ${secondaryColor} !important; font-size: 12px;">${count} ${unitLabel}</div>
        </div>
      `
    },
  },
  xaxis: {
    type: 'category' as const,
    labels: {
      show: false,
    },
    axisBorder: {
      show: false,
    },
    axisTicks: {
      show: false,
    },
    tooltip: {
      enabled: false,
    },
  },
  yaxis: {
    labels: {
      show: false,
    },
    axisBorder: {
      show: false,
    },
    axisTicks: {
      show: false,
    },
    tooltip: {
      enabled: false,
    },
  },
})

interface ContributionHeatmapProps {
  contributionData: Record<string, number>
  startDate: string
  endDate: string
  title?: string
  unit?: string
  variant?: 'default' | 'medium' | 'compact'
}

const ContributionHeatmap: React.FC<ContributionHeatmapProps> = ({
  contributionData,
  startDate,
  endDate,
  title,
  unit = 'contribution',
  variant = 'default',
}) => {
  const { theme } = useTheme()
  const isDarkMode = theme === 'dark'

  const { heatmapSeries, weeksCount } = useMemo(
    () => buildContributionCalendar(startDate, endDate, contributionData, new Date()),
    [contributionData, startDate, endDate]
  )

  const options = useMemo(() => getChartOptions(isDarkMode, unit), [isDarkMode, unit])

  const calculateChartWidth = useMemo(() => {
    if (variant === 'compact') {
      const pixelPerWeek = 13.4
      const padding = 40
      const calculatedWidth = weeksCount * pixelPerWeek + padding
      return Math.max(400, calculatedWidth)
    }

    if (variant === 'medium') {
      const pixelPerWeek = 16
      const padding = 45
      const calculatedWidth = weeksCount * pixelPerWeek + padding
      return Math.max(500, calculatedWidth)
    }

    const pixelPerWeek = 19.5
    const padding = 50
    const calculatedWidth = weeksCount * pixelPerWeek + padding
    return Math.max(600, calculatedWidth)
  }, [weeksCount, variant])

  const chartWidth = calculateChartWidth

  const getChartHeight = () => {
    if (variant === 'compact') return 150
    if (variant === 'medium') return 172
    return 195
  }

  return (
    <div className="contribution-heatmap w-full">
      {title && (
        <h3 className="mb-4 text-sm font-semibold text-gray-800 dark:text-gray-200">{title}</h3>
      )}

      {/* scroll wrapper for small screens */}
      <div className="scrollbar-default w-full overflow-x-auto overflow-y-hidden">
        <style>
          {`
            /* ApexCharts omits the value attribute for null padding cells. */
            .contribution-heatmap .apexcharts-heatmap-rect:not([val]) {
              visibility: hidden;
              pointer-events: none;
            }
            .apexcharts-tooltip {
              background: ${isDarkMode ? '#1F2937' : '#FFFFFF'} !important;
              border: 1px solid ${isDarkMode ? '#374151' : '#E5E7EB'} !important;
              box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.3), 0 4px 6px -4px rgb(0 0 0 / 0.2) !important;
            }
            .apexcharts-tooltip * {
              border: none !important;
            }
            .scrollbar-default {
              scrollbar-width: thin;
            }

          `}
        </style>

        <div className="inline-block">
          <Chart
            height={getChartHeight()}
            options={options}
            series={heatmapSeries}
            type="heatmap"
            width={chartWidth}
          />
        </div>
      </div>
    </div>
  )
}

export default ContributionHeatmap
