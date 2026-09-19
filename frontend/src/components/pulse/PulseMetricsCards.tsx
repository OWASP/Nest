import { Skeleton } from '@heroui/skeleton'
import { FaCodeBranch, FaRocket, FaUsers, FaWaveSquare } from 'react-icons/fa6'
import { GoIssueOpened } from 'react-icons/go'
import type { PulseMetricsCardsProps } from 'types/pulse'

export default function PulseMetricsCards({
  error,
  loading,
  stats,
}: Readonly<PulseMetricsCardsProps>) {
  const renderValue = (val?: number) => {
    if (loading) {
      return <Skeleton className="my-1 h-7 w-20 rounded-lg" />
    }
    if (error || val === undefined || val === null) {
      return <span className="text-gray-400 dark:text-gray-500">N/A</span>
    }
    return val.toLocaleString()
  }

  const cards = [
    {
      color: 'border-blue-500/30 bg-blue-500/10 text-blue-500 dark:text-blue-400',
      icon: FaWaveSquare,
      title: 'Total Activities',
      value: stats?.totalActivities,
    },
    {
      color: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-500 dark:text-emerald-400',
      icon: FaCodeBranch,
      title: 'PR Activities',
      value: stats?.pullRequests,
    },
    {
      color: 'border-amber-500/30 bg-amber-500/10 text-amber-500 dark:text-amber-400',
      icon: GoIssueOpened,
      title: 'Issue Activities',
      value: stats?.issues,
    },
    {
      color: 'border-purple-500/30 bg-purple-500/10 text-purple-500 dark:text-purple-400',
      icon: FaUsers,
      title: 'Contributors',
      value: stats?.contributors,
    },
    {
      color: 'border-pink-500/30 bg-pink-500/10 text-pink-500 dark:text-pink-400',
      icon: FaRocket,
      title: 'Release Activities',
      value: stats?.releases,
    },
  ]

  return (
    <div className="mb-3 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
      {cards.map(({ color, icon: Icon, title, value }) => (
        <div
          key={title}
          className="flex items-center gap-4 rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800"
        >
          <div
            className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border ${color}`}
          >
            <Icon className="h-5 w-5" />
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {renderValue(value)}
            </div>
            <div className="text-xs font-semibold text-gray-700 dark:text-gray-300">{title}</div>
            <div className="text-[11px] text-gray-500 dark:text-gray-400">All time</div>
          </div>
        </div>
      ))}
    </div>
  )
}
