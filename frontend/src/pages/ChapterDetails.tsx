import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { formatDate } from 'utils/dateFormatter'
import { ErrorDisplay } from 'wrappers/ErrorWrapper'
import LoadingSpinner from 'components/LoadingSpinner'
import GenericDetails from './CardDetailsPage'

export default function ChapterDetailsPage() {
  const { chapterKey } = useParams()
  const [chapter, setChapter] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchChapterData = async () => {
      setIsLoading(true)
      const { hits } = await fetchAlgoliaData('chapters', chapterKey, 1, chapterKey)
      if (hits && hits.length > 0) {
        setChapter(hits[0])
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
    { label: 'Location', value: chapter.suggested_location },
    { label: 'Region', value: chapter.region },
    { label: 'Last Updated', value: formatDate(chapter.updated_at) },
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
    <GenericDetails
      title={chapter.name}
      is_active={chapter.is_active}
      details={details}
      summary={chapter.summary}
      data={chapter}
      type="chapter"
      topContributors={chapter.top_contributors}
    />
  )
}
