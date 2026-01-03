'use client'

import { useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { handleAppError, ErrorDisplay } from 'app/global-error'
import { GetChapterDataDocument } from 'types/__generated__/chapterQueries.generated'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'

export default function ChapterDetailsPage() {
  const { chapterKey } = useParams<{ chapterKey: string }>()

  const { data, error, loading } = useQuery(GetChapterDataDocument, {
    variables: { key: chapterKey },
  })

  if (error) {
    handleAppError(error)
  }

  if (loading) {
    return <LoadingSpinner />
  }

  if (!data?.chapter) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Chapter not found"
        message="Sorry, the chapter you're looking for doesn't exist"
      />
    )
  }

  const { chapter, topContributors } = data

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
      topContributors={topContributors}
      type="chapter"
    />
  )
}
