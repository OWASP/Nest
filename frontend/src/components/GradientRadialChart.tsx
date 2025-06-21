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
  days: number
  requirement: number
}> = ({ title, days, icon, requirement }) => {
  const { theme } = useTheme()
  let checkpoint = days > requirement ? days : requirement
  if (checkpoint === 0) {
    checkpoint = 1 // Avoid division by zero
  }
  // Normalize days and requirement based on the checkpoint
  const normalizedDays = (days / checkpoint) * 100

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
                  formatter: () => `${days} days`,
                  color: theme === 'dark' ? '#ececec' : '#1E1E2C',
                  fontSize: '24px',
                  show: true,
                },
              },
              track: {
                background: theme === 'dark' ? '#1E1E2C' : '#ececec',
              },
            },
          },
          fill: {
            type: 'image',
            image: {
              src: ['/img/gradient.png'],
            },
          },
        }}
        series={[normalizedDays]}
        height={400}
        type="radialBar"
      />
    </SecondaryCard>
  )
}

export default GradientRadialChart
