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
      <div className="space-y-4 rounded-lg bg-white p-4 transition-colors duration-200 hover:bg-gray-100 lg:px-8 lg:py-4 dark:bg-gray-800 dark:hover:bg-gray-700">
        <div className="flex items-center justify-between gap-3">
          <div className="flex-1 truncate">
            <p
              className={clsx(
                'text-md truncate font-semibold lg:text-xl',
                metric.projectName === '' ? 'text-gray-500' : 'text-gray-800 dark:text-gray-200'
              )}
            >
              {metric.projectName === '' ? 'No name' : metric.projectName}
            </p>
          </div>
          <div
            className={clsx(
              'flex-shrink-0 rounded px-3 py-1.5 text-center text-white lg:px-4 lg:py-2 dark:text-gray-900',
              {
                'bg-green-500': metric.score >= 75,
                'bg-orange-500': metric.score >= 50 && metric.score < 75,
                'bg-red-500': metric.score < 50,
              }
            )}
          >
            <p className="text-sm font-semibold lg:text-base">Score: {metric.score}</p>
          </div>
        </div>
        <hr className="my-4 border-0 border-t border-gray-200 dark:border-gray-600" />
        <div className="grid grid-cols-3 gap-4 md:grid-cols-4">
          <div>
            <p className="text-xs font-medium text-gray-600 lg:text-base dark:text-gray-400">
              Stars
            </p>
            <p className="text-md font-semibold text-gray-800 lg:text-xl dark:text-gray-200">
              {metric.starsCount}
            </p>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-600 lg:text-base dark:text-gray-400">
              Forks
            </p>
            <p className="text-md font-semibold text-gray-800 lg:text-xl dark:text-gray-200">
              {metric.forksCount}
            </p>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-600 lg:text-base dark:text-gray-400">
              Contributors
            </p>
            <p className="text-md font-semibold text-gray-800 lg:text-xl dark:text-gray-200">
              {metric.contributorsCount}
            </p>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-600 lg:text-base dark:text-gray-400">
              Health Checked
            </p>
            <p className="text-sm text-gray-800 lg:text-lg dark:text-gray-200">
              {new Date(metric.createdAt).toLocaleString('default', {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
              })}
            </p>
          </div>
        </div>
      </div>
    </Link>
  )
}

export default MetricsCard
