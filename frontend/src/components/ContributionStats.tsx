import { FaChartLine, FaCode, FaCodeBranch, FaExclamationCircle } from 'react-icons/fa'
import type { ContributionStats as ContributionStatsType } from 'utils/contributionDataUtils'

interface ContributionStatsProps {
  readonly title: string
  readonly stats?: ContributionStatsType
}

export default function ContributionStats({ title, stats }: Readonly<ContributionStatsProps>) {
  const formatNumber = (value?: number) => {
    return typeof value === 'number' ? value.toLocaleString() : '0'
  }

  return (
    <div role="region" className="">
      <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-gray-800 sm:text-xl md:text-2xl dark:text-gray-200">
        <FaChartLine className="h-5 w-5 text-gray-600 sm:h-6 sm:w-6 dark:text-gray-400" />
        {title}
      </h2>
      <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="flex items-center gap-2">
          <FaCode className="h-5 w-5 text-gray-600 dark:text-gray-400" />
          <div>
            <p className="text-xs font-medium text-gray-500 sm:text-sm dark:text-gray-400">
              Commits
            </p>
            <p className="text-base font-bold text-gray-900 sm:text-lg dark:text-white">
              {formatNumber(stats?.commits)}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <FaCodeBranch className="h-5 w-5 text-gray-600 dark:text-gray-400" />
          <div>
            <p className="text-xs font-medium text-gray-500 sm:text-sm dark:text-gray-400">PRs</p>
            <p className="text-base font-bold text-gray-900 sm:text-lg dark:text-white">
              {formatNumber(stats?.pullRequests)}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <FaExclamationCircle className="h-5 w-5 text-gray-600 dark:text-gray-400" />
          <div>
            <p className="text-xs font-medium text-gray-500 sm:text-sm dark:text-gray-400">
              Issues
            </p>
            <p className="text-base font-bold text-gray-900 sm:text-lg dark:text-white">
              {formatNumber(stats?.issues)}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <FaCodeBranch className="h-5 w-5 text-gray-600 dark:text-gray-400" />
          <div>
            <p className="text-xs font-medium text-gray-500 sm:text-sm dark:text-gray-400">Total</p>
            <p className="text-base font-bold text-gray-900 sm:text-lg dark:text-white">
              {formatNumber(stats?.total)}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
