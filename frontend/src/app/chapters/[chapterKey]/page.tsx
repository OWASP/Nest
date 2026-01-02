'use client'
import { useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useEffect } from 'react'
import { handleAppError, ErrorDisplay } from 'app/global-error'
import { GetChapterDataDocument } from 'types/__generated__/chapterQueries.generated'
import type { Chapter } from 'types/chapter'
import type { Contributor } from 'types/contributor'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'

export default function ChapterDetailsPage() {
  const { chapterKey } = useParams<{ chapterKey: string }>()
  const { data, loading, error: graphQLRequestError } = useQuery(GetChapterDataDocument, {
    variables: { key: chapterKey },
  })

  useEffect(() => {
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
    }
  }, [graphQLRequestError, chapterKey])

  if (loading) {
    return <LoadingSpinner />
  }

  if (!data?.chapter && !loading)
    return (
      <ErrorDisplay
        statusCode={404}
        title="Chapter not found"
        message="Sorry, the chapter you're looking for doesn't exist"
      />
    )

  const chapter = data.chapter
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
      entityKey={chapter.key}
      entityLeaders={chapter.entityLeaders}
      geolocationData={[chapter]}
      isActive={chapter.isActive}
      socialLinks={chapter.relatedUrls}
      summary={chapter.summary}
      title={chapter.name}
      topContributors={data.topContributors}
      type="chapter"
    />
  )
}
