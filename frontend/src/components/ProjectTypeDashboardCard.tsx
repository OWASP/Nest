'use client'

import { IconProp } from '@fortawesome/fontawesome-svg-core'
import { FC } from 'react'
import SecondaryCard from 'components/SecondaryCard'

const ProjectTypeDashboardCard: FC<{
  type: string
  color: string
  count: number
  icon: IconProp
}> = ({ type, count, icon, color }) => {
  let title = 'Healthy Projects'
  if (type === 'unhealthy') {
    title = 'Unhealthy Projects'
  } else if (type === 'needsAttention') {
    title = 'Projects Needing Attention'
  }

  return (
    <SecondaryCard
      title={title}
      icon={icon}
      className={`transition-colors duration-300 hover:bg-${color}-200 dark:bg-${color}-800 dark:text-${color}-400 dark:hover:bg-${color}-700 text-${color}-800 bg-${color}-100 hover:text-${color}-800 overflow-hidden`}
    >
      <p className="text-2xl font-bold md:text-3xl">{count}</p>
    </SecondaryCard>
  )
}

export default ProjectTypeDashboardCard
