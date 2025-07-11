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
  let title = 'Healthy'
  if (type === 'unhealthy') {
    title = 'Unhealthy'
  } else if (type === 'needsAttention') {
    title = 'Need Attention'
  }

  return (
    <SecondaryCard
      title={title}
      icon={icon}
      className={clsx('overflow-hidden transition-colors duration-300', {
        'bg-green-100 text-green-800 hover:bg-green-200 hover:text-green-800 dark:bg-green-800 dark:text-green-400 dark:hover:bg-green-700':
          type === 'healthy',
        'bg-red-100 text-red-800 hover:bg-red-200 hover:text-red-800 dark:bg-red-800 dark:text-red-400 dark:hover:bg-red-700':
          type === 'unhealthy',
        'bg-yellow-100 text-yellow-800 hover:bg-yellow-200 hover:text-yellow-800 dark:bg-yellow-800 dark:text-yellow-400 dark:hover:bg-yellow-700':
          type === 'needsAttention',
      })}
    >
      <p className="text-2xl font-bold md:text-3xl">{count}</p>
    </SecondaryCard>
  )
}

export default ProjectTypeDashboardCard
