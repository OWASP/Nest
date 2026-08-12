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
import { getLinkableEntityChannels } from 'utils/entityChannels'
import Contributions from 'components/cards/Contributions'
import Contributors from 'components/cards/Contributors'
import Header from 'components/cards/Header'
import Leaders from 'components/cards/Leaders'
import Metadata from 'components/cards/Metadata'
import PageWrapper from 'components/cards/PageWrapper'
import Summary from 'components/cards/Summary'
import Tags from 'components/cards/Tags'
import EntityChannelLinks from 'components/EntityChannelLinks'
import LoadingSpinner from 'components/LoadingSpinner'
import SponsorCard from 'components/SponsorCard'

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

  const channels = getLinkableEntityChannels(chapter.entityChannels)

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
    ...(channels.length > 0
      ? [
          {
            label: 'Channels',
            value: <EntityChannelLinks channels={channels} />,
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
    <PageWrapper>
      <Header title={chapter.name} isActive={chapter.isActive} isArchived={false} />

      <Summary summary={chapter.summary} />

      <Metadata
        details={details}
        showGeolocation={true}
        geolocationData={[chapter as unknown as Chapter]}
        showSocialLinks={true}
        socialLinks={chapter.relatedUrls}
        detailsTitle="Chapter Details"
      />

      <Tags entityKey={chapter.key} />

      <Leaders entityLeaders={chapter.entityLeaders} />

      <Contributions
        hasContributions={
          !!(
            (contributionStats && contributionStats.total > 0) ||
            (chapter.contributionData && Object.keys(chapter.contributionData).length > 0)
          )
        }
        contributionStats={contributionStats}
        contributionData={chapter.contributionData}
        startDate={startDate}
        endDate={endDate}
        title="Chapter Contribution Activity"
      />

      <Contributors entityKey={chapter.key} topContributors={topContributors} />

      {chapter.key && chapter.name && (
        <SponsorCard target={chapter.key} title={chapter.name} type="chapter" />
      )}
    </PageWrapper>
  )
}
