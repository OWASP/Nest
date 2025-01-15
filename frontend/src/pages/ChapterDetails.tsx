import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getFilteredIcons, handleSocialUrls } from 'utils/utility'
import { ErrorDisplay } from 'wrappers/ErrorWrapper'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'

import Card from 'components/Card'
import LoadingSpinner from 'components/LoadingSpinner'

const ChapterDetailsPage = () => {
  const { chapterKey } = useParams()
  const [chapter, setchapter] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

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

  const params = ['idx_updated_at']
  const filteredIcons = getFilteredIcons(chapter, params)
  const formattedUrls = handleSocialUrls(chapter.idx_related_urls)

  const SubmitButton = {
    label: 'Join',
    icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
    url: chapter.idx_url,
  }

  return (
    <div className="container mx-auto pb-16 pt-24 xl:max-w-full">
      <div className="flex justify-center">
        <Card
          key={chapter.objectID}
          title={chapter.idx_name}
          url={chapter.idx_url}
          summary={chapter.idx_summary}
          icons={filteredIcons}
          topContributors={chapter.idx_top_contributors}
          button={SubmitButton}
          social={formattedUrls}
        />
      </div>
    </div>
  )
}
export default ChapterDetailsPage
