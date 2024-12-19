import { useEffect, useState } from 'react'

import Card from '../components/Card'
import FontAwesomeIconWrapper from '../lib/FontAwesomeIconWrapper'
import { CommitteeDataType } from '../lib/types'
import { getFilteredIcons, handleSocialUrls } from '../lib/utils'
import { API_URL } from '../utils/credentials'
import { logger } from '../utils/logger'

export default function Committees() {
  const [committeeData, setCommitteeData] = useState<CommitteeDataType | null>(null)

  useEffect(() => {
    document.title = 'OWASP Committees'
    const fetchApiData = async () => {
      try {
        const response = await fetch(`${API_URL}/owasp/search/committee`)
        const data = await response.json()
        setCommitteeData(data)
      } catch (error) {
        logger.error(error)
      }
    }
    fetchApiData()
  }, [])

  return (
    <div className="flex min-h-screen w-full flex-col items-center justify-normal p-5 text-text md:p-20">
      <div className="flex h-fit w-full flex-col items-center justify-normal gap-4">
        {committeeData &&
          committeeData.committees.map((committee, index) => {
            const params: string[] = ['idx_updated_at']
            const filteredIcons = getFilteredIcons(committee, params)
            const formattedUrls = handleSocialUrls(committee.idx_related_urls)

            const SubmitButton = {
              label: 'Learn More',
              icon: <FontAwesomeIconWrapper icon="fa-solid fa-people-group" />,
              url: committee.idx_url,
            }

            return (
              <Card
                key={committee.objectID || `committee-${index}`}
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
            )
          })}
      </div>
    </div>
  )
}
