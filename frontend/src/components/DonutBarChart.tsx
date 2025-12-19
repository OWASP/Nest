import dynamic from 'next/dynamic'
import { useTheme } from 'next-themes'
import React from 'react'
import type { IconType } from 'react-icons'
import { round } from 'utils/round'
import AnchorTitle from 'components/AnchorTitle'
import SecondaryCard from 'components/SecondaryCard'

// Importing Chart dynamically to avoid SSR issues with ApexCharts
const Chart = dynamic(() => import('react-apexcharts'), {
  ssr: false,
})

const DonutBarChart: React.FC<{
  icon: IconType
  title: string
  series: number[]
}> = ({ icon, title, series }) => {
  const { theme } = useTheme()
  const greenColor = '#0ef94e'
  const redColor = '#f94e0e'
  const orangeColor = '#f9b90e'

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
            },
            stroke: {
              show: false,
            },
            colors: [greenColor, orangeColor, redColor],
            labels: ['Healthy', 'Need Attention', 'Unhealthy'],
          }}
          series={series.map((value) => round(value, 1))}
          height={250}
          type="donut"
        />
      </div>
    </SecondaryCard>
  )
}

export default DonutBarChart
