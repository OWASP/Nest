import clsx from 'clsx'
import Link from 'next/link'
import { FC } from 'react'
import { HealthMetricsProps } from 'types/healthMetrics'
const MetricsCard: FC<{ metric: HealthMetricsProps }> = ({ metric }) => {
  return (
    <Link
      href={`/projects/dashboard/metrics/${metric.projectKey}`}
      className="text-gray-800 no-underline dark:text-gray-200"
    >
      <div className="grid grid-cols-[4fr_1fr_1fr_1fr_1.5fr_1fr] rounded-lg bg-white p-4 transition-colors duration-200 hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700">
        <div className="truncate">
          <p
            className={clsx(
              'text-md font-semibold',
              metric.projectName === '' ? 'text-gray-500' : 'text-gray-800 dark:text-gray-200'
            )}
          >
            {metric.projectName === '' ? 'No name' : metric.projectName}
          </p>
        </div>
        <div className="truncate text-center">
          <p className="text-md">{metric.starsCount}</p>
        </div>
        <div className="truncate text-center">
          <p className="text-md">{metric.forksCount}</p>
        </div>
        <div className="truncate text-center">
          <p className="text-md">{metric.contributorsCount}</p>
        </div>
        <div className="truncate text-center">
          <p className="text-md">
            {new Date(metric.createdAt).toLocaleString('default', {
              month: 'short',
              day: 'numeric',
              year: 'numeric',
            })}
          </p>
        </div>
        <div
          className={clsx(
            'truncate rounded border-l-1 border-l-gray-200 bg-linear-to-br from-white/20 to-transparent dark:border-l-gray-600',
            {
              'bg-green-500 text-green-900': metric.score >= 75,
              'bg-orange-500 text-orange-900': metric.score >= 50 && metric.score < 75,
              'bg-red-500 text-red-900': metric.score < 50,
            }
          )}
        >
          <p className="text-center text-xl font-semibold">{metric.score}</p>
        </div>
      </div>
    </Link>
  )
}

export default MetricsCard
