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
      <div className="hidden grid-cols-[4fr_1fr_1fr_1fr_1.5fr_1fr] rounded-lg bg-white p-4 transition-colors duration-200 hover:bg-gray-100 sm:grid dark:bg-gray-800 dark:hover:bg-gray-700">
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
      {/* Mobile Screen Layout */}
      <div className="space-y-4 rounded-lg bg-white p-4 transition-colors duration-200 hover:bg-gray-100 sm:hidden dark:bg-gray-800 dark:hover:bg-gray-700">
        <div className="flex items-center justify-between gap-3">
          <div className="flex-1 truncate">
            <p
              className={clsx(
                'text-md truncate font-semibold',
                metric.projectName === '' ? 'text-gray-500' : 'text-gray-800 dark:text-gray-200'
              )}
            >
              {metric.projectName === '' ? 'No name' : metric.projectName}
            </p>
          </div>
          <div
            className={clsx(
              'flex-shrink-0 rounded px-3 py-2 text-center text-white dark:text-gray-900',
              {
                'bg-green-500': metric.score >= 75,
                'bg-orange-500': metric.score >= 50 && metric.score < 75,
                'bg-red-500': metric.score < 50,
              }
            )}
          >
            <p className="text-sm font-semibold">Score: {metric.score}</p>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4 pt-2">
          <div>
            <p className="text-xs font-medium text-gray-600 dark:text-gray-400">Stars</p>
            <p className="text-md font-semibold text-gray-800 dark:text-gray-200">
              {metric.starsCount}
            </p>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-600 dark:text-gray-400">Forks</p>
            <p className="text-md font-semibold text-gray-800 dark:text-gray-200">
              {metric.forksCount}
            </p>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-600 dark:text-gray-400">Contributors</p>
            <p className="text-md font-semibold text-gray-800 dark:text-gray-200">
              {metric.contributorsCount}
            </p>
          </div>
        </div>
        <div>
          <p className="text-xs font-medium text-gray-600 dark:text-gray-400">Health Checked</p>
          <p className="text-sm text-gray-800 dark:text-gray-200">
            {new Date(metric.createdAt).toLocaleString('default', {
              month: 'short',
              day: 'numeric',
              year: 'numeric',
            })}
          </p>
        </div>
      </div>
    </Link>
  )
}

export default MetricsCard
