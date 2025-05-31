'use client'
import { useQuery } from '@apollo/client'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useState, useEffect } from 'react'
import { handleAppError, ErrorDisplay } from 'app/global-error'
import { GET_CHAPTER_DATA } from 'server/queries/chapterQueries'
import { ChapterTypeGraphQL } from 'types/chapter'
import { TopContributorsTypeGraphql } from 'types/contributor'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'
import PageLayout from 'components/PageLayout'

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
  return (
    <PageLayout
      bcItems={[
        { title: 'Chapters', href: '/chapters' },
        { title: chapter.name, href: `/chapters/${chapter.key}` },
      ]}
    >
      <DetailsCard
        details={details}
        geolocationData={chapter}
        is_active={chapter.isActive}
        socialLinks={chapter.relatedUrls}
        summary={chapter.summary}
        title={chapter.name}
        topContributors={topContributors}
        type="chapter"
      />
    </PageLayout>
  )
}
