import { IconProp } from '@fortawesome/fontawesome-svg-core'
import dynamic from 'next/dynamic'
import { useTheme } from 'next-themes'
import React from 'react'
import { pluralize } from 'utils/pluralize'
import SecondaryCard from 'components/SecondaryCard'

// Importing Chart dynamically to avoid SSR issues with ApexCharts
const Chart = dynamic(() => import('react-apexcharts'), {
  ssr: false,
})

const GradientRadialChart: React.FC<{
  title: string
  icon?: IconProp
  days: number
  requirement: number
}> = ({ title, days, icon, requirement }) => {
  const { theme } = useTheme()
  let checkpoint = requirement
  let showRed = false
  const stops = [0, 100]
  const greenColor = '#0ef94e'
  const redColor = '#f94e0e' // Red color for the end of the gradient
  const orangeColor = '#f9b90e' // Orange color for the middle of the gradient
  const colorStops = [
    {
      offset: 0,
      color: greenColor,
      opacity: 1,
    },
  ]
  if (days > requirement) {
    checkpoint = days
    showRed = true
  }
  // Ensure checkpoint is at least 1 to avoid division by zero
  checkpoint = checkpoint || 1
  // Normalize days based on the checkpoint
  const normalizedDays = (days / checkpoint) * 100
  const normalizedRequirement = (requirement / checkpoint) * 100

  if (showRed) {
    const orangeStop = normalizedRequirement / 2
    stops.splice(1, 0, orangeStop, normalizedRequirement)
    colorStops.push(
      {
        offset: orangeStop,
        color: orangeColor,
        opacity: 1,
      },
      {
        offset: normalizedRequirement,
        color: redColor,
        opacity: 1,
      },
      {
        offset: 100,
        color: redColor,
        opacity: 1,
      }
    )
  }

  return (
    <SecondaryCard title={title} icon={icon}>
      <div className="relative h-[200px] w-full">
        <Chart
          key={theme}
          options={{
            chart: {
              animations: {
                enabled: true,
                speed: 1000,
              },
            },
            plotOptions: {
              radialBar: {
                startAngle: -90,
                endAngle: 90,
                dataLabels: {
                  show: true,
                  name: {
                    show: false,
                  },
                  value: {
                    formatter: () => `${days} ${pluralize(days, 'day', 'days')}`,
                    color: theme === 'dark' ? '#ececec' : '#1E1E2C',
                    fontSize: '20px',
                    show: true,
                    offsetY: 0,
                  },
                },
                track: {
                  background: theme === 'dark' ? '#1E1E2C' : '#ececec',
                  margin: 0,
                },
              },
            },
            fill: {
              type: 'gradient',
              gradient: {
                shade: theme,
                type: 'horizontal',
                shadeIntensity: 0.5,
                stops: stops,
                colorStops: colorStops,
              },
            },
          }}
          series={[requirement ? normalizedDays : 0]}
          height={300}
          type="radialBar"
        />
        <div className="pointer-events-none absolute bottom-4 left-0 right-0 flex justify-around">
          <span className="text-md leading-none text-gray-800 dark:text-white">Active</span>
          <span className="text-md leading-none text-gray-800 dark:text-white">Stale</span>
        </div>
        {requirement > 0 && (
          <div className="pointer-events-none absolute bottom-0 left-0 right-0 flex justify-center">
            <span className="text-md text-center text-gray-800 dark:text-white">
              {`Required: ${requirement} ${pluralize(requirement, 'day', 'days')}`}
            </span>
          </div>
        )}
      </div>
    </SecondaryCard>
  )
}

export default GradientRadialChart
