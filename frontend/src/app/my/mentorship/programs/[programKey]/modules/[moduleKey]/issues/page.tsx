'use client'

import { useQuery } from '@apollo/client/react'
import { Select, SelectItem } from '@heroui/select'
import { Tooltip } from '@heroui/tooltip'
import Image from 'next/image'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import { useEffect, useMemo, useState } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GetModuleIssuesDocument } from 'types/__generated__/moduleQueries.generated'
import LoadingSpinner from 'components/LoadingSpinner'
import Pagination from 'components/Pagination'

const ITEMS_PER_PAGE = 20
const LABEL_ALL = 'all'
const MAX_VISIBLE_LABELS = 5

const IssuesPage = () => {
  const { programKey, moduleKey } = useParams<{ programKey: string; moduleKey: string }>()
  const router = useRouter()
  const searchParams = useSearchParams()
  const [selectedLabel, setSelectedLabel] = useState<string>(searchParams.get('label') || LABEL_ALL)
  const [currentPage, setCurrentPage] = useState(1)

  const { data, loading, error } = useQuery(GetModuleIssuesDocument, {
    variables: {
      programKey,
      moduleKey,
      limit: ITEMS_PER_PAGE,
      offset: (currentPage - 1) * ITEMS_PER_PAGE,
      label: selectedLabel === LABEL_ALL ? null : selectedLabel,
    },
    skip: !programKey || !moduleKey,
    fetchPolicy: 'cache-and-network',
  })

  useEffect(() => {
    if (error) handleAppError(error)
  }, [error])

  const moduleData = data?.getModule
  type ModuleIssueRow = {
    objectID: string
    number: number
    title: string
    state: string
    isMerged: boolean
    labels: string[]
    assignees: Array<{ avatarUrl: string; login: string; name: string }>
  }

  const moduleIssues: ModuleIssueRow[] = useMemo(() => {
    return (moduleData?.issues || []).map((i) => ({
      objectID: i.id,
      number: i.number,
      title: i.title,
      state: i.state,
      isMerged: i.isMerged,
      labels: i.labels || [],
      assignees: i.assignees || [],
    }))
  }, [moduleData])

  const totalPages = Math.ceil((moduleData?.issuesCount || 0) / ITEMS_PER_PAGE)

  const allLabels: string[] = useMemo(() => {
    const serverLabels = moduleData?.availableLabels
    if (serverLabels && serverLabels.length > 0) {
      return serverLabels
    }

    const labels = new Set<string>()
    ;(moduleData?.issues || []).forEach((i) =>
      (i.labels || []).forEach((l: string) => labels.add(l))
    )
    return Array.from(labels).sort((a, b) => a.localeCompare(b))
  }, [moduleData])

  const handleLabelChange = (label: string) => {
    setSelectedLabel(label)
    setCurrentPage(1)
    const params = new URLSearchParams(searchParams.toString())
    if (label === LABEL_ALL) {
      params.delete('label')
    } else {
      params.set('label', label)
    }
    router.replace(`?${params.toString()}`)
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
  }

  const handleIssueClick = (issueNumber: number) => {
    router.push(`/my/mentorship/programs/${programKey}/modules/${moduleKey}/issues/${issueNumber}`)
  }

  if (loading) return <LoadingSpinner />
  if (!moduleData)
    return <ErrorDisplay statusCode={404} title="Module Not Found" message="Module not found" />

  return (
    <div className="mt-16 min-h-screen bg-white p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-3xl font-bold">{moduleData.name} Issues</h1>
          <div className="inline-flex h-12 items-center rounded-lg bg-gray-200 dark:bg-[#323232]">
            <Select
              labelPlacement="outside-left"
              size="md"
              aria-label="Filter by label"
              label="Label :"
              classNames={{
                label:
                  'font-small text-sm text-gray-600 hover:cursor-pointer dark:text-gray-300 pl-[1.4rem] w-auto',
                trigger: 'bg-gray-200 dark:bg-[#323232] pl-0 text-nowrap w-40',
                popoverContent: 'text-md min-w-40 dark:bg-[#323232] rounded-none p-0',
              }}
              selectedKeys={new Set([selectedLabel])}
              onSelectionChange={(keys) => {
                const [key] = Array.from(keys as Set<string>)
                if (key) handleLabelChange(key)
              }}
            >
              {[LABEL_ALL, ...allLabels].map((l) => (
                <SelectItem
                  key={l}
                  classNames={{
                    base: 'text-sm hover:bg-[#D1DBE6] dark:hover:bg-[#454545] rounded-none px-3 py-0.5',
                  }}
                >
                  {l === LABEL_ALL ? 'All' : l}
                </SelectItem>
              ))}
            </Select>
          </div>
        </div>

        {/* Desktop Table - unchanged */}
        <div className="hidden overflow-hidden rounded-lg border border-gray-200 lg:block dark:border-gray-700">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-[#2a2e33]">
              <tr>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-400"
                >
                  Title
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-400"
                >
                  Status
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-400"
                >
                  Labels
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-400"
                >
                  Assignee
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white dark:divide-gray-700 dark:bg-[#1f2327]">
              {moduleIssues.map((issue) => (
                <tr key={issue.objectID} className="hover:bg-gray-50 dark:hover:bg-[#2a2e33]">
                  <td className="px-6 py-4 text-sm font-medium whitespace-nowrap text-blue-600 dark:text-blue-400">
                    <Tooltip
                      closeDelay={100}
                      delay={100}
                      showArrow
                      content={issue.title}
                      placement="bottom"
                      isDisabled={issue.title.length > 50 ? false : true}
                    >
                      <button
                        type="button"
                        onClick={() => handleIssueClick(Number(issue.number))}
                        className="block max-w-md cursor-pointer truncate text-left hover:underline"
                      >
                        {issue.title}
                      </button>
                    </Tooltip>
                  </td>
                  <td className="px-6 py-4 text-center text-sm whitespace-nowrap">
                    <div className="flex justify-center">
                      <span
                        className={`inline-flex items-center rounded-lg px-2 py-0.5 text-xs font-medium ${
                          issue.state === 'open'
                            ? 'bg-[#238636] text-white'
                            : issue.isMerged
                              ? 'bg-[#8657E5] text-white'
                              : 'bg-[#DA3633] text-white'
                        }`}
                      >
                        {issue.state === 'open' ? 'Open' : issue.isMerged ? 'Merged' : 'Closed'}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-2">
                      {(() => {
                        const labels = issue.labels || []
                        const visible = labels.slice(0, MAX_VISIBLE_LABELS)
                        const remaining = labels.length - visible.length
                        return (
                          <>
                            {visible.map((label) => (
                              <span
                                key={label}
                                className="rounded-lg border border-gray-400 px-2 py-0.5 text-xs text-gray-700 hover:bg-gray-200 dark:border-gray-300 dark:text-gray-300 dark:hover:bg-gray-700"
                              >
                                {label}
                              </span>
                            ))}
                            {remaining > 0 && (
                              <span className="rounded-lg border border-gray-400 px-2 py-0.5 text-xs text-gray-700 hover:bg-gray-200 dark:border-gray-300 dark:text-gray-300 dark:hover:bg-gray-700">
                                +{remaining} more
                              </span>
                            )}
                          </>
                        )
                      })()}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm whitespace-nowrap text-gray-700 dark:text-gray-300">
                    {issue.assignees?.length ? (
                      <div className="flex items-center gap-2">
                        <div className="flex items-center gap-2">
                          <Image
                            height={24}
                            width={24}
                            src={issue.assignees[0].avatarUrl}
                            alt={issue.assignees[0].login}
                            className="rounded-full"
                          />
                          <span className="max-w-[80px] truncate sm:max-w-[100px] md:max-w-[120px] lg:max-w-[150px]">
                            {issue.assignees[0].login || issue.assignees[0].name}
                          </span>
                        </div>
                        {issue.assignees.length > 1 && (
                          <div className="flex h-6 w-6 items-center justify-center rounded-full bg-gray-200 text-xs font-medium text-gray-600 dark:bg-gray-700 dark:text-gray-300">
                            +{issue.assignees.length - 1}
                          </div>
                        )}
                      </div>
                    ) : null}
                  </td>
                </tr>
              ))}
              {moduleIssues.length === 0 && (
                <tr>
                  <td
                    colSpan={4}
                    className="px-6 py-8 text-center text-sm text-gray-500 dark:text-gray-400"
                  >
                    No issues found for the selected filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Mobile & Tablet Cards */}
        <div className="space-y-6 lg:hidden">
          {moduleIssues.map((issue) => (
            <div
              key={issue.objectID}
              className="mt-4 rounded-lg border border-gray-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md dark:border-gray-700 dark:bg-[#1f2327]"
            >
              <div className="mb-3 flex items-start justify-between gap-3">
                <button
                  type="button"
                  onClick={() => handleIssueClick(Number(issue.number))}
                  className="flex-1 text-left text-sm font-medium text-gray-900 hover:text-blue-600 dark:text-gray-100 dark:hover:text-blue-400"
                >
                  {issue.title}
                </button>
                <span
                  className={`inline-flex flex-shrink-0 items-center rounded-full px-2 py-1 text-xs font-medium ${
                    issue.state === 'open'
                      ? 'bg-[#238636] text-white'
                      : issue.isMerged
                        ? 'bg-[#8657E5] text-white'
                        : 'bg-[#DA3633] text-white'
                  }`}
                >
                  {issue.state === 'open' ? 'Open' : issue.isMerged ? 'Merged' : 'Closed'}
                </span>
              </div>

              {issue.labels?.length > 0 && (
                <div className="mb-3 flex flex-wrap gap-1">
                  {issue.labels.slice(0, 3).map((label) => (
                    <span
                      key={label}
                      className="inline-flex items-center rounded-md bg-gray-100 px-2 py-0.5 text-xs text-gray-700 dark:bg-gray-800 dark:text-gray-300"
                    >
                      {label}
                    </span>
                  ))}
                  {issue.labels.length > 3 && (
                    <span className="inline-flex items-center rounded-md bg-gray-100 px-2 py-0.5 text-xs text-gray-500 dark:bg-gray-800 dark:text-gray-400">
                      +{issue.labels.length - 3}
                    </span>
                  )}
                </div>
              )}

              {issue.assignees?.length > 0 && (
                <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                  <Image
                    height={18}
                    width={18}
                    src={issue.assignees[0].avatarUrl}
                    alt={issue.assignees[0].login}
                    className="rounded-full"
                  />
                  <span className="truncate">
                    {issue.assignees[0].login || issue.assignees[0].name}
                    {issue.assignees.length > 1 && ` +${issue.assignees.length - 1}`}
                  </span>
                </div>
              )}
            </div>
          ))}

          {moduleIssues.length === 0 && (
            <div className="rounded-lg border border-gray-200 bg-white p-6 text-center dark:border-gray-700 dark:bg-[#1f2327]">
              <p className="text-sm text-gray-500 dark:text-gray-400">
                No issues found for the selected filter.
              </p>
            </div>
          )}
        </div>

        {/* Pagination Controls */}
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={handlePageChange}
          isLoaded={!loading}
        />
      </div>
    </div>
  )
}

export default IssuesPage
