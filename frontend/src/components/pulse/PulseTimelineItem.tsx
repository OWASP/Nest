import Image from 'next/image'
import { FaCode, FaCodeBranch, FaCodeMerge, FaGithub, FaUser } from 'react-icons/fa6'
import type { PulseTimelineItemProps } from 'types/pulse'

const formatRelativeTime = (dateStr: string) => {
  try {
    const eventDate = new Date(dateStr)
    const currentDate = new Date()
    const timeDifferenceMs = currentDate.getTime() - eventDate.getTime()
    const hoursAgo = Math.floor(timeDifferenceMs / (1000 * 60 * 60))
    const daysAgo = Math.floor(hoursAgo / 24)

    if (hoursAgo < 1) return 'just now'
    if (hoursAgo === 1) return '1 hour ago'
    if (hoursAgo < 24) return `${hoursAgo} hours ago`
    if (daysAgo === 1) return 'yesterday'
    if (daysAgo < 30) return `${daysAgo} days ago`
    return eventDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  } catch {
    return dateStr
  }
}

const getActionText = (activityType: string) => {
  switch (activityType) {
    case 'pr_opened':
      return 'opened a pull request'
    case 'pr_closed':
      return 'closed a pull request'
    case 'pr_merged':
      return 'merged a pull request'
    case 'issue_opened':
      return 'opened an issue'
    case 'issue_closed':
      return 'closed an issue'
    case 'release_published':
      return 'published a release'
    default:
      return 'created an activity event'
  }
}

const renderBadge = (activityType: string) => {
  switch (activityType) {
    case 'pr_opened':
      return (
        <span className="rounded-md border border-emerald-500/40 bg-emerald-500/10 px-2.5 py-1 text-[11px] font-bold tracking-wider text-emerald-600 uppercase dark:text-emerald-400">
          PR OPENED
        </span>
      )
    case 'pr_closed':
    case 'pr_merged':
      return (
        <span className="rounded-md border border-purple-500/40 bg-purple-500/10 px-2.5 py-1 text-[11px] font-bold tracking-wider text-purple-600 uppercase dark:text-purple-400">
          {activityType === 'pr_merged' ? 'PR MERGED' : 'PR CLOSED'}
        </span>
      )
    case 'issue_opened':
      return (
        <span className="rounded-md border border-amber-500/40 bg-amber-500/10 px-2.5 py-1 text-[11px] font-bold tracking-wider text-amber-600 uppercase dark:text-amber-400">
          ISSUE OPENED
        </span>
      )
    case 'issue_closed':
      return (
        <span className="rounded-md border border-red-500/40 bg-red-500/10 px-2.5 py-1 text-[11px] font-bold tracking-wider text-red-600 uppercase dark:text-red-400">
          ISSUE CLOSED
        </span>
      )
    case 'release_published':
      return (
        <span className="rounded-md border border-pink-500/40 bg-pink-500/10 px-2.5 py-1 text-[11px] font-bold tracking-wider text-pink-600 uppercase dark:text-pink-400">
          RELEASE
        </span>
      )
    default:
      return (
        <span className="rounded-md border border-gray-500/40 bg-gray-500/10 px-2.5 py-1 text-[11px] font-bold tracking-wider text-gray-600 uppercase dark:text-gray-400">
          {activityType.toUpperCase()}
        </span>
      )
  }
}

const renderTimelineIcon = (activityType: string) => {
  switch (activityType) {
    case 'pr_opened':
      return (
        <div className="flex h-9 w-9 items-center justify-center rounded-full border border-emerald-500/60 bg-white text-emerald-600 shadow-md dark:bg-gray-800 dark:text-emerald-400">
          <FaCodeBranch className="h-4 w-4" />
        </div>
      )
    case 'pr_closed':
    case 'pr_merged':
      return (
        <div className="flex h-9 w-9 items-center justify-center rounded-full border border-purple-500/60 bg-white text-purple-600 shadow-md dark:bg-gray-800 dark:text-purple-400">
          <FaCodeMerge className="h-4 w-4" />
        </div>
      )
    case 'issue_opened':
    case 'issue_closed':
      return (
        <div className="flex h-9 w-9 items-center justify-center rounded-full border border-amber-500/60 bg-white text-amber-600 shadow-md dark:bg-gray-800 dark:text-amber-400">
          <div className="h-3 w-3 rounded-full border-2 border-amber-500 dark:border-amber-400" />
        </div>
      )
    default:
      return (
        <div className="flex h-9 w-9 items-center justify-center rounded-full border border-blue-500/60 bg-white text-blue-600 shadow-md dark:bg-gray-800 dark:text-blue-400">
          <FaCode className="h-4 w-4" />
        </div>
      )
  }
}

export default function PulseTimelineItem({ event }: Readonly<PulseTimelineItemProps>) {
  return (
    <div className="group relative">
      <div className="absolute top-3 -left-[43px]">{renderTimelineIcon(event.activityType)}</div>

      <div className="flex flex-col gap-4 rounded-xl border border-gray-200 bg-white p-4 shadow-sm transition hover:border-gray-300 sm:flex-row sm:items-center sm:justify-between dark:border-gray-700 dark:bg-gray-800 dark:hover:border-gray-600">
        <div className="flex items-start gap-4">
          {event.githubUser?.avatarUrl ? (
            <Image
              src={event.githubUser.avatarUrl}
              alt={event.githubUser.login}
              width={40}
              height={40}
              className="mt-0.5 shrink-0 rounded-full border border-gray-200 dark:border-gray-700"
            />
          ) : (
            <div className="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gray-200 text-gray-500 dark:bg-gray-700 dark:text-gray-400">
              <FaUser className="h-4 w-4" />
            </div>
          )}

          <div className="space-y-1">
            <div className="text-sm text-gray-600 dark:text-gray-300">
              <span className="font-bold text-gray-900 dark:text-white">
                {event.githubUser?.name || event.githubUser?.login || 'OWASP Contributor'}
              </span>{' '}
              <span className="text-gray-500 dark:text-gray-400">
                {getActionText(event.activityType)}
              </span>
            </div>

            <div className="text-sm font-semibold text-blue-600 hover:underline dark:text-blue-400">
              {event.url ? (
                <a href={event.url} target="_blank" rel="noreferrer">
                  {event.number ? `#${event.number} ` : ''}
                  {event.title || 'Activity Title'}
                </a>
              ) : (
                <span>
                  {event.number ? `#${event.number} ` : ''}
                  {event.title || 'Activity Title'}
                </span>
              )}
            </div>

            <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
              <span className="flex items-center gap-1 font-mono text-gray-700 dark:text-gray-300">
                <FaCodeBranch className="h-3 w-3" />
                {event.githubRepository?.key || event.githubRepository?.name || 'nest'}
              </span>
              <span>&bull;</span>
              <span>{formatRelativeTime(event.occurredAt)}</span>
            </div>
          </div>
        </div>

        <div className="flex shrink-0 items-center justify-between gap-4 sm:justify-end">
          {renderBadge(event.activityType)}

          {event.url && (
            <a
              href={event.url}
              target="_blank"
              rel="noreferrer"
              aria-label="View on GitHub"
              className="text-gray-400 transition hover:text-gray-700 dark:hover:text-white"
            >
              <FaGithub aria-hidden="true" className="h-5 w-5" />
            </a>
          )}
        </div>
      </div>
    </div>
  )
}
