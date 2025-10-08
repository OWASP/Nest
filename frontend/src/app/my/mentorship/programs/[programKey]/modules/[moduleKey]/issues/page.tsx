'use client'

import { useQuery } from '@apollo/client'
import { Select, SelectItem } from '@heroui/select'
import Image from 'next/image'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import { useEffect, useMemo, useState } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GET_MODULE_ISSUES } from 'server/queries/moduleQueries'
import type { Issue } from 'types/issue'
import LoadingSpinner from 'components/LoadingSpinner'
import { TruncatedText } from 'components/TruncatedText'

const LABEL_ALL = 'all'

const IssuesPage = () => {
  const { programKey, moduleKey } = useParams() as { programKey: string; moduleKey: string }
  const router = useRouter()
  const searchParams = useSearchParams()
  const [selectedLabel, setSelectedLabel] = useState<string>(searchParams.get('label') || LABEL_ALL)

  const { data, loading, error } = useQuery(GET_MODULE_ISSUES, {
    variables: { programKey, moduleKey },
    skip: !programKey || !moduleKey,
    fetchPolicy: 'cache-and-network',
  })

  useEffect(() => {
    if (error) handleAppError(error)
  }, [error])

  const moduleData = data?.getModule
  const moduleIssues: Issue[] = useMemo(() => {
    const issues = (moduleData?.issues || []).map((i) => ({
      author: i.author,
      createdAt: i.createdAt,
      hint: '',
      labels: i.labels || [],
      number: i.number,
      organizationName: i.organizationName,
      projectName: moduleData?.projectName || '',
      projectUrl: '',
      repository: undefined,
      repositoryLanguages: [],
      summary: '',
      title: i.title,
      updatedAt: i.createdAt,
      url: i.url,
      objectID: i.id,
    }))
    if (selectedLabel === LABEL_ALL) return issues
    return issues.filter((iss) => (iss.labels || []).includes(selectedLabel))
  }, [moduleData, selectedLabel])

  const allLabels: string[] = useMemo(() => {
    const labels = new Set<string>()
    ;(moduleData?.issues || []).forEach((i) =>
      (i.labels || []).forEach((l: string) => labels.add(l))
    )
    return Array.from(labels).sort()
  }, [moduleData])

  const handleLabelChange = (label: string) => {
    setSelectedLabel(label)
    const params = new URLSearchParams(searchParams.toString())
    if (label === LABEL_ALL) {
      params.delete('label')
    } else {
      params.set('label', label)
    }
    router.replace(`?${params.toString()}`)
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

        <div className="overflow-hidden rounded-lg border border-gray-200 dark:border-gray-700">
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
                    <button
                      type="button"
                      onClick={() =>
                        router.push(
                          `/my/mentorship/programs/${programKey}/modules/${moduleKey}/issues/${issue.number}`
                        )
                      }
                      className="block max-w-xl text-left hover:underline"
                    >
                      <TruncatedText
                        text={`${issue.title.slice(0, 50)}${issue.title.length > 50 ? '…' : ''}`}
                      />
                    </button>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-2">
                      {(() => {
                        const labels = issue.labels || []
                        const visible = labels.slice(0, 5)
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
                    {((assignees) =>
                      assignees?.length ? (
                        <div className="flex items-center gap-2">
                          <div className="flex items-center gap-2">
                            <Image
                              height={24}
                              width={24}
                              src={assignees[0].avatarUrl}
                              alt={assignees[0].login}
                              className="rounded-full"
                            />
                            <span>{assignees[0].login || assignees[0].name}</span>
                          </div>
                          {assignees.length > 1 && (
                            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-gray-200 text-xs font-medium text-gray-600 dark:bg-gray-700 dark:text-gray-300">
                              +{assignees.length - 1}
                            </div>
                          )}
                        </div>
                      ) : (
                        <span className="text-gray-400">Unassigned</span>
                      ))(
                      (data?.getModule?.issues || []).find((i) => i.id === issue.objectID)
                        ?.assignees
                    )}
                  </td>
                </tr>
              ))}
              {moduleIssues.length === 0 && (
                <tr>
                  <td
                    colSpan={3}
                    className="px-6 py-8 text-center text-sm text-gray-500 dark:text-gray-400"
                  >
                    No issues found for the selected filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default IssuesPage
