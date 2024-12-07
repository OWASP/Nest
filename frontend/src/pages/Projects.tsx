import { useEffect, useState } from 'react'
import { ProjectDataType } from '../lib/types'
import FontAwesomeIconWrapper from '../lib/FontAwesomeIconWrapper'
import { getFilteredIcons } from '../lib/utils'
import Card from '../components/Card'
import { level } from '../components/data'
import SearchBar from '../components/Search'

export default function Projects() {
  const [projectData, setProjectData] = useState<ProjectDataType | null>(null)
  const [defaultProjects, setDefaultProjects] = useState<any[]>([])

  useEffect(() => {
    document.title = 'OWASP Projects'
    const fetchApiData = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_NEST_API_URL}/owasp/search/project`)
        const data = await response.json()
        setProjectData(data)
        setDefaultProjects(data)
      } catch (error) {
        console.error(error)
      }
    }
    fetchApiData()
  }, [])

  return (
    <div className="w-full min-h-screen flex flex-col justify-normal items-center text-text p-5">
      <div className="w-full h-fit flex flex-col justify-normal items-center gap-4">
        <SearchBar
          placeholder="Search for OWASP projects..."
          searchEndpoint={`${import.meta.env.VITE_NEST_API_URL}/owasp/search/project`}
          onSearchResult={setProjectData}
          defaultResults={defaultProjects}
        />
        {projectData &&
          projectData?.projects?.map((project) => {
            const params: string[] = [
              'idx_updated_at',
              'idx_forks_count',
              'idx_stars_count',
              'idx_contributors_count',
            ]
            const filteredIcons = getFilteredIcons(project, params)
            const handleButtonClick = () => {
              window.open(`/projects/contribute?q=${project.idx_name}`, '_blank')
            }

            const SubmitButton = {
              label: 'Contribute',
              icon: <FontAwesomeIconWrapper icon="fa-solid fa-code-fork" />,
              onclick: handleButtonClick,
            }

            return (
              <Card
                key={project.objectID}
                title={project.idx_name}
                url={project.idx_url}
                summary={project.idx_summary}
                level={level[`${project.idx_level as keyof typeof level}`]}
                icons={filteredIcons}
                leaders={project.idx_leaders}
                topContributors={project.idx_top_contributors}
                topics={project.idx_topics}
                button={SubmitButton}
              />
            )
          })}
      </div>
    </div>
  )
}
