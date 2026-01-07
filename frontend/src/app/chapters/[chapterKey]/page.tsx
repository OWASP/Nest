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
import { formatDate, getDateRange } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'

export default function ChapterDetailsPage() {
  const { chapterKey } = useParams<{ chapterKey: string }>()
  // Fixed: Initialize as null instead of an empty object assertion to satisfy strict checks
  const [chapter, setChapter] = useState<Chapter | null>(null)
  const [topContributors, setTopContributors] = useState<Contributor[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(true)

  const { data, error: graphQLRequestError } = useQuery(GetChapterDataDocument, {
    variables: { key: chapterKey || '' },
    skip: !chapterKey,
  })

  useEffect(() => {
    if (data?.chapter) {
      setChapter(data.chapter as Chapter)
      setTopContributors((data.topContributors as Contributor[]) || [])
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

  // Fixed: Now that chapter is nullable, this check correctly guards all property access below
  if (!chapter) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Chapter not found"
        message="Sorry, the chapter you're looking for doesn't exist"
      />
    )
  }

  const details = [
    { label: 'Last Updated', value: formatDate(chapter.updatedAt ?? '') },
    { label: 'Location', value: chapter.suggestedLocation || 'Not Specified' },
    { label: 'Region', value: chapter.region || 'Not Specified' },
    {
      label: 'URL',
      value: (
        <Link href={chapter.url || '#'} className="text-blue-400 hover:underline">
          {chapter.url || ''}
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
      entityKey={chapter.key || ''}
      entityLeaders={chapter.entityLeaders || []}
      geolocationData={[chapter]}
      isActive={chapter.isActive ?? false}
      socialLinks={chapter.relatedUrls || []}
      startDate={startDate}
      summary={chapter.summary || ''}
      title={chapter.name || ''}
      topContributors={topContributors}
      type="chapter"
    />
  )
}