'use client'
import { useQuery } from '@apollo/client'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useState, useEffect } from 'react'
import { GET_CHAPTER_DATA } from 'server/queries/chapterQueries'
import { ChapterTypeGraphQL } from 'types/chapter'
import { TopContributorsTypeGraphql } from 'types/contributor'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'
import { handleAppError, ErrorDisplay } from 'app/global-error'
import SponsorBanner from 'components/SponsorBanner'
import SecondaryCard from 'components/SecondaryCard'

export default function ChapterDetailsPage() {
  const { chapterKey } = useParams()
  const [chapter, setChapter] = useState<ChapterTypeGraphQL>({} as ChapterTypeGraphQL)
  const [topContributors, setTopContributors] = useState<TopContributorsTypeGraphql[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(true)

  const { data, error: graphQLRequestError } = useQuery(GET_CHAPTER_DATA, {
    variables: { key: chapterKey },
  })

  useEffect(() => {
    if (data) {
      setChapter(data?.chapter)
      setTopContributors(data?.topContributors)
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
  return (
    <>
      <DetailsCard
        details={details}
        geolocationData={chapter}
        is_active={chapter.isActive}
        socialLinks={chapter.relatedUrls}
        summary={chapter.summary}
        title={chapter.name}
        topContributors={chapter.topContributors}
        type="chapter"
      />
      <div className="mt-8 max-w-6xl mx-auto">
        <SecondaryCard>
          <SponsorBanner
            entityType="chapter"
            entityKey={chapterKey as string}
            entityName={chapter.name}
          />
        </SecondaryCard>
      </div>
    </>
  )
}
