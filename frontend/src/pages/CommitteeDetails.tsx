import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getFilteredIcons, handleSocialUrls } from 'utils/utility'
import { ErrorDisplay } from 'wrappers/ErrorWrapper'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import Card from 'components/Card'
import LoadingSpinner from 'components/LoadingSpinner'

const CommitteeDetailsPage = () => {
  const { committeeKey } = useParams()
  const [committee, setcommittee] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchcommitteeData = async () => {
      setIsLoading(true)
      const { hits } = await fetchAlgoliaData('committees', committeeKey, 1, committeeKey)
      if (hits && hits.length > 0) {
        setcommittee(hits[0])
      }
      setIsLoading(false)
    }

    fetchcommitteeData()
  }, [committeeKey])
  if (isLoading)
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner imageUrl="/img/owasp_icon_white_sm.png" />
      </div>
    )

  if (!committee)
    return (
      <ErrorDisplay
        statusCode={404}
        title="Committee not found"
        message="Sorry, the committee you're looking for doesn't exist"
      />
    )

  const SubmitButton = {
    label: 'Learn More',
    icon: <FontAwesomeIconWrapper icon="fa-solid fa-people-group" />,
    url: committee.url,
  }

  const params: string[] = ['updated_at']
  const filteredIcons = getFilteredIcons(committee, params)
  const formattedUrls = handleSocialUrls(committee.related_urls)
  return (
    <div className="container mx-auto pb-16 pt-24 xl:max-w-full">
      <div className="flex justify-center">
        <Card
          key={committee.objectID}
          title={committee.name}
          url={committee.url}
          summary={committee.summary}
          icons={filteredIcons}
          topContributors={committee.top_contributors}
          button={SubmitButton}
          social={formattedUrls}
          tooltipLabel={`Learn more about ${committee.name}`}
        />
      </div>
    </div>
  )
}
export default CommitteeDetailsPage
