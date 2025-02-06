import { useQuery } from '@apollo/client'
import { GET_CHAPTER_DATA } from 'api/queries/chapterQueries'
import { toast } from 'hooks/useToast'
import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { ChapterType } from 'types/chapter'
import { formatDate } from 'utils/dateFormatter'
import { ErrorDisplay } from 'wrappers/ErrorWrapper'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'

export default function ChapterDetailsPage() {
  const { chapterKey } = useParams()
  const [chapter, setChapter] = useState<ChapterType>(null)
  const {
    data,
    loading: isGraphQlDataLoading,
    error: graphQLRequestError,
  } = useQuery(GET_CHAPTER_DATA, {
    variables: { key: chapterKey },
  })

  useEffect(() => {
    if (data && data.chapter) {
      setChapter(data.chapter)
    }
  }, [data])

  useEffect(() => {
    if (graphQLRequestError) {
      toast({
        variant: 'destructive',
        title: 'GraphQL Request Failed',
        description: 'Unable to complete the requested operation.',
      })
    }
  }, [graphQLRequestError])

  if (isGraphQlDataLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner imageUrl="/img/owasp_icon_white_sm.png" />
      </div>
    )
  }

  if (!chapter || !chapter.isActive)
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
        <a href={chapter.url} className="hover:underline dark:text-sky-600">
          {chapter.url}
        </a>
      ),
    },
  ]
  return (
    <DetailsCard
      title={chapter.name}
      socialLinks={chapter.relatedUrls}
      is_active={chapter.isActive}
      details={details}
      summary={chapter.summary}
      type="chapter"
      topContributors={chapter.topContributors}
      geolocationData={chapter}
    />
  )
}
