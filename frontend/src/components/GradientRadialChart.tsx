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
  let checkpoint = days > requirement ? days : requirement
  // Ensure checkpoint is at least 1 to avoid division by zero
  checkpoint = checkpoint || 1
  // Normalize days based on the checkpoint
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
              hollow: {
                margin: 0,
              },
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
      <div className="mt-0 flex justify-around">
        <span className="text-md text-gray-800 dark:text-white md:ml-4">Active</span>
        <span className="text-md text-gray-800 dark:text-white md:mr-4">Stale</span>
      </div>
    </SecondaryCard>
  )
}

export default GradientRadialChart
