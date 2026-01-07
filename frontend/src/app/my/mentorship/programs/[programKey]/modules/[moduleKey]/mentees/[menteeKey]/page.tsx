'use client'

import { useQuery } from '@apollo/client/react'
import { Select, SelectItem } from '@heroui/select'
import Image from 'next/image'
import { useParams } from 'next/navigation'
import { useMemo, useEffect, useState } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import {
  GetModuleMenteeDetailsDocument,
  type GetModuleMenteeDetailsQuery,
} from 'types/__generated__/menteeQueries.generated'
import { MenteeDetails } from 'types/mentorship'
import IssuesTable, { type IssueRow } from 'components/IssuesTable'
import { LabelList } from 'components/LabelList'
import LoadingSpinner from 'components/LoadingSpinner'
import Pagination from 'components/Pagination'
import SecondaryCard from 'components/SecondaryCard'

const ITEMS_PER_PAGE = 20

const MenteeProfilePage = () => {
  const { programKey, moduleKey, menteeKey } = useParams<{
    programKey: string
    moduleKey: string
    menteeKey: string
  }>()

  const [menteeDetails, setMenteeDetails] = useState<MenteeDetails | null>(null)
  const [menteeIssuesData, setMenteeIssuesData] = useState<
    GetModuleMenteeDetailsQuery['getMenteeModuleIssues']
  >([])

  const [isLoading, setIsLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [currentPage, setCurrentPage] = useState(1)

  const { data, error } = useQuery(GetModuleMenteeDetailsDocument, {
    variables: {
      programKey,
      moduleKey,
      menteeKey,
    },
    skip: !programKey || !moduleKey || !menteeKey,
    fetchPolicy: 'cache-and-network',
  })

  useEffect(() => {
    if (data) {
      setMenteeDetails(data.getMenteeDetails as MenteeDetails || null)
      setMenteeIssuesData(data.getMenteeModuleIssues || [])
    }
    if (error) {
      handleAppError(error)
    }
    if (data || error) {
      setIsLoading(false)
    }
  }, [data, error])

  const menteeIssues: IssueRow[] = useMemo(() => {
    return (menteeIssuesData || []).map((issue) => ({
      objectID: issue.id,
      number: issue.number,
      title: issue.title,
      state: issue.state,
      isMerged: issue.isMerged,
      labels: issue.labels || [],
      assignees: issue.assignees || [],
      url: issue.url,
    }))
  }, [menteeIssuesData])

  if (isLoading) return <LoadingSpinner />

  if (!menteeDetails) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Mentee Not Found"
        message="Sorry, the mentee you're looking for doesn't exist or is not enrolled in this module."
      />
    )
  }

  const openIssues = menteeIssues.filter((issue) => issue.state.toLowerCase() === 'open')
  const closedIssues = menteeIssues.filter((issue) => issue.state.toLowerCase() === 'closed')

  const issueMap: Record<string, IssueRow[]> = {
    all: menteeIssues,
    open: openIssues,
    closed: closedIssues,
  }
  const filteredIssues = issueMap[statusFilter] || menteeIssues

  const totalPages = Math.ceil(filteredIssues.length / ITEMS_PER_PAGE)
  const paginatedIssues = filteredIssues.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  )

  const statusFilterOptions = [
    { key: 'all', label: 'All', count: menteeIssues.length },
    { key: 'open', label: 'Open', count: openIssues.length },
    { key: 'closed', label: 'Closed', count: closedIssues.length },
  ]

  const handleIssueClick = (issueNumber: number) => {
    const issue = menteeIssues.find((i) => i.number === issueNumber)
    if (issue?.url) {
      window.open(issue.url, '_blank', 'noopener,noreferrer')
    }
  }

  return (
    <div className="min-h-screen p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl space-y-6">
        <SecondaryCard>
          <div className="flex items-center space-x-6">
            <Image
              width={80}
              height={80}
              src={menteeDetails.avatarUrl || '/default-avatar.png'}
              alt={`${menteeDetails.name || menteeDetails.login} avatar`}
              className="h-20 w-20 rounded-full"
            />
            <div className="ml-8">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                {menteeDetails.name || menteeDetails.login}
              </h1>
              <p className="text-lg text-gray-600 dark:text-gray-400">@{menteeDetails.login}</p>
              {menteeDetails.bio && (
                <p className="mt-2 text-gray-700 dark:text-gray-300">{menteeDetails.bio}</p>
              )}
            </div>
          </div>
        </SecondaryCard>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <SecondaryCard title="Completed Levels">
            <p className="text-gray-500 italic dark:text-gray-400">
              No completed levels data available yet
            </p>
          </SecondaryCard>

          <SecondaryCard title="Penalties">
            <p className="text-gray-500 italic dark:text-gray-400">
              No penalties data available yet
            </p>
          </SecondaryCard>
        </div>

        {((menteeDetails.domains?.length || 0) > 0 || (menteeDetails.tags?.length || 0) > 0) && (
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {menteeDetails.domains && menteeDetails.domains.length > 0 && (
              <SecondaryCard title="Domains">
                <LabelList labels={menteeDetails.domains} maxVisible={5} />
              </SecondaryCard>
            )}

            {menteeDetails.tags && menteeDetails.tags.length > 0 && (
              <SecondaryCard title="Skills & Technologies">
                <LabelList labels={menteeDetails.tags} maxVisible={5} />
              </SecondaryCard>
            )}
          </div>
        )}

        <SecondaryCard>
          <div className="w-full">
            <div className="flex justify-between">
              <h1 className="text-3xl font-bold">Assigned Issues</h1>
              <div className="mb-4 flex justify-end">
                <div className="inline-flex h-12 items-center rounded-lg bg-gray-200 dark:bg-[#323232]">
                  <Select
                    size="md"
                    aria-label="Filter by status"
                    selectedKeys={new Set([statusFilter])}
                    onSelectionChange={(keys) => {
                      const [key] = Array.from(keys as Set<string>)
                      if (key) {
                        setStatusFilter(key)
                        setCurrentPage(1)
                      }
                    }}
                    classNames={{
                      trigger: 'bg-gray-200 dark:bg-[#323232] pl-4 text-nowrap w-32',
                      popoverContent: 'text-md min-w-32 dark:bg-[#323232] rounded-none p-0',
                    }}
                  >
                    {statusFilterOptions.map((option) => (
                      <SelectItem
                        key={option.key}
                        classNames={{
                          base: 'text-sm hover:bg-[#D1DBE6] dark:hover:bg-[#454545] rounded-none px-3 py-0.5',
                        }}
                      >
                        {option.key === 'all' ? option.label : `${option.label} (${option.count})`}
                      </SelectItem>
                    ))}
                  </Select>
                </div>
              </div>
            </div>

            <IssuesTable
              issues={paginatedIssues}
              showAssignee={false}
              onIssueClick={handleIssueClick}
              emptyMessage="No issues found for the selected filter."
            />

            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
              isLoaded={!isLoading}
            />
          </div>
        </SecondaryCard>
      </div>
    </div>
  )
}

export default MenteeProfilePage