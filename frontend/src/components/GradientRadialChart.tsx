import { IconProp } from '@fortawesome/fontawesome-svg-core'
import dynamic from 'next/dynamic'
import { useTheme } from 'next-themes'
import React from 'react'
import SecondaryCard from 'components/SecondaryCard'

// Importing Chart dynamically to avoid SSR issues with ApexCharts
const Chart = dynamic(() => import('react-apexcharts'), {
  ssr: false,
})

const GradientRadialChart: React.FC<{
  title: string
  icon?: IconProp
  labels: string[]
  days: number
  requirement: number
}> = ({ title, days, icon, labels, requirement }) => {
  const { theme } = useTheme()
  const redColor = '#FF4560'
  const greenColor = '#00E396'

  let checkpoint = requirement
  if (days > requirement) {
    checkpoint = days
  }
  const normalizedDays = (days / checkpoint) * 100
  const normalizedRequirement = (requirement / checkpoint) * 100

  const showRed = days > requirement
  const colorStops = [
    {
      offset: 0,
      color: greenColor,
      opacity: 1,
    },
  ]
  const stops = [0, 100]

  if (showRed) {
    stops[0] = normalizedRequirement
    colorStops.push({
      offset: normalizedRequirement,
      color: redColor,
      opacity: 1,
    })
  }

  return (
    <SecondaryCard title={title} icon={icon}>
      <Chart
        key={theme}
        options={{
          chart: {
            animations: {
              enabled: true,
              speed: 1000,
            },
          },
          labels: labels,
          plotOptions: {
            radialBar: {
              startAngle: -90,
              endAngle: 90,
              dataLabels: {
                show: true,
                value: {
                  formatter: () => {
                    return `${days} days`
                  },
                  color: theme === 'dark' ? '#fff' : '#000',
                  fontSize: '16px',
                },
              },
              track: {
                background: theme === 'dark' ? '#1E1E2C' : '#ececec',
              },
            },
          },
          fill: {
            type: 'gradient',
            gradient: {
              shade: 'dark',
              type: 'horizontal',
              shadeIntensity: 0.5,
              gradientToColors: [redColor],
              stops: stops,
              colorStops: colorStops,
            },
          },
        }}
        series={[normalizedDays]}
        height={450}
        type="radialBar"
      />
    </SecondaryCard>
  )
}

export default GradientRadialChart
