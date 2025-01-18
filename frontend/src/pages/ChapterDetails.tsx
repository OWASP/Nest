import {
  faDiscord,
  faInstagram,
  faLinkedin,
  faYoutube,
  faTwitter,
} from '@fortawesome/free-brands-svg-icons'
import {
  faGlobe,
  faCalendarAlt,
  faMapMarkerAlt,
  faChevronDown,
  faChevronUp,
  faLink,
  faTags,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { formatDate } from 'utils/dateFormatter'
import { ErrorDisplay } from 'wrappers/ErrorWrapper'
import LoadingSpinner from 'components/LoadingSpinner'

const getSocialIcon = (url: string) => {
  if (url.includes('discord')) return faDiscord
  if (url.includes('instagram')) return faInstagram
  if (url.includes('linkedin')) return faLinkedin
  if (url.includes('youtube')) return faYoutube
  if (url.includes('twitter') || url.includes('x.com')) return faTwitter
  return faGlobe
}

export default function ChapterDetailsPage() {
  const { chapterKey } = useParams()
  const [chapter, setchapter] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [showAllContributors, setShowAllContributors] = useState(false)

  useEffect(() => {
    const fetchchapterData = async () => {
      setIsLoading(true)
      const { hits } = await fetchAlgoliaData('chapters', chapterKey, 1, chapterKey)
      if (hits && hits.length > 0) {
        setchapter(hits[0])
      }
      setIsLoading(false)
    }

    fetchchapterData()
  }, [chapterKey])

  if (isLoading)
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner imageUrl="/img/owasp_icon_white_sm.png" />
      </div>
    )

  if (!chapter)
    return (
      <ErrorDisplay
        statusCode={404}
        title="Chapter not found"
        message="Sorry, the chapter you're looking for doesn't exist"
      />
    )

  return (
    <div className="mt-16 min-h-screen bg-white p-4 text-gray-600 dark:bg-[#212529] dark:text-gray-300 md:p-8">
      <div className="mx-auto max-w-7xl">
        <h1 className="mb-6 text-3xl font-bold md:text-4xl">{chapter.name}</h1>

        <div className="grid gap-6 md:grid-cols-2">
          <div className="rounded-lg bg-gray-100 p-4 shadow-lg dark:bg-gray-800 md:p-6">
            <h2 className="mb-4 text-xl font-semibold md:text-2xl">Chapter Details</h2>
            <div className="space-y-3">
              <div className="flex items-start">
                <FontAwesomeIcon icon={faMapMarkerAlt} className="mr-3 mt-1 w-5" />
                <div>
                  <div className="text-sm font-medium">Location</div>
                  <div className="text-sm md:text-base">{chapter.suggested_location}</div>
                </div>
              </div>

              <div className="flex items-start">
                <FontAwesomeIcon icon={faGlobe} className="mr-3 mt-1 w-5" />
                <div>
                  <div className="text-sm font-medium">Region</div>
                  <div className="text-sm md:text-base">{chapter.region}</div>
                </div>
              </div>

              <div className="flex items-start">
                <FontAwesomeIcon icon={faTags} className="mr-3 mt-1 w-5" />
                <div>
                  <div className="text-sm font-medium">Tags</div>
                  <div className="text-sm md:text-base">{chapter.tags}</div>
                </div>
              </div>

              <div className="flex items-start">
                <FontAwesomeIcon icon={faCalendarAlt} className="mr-3 mt-1 w-5" />
                <div>
                  <div className="text-sm font-medium">Last Updated</div>
                  <div className="text-sm md:text-base">{formatDate(chapter.updated_at)}</div>
                </div>
              </div>

              <div className="flex items-start">
                <FontAwesomeIcon icon={faLink} className="mr-3 mt-1 w-5" />
                <div>
                  <div className="text-sm font-medium">URL</div>
                  <a href={chapter.url} className="hover:underline dark:text-sky-600">
                    {chapter.url}
                  </a>
                </div>
              </div>

              <div>
                <div className="text-sm font-medium">Social Links</div>
                <div className="mt-2 flex space-x-4">
                  {chapter.related_urls.map((url, index) => (
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
            </div>
          </div>

          <div className="rounded-lg bg-gray-100 p-4 shadow-md dark:bg-gray-800 md:p-6">
            <h2 className="mb-4 text-xl font-semibold md:text-2xl">Summary</h2>
            <p className="text-sm leading-relaxed md:text-base">{chapter.summary}</p>
          </div>
        </div>

        <div className="mt-6 rounded-lg bg-gray-100 p-4 shadow-md dark:bg-gray-800 md:p-6">
          <h2 className="mb-4 text-xl font-semibold md:text-2xl">Top Contributors</h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {(showAllContributors
              ? chapter.top_contributors
              : chapter.top_contributors.slice(0, 6)
            ).map((contributor, index) => (
              <div key={index} className="flex items-center space-x-3">
                <img
                  src={contributor.avatar_url || '/placeholder.svg'}
                  alt={contributor.name}
                  className="h-10 w-10 rounded-full"
                />
                <div>
                  <p className="font-medium">{contributor.name}</p>
                  <p className="text-sm">{contributor.contributions_count} contributions</p>
                </div>
              </div>
            ))}
          </div>
          {chapter.top_contributors.length > 6 && (
            <button
              onClick={() => setShowAllContributors(!showAllContributors)}
              className="mt-4 flex items-center text-[#1d7bd7] hover:underline dark:text-sky-600"
            >
              {showAllContributors ? 'Show Less' : 'Show All'}
              <FontAwesomeIcon
                icon={showAllContributors ? faChevronUp : faChevronDown}
                className="ml-2"
              />
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
