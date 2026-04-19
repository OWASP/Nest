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
import type { SponsorInfo } from 'components/SponsorBadge'

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

  const sponsors: SponsorInfo[] = (chapter?.sponsors || []).map(
    (sponsor: {
      key: string
      name: string
      sponsorType: string
      imageUrl: string
      url: string
      description?: string
      status?: string
    }) => ({
      key: sponsor.key,
      name: sponsor.name,
      sponsorType: sponsor.sponsorType,
      imageUrl: sponsor.imageUrl,
      url: sponsor.url,
      description: sponsor.description || '',
    })
  )

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
      sponsors={sponsors}
      startDate={startDate}
      summary={chapter.summary}
      title={chapter.name}
      topContributors={topContributors}
      type="chapter"
    />
  )
}
