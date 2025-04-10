'use client'
import { useQuery } from '@apollo/client'
import { addToast } from '@heroui/toast'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useState, useEffect } from 'react'
import { GET_CHAPTER_DATA } from 'server/queries/chapterQueries'
import { ChapterTypeGraphQL } from 'types/chapter'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'
import { handleAppError, ErrorDisplay } from 'app/global-error'

export default function ChapterDetailsPage() {
  const { chapterKey } = useParams()
  const [chapter, setChapter] = useState<ChapterTypeGraphQL>({} as ChapterTypeGraphQL)
  const [isLoading, setIsLoading] = useState<boolean>(true)

  const { data, error: graphQLRequestError } = useQuery(GET_CHAPTER_DATA, {
    variables: { key: chapterKey },
  })

  useEffect(() => {
    if (data) {
      setChapter(data?.chapter)
      setIsLoading(false)
    }
    if (graphQLRequestError) {
      addToast({
        description: 'Unable to complete the requested operation.',
        title: 'GraphQL Request Failed',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'danger',
        variant: 'solid',
      })
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
  )
}
