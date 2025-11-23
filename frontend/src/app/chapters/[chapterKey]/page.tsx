'use client'
import { useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useState, useEffect } from 'react'
import { handleAppError, ErrorDisplay } from 'app/global-error'
import { GetChapterDataDocument } from 'types/__generated__/chapterQueries.generated'
import type { Chapter } from 'types/chapter'
import type { Contributor } from 'types/contributor'
import { getContributionStats } from 'utils/contributionDataUtils'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import ContributionHeatmap from 'components/ContributionHeatmap'
import ContributionStats from 'components/ContributionStats'
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

  // Use real contribution stats from API with fallback to legacy data
  const contributionStats = getContributionStats(
    chapter.contributionStats,
    chapter.contributionData
  )

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
        <div className="bg-white px-4 pb-10 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
          <div className="mx-auto w-full max-w-6xl">
            <div className="rounded-lg bg-gray-100 px-4 pt-6 shadow-md sm:px-6 lg:px-10 dark:bg-gray-800">
              <ContributionStats title="Chapter Contribution Activity" stats={contributionStats} />
              <div className="mt-4 flex w-full items-center justify-center">
                <div className="w-full">
                  <ContributionHeatmap
                    contributionData={chapter.contributionData}
                    startDate={startDate}
                    endDate={endDate}
                    unit="contribution"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
