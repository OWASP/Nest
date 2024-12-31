import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { fetchAlgoliaData } from 'lib/api'
import FontAwesomeIconWrapper from 'lib/FontAwesomeIconWrapper'
import { getFilteredIcons, handleSocialUrls } from 'lib/utils'
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
      <div className="flex min-h-[60vh] items-center justify-center">
        <p className="text-muted-foreground text-lg font-medium">No chapter details found.</p>
      </div>
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
    <div className="container mx-auto pb-16 pt-24">
      <div className="flex justify-center">
        <Card
          key={chapter.objectID}
          title={chapter.idx_name}
          url={chapter.idx_url}
          summary={chapter.idx_summary}
          icons={filteredIcons}
          leaders={chapter.idx_leaders}
          topContributors={chapter.idx_top_contributors}
          button={SubmitButton}
          social={formattedUrls}
        />
      </div>
    </div>
  )
}
export default ChapterDetailsPage
