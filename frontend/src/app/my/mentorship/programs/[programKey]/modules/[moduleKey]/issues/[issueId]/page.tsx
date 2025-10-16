'use client'

import { useMutation, useQuery } from '@apollo/client'
import {
  faCodeBranch,
  faLink,
  faPlus,
  faTags,
  faUsers,
  faXmark,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { addToast } from '@heroui/toast'
import Image from 'next/image'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useState } from 'react'
import { ErrorDisplay } from 'app/global-error'
import {
  ASSIGN_ISSUE_TO_USER,
  GET_MODULE_ISSUE_VIEW,
  UNASSIGN_ISSUE_FROM_USER,
  SET_TASK_DEADLINE,
} from 'server/queries/issueQueries'
import ActionButton from 'components/ActionButton'
import AnchorTitle from 'components/AnchorTitle'
import LoadingSpinner from 'components/LoadingSpinner'
import Markdown from 'components/MarkdownWrapper'
import SecondaryCard from 'components/SecondaryCard'
import { TruncatedText } from 'components/TruncatedText'

const ModuleIssueDetailsPage = () => {
  const params = useParams() as { programKey: string; moduleKey: string; issueId: string }
  const { programKey, moduleKey, issueId } = params
  const { data, loading, error } = useQuery(GET_MODULE_ISSUE_VIEW, {
    variables: { programKey, moduleKey, number: Number(issueId) },
    skip: !issueId,
    fetchPolicy: 'cache-first',
    nextFetchPolicy: 'cache-and-network',
  })

  const [assignIssue, { loading: assigning }] = useMutation(ASSIGN_ISSUE_TO_USER, {
    refetchQueries: [
      {
        query: GET_MODULE_ISSUE_VIEW,
        variables: { programKey, moduleKey, number: Number(issueId) },
      },
    ],
    awaitRefetchQueries: true,
    onCompleted: () => {
      addToast({
        title: 'Issue assigned successfully',
        variant: 'solid',
        color: 'success',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
      })
    },
    onError: (error) => {
      addToast({
        title: 'Failed to assign issue: ' + error.message,
        variant: 'solid',
        color: 'danger',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
      })
    },
  })
  const [unassignIssue, { loading: unassigning }] = useMutation(UNASSIGN_ISSUE_FROM_USER, {
    refetchQueries: [
      {
        query: GET_MODULE_ISSUE_VIEW,
        variables: { programKey, moduleKey, number: Number(issueId) },
      },
    ],
    awaitRefetchQueries: true,
    onCompleted: () => {
      addToast({
        title: 'Issue unassigned successfully',
        variant: 'solid',
        color: 'success',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
      })
    },
    onError: (error) => {
      addToast({
        title: 'Failed to unassign issue: ' + error.message,
        variant: 'solid',
        color: 'danger',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
      })
    },
  })

  const issue = data?.getModule?.issueByNumber
  const taskDeadline = data?.getModule?.taskDeadline as string | undefined
  const [isEditingDeadline, setIsEditingDeadline] = useState(false)
  const [deadlineInput, setDeadlineInput] = useState<string>(
    taskDeadline ? new Date(taskDeadline).toISOString().slice(0, 10) : ''
  )

  const getButtonClassName = (disabled: boolean) =>
    `inline-flex items-center justify-center rounded-md border p-1.5 text-sm ${
      disabled
        ? 'cursor-not-allowed border-gray-300 text-gray-400 dark:border-gray-600'
        : 'border-gray-300 hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-800'
    }`

  const labelButtonClassName =
    'rounded-lg border border-gray-400 px-3 py-1 text-sm hover:bg-gray-200 dark:border-gray-300 dark:hover:bg-gray-700'

  const [setTaskDeadlineMutation, { loading: settingDeadline }] = useMutation(SET_TASK_DEADLINE, {
    refetchQueries: [
      {
        query: GET_MODULE_ISSUE_VIEW,
        variables: { programKey, moduleKey, number: Number(issueId) },
      },
    ],
    awaitRefetchQueries: true,
    onCompleted: () => {
      addToast({
        title: 'Deadline updated',
        variant: 'solid',
        color: 'success',
        timeout: 2500,
        shouldShowTimeoutProgress: true,
      })
      setIsEditingDeadline(false)
    },
    onError: (err) => {
      addToast({
        title: 'Failed to update deadline: ' + err.message,
        variant: 'solid',
        color: 'danger',
        timeout: 3500,
        shouldShowTimeoutProgress: true,
      })
    },
  })

  if (error) {
    return <ErrorDisplay statusCode={500} title="Error Loading Issue" message={error.message} />
  }
  if (loading) return <LoadingSpinner />
  if (!issue)
    return <ErrorDisplay statusCode={404} title="Issue Not Found" message="Issue not found" />

  const assignees = issue.assignees || []
  const labels = issue.labels || []
  const visibleLabels = labels.slice(0, 5)
  const remainingLabels = labels.length - visibleLabels.length
  const canEditDeadline = assignees.length > 0

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
                className={`rounded-full px-2 py-1 text-xs font-medium ${
                  issue.state === 'open'
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                    : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                }`}
              >
                {issue.state === 'open' ? 'Open' : 'Closed'}
              </span>
            </div>
          </div>
          <ActionButton url={issue.url} tooltipLabel="View on GitHub">
            <FontAwesomeIcon icon={faLink} /> View on GitHub
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
              {data?.getModule?.taskAssignedAt
                ? new Date(data.getModule.taskAssignedAt).toLocaleDateString()
                : 'Not assigned'}
            </div>

            <div className="flex flex-col gap-2">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-medium">Deadline:</span>
                {isEditingDeadline && canEditDeadline ? (
                  <span className="inline-flex items-center gap-2">
                    <input
                      type="date"
                      value={deadlineInput}
                      onChange={(e) => setDeadlineInput(e.target.value)}
                      min={new Date().toISOString().slice(0, 10)}
                      className="h-8 rounded border border-gray-300 px-2 text-xs dark:border-gray-600"
                    />
                    <button
                      type="button"
                      disabled={!deadlineInput || settingDeadline}
                      onClick={async () => {
                        if (!deadlineInput || settingDeadline || !issueId) return
                        const iso = new Date(deadlineInput + 'T23:59:59').toISOString()
                        await setTaskDeadlineMutation({
                          variables: {
                            programKey,
                            moduleKey,
                            issueNumber: Number(issueId),
                            deadlineAt: iso,
                          },
                        })
                      }}
                      className="flex items-center justify-center rounded-md border border-[#1D7BD7] px-3 py-1 text-xs font-medium text-[#1D7BD7] transition-all hover:bg-[#1D7BD7] hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {settingDeadline ? 'Saving…' : 'Save'}
                    </button>
                    <button
                      type="button"
                      aria-label="Cancel deadline edit"
                      title="Cancel"
                      onClick={() => {
                        setDeadlineInput(
                          taskDeadline ? new Date(taskDeadline).toISOString().slice(0, 10) : ''
                        )
                        setIsEditingDeadline(false)
                      }}
                      className="inline-flex h-7 w-7 items-center justify-center rounded-md text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
                    >
                      <FontAwesomeIcon icon={faXmark} className="h-3.5 w-3.5" />
                    </button>
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-2">
                    {(() => {
                      if (!taskDeadline) {
                        return (
                          <span className="text-xs font-medium text-gray-600 dark:text-gray-300">
                            No deadline set
                          </span>
                        )
                      }
                      const d = new Date(taskDeadline)
                      const today = new Date()
                      const isPast = d.setHours(0, 0, 0, 0) < today.setHours(0, 0, 0, 0)
                      const diffDays = Math.ceil(
                        (d.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)
                      )
                      const textClass = 'text-red-700 dark:text-red-300'
                      return (
                        <span className={`text-xs font-medium ${textClass}`}>
                          {d.toLocaleDateString()}{' '}
                          {isPast
                            ? '(overdue)'
                            : diffDays > 0
                              ? `(in ${diffDays} days)`
                              : '(today)'}
                        </span>
                      )
                    })()}
                    {canEditDeadline && (
                      <button
                        type="button"
                        className="ml-2 text-xs text-blue-600 hover:underline dark:text-blue-400"
                        onClick={() => setIsEditingDeadline(true)}
                      >
                        Edit
                      </button>
                    )}
                  </span>
                )}
              </div>
            </div>
          </div>
        </SecondaryCard>

        <div className="mb-8 rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
          <h2 className="mb-4 text-2xl font-semibold">
            <div className="flex items-center">
              <div className="flex flex-row items-center gap-2">
                <FontAwesomeIcon icon={faTags} className="mr-2 h-5 w-5" />
              </div>
              <span>Labels</span>
            </div>
          </h2>
          <div className="flex flex-wrap gap-2">
            {visibleLabels.map((label, index) => (
              <button key={index} className={labelButtonClassName}>
                {label}
              </button>
            ))}
            {remainingLabels > 0 && (
              <button className={labelButtonClassName}>+{remainingLabels} more</button>
            )}
          </div>
        </div>

        {assignees.length > 0 && (
          <div className="mb-8 rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
            <h2 className="mb-4 text-2xl font-semibold">
              <div className="flex items-center">
                <div className="flex flex-row items-center gap-2">
                  <FontAwesomeIcon icon={faUsers} className="mr-2 h-5 w-5" />
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
                    href={`/members/${a.login}`}
                    className="inline-flex items-center gap-2 text-blue-600 hover:underline dark:text-blue-400"
                  >
                    {a.avatarUrl ? (
                      <Image
                        src={a.avatarUrl}
                        alt={a.login}
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
                    <FontAwesomeIcon icon={faXmark} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        <SecondaryCard icon={faCodeBranch} title="Pull Requests">
          <div className="grid grid-cols-1 gap-3">
            {issue.pullRequests?.length ? (
              issue.pullRequests.map((pr) => (
                <div
                  key={pr.id}
                  className="flex items-center justify-between gap-3 rounded-lg bg-gray-200 p-4 dark:bg-gray-700"
                >
                  <div className="flex min-w-0 flex-1 items-center gap-3">
                    {pr.author?.avatarUrl ? (
                      <Image
                        src={pr.author.avatarUrl}
                        alt={pr.author?.login || 'Unknown'}
                        width={32}
                        height={32}
                        className="flex-shrink-0 rounded-full"
                      />
                    ) : (
                      <div
                        className="h-8 w-8 flex-shrink-0 rounded-full bg-gray-400"
                        aria-hidden="true"
                      />
                    )}
                    <div className="min-w-0 flex-1">
                      <Link
                        href={pr.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-medium text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                      >
                        <TruncatedText text={pr.title} />
                      </Link>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        by {pr.author?.login || 'Unknown'} •{' '}
                        {new Date(pr.createdAt).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {pr.state === 'closed' && pr.mergedAt ? (
                      <span className="rounded-full bg-purple-100 px-2 py-1 text-xs font-medium text-purple-800 dark:bg-purple-900 dark:text-purple-200">
                        Merged
                      </span>
                    ) : pr.state === 'closed' ? (
                      <span className="rounded-full bg-red-100 px-2 py-1 text-xs font-medium text-red-800 dark:bg-red-900 dark:text-red-200">
                        Closed
                      </span>
                    ) : (
                      <span className="rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-800 dark:bg-green-900 dark:text-green-200">
                        Open
                      </span>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <span className="text-sm text-gray-400">No linked pull requests.</span>
            )}
          </div>
        </SecondaryCard>

        <div className="rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
          <h2 className="mb-4 text-2xl font-semibold">
            <div className="flex items-center">
              <div className="flex flex-row items-center gap-2">
                <FontAwesomeIcon icon={faUsers} className="mr-2 h-5 w-5" />
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
                      alt={u.login}
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
                  title={
                    !issueId ? 'Loading issue…' : assigning ? 'Assigning…' : 'Assign to this user'
                  }
                >
                  <FontAwesomeIcon icon={faPlus} className="text-gray-500" />
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
