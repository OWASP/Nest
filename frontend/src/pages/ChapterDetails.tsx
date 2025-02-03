import { Link } from '@chakra-ui/react'
import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
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
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchChapterData = async () => {
      setIsLoading(true)
      const { hits } = await fetchAlgoliaData('chapters', chapterKey, 1, chapterKey)
      if (hits && hits.length > 0) {
        setChapter(hits[0] as ChapterType)
      }
      setIsLoading(false)
    }

    fetchChapterData()
  }, [chapterKey])

  if (isLoading)
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner imageUrl="/img/owasp_icon_white_sm.png" />
      </div>
    )

  if (!chapter || !chapter.is_active)
    return (
      <ErrorDisplay
        statusCode={404}
        title="Chapter not found"
        message="Sorry, the chapter you're looking for doesn't exist"
      />
    )

  const details = [
    { label: 'Last Updated', value: formatDate(chapter.updated_at) },
    { label: 'Location', value: chapter.suggested_location },
    { label: 'Region', value: chapter.region },
    {
      label: 'URL',
      value: (
        <Link href={chapter.url} className="hover:underline dark:text-sky-600">
          {chapter.url}
        </Link>
      ),
    },
  ]
  return (
    <DetailsCard
      title={chapter.name}
      socialLinks={chapter.related_urls}
      is_active={chapter.is_active}
      details={details}
      summary={chapter.summary}
      type="chapter"
      topContributors={chapter.top_contributors}
      geolocationData={chapter}
    />
  )
}
