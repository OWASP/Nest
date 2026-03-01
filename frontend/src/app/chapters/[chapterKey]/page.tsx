'use client'
import { useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useEffect } from 'react'
import { handleAppError, ErrorDisplay } from 'app/global-error'
import { GetChapterDataDocument } from 'types/__generated__/chapterQueries.generated'
import type { Chapter } from 'types/chapter'
import { getContributionStats } from 'utils/contributionDataUtils'
import { formatDate, getDateRange } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'

export default function ChapterDetailsPage() {
  const { chapterKey } = useParams<{ chapterKey: string }>()

  const {
    data,
    error: graphQLRequestError,
    loading: isLoading,
  } = useQuery(GetChapterDataDocument, {
    variables: { key: chapterKey },
  })

  const chapter = data?.chapter
  const topContributors = data?.topContributors

  useEffect(() => {
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
    }
  }, [graphQLRequestError, chapterKey])

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (graphQLRequestError) {
    return (
      <ErrorDisplay
        statusCode={500}
        title="Error loading chapter"
        message="An error occurred while loading the chapter data"
      />
    )
  }

  if (!data || !chapter) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Chapter not found"
        message="Sorry, the chapter you're looking for doesn't exist"
      />
    )
  }

  const slackChannelUrl = (slackChannelId: string) =>
    `https://owasp.slack.com/archives/${slackChannelId}`

  const details = [
    { label: 'Last Updated', value: formatDate(chapter.updatedAt) },
    { label: 'Location', value: chapter.suggestedLocation ?? '' },
    { label: 'Region', value: chapter.region ?? '' },
    {
      label: 'URL',
      value: (
        <Link href={chapter.url} className="text-blue-400 hover:underline">
          {chapter.url}
        </Link>
      ),
    },
    ...(chapter.entityChannels && chapter.entityChannels.length > 0
      ? [
          {
            label: 'Slack',
            value: (
              <div className="inline-flex flex-wrap gap-3">
                {chapter.entityChannels.map((ch) => (
                  <Link
                    key={ch.slackChannelId}
                    href={slackChannelUrl(ch.slackChannelId)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:underline"
                  >
                    {ch.name}
                  </Link>
                ))}
              </div>
            ),
          },
        ]
      : []),
  ]

  const { startDate, endDate } = getDateRange({ years: 1 })

  const contributionStats = getContributionStats(
    chapter.contributionStats,
    chapter.contributionData
  )

  return (
    <DetailsCard
      contributionData={chapter.contributionData}
      contributionStats={contributionStats}
      details={details}
      endDate={endDate}
      entityKey={chapter.key}
      entityLeaders={chapter.entityLeaders}
      geolocationData={[chapter as unknown as Chapter]}
      isActive={chapter.isActive}
      socialLinks={chapter.relatedUrls}
      startDate={startDate}
      summary={chapter.summary}
      title={chapter.name}
      topContributors={topContributors}
      type="chapter"
    />
  )
}
