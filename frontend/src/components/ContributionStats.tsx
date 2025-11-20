import {
  faChartLine,
  faCode,
  faCodeBranch,
  faCodeMerge,
  faExclamationCircle,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

interface ContributionStatsData {
  commits?: number
  pullRequests?: number
  issues?: number
  total?: number
}

interface ContributionStatsProps {
  readonly title: string
  readonly stats?: ContributionStatsData
}

export default function ContributionStats({ title, stats }: Readonly<ContributionStatsProps>) {
  const formatNumber = (value?: number) => {
    return typeof value === 'number' ? value.toLocaleString() : '0'
  }

  return (
    <>
      <h2 className="mb-4 flex items-center gap-2 text-2xl font-semibold text-gray-800 dark:text-gray-200">
        <FontAwesomeIcon icon={faChartLine} className="h-6 w-6 text-gray-600 dark:text-gray-400" />
        {title}
      </h2>
      <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="flex items-center gap-2">
          <FontAwesomeIcon icon={faCode} className="h-5 w-5 text-gray-600 dark:text-gray-400" />
          <div>
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Commits</p>
            <p className="text-lg font-bold text-gray-900 dark:text-white">
              {formatNumber(stats?.commits)}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <FontAwesomeIcon
            icon={faCodeBranch}
            className="h-5 w-5 text-gray-600 dark:text-gray-400"
          />
          <div>
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">PRs</p>
            <p className="text-lg font-bold text-gray-900 dark:text-white">
              {formatNumber(stats?.pullRequests)}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <FontAwesomeIcon
            icon={faExclamationCircle}
            className="h-5 w-5 text-gray-600 dark:text-gray-400"
          />
          <div>
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Issues</p>
            <p className="text-lg font-bold text-gray-900 dark:text-white">
              {formatNumber(stats?.issues)}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <FontAwesomeIcon
            icon={faCodeMerge}
            className="h-5 w-5 text-gray-600 dark:text-gray-400"
          />
          <div>
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Total</p>
            <p className="text-lg font-bold text-gray-900 dark:text-white">
              {formatNumber(stats?.total)}
            </p>
          </div>
        </div>
      </div>
    </>
  )
}
