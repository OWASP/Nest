import {
  faMapMarkerAlt,
  faTags,
  faCalendarAlt,
  faLink,
  faGlobe,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { formatDate } from 'utils/dateFormatter'
import { getSocialIcon } from 'utils/urlIconMappings'
import { ErrorDisplay } from 'wrappers/ErrorWrapper'
import InfoBlock from 'components/InfoBlock'
import LoadingSpinner from 'components/LoadingSpinner'
import SecondaryCard from 'components/SecondaryCard'
import TopContributors from 'components/ToggleContributors'

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

  return (
    <div className="mt-16 min-h-screen bg-white p-4 text-gray-600 md:p-8 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        <h1 className="mb-6 text-3xl font-bold md:text-4xl">{chapter.name}</h1>

        <div className="grid gap-6 md:grid-cols-2">
          <SecondaryCard title="Chapter Details">
            <InfoBlock
              className="pb-1"
              icon={faMapMarkerAlt}
              label="Location"
              value={chapter.suggested_location}
            />
            <InfoBlock className="pb-1" icon={faGlobe} label="Region" value={chapter.region} />
            <InfoBlock
              className="pb-1"
              icon={faTags}
              label="Tags"
              value={chapter.tags[0].toUpperCase() + chapter.tags.slice(1)}
            />
            <InfoBlock
              className="pb-1"
              icon={faCalendarAlt}
              label="Last Updated"
              value={formatDate(chapter.updated_at)}
            />
            <InfoBlock className="pb-1" icon={faLink} label="URL" value={chapter.url} isLink />
            <SocialLinks urls={chapter.related_urls} />
          </SecondaryCard>
          <SecondaryCard title="Summary">
            <div className="text-sm leading-relaxed md:text-base">{chapter.summary}</div>
          </SecondaryCard>
        </div>

        <TopContributors contributors={chapter.top_contributors} maxInitialDisplay={6} />
      </div>
    </div>
  )
}

const SocialLinks = ({ urls }) => (
  <div>
    <div className="text-sm font-medium">Social Links</div>
    <div className="mt-2 flex flex-wrap gap-3">
      {urls.map((url, index) => (
        <a
          key={index}
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-gray-600 transition-colors hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
        >
          <FontAwesomeIcon icon={getSocialIcon(url)} className="h-5 w-5" />
        </a>
      ))}
    </div>
  </div>
)
