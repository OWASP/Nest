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
  series: number[]
  requirements: number[]
}> = ({ title, series, icon, labels, requirements }) => {
  const { theme } = useTheme()
  const colors = series.map((days, index) => {
    if (days < requirements[index]) return '#00E396' // Green

    return '#FF4560' // Red
  })
  return (
    <SecondaryCard title={title} icon={icon}>
      <Chart
        key={theme}
        options={{
          labels: labels,
          colors: colors,
          plotOptions: {
            radialBar: {
              dataLabels: {
                show: true,
                value: {
                  formatter: (val) => {
                    return `${val} days`
                  },
                  color: theme === 'dark' ? '#fff' : '#000',
                  fontSize: '16px',
                },
              },
              track: {
                background: theme === 'dark' ? '#1E1E2C' : '#ececec',
                strokeWidth: '97%',
              },
            },
          },
          fill: {
            type: 'gradient',
            gradient: {
              shade: 'dark',
              type: 'horizontal',
              shadeIntensity: 0.5,
              gradientToColors: colors,
              inverseColors: true,
              opacityFrom: 1,
              opacityTo: 1,
              stops: [0, 100],
            },
          },
        }}
        series={series}
        height={450}
        type="radialBar"
      />
    </SecondaryCard>
  )
}

export default GradientRadialChart
