'use client'

import clsx from 'clsx'
import Link from 'next/link'
import { FC } from 'react'
import { IconType } from 'react-icons'
import SecondaryCard from 'components/SecondaryCard'

const ProjectTypeDashboardCard: FC<{
  type: 'healthy' | 'needsAttention' | 'unhealthy'
  count: number
  icon: IconType
}> = ({ type, count, icon }) => {
  const titleMapping = {
    healthy: 'Healthy',
    needsAttention: 'Need Attention',
    unhealthy: 'Unhealthy',
  }

  return (
    <Link href={'/projects/dashboard/metrics?health=' + type} className="group">
      <SecondaryCard
        title={titleMapping[type]}
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
    </Link>
  )
}

export default ProjectTypeDashboardCard
