import { IconProp } from '@fortawesome/fontawesome-svg-core'
import dynamic from 'next/dynamic'
import { useTheme } from 'next-themes'
import React from 'react'
import { round } from 'utils/round'
import AnchorTitle from 'components/AnchorTitle'
import SecondaryCard from 'components/SecondaryCard'

// Importing Chart dynamically to avoid SSR issues with ApexCharts
const Chart = dynamic(() => import('react-apexcharts'), {
  ssr: false,
})

const DonutBarChart: React.FC<{
  title: string
  icon: IconProp
  projectsPercentageHealthy: number
  projectsPercentageNeedAttention: number
  projectsPercentageUnhealthy: number
}> = ({
  title,
  projectsPercentageHealthy,
  projectsPercentageNeedAttention,
  projectsPercentageUnhealthy,
  icon,
}) => {
  const { theme } = useTheme()
  const greenColor = '#0ef94e'
  const redColor = '#f94e0e' // Red color for the end of the gradient
  const orangeColor = '#f9b90e' // Orange color for the middle of the gradient

  return (
    <SecondaryCard title={<AnchorTitle title={title} />} icon={icon}>
      <div>
        <Chart
          key={theme}
          options={{
            chart: {
              animations: {
                enabled: true,
                speed: 1000,
              },
            },
            legend: {
              show: true,
              position: 'bottom',
              labels: {
                colors: theme === 'dark' ? '#ececec' : '#1E1E2C',
              },
              customLegendItems: [
                'Healthy Projects',
                'Projects Needing Attention',
                'Unhealthy Projects',
              ],
            },
            colors: [greenColor, orangeColor, redColor],
            labels: ['Healthy Projects', 'Projects Needing Attention', 'Unhealthy Projects'],
          }}
          series={[
            round(projectsPercentageHealthy, 1),
            round(projectsPercentageNeedAttention, 1),
            round(projectsPercentageUnhealthy, 1),
          ]}
          height={250}
          type="donut"
        />
      </div>
    </SecondaryCard>
  )
}

export default DonutBarChart
