import clsx from 'clsx'
import Link from 'next/link'
import { FC } from 'react'
import { HealthMetricsProps } from 'types/healthMetrics'

const MetricsCard: FC<{ metric: HealthMetricsProps }> = ({ metric }) => {
  // Defensive check for date validity
  const formattedDate = metric.createdAt 
    ? new Date(metric.createdAt).toLocaleString('default', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      })
    : 'N/A'

  // Normalize score for comparison to handle undefined/null
  const score = metric.score ?? 0

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
          <p className="text-md">{metric.starsCount ?? 0}</p>
        </div>
        <div className="truncate text-center">
          <p className="text-md">{metric.forksCount ?? 0}</p>
        </div>
        <div className="truncate text-center">
          <p className="text-md">{metric.contributorsCount ?? 0}</p>
        </div>
        <div className="truncate text-center">
          <p className="text-md">{formattedDate}</p>
        </div>
        <div
          className={clsx(
            'truncate rounded border-l-1 border-l-gray-200 bg-linear-to-br from-white/20 to-transparent dark:border-l-gray-600',
            {
              'bg-green-500 text-green-900': score >= 75,
              'bg-orange-500 text-orange-900': score >= 50 && score < 75,
              'bg-red-500 text-red-900': score < 50,
            }
          )}
        >
          <p className="text-center text-xl font-semibold">{score}</p>
        </div>
      </div>
    </Link>
  )
}

export default MetricsCard