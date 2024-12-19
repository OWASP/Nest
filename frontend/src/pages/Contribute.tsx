import { useEffect, useState } from 'react'

import Card from '../components/Card'
import FontAwesomeIconWrapper from '../lib/FontAwesomeIconWrapper'
import { ContributeDataType } from '../lib/types'
import { getFilteredIcons, handleSocialUrls } from '../lib/utils'
import { API_URL } from '../utils/credentials'
import { logger } from '../utils/logger'

export default function Contribute() {
  const [contributeData, setContributeData] = useState<ContributeDataType | null>(null)

  useEffect(() => {
    document.title = 'OWASP Contribute'
    const fetchApiData = async () => {
      try {
        const response = await fetch(`${API_URL}/owasp/search/contribute`)
        const data = await response.json()
        setContributeData(data)
      } catch (error) {
        logger.error(error)
      }
    }
    fetchApiData()
  }, [])

  return (
    <div className="flex min-h-screen w-full flex-col items-center justify-normal p-5 text-text md:p-20">
      <div className="flex h-fit w-full flex-col items-center justify-normal gap-4">
        {contributeData &&
          contributeData.contributions.map((contribution, index) => {
            const params: string[] = ['idx_updated_at']
            const filteredIcons = getFilteredIcons(contribution, params)
            const formattedUrls = handleSocialUrls(contribution.idx_related_urls)

            const SubmitButton = {
              label: 'Contribute Now',
              icon: <FontAwesomeIconWrapper icon="fa-solid fa-hands-helping" />,
              url: contribution.idx_url,
            }

            return (
              <Card
                key={contribution.objectID || `contribution-${index}`}
                title={contribution.idx_name}
                url={contribution.idx_url}
                summary={contribution.idx_summary}
                icons={filteredIcons}
                leaders={contribution.idx_leaders}
                topContributors={contribution.idx_top_contributors}
                button={SubmitButton}
                social={formattedUrls}
                tooltipLabel={`Learn more about ${contribution.idx_name}`}
              />
            )
          })}
      </div>
    </div>
  )
}
