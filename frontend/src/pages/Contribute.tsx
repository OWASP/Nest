import { useEffect, useState } from 'react'

import Card from '../components/Card'
import FontAwesomeIconWrapper from '../lib/FontAwesomeIconWrapper'
import { ContributeDataType } from '../lib/types'
import { getFilteredIcons, handleSocialUrls } from '../lib/utils'
import { API_URL } from '../utils/credentials'

export default function Contribute() {
  const [contributeData, setContributeData] = useState<ContributeDataType | null>(null)

  useEffect(() => {
    document.title = 'Contribute Page'
    const fetchApiData = async () => {
      try {
        const response = await fetch(`${API_URL}/owasp/search/contribute`)
        const data = await response.json()
        setContributeData(data)
      } catch (error) {
        console.error(error)
      }
    }
    fetchApiData()
  }, [])

  return (
    <div className="flex min-h-screen w-full flex-col items-center justify-normal p-5 text-text md:p-20">
      <div className="flex h-fit w-full flex-col items-center justify-normal gap-4">
        {contributeData &&
          contributeData.projects.projects.map((project, index) => {
            const params: string[] = ['idx_updated_at']
            const filteredIcons = getFilteredIcons(project, params)
            const formattedUrls = handleSocialUrls(project.idx_topics)

            const SubmitButton = {
              label: 'Learn More',
              icon: <FontAwesomeIconWrapper icon="fa-solid fa-code-branch" />,
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
        {contributeData &&
          contributeData.issues.issues.map((issue, index) => {
            const params: string[] = ['idx_updated_at']
            const filteredIcons = getFilteredIcons(issue, params)
            const formattedUrls = handleSocialUrls(issue.idx_labels)

            const SubmitButton = {
              label: 'View Issue',
              icon: <FontAwesomeIconWrapper icon="fa-solid fa-bug" />,
              url: issue.idx_url,
            }

            return (
              <Card
                key={issue.objectID || `issue-${index}`}
                title={issue.idx_title}
                url={issue.idx_url}
                summary={issue.idx_summary}
                icons={filteredIcons}
                leaders={[]}
                topContributors={[]}
                button={SubmitButton}
                social={formattedUrls}
                tooltipLabel={`Learn more about ${issue.idx_title}`}
              />
            )
          })}
      </div>
    </div>
  )
}
