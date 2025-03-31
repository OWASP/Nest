import { useQuery } from '@apollo/client'
import { Link } from '@chakra-ui/react'
import { GET_CHAPTER_DATA } from 'api/queries/chapterQueries'
import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { ChapterTypeGraphQL } from 'types/chapter'
import { formatDate } from 'utils/dateFormatter'
import { ErrorDisplay } from 'wrappers/ErrorWrapper'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'
import MetadataManager from 'components/MetadataManager'
import { toaster } from 'components/ui/toaster'

export default function ChapterDetailsPage() {
  const { chapterKey } = useParams()
  const [chapter, setChapter] = useState<ChapterTypeGraphQL>(null)
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
      toaster.create({
        description: 'Unable to complete the requested operation.',
        title: 'GraphQL Request Failed',
        type: 'error',
      })
      setIsLoading(false)
    }
  }, [data, graphQLRequestError, chapterKey])

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner imageUrl="/img/owasp_icon_white_sm.png" />
      </div>
    )
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
    <MetadataManager pageTitle={chapter.name} description={chapter.summary} url={chapter.url}>
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
    </MetadataManager>
  )
}
