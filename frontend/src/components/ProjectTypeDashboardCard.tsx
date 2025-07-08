'use client'

import { IconProp } from '@fortawesome/fontawesome-svg-core'
import clsx from 'clsx'
import { FC } from 'react'
import SecondaryCard from 'components/SecondaryCard'

const ProjectTypeDashboardCard: FC<{
  type: string
  count: number
  icon: IconProp
}> = ({ type, count, icon }) => {
  let title = 'Healthy Projects'
  const baseClassNames = 'transition-colors duration-300'
  if (type === 'unhealthy') {
    title = 'Unhealthy Projects'
  } else if (type === 'needsAttention') {
    title = 'Projects Needing Attention'
  }

  return (
    <SecondaryCard
      title={title}
      icon={icon}
      className={clsx(baseClassNames, {
        'bg-green-100 text-green-800 hover:bg-green-200 dark:bg-green-800 dark:text-green-400 dark:hover:bg-green-700':
          type === 'healthy',
        'bg-red-100 text-red-800 hover:bg-red-200 dark:bg-red-800 dark:text-red-400 dark:hover:bg-red-700':
          type === 'unhealthy',
        'bg-yellow-100 text-yellow-800 hover:bg-yellow-200 dark:bg-yellow-800 dark:text-yellow-400 dark:hover:bg-yellow-700':
          type === 'needsAttention',
      })}
    >
      <p className="text-3xl font-bold">{count}</p>
    </SecondaryCard>
  )
}

export default ProjectTypeDashboardCard
