import dynamic from 'next/dynamic'
import { useTheme } from 'next-themes'
import React, { useMemo } from 'react'

const Chart = dynamic(() => import('react-apexcharts'), {
  ssr: false,
})

interface ContributionHeatmapProps {
  contributionData: Record<string, number>
  startDate: string
  endDate: string
  title?: string
  unit?: string
}

const ContributionHeatmap: React.FC<ContributionHeatmapProps> = ({
  contributionData,
  startDate,
  endDate,
  title,
  unit = 'contribution',
}) => {
  const { theme } = useTheme()
  const isDarkMode = theme === 'dark'

  const heatmapSeries = useMemo(() => {
    const start = new Date(startDate)
    const end = new Date(endDate)
    const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    // Initialize series for each day of week
    const series = dayNames.map((day) => ({
      name: day,
      data: [] as Array<{ x: string; y: number; date: string }>,
    }))

    // Find the first Monday before or on start date
    const firstDay = new Date(start)
    const daysToMonday = (firstDay.getDay() + 6) % 7
    firstDay.setDate(firstDay.getDate() - daysToMonday)

    const currentDate = new Date(firstDay)
    let weekNumber = 1

    while (currentDate <= end) {
      const dayOfWeek = currentDate.getDay()
      // Convert Sunday=0 to Sunday=6, Monday=1 to Monday=0, etc.
      const adjustedDayIndex = dayOfWeek === 0 ? 6 : dayOfWeek - 1
      // Format date in local time to avoid timezone shift
      const year = currentDate.getFullYear()
      const month = String(currentDate.getMonth() + 1).padStart(2, '0')
      const day = String(currentDate.getDate()).padStart(2, '0')
      const dateStr = `${year}-${month}-${day}`
      const weekLabel = `W${weekNumber}`

      // Only count contributions within the actual range
      const isInRange = currentDate >= start && currentDate <= end
      const contributionCount = isInRange ? contributionData[dateStr] || 0 : 0

      series[adjustedDayIndex].data.push({
        x: weekLabel,
        y: contributionCount,
        date: dateStr,
      })

      // Move to next day
      currentDate.setDate(currentDate.getDate() + 1)

      // Increment week number when we hit Monday
      if (currentDate.getDay() === 1 && currentDate <= end) {
        weekNumber++
      }
    }

    // Reverse the series so Monday is at the top and Sunday at the bottom
    return series.reverse()
  }, [contributionData, startDate, endDate])

  const options = {
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
              color: isDarkMode ? '#394d65' : '#8BA7C0',
              name: 'Low',
            },
            {
              from: 5,
              to: 8,
              color: isDarkMode ? '#314257' : '#6C8EAB',
              name: 'Medium',
            },
            {
              from: 9,
              to: 12,
              color: isDarkMode ? '#46627B' : '#5C7BA2',
              name: 'High',
            },
            {
              from: 13,
              to: 1000,
              color: isDarkMode ? '#5F87A8' : '#567498',
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
          type: 'none',
        },
      },
      active: {
        filter: {
          type: 'none',
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
      custom: ({ seriesIndex, dataPointIndex, w }) => {
        const data = w.config.series[seriesIndex].data[dataPointIndex]
        if (!data) return ''

        const count = data.y
        const date = data.date
        // Parse date as UTC to match data format
        const formattedDate = new Date(date + 'T00:00:00Z').toLocaleDateString('en-US', {
          weekday: 'short',
          month: 'short',
          day: 'numeric',
          year: 'numeric',
          timeZone: 'UTC',
        })

        const bgColor = isDarkMode ? '#1F2937' : '#FFFFFF'
        const textColor = isDarkMode ? '#F3F4F6' : '#111827'
        const secondaryColor = isDarkMode ? '#9CA3AF' : '#6B7280'

        const unitLabel = count !== 1 ? `${unit}s` : unit

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
  }

  return (
    <div>
      {title && (
        <h4 className="mb-1 text-sm text-gray-700 dark:text-gray-300">
          <span className="font-semibold">{title}</span>
        </h4>
      )}
      <div className="w-full overflow-x-auto" style={{ minWidth: '560px' }}>
        <style>
          {`
            .apexcharts-tooltip {
              background: ${isDarkMode ? '#1F2937' : '#FFFFFF'} !important;
              border: 1px solid ${isDarkMode ? '#374151' : '#E5E7EB'} !important;
              box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.3), 0 4px 6px -4px rgb(0 0 0 / 0.2) !important;
            }
            .apexcharts-tooltip * {
              border: none !important;
            }
          `}
        </style>
        <Chart options={options} series={heatmapSeries} type="heatmap" height={150} />
      </div>
    </div>
  )
}

export default ContributionHeatmap
