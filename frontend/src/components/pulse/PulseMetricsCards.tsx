import { Skeleton } from '@heroui/skeleton'
import { FaCodeBranch, FaRocket, FaUsers, FaWaveSquare } from 'react-icons/fa6'
import type { PulseMetricsCardsProps } from 'types/pulse'

export default function PulseMetricsCards({ error, loading, stats }: PulseMetricsCardsProps) {
  const renderValue = (val?: number) => {
    if (loading) {
      return <Skeleton className="my-1 h-7 w-20 rounded-lg" />
    }
    if (error || val === undefined || val === null) {
      return <span className="text-gray-400 dark:text-gray-500">N/A</span>
    }
    return val.toLocaleString()
  }

  return (
    <div className="mb-3 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
      <div className="flex items-center gap-4 rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border border-blue-500/30 bg-blue-500/10 text-blue-500 dark:text-blue-400">
          <FaWaveSquare className="h-5 w-5" />
        </div>
        <div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {renderValue(stats?.totalActivities)}
          </div>
          <div className="text-xs font-semibold text-gray-700 dark:text-gray-300">Activities</div>
          <div className="text-[11px] text-gray-500 dark:text-gray-400">All time</div>
        </div>
      </div>

      <div className="flex items-center gap-4 rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border border-emerald-500/30 bg-emerald-500/10 text-emerald-500 dark:text-emerald-400">
          <FaCodeBranch className="h-5 w-5" />
        </div>
        <div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {renderValue(stats?.pullRequests)}
          </div>
          <div className="text-xs font-semibold text-gray-700 dark:text-gray-300">
            Pull Requests
          </div>
          <div className="text-[11px] text-gray-500 dark:text-gray-400">All time</div>
        </div>
      </div>

      <div className="flex items-center gap-4 rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border border-amber-500/30 bg-amber-500/10 text-amber-500 dark:text-amber-400">
          <div className="h-4 w-4 rounded-full border-2 border-amber-500 dark:border-amber-400" />
        </div>
        <div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {renderValue(stats?.issues)}
          </div>
          <div className="text-xs font-semibold text-gray-700 dark:text-gray-300">Issues</div>
          <div className="text-[11px] text-gray-500 dark:text-gray-400">All time</div>
        </div>
      </div>

      <div className="flex items-center gap-4 rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border border-purple-500/30 bg-purple-500/10 text-purple-500 dark:text-purple-400">
          <FaUsers className="h-5 w-5" />
        </div>
        <div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {renderValue(stats?.contributors)}
          </div>
          <div className="text-xs font-semibold text-gray-700 dark:text-gray-300">Contributors</div>
          <div className="text-[11px] text-gray-500 dark:text-gray-400">All time</div>
        </div>
      </div>

      <div className="flex items-center gap-4 rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border border-pink-500/30 bg-pink-500/10 text-pink-500 dark:text-pink-400">
          <FaRocket className="h-5 w-5" />
        </div>
        <div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {renderValue(stats?.releases)}
          </div>
          <div className="text-xs font-semibold text-gray-700 dark:text-gray-300">Releases</div>
          <div className="text-[11px] text-gray-500 dark:text-gray-400">All time</div>
        </div>
      </div>
    </div>
  )
}
