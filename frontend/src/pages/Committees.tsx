import { useEffect, useState } from 'react'
import { API_URL } from '../utils/credentials'
import { CommitteeDataType } from '../lib/types'
import FontAwesomeIconWrapper from '../lib/FontAwesomeIconWrapper'
import Card from '../components/Card'
import { getFilteredIcons, handleSocialUrls } from '../lib/utils'

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
          console.error(error)
        }
      }
      fetchApiData()
    }, [])

  return (
    <div className="flex min-h-screen w-full flex-col items-center justify-normal p-5 text-text md:p-20">
      <div className="flex h-fit w-full flex-col items-center justify-normal gap-4">
        {committeeData &&
          committeeData.committees.map((project, index) => {
            const params: string[] = ['idx_updated_at']
            const filteredIcons = getFilteredIcons(project, params)
            const formattedUrls = handleSocialUrls(project.idx_related_urls)

              const SubmitButton = {
                label: 'Learn More',
                icon: <FontAwesomeIconWrapper icon="fa-solid fa-people-group" />,
                url: project.idx_url,
              }

            return (
              <Card
                key={project.objectID || `project-${index}`}
                title={project.idx_name}
                url={project.idx_url}
                summary={project.idx_summary}
                icons={filteredIcons}
                leaders={project.idx_leaders}
                topContributors={project.idx_top_contributors}
                button={SubmitButton}
                social={formattedUrls}
                tooltipLabel={`Learn more about ${project.idx_name}`}
              />
            )
          })}
      </div>
    </div>
  )
}
