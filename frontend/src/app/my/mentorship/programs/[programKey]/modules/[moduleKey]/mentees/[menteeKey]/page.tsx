'use client'

import { useQuery } from '@apollo/client/react'
import Image from 'next/image'
import { useParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GetModuleMenteeDetailsDocument } from 'types/__generated__/menteeQueries.generated'
import { Issue } from 'types/issue'
import { MenteeDetails } from 'types/mentorship'
import { LabelList } from 'components/LabelList'
import LoadingSpinner from 'components/LoadingSpinner'
import SecondaryCard from 'components/SecondaryCard'

const MenteeProfilePage = () => {
  const { programKey, moduleKey, menteeKey } = useParams<{
    programKey: string
    moduleKey: string
    menteeKey: string
  }>()

  const [menteeDetails, setMenteeDetails] = useState<MenteeDetails | null>(null)
  const [menteeIssues, setMenteeIssues] = useState<Issue[]>([])

  const [isLoading, setIsLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState<string>('all')

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
      setMenteeDetails(data.getMenteeDetails ?? null)
      setMenteeIssues(data.getMenteeModuleIssues ?? [])
    }
    if (error) {
      handleAppError(error)
    }
    if (data || error) {
      setIsLoading(false)
    }
  }, [data, error])

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

  const issueMap: Record<string, Issue[]> = {
    all: menteeIssues,
    open: openIssues,
    closed: closedIssues,
  }
  const filteredIssues = issueMap[statusFilter] || closedIssues

  return (
    <div className="min-h-screen p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl space-y-6">
        {/* Header */}
        <SecondaryCard>
          <div className="flex items-center space-x-6">
            <Image
              width={80}
              height={80}
              src={menteeDetails.avatarUrl}
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

        {/* Stats */}
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <SecondaryCard title="Total Issues">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                {menteeIssues.length}
              </div>
            </div>
          </SecondaryCard>

          <SecondaryCard title="Open Issues">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 dark:text-green-400">
                {openIssues.length}
              </div>
            </div>
          </SecondaryCard>

          <SecondaryCard title="Closed Issues">
            <div className="text-center">
              <div className="text-3xl font-bold text-gray-600 dark:text-gray-400">
                {closedIssues.length}
              </div>
            </div>
          </SecondaryCard>
        </div>

        {/* Mentee Information */}
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

        {/* Domains and Skills */}
        {(menteeDetails.domains?.length > 0 || menteeDetails.tags?.length > 0) && (
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

        {/* Issues - moved to the end */}
        <SecondaryCard title="Issues Assigned">
          {menteeIssues.length === 0 ? (
            <p className="py-8 text-center text-gray-500 italic dark:text-gray-400">
              No issues assigned to this mentee in this module
            </p>
          ) : (
            <div>
              {/* Filter Dropdown */}
              <div className="mb-4">
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                >
                  <option value="all">All Issues ({menteeIssues.length})</option>
                  <option value="open">Open Issues ({openIssues.length})</option>
                  <option value="closed">Closed Issues ({closedIssues.length})</option>
                </select>
              </div>

              <div className="space-y-4">
                {filteredIssues.map((issue) => (
                  <div
                    key={issue.number}
                    className="rounded-lg border border-gray-200 p-4 hover:bg-gray-50 dark:border-gray-600 dark:hover:bg-gray-700"
                  >
                    <div className="flex items-center pb-4">
                      <a
                        href={issue.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-medium text-gray-900 transition-colors hover:text-blue-600 dark:text-white dark:hover:text-blue-400"
                      >
                        {issue.title}
                      </a>
                    </div>

                    {issue.labels && issue.labels.length > 0 && (
                      <div className="mb-2">
                        <LabelList labels={issue.labels} maxVisible={3} />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </SecondaryCard>
      </div>
    </div>
  )
}

export default MenteeProfilePage
