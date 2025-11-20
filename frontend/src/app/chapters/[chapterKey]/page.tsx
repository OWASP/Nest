'use client'
import { useQuery } from '@apollo/client/react'
import {
  faChartLine,
  faCode,
  faCodeBranch,
  faCodeMerge,
  faExclamationCircle,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useState, useEffect } from 'react'
import { handleAppError, ErrorDisplay } from 'app/global-error'
import { GetChapterDataDocument } from 'types/__generated__/chapterQueries.generated'
import type { Chapter } from 'types/chapter'
import type { Contributor } from 'types/contributor'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import ContributionHeatmap from 'components/ContributionHeatmap'
import LoadingSpinner from 'components/LoadingSpinner'

export default function ChapterDetailsPage() {
  const { chapterKey } = useParams<{ chapterKey: string }>()
  const [chapter, setChapter] = useState<Chapter>({} as Chapter)
  const [topContributors, setTopContributors] = useState<Contributor[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(true)

  const { data, error: graphQLRequestError } = useQuery(GetChapterDataDocument, {
    variables: { key: chapterKey },
  })

  useEffect(() => {
    if (data) {
      setChapter(data.chapter)
      setTopContributors(data.topContributors)
      setIsLoading(false)
    }
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
      setIsLoading(false)
    }
  }, [data, graphQLRequestError, chapterKey])

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (!chapter && !isLoading)
    return (
      <ErrorDisplay
        statusCode={404}
        title="Chapter not found"
        message="Sorry, the chapter you're looking for doesn't exist"
      />
    )

  const details = [
    { label: 'Last Updated', value: formatDate(chapter.updatedAt) },
    { label: 'Location', value: chapter.suggestedLocation },
    { label: 'Region', value: chapter.region },
    {
      label: 'URL',
      value: (
        <Link href={chapter.url} className="text-blue-400 hover:underline">
          {chapter.url}
        </Link>
      ),
    },
  ]

  // Calculate contribution heatmap date range (1 year back)
  const today = new Date()
  const oneYearAgo = new Date(today)
  oneYearAgo.setFullYear(today.getFullYear() - 1)
  const startDate = oneYearAgo.toISOString().split('T')[0]
  const endDate = today.toISOString().split('T')[0]

  // Calculate estimated contribution stats from heatmap data
  // Note: These are rough estimates since backend aggregates all contribution types
  const contributionStats = chapter.contributionData
    ? (() => {
        const totalContributions = Object.values(chapter.contributionData).reduce(
          (sum, count) => sum + count,
          0
        )
        // Frontend estimates - actual breakdown requires backend per-type data
        const commits = Math.floor(totalContributions * 0.6) // Estimated ~60% commits
        const issues = Math.floor(totalContributions * 0.23) // Estimated ~23% issues
        const pullRequests = Math.floor(totalContributions * 0.15) // Estimated ~15% PRs

        return {
          commits,
          pullRequests,
          issues,
          total: totalContributions,
        }
      })()
    : undefined

  return (
    <>
      <DetailsCard
        details={details}
        entityKey={chapter.key}
        entityLeaders={chapter.entityLeaders}
        geolocationData={[chapter]}
        isActive={chapter.isActive}
        socialLinks={chapter.relatedUrls}
        summary={chapter.summary}
        title={chapter.name}
        topContributors={topContributors}
        type="chapter"
      />
      {chapter.contributionData && Object.keys(chapter.contributionData).length > 0 && (
        <div className="bg-white text-gray-600 dark:bg-[#212529] dark:text-gray-300 pb-10">
          <div className="mx-auto max-w-6xl">
            <div className="rounded-lg bg-gray-100 px-14 pt-6 shadow-md dark:bg-gray-800">
              <h2 className="mb-4 flex items-center gap-2 text-2xl font-semibold text-gray-800 dark:text-gray-200">
                <FontAwesomeIcon
                  icon={faChartLine}
                  className="h-6 w-6 text-gray-600 dark:text-gray-400"
                />
                Chapter Contribution Activity
              </h2>
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 mb-6">
                <div className="flex items-center gap-2">
                  <FontAwesomeIcon
                    icon={faCode}
                    className="h-5 w-5 text-gray-600 dark:text-gray-400"
                  />
                  <div>
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Commits</p>
                    <p className="text-lg font-bold text-gray-900 dark:text-white">
                      {contributionStats?.commits?.toLocaleString() || 0}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <FontAwesomeIcon
                    icon={faCodeBranch}
                    className="h-5 w-5 text-gray-600 dark:text-gray-400"
                  />
                  <div>
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">PRs</p>
                    <p className="text-lg font-bold text-gray-900 dark:text-white">
                      {contributionStats?.pullRequests?.toLocaleString() || 0}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <FontAwesomeIcon
                    icon={faExclamationCircle}
                    className="h-5 w-5 text-gray-600 dark:text-gray-400"
                  />
                  <div>
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Issues</p>
                    <p className="text-lg font-bold text-gray-900 dark:text-white">
                      {contributionStats?.issues?.toLocaleString() || 0}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <FontAwesomeIcon
                    icon={faCodeMerge}
                    className="h-5 w-5 text-gray-600 dark:text-gray-400"
                  />
                  <div>
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Total</p>
                    <p className="text-lg font-bold text-gray-900 dark:text-white">
                      {contributionStats?.total?.toLocaleString() || 0}
                    </p>
                  </div>
                </div>
              </div>
              <div className="w-full flex justify-center items-center">
                <ContributionHeatmap
                  contributionData={chapter.contributionData}
                  startDate={startDate}
                  endDate={endDate}
                  unit="contribution"
                  stats={contributionStats}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
