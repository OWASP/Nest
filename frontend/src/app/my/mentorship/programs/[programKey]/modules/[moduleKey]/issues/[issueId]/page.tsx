'use client'

import { useMutation, useQuery } from '@apollo/client'
import { faLink, faPlus, faTags, faUsers, faXmark } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import Image from 'next/image'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useMemo } from 'react'
import { ErrorDisplay } from 'app/global-error'
import {
  ASSIGN_ISSUE_TO_USER,
  GET_MODULE_ISSUE_VIEW,
  UNASSIGN_ISSUE_FROM_USER,
} from 'server/queries/issueQueries'
import ActionButton from 'components/ActionButton'
import AnchorTitle from 'components/AnchorTitle'
import LoadingSpinner from 'components/LoadingSpinner'
import SecondaryCard from 'components/SecondaryCard'
import { TruncatedText } from 'components/TruncatedText'

const ModuleIssueDetailsPage = () => {
  const { issueId } = useParams() as { issueId: string }

  const { programKey, moduleKey } = useParams() as {
    programKey: string
    moduleKey: string
    issueId: string
  }
  const { data, loading } = useQuery(GET_MODULE_ISSUE_VIEW, {
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
  })
  const [unassignIssue, { loading: unassigning }] = useMutation(UNASSIGN_ISSUE_FROM_USER, {
    refetchQueries: [
      {
        query: GET_MODULE_ISSUE_VIEW,
        variables: { programKey, moduleKey, number: Number(issueId) },
      },
    ],
    awaitRefetchQueries: true,
  })

  const issue = useMemo(() => data?.getModule?.issueByNumber || null, [data])
  const issueGlobalId = issue?.id as string | undefined
  const issuePk = useMemo(() => {
    if (!issueGlobalId) return null
    try {
      const decoded = atob(issueGlobalId)
      const pk = parseInt(decoded.split(':').pop() || '', 10)
      return Number.isNaN(pk) ? null : pk
    } catch {
      return null
    }
  }, [issueGlobalId])

  if (loading) return <LoadingSpinner />
  if (!issue)
    return <ErrorDisplay statusCode={404} title="Issue Not Found" message="Issue not found" />

  const assignees = issue.assignees || []
  const labels: string[] = issue.labels || []
  const visible = labels.slice(0, 5)
  const remaining = labels.length - visible.length

  return (
    <div className="min-h-screen bg-white p-8 text-gray-700 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-5xl">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="flex items-center gap-2 text-3xl font-bold">
              <TruncatedText text={issue.title} />
            </h1>
            <div className="mt-1 text-sm text-gray-500">
              {issue.organizationName}/{issue.repositoryName} • #{issue.number}
            </div>
          </div>
          <ActionButton url={issue.url} tooltipLabel="View on GitHub">
            <FontAwesomeIcon icon={faLink} /> View on GitHub
          </ActionButton>
        </div>

        <SecondaryCard title={<AnchorTitle title="Description" />}>
          <div className={`prose dark:prose-invert line-clamp-[15] max-w-none whitespace-pre-wrap`}>
            {issue.summary || 'No description.'}
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
            {visible.map((l: string, index) => (
              <button
                key={index}
                className="rounded-lg border border-gray-400 px-3 py-1 text-sm hover:bg-gray-200 dark:border-gray-300 dark:hover:bg-gray-700"
              >
                {l}
              </button>
            ))}
            {remaining > 0 && (
              <button className="rounded-lg border border-gray-400 px-3 py-1 text-sm hover:bg-gray-200 dark:border-gray-300 dark:hover:bg-gray-700">
                +{remaining} more
              </button>
            )}
          </div>
        </div>

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
                  <Image
                    src={a.avatarUrl}
                    alt={a.login}
                    width={32}
                    height={32}
                    className="rounded-full"
                  />
                  <span className="text-sm font-medium">{a.login || a.name}</span>
                </Link>
                <button
                  type="button"
                  aria-label={`Unassign @${a.login}`}
                  disabled={!issuePk || unassigning}
                  onClick={async () => {
                    if (!issuePk || unassigning) return
                    await unassignIssue({
                      variables: { programKey, moduleKey, issueId: issuePk, userLogin: a.login },
                    })
                  }}
                  className={`inline-flex items-center justify-center rounded-md border p-1.5 text-sm ${!issuePk ? 'cursor-not-allowed border-gray-300 text-gray-400 dark:border-gray-600' : 'border-gray-300 hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-800'}`}
                  title={unassigning ? 'Unassigning…' : `Unassign @${a.login}`}
                >
                  <FontAwesomeIcon icon={faXmark} />
                </button>
              </div>
            ))}
            {assignees.length === 0 && <span className="text-sm text-gray-400">Unassigned</span>}
          </div>
        </div>

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
                  <Image
                    src={u.avatarUrl}
                    alt={u.login}
                    width={32}
                    height={32}
                    className="rounded-full"
                  />
                  <span className="text-sm font-medium">@{u.login}</span>
                </div>
                <button
                  type="button"
                  disabled={!issuePk || assigning}
                  onClick={async () => {
                    if (!issuePk || assigning) return
                    await assignIssue({
                      variables: { programKey, moduleKey, issueId: issuePk, userLogin: u.login },
                    })
                  }}
                  className={`inline-flex items-center gap-1.5 rounded-md border px-3 py-1 text-sm ${!issuePk ? 'cursor-not-allowed border-gray-300 text-gray-400 dark:border-gray-600' : 'border-gray-300 hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-800'}`}
                  title={
                    !issuePk ? 'Loading issue…' : assigning ? 'Assigning…' : 'Assign to this user'
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
