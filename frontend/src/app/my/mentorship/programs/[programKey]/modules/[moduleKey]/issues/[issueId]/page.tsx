'use client'

import { useQuery } from '@apollo/client/react'
import { useIssueMutations } from 'hooks/useIssueMutations'
import Image from 'next/image'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useState } from 'react'
import { FaCodeBranch, FaLink, FaPlus, FaTags, FaXmark } from 'react-icons/fa6'
import { HiUserGroup } from 'react-icons/hi'
import { ErrorDisplay } from 'app/global-error'
import { GetModuleIssueViewDocument } from 'types/__generated__/issueQueries.generated'
import ActionButton from 'components/ActionButton'
import AnchorTitle from 'components/AnchorTitle'
import { LabelList } from 'components/LabelList'
import LoadingSpinner from 'components/LoadingSpinner'
import Markdown from 'components/MarkdownWrapper'
import MentorshipPullRequest from 'components/MentorshipPullRequest'
import SecondaryCard from 'components/SecondaryCard'
import ShowMoreButton from 'components/ShowMoreButton'

const ModuleIssueDetailsPage = () => {
  const params = useParams<{ programKey: string; moduleKey: string; issueId: string }>()
  const [showAllPRs, setShowAllPRs] = useState(false)
  const { programKey, moduleKey, issueId } = params

  const formatDeadline = (deadline: string | null) => {
    if (!deadline) return { text: 'No deadline set', color: 'text-gray-600 dark:text-gray-300' }

    const deadlineDate = new Date(deadline)
    const today = new Date()

    const deadlineUTC = new Date(
      deadlineDate.getUTCFullYear(),
      deadlineDate.getUTCMonth(),
      deadlineDate.getUTCDate()
    )
    const todayUTC = new Date(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate())

    const isOverdue = deadlineUTC < todayUTC
    const daysLeft = Math.ceil((deadlineUTC.getTime() - todayUTC.getTime()) / (1000 * 60 * 60 * 24))

    let statusText: string
    if (isOverdue) {
      statusText = '(overdue)'
    } else if (daysLeft === 0) {
      statusText = '(today)'
    } else {
      statusText = `(${daysLeft} days left)`
    }

    const displayDate = deadlineDate.toLocaleDateString()

    let color: string
    if (isOverdue) {
      color = 'text-[#DA3633]'
    } else if (daysLeft <= 3) {
      color = 'text-[#F59E0B]'
    } else {
      color = 'text-gray-600 dark:text-gray-300'
    }

    return {
      text: `${displayDate} ${statusText}`,
      color,
    }
  }
  const { data, loading, error } = useQuery(GetModuleIssueViewDocument, {
    variables: { programKey, moduleKey, number: Number(issueId) },
    skip: !issueId,
    fetchPolicy: 'cache-first',
    nextFetchPolicy: 'cache-and-network',
  })

  const {
    assignIssue,
    unassignIssue,
    setTaskDeadlineMutation,
    clearTaskDeadlineMutation,
    assigning,
    unassigning,
    settingDeadline,
    clearingDeadline,
    isEditingDeadline,
    setIsEditingDeadline,
    deadlineInput,
    setDeadlineInput,
  } = useIssueMutations({ programKey, moduleKey, issueId })

  const issue = data?.getModule?.issueByNumber
  const taskDeadline = (data?.getModule?.taskDeadline as string | undefined) ?? null

  const getButtonClassName = (disabled: boolean) =>
    `inline-flex items-center justify-center rounded-md border p-1.5 text-sm ${
      disabled
        ? 'cursor-not-allowed border-gray-300 text-gray-400 dark:border-gray-600'
        : 'border-gray-300 hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-800'
    }`

  if (error) {
    return <ErrorDisplay statusCode={500} title="Error Loading Issue" message={error.message} />
  }
  if (loading) return <LoadingSpinner />
  if (!issue)
    return <ErrorDisplay statusCode={404} title="Issue Not Found" message="Issue not found" />

  const assignees = issue.assignees || []
  const labels = issue.labels || []
  const canEditDeadline = assignees.length > 0

  let issueStatusClass: string
  let issueStatusLabel: string
  if (issue.state === 'open') {
    issueStatusClass = 'bg-[#238636] text-white'
    issueStatusLabel = 'Open'
  } else if (issue.isMerged) {
    issueStatusClass = 'bg-[#8657E5] text-white'
    issueStatusLabel = 'Merged'
  } else {
    issueStatusClass = 'bg-[#DA3633] text-white'
    issueStatusLabel = 'Closed'
  }

  const getAssignButtonTitle = (assigning: boolean) => {
    let title: string
    if (!issueId) {
      title = 'Loading issue…'
    } else if (assigning) {
      title = 'Assigning…'
    } else {
      title = 'Assign to this user'
    }
    return title
  }

  return (
    <div className="min-h-screen bg-white p-8 text-gray-700 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-5xl">
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="min-w-0 flex-1">
            <h1 className="text-2xl font-bold sm:text-3xl">
              <span className="break-words">{issue.title}</span>
            </h1>
            <div className="mt-1 flex items-center gap-2 text-sm text-gray-500">
              <span>
                {issue.organizationName}/{issue.repositoryName} • #{issue.number}
              </span>
              <span
                className={`inline-flex items-center rounded-lg px-2 py-0.5 text-xs font-medium ${issueStatusClass}`}
              >
                {issueStatusLabel}
              </span>
            </div>
          </div>
          <ActionButton url={issue.url} tooltipLabel="View on GitHub">
            <FaLink className="mr-2 inline-block" /> View on GitHub
          </ActionButton>
        </div>

        <SecondaryCard title={<AnchorTitle title="Description" />}>
          <div className="prose dark:prose-invert line-clamp-[15] max-w-none">
            <Markdown content={issue.body || 'No description.'} />
          </div>
        </SecondaryCard>

        <SecondaryCard title={<AnchorTitle title="Task Timeline" />}>
          <div className="space-y-4 text-sm text-gray-700 dark:text-gray-300">
            <div>
              <span className="font-medium">Assigned:</span>{' '}
              <span>
                {data?.getModule?.taskAssignedAt
                  ? new Date(data.getModule.taskAssignedAt).toLocaleDateString()
                  : 'Not assigned'}
              </span>
            </div>

            <div className="flex flex-col gap-2">
              <div className="flex flex-wrap items-center">
                <span className="font-medium">Deadline: </span>
                {isEditingDeadline && canEditDeadline ? (
                  <div className="inline-flex items-center gap-2">
                    <input
                      type="date"
                      value={deadlineInput}
                      onChange={async (e) => {
                        const newValue = e.target.value
                        setDeadlineInput(newValue)

                        if (!settingDeadline && !clearingDeadline && issueId) {
                          if (newValue) {
                            const [year, month, day] = newValue.split('-').map(Number)
                            const utcEndOfDay = new Date(
                              Date.UTC(year, month - 1, day, 23, 59, 59, 999)
                            )
                            const iso = utcEndOfDay.toISOString()

                            await setTaskDeadlineMutation({
                              variables: {
                                programKey,
                                moduleKey,
                                issueNumber: Number(issueId),
                                deadlineAt: iso,
                              },
                            })
                          } else {
                            // Clear deadline
                            await clearTaskDeadlineMutation({
                              variables: {
                                programKey,
                                moduleKey,
                                issueNumber: Number(issueId),
                              },
                            })
                          }
                        }
                      }}
                      min={new Date().toISOString().slice(0, 10)}
                      className="h-8 rounded border border-gray-300 px-2 dark:border-gray-600"
                    />
                  </div>
                ) : (
                  <button
                    type="button"
                    disabled={!canEditDeadline}
                    onClick={() => {
                      if (canEditDeadline) {
                        setDeadlineInput(
                          taskDeadline ? new Date(taskDeadline).toISOString().slice(0, 10) : ''
                        )
                        setIsEditingDeadline(true)
                      }
                    }}
                    className={`inline-flex items-center gap-2 rounded px-2 py-1 text-left transition-colors ${
                      canEditDeadline
                        ? 'cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800'
                        : 'cursor-not-allowed font-medium'
                    }`}
                  >
                    {(() => {
                      const { text, color } = formatDeadline(taskDeadline)
                      return <span className={`font-normal ${color}`}>{text}</span>
                    })()}
                  </button>
                )}
              </div>
            </div>
          </div>
        </SecondaryCard>

        <div className="mb-8 rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
          <h2 className="mb-4 text-2xl font-semibold">
            <div className="flex items-center">
              <div className="flex flex-row items-center gap-2">
                <FaTags className="mr-2 h-5 w-5" />
              </div>
              <span>Labels</span>
            </div>
          </h2>
          <LabelList entityKey={`issue-${issueId}`} labels={labels} maxVisible={5} />
        </div>

        {assignees.length > 0 && (
          <div className="mb-8 rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
            <h2 className="mb-4 text-2xl font-semibold">
              <div className="flex items-center">
                <div className="flex flex-row items-center gap-2">
                  <HiUserGroup className="mr-2 h-5 w-5" />
                </div>
                <span>Assignees</span>
              </div>
            </h2>
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {assignees.map((a) => (
                <div
                  key={a.id}
                  className="flex items-center justify-between gap-2 rounded-lg bg-gray-200 p-3 dark:bg-gray-700"
                >
                  <Link
                    href={`/my/mentorship/programs/${programKey}/modules/${moduleKey}/mentees/${a.login}`}
                    className="inline-flex items-center gap-2 text-blue-600 hover:underline dark:text-blue-400"
                  >
                    {a.avatarUrl ? (
                      <Image
                        src={a.avatarUrl}
                        alt=""
                        width={32}
                        height={32}
                        className="rounded-full"
                      />
                    ) : (
                      <div className="h-8 w-8 rounded-full bg-gray-400" aria-hidden="true" />
                    )}
                    <span className="text-sm font-medium">{a.login || a.name}</span>
                  </Link>
                  <button
                    type="button"
                    aria-label={`Unassign @${a.login}`}
                    disabled={!issueId || unassigning}
                    onClick={async () => {
                      if (!issueId || unassigning) return
                      await unassignIssue({
                        variables: {
                          programKey,
                          moduleKey,
                          issueNumber: Number(issueId),
                          userLogin: a.login,
                        },
                      })
                    }}
                    className={getButtonClassName(!issueId || unassigning)}
                    title={unassigning ? 'Unassigning…' : `Unassign @${a.login}`}
                  >
                    <FaXmark />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        <SecondaryCard icon={FaCodeBranch} title="Pull Requests">
          <div className="grid grid-cols-1 gap-3">
            {(issue.pullRequests || []).slice(0, showAllPRs ? undefined : 4).map((pr) => (
              <MentorshipPullRequest key={pr.id} pr={pr} />
            ))}
            {(!issue.pullRequests || issue.pullRequests.length === 0) && (
              <span className="text-sm text-gray-400">No linked pull requests.</span>
            )}
            {issue.pullRequests && issue.pullRequests.length > 4 && (
              <ShowMoreButton onToggle={() => setShowAllPRs(!showAllPRs)} />
            )}
          </div>
        </SecondaryCard>

        <div className="rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
          <h2 className="mb-4 text-2xl font-semibold">
            <div className="flex items-center">
              <div className="flex flex-row items-center gap-2">
                <HiUserGroup className="mr-2 h-5 w-5" />
              </div>
              <span>Interested Users</span>
            </div>
          </h2>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {(data?.getModule?.interestedUsers || []).map((u) => (
              <div
                key={u.id}
                className="flex items-center justify-between gap-2 rounded-lg bg-gray-200 p-3 dark:bg-gray-700"
              >
                <div className="inline-flex items-center gap-2">
                  {u.avatarUrl ? (
                    <Image
                      src={u.avatarUrl}
                      alt=""
                      width={32}
                      height={32}
                      className="rounded-full"
                    />
                  ) : (
                    <div className="h-8 w-8 rounded-full bg-gray-400" aria-hidden="true" />
                  )}
                  <span className="text-sm font-medium">@{u.login}</span>
                </div>
                <button
                  type="button"
                  disabled={!issueId || assigning}
                  onClick={async () => {
                    if (!issueId || assigning) return
                    await assignIssue({
                      variables: {
                        programKey,
                        moduleKey,
                        issueNumber: Number(issueId),
                        userLogin: u.login,
                      },
                    })
                  }}
                  className={`${getButtonClassName(!issueId || assigning)} px-3 py-1`}
                  title={getAssignButtonTitle(assigning)}
                >
                  <FaPlus className="text-gray-500" />
                  <span>Assign</span>
                </button>
              </div>
            ))}
            {(data?.getModule?.interestedUsers || []).length === 0 && (
              <span className="text-sm text-gray-400">No interested users yet.</span>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ModuleIssueDetailsPage
