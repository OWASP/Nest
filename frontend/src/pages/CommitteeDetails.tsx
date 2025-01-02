import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { fetchAlgoliaData } from 'lib/api'
import FontAwesomeIconWrapper from 'lib/FontAwesomeIconWrapper'
import { getFilteredIcons, handleSocialUrls } from 'lib/utils'
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
      <div className="flex min-h-[60vh] items-center justify-center">
        <p className="text-muted-foreground text-lg font-medium">No committee details found.</p>
      </div>
    )

  const SubmitButton = {
    label: 'Learn More',
    icon: <FontAwesomeIconWrapper icon="fa-solid fa-people-group" />,
    url: committee.idx_url,
  }

  const params: string[] = ['idx_updated_at']
  const filteredIcons = getFilteredIcons(committee, params)
  const formattedUrls = handleSocialUrls(committee.idx_related_urls)
  return (
    <div className="container mx-auto pb-16 pt-24 xl:max-w-full">
      <div className="flex justify-center">
        <Card
          key={committee.objectID}
          title={committee.idx_name}
          url={committee.idx_url}
          summary={committee.idx_summary}
          icons={filteredIcons}
          leaders={committee.idx_leaders}
          topContributors={committee.idx_top_contributors}
          button={SubmitButton}
          social={formattedUrls}
          tooltipLabel={`Learn more about ${committee.idx_name}`}
        />
      </div>
    </div>
  )
}
export default CommitteeDetailsPage
