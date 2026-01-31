'use client'

import { Tooltip } from '@heroui/tooltip'
import Image from 'next/image'
import { useRouter } from 'next/navigation'
import type React from 'react'

export type IssueRow = {
  objectID: string
  number: number
  title: string
  state: string
  isMerged?: boolean
  labels: string[]
  assignees?: Array<{ avatarUrl: string; login: string; name: string }>
  url?: string
  deadline?: string | null
}

interface IssuesTableProps {
  issues: IssueRow[]
  showAssignee?: boolean
  showDeadline?: boolean
  onIssueClick?: (issueNumber: number) => void
  issueUrl?: (issueNumber: number) => string
  maxVisibleLabels?: number
  emptyMessage?: string
}

const MAX_VISIBLE_LABELS = 5

const IssuesTable: React.FC<IssuesTableProps> = ({
  issues,
  showAssignee = true,
  showDeadline = false,
  onIssueClick,
  issueUrl,
  maxVisibleLabels = MAX_VISIBLE_LABELS,
  emptyMessage = 'No issues found.',
}) => {
  const router = useRouter()

  const handleIssueClick = (issueNumber: number) => {
    if (onIssueClick) {
      onIssueClick(issueNumber)
    } else if (issueUrl) {
      router.push(issueUrl(issueNumber))
    }
  }

  const getStatusBadge = (state: string, isMerged?: boolean) => {
    const statusMap: Record<string, { text: string; class: string }> = {
      open: { text: 'Open', class: 'bg-[#238636]' },
      merged: { text: 'Merged', class: 'bg-[#8657E5]' },
      closed: { text: 'Closed', class: 'bg-[#DA3633]' },
    }

    const statusKey = isMerged ? 'merged' : state.toLowerCase()
    const status = statusMap[statusKey] || statusMap.closed

    return (
      <span
        className={`inline-flex items-center rounded-lg px-2 py-0.5 text-xs font-medium text-white ${status.class}`}
      >
        {status.text}
      </span>
    )
  }

  const getColumnCount = () => {
    let count = 3 // Title, Status, Labels
    if (showAssignee) count++
    if (showDeadline) count++
    return count
  }

  const getDeadlineStatus = (deadline?: string | null) => {
    if (!deadline)
      return {
        text: 'No Deadline',
        class: 'border border-dashed border-gray-500 text-gray-500 bg-transparent',
      }

    const now = new Date()
    const deadlineDate = new Date(deadline)
    const nowStart = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const deadlineStart = new Date(
      deadlineDate.getFullYear(),
      deadlineDate.getMonth(),
      deadlineDate.getDate()
    )
    const diffDays = Math.round((deadlineStart.getTime() - nowStart.getTime()) / 86400000)

    if (diffDays < 0)
      return {
        text: 'Overdue',
        class: 'bg-red-500/15 text-red-400 border border-red-500/30',
      }

    if (diffDays <= 7)
      return {
        text: 'Due Soon',
        class: 'bg-amber-500/15 text-amber-400 border border-amber-500/30',
      }

    return {
      text: 'Upcoming',
      class: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
    }
  }

  return (
    <div className="overflow-hidden rounded-lg border border-gray-200 dark:border-gray-700">
      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead className="hidden bg-gray-50 lg:table-header-group dark:bg-[#2a2e33]">
          <tr>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-400"
            >
              Title
            </th>
            <th
              scope="col"
              className="hidden px-6 py-3 text-center text-xs font-medium tracking-wider text-gray-500 uppercase lg:table-cell dark:text-gray-400"
            >
              Status
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-400"
            >
              Labels
            </th>
            {showAssignee && (
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-400"
              >
                Assignee
              </th>
            )}
            {showDeadline && (
              <th
                scope="col"
                className="px-6 py-3 text-right text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-400"
              >
                Deadline
              </th>
            )}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 bg-white dark:divide-gray-700 dark:bg-[#1f2327]">
          {issues.map((issue) => (
            <tr
              key={issue.objectID}
              className="relative block border-b border-gray-200 p-4 transition-colors hover:bg-gray-50 lg:table-row lg:border-b lg:p-0 dark:border-gray-700 dark:hover:bg-[#2a2e33]"
            >
              {/* Title */}
              <td className="block pr-12 pb-3 lg:table-cell lg:px-6 lg:py-4">
                <div className="flex items-start justify-between gap-3 lg:block">
                  <Tooltip
                    closeDelay={100}
                    delay={100}
                    showArrow
                    content={issue.title}
                    placement="bottom"
                    isDisabled={issue.title.length <= 50}
                  >
                    <button
                      type="button"
                      onClick={() => handleIssueClick(issue.number)}
                      className="line-clamp-2 h-12 cursor-pointer overflow-hidden text-left text-sm font-medium text-blue-600 hover:underline lg:max-w-md dark:text-blue-400"
                    >
                      {issue.title}
                    </button>
                  </Tooltip>
                </div>
              </td>

              {/* Status */}
              <td className="absolute top-4 right-4 block lg:relative lg:top-auto lg:right-auto lg:table-cell lg:px-6 lg:py-4 lg:text-center lg:text-sm lg:whitespace-nowrap">
                <div className="flex justify-center">
                  {getStatusBadge(issue.state, issue.isMerged)}
                </div>
              </td>

              {/* Labels */}
              <td className="block pb-3 lg:table-cell lg:px-6 lg:py-4">
                {issue.labels && issue.labels.length > 0 ? (
                  <div className="flex flex-wrap gap-1 lg:gap-2">
                    {issue.labels.slice(0, maxVisibleLabels).map((label) => (
                      <span
                        key={label}
                        className="inline-flex items-center rounded-md bg-gray-100 px-2 py-0.5 text-xs text-gray-700 lg:rounded-lg lg:border lg:border-gray-400 lg:bg-transparent lg:hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:lg:border-gray-300 dark:lg:hover:bg-gray-700"
                      >
                        {label}
                      </span>
                    ))}
                    {issue.labels.length > maxVisibleLabels && (
                      <span className="inline-flex items-center rounded-md bg-gray-100 px-2 py-0.5 text-xs text-gray-500 lg:rounded-lg lg:border lg:border-gray-400 lg:bg-transparent lg:text-gray-700 lg:hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:lg:border-gray-300 dark:lg:text-gray-300 dark:lg:hover:bg-gray-700">
                        +{issue.labels.length - maxVisibleLabels} more
                      </span>
                    )}
                  </div>
                ) : null}
              </td>

              {/* Assignee */}
              {showAssignee && (
                <td className="block pb-0 text-xs text-gray-600 lg:table-cell lg:px-6 lg:py-4 lg:text-sm lg:text-gray-700 dark:text-gray-400 dark:lg:text-gray-300">
                  {issue.assignees && issue.assignees.length > 0 ? (
                    <div className="flex items-center gap-2">
                      <Image
                        height={18}
                        width={18}
                        src={issue.assignees[0].avatarUrl}
                        alt=""
                        className="rounded-full lg:h-6 lg:w-6"
                      />
                      <span className="max-w-[80px] truncate sm:max-w-[100px] md:max-w-[120px] lg:max-w-[150px]">
                        {issue.assignees[0].login || issue.assignees[0].name}
                        {issue.assignees.length > 1 && ` +${issue.assignees.length - 1}`}
                      </span>
                    </div>
                  ) : null}
                </td>
              )}

              {/* Deadline */}
              {showDeadline && (
                <td className="pt-2 text-right lg:table-cell lg:px-6 lg:py-4 lg:pt-0">
                  {(() => {
                    const status = getDeadlineStatus(issue.deadline)
                    return (
                      <span
                        className={`inline-flex items-center rounded-md px-2 py-0.5 text-[11px] font-medium whitespace-nowrap ${status.class}`}
                      >
                        {status.text}
                      </span>
                    )
                  })()}
                </td>
              )}
            </tr>
          ))}
          {issues.length === 0 && (
            <tr>
              <td
                colSpan={getColumnCount()}
                className="block p-6 text-center text-sm text-gray-500 lg:table-cell lg:px-6 lg:py-8 dark:text-gray-400"
              >
                {emptyMessage}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}

export default IssuesTable
