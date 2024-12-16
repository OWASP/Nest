import { useEffect, useState } from 'react'

import Card from '../components/Card'
import { level } from '../components/data'
import Pagination from '../components/Pagination'
import SearchBar from '../components/Search'
import FontAwesomeIconWrapper from '../lib/FontAwesomeIconWrapper'
import { ProjectDataType } from '../lib/types'
import { getFilteredIcons } from '../lib/utils'
import { API_URL } from '../utils/credentials.ts'

export default function Projects() {
  const [projectData, setProjectData] = useState<ProjectDataType | null>(null)
  const [defaultProjects, setDefaultProjects] = useState<ProjectDataType | null>(null)
  const [currentPage, setCurrentPage] = useState<number>(1)
  const [totalPages, setTotalPages] = useState<number>(1)
  const [isLoaded, setLoading] = useState<boolean>(false)
  useEffect(() => {
    if (projectData) return
    document.title = 'OWASP Projects'
    const fetchApiData = async () => {
      try {
        const response = await fetch(`${API_URL}/owasp/search/project?page=${currentPage}`)
        const data = await response.json()
        setProjectData(data)
        setDefaultProjects(data)
        setTotalPages(data.total_pages)
        setLoading(true)
      } catch (error) {
        console.error(error)
      }
    }
    fetchApiData()
  }, [currentPage])
  useEffect(() => {
    setTotalPages(projectData?.total_pages || 1)
  }, [projectData])
  const handlePageChange = (page: number) => {
    setCurrentPage(page)
    window.scrollTo({
      top: 0,
      behavior: 'auto',
    })
  }
  return (
    <div className="flex min-h-screen w-full flex-col items-center justify-normal p-5 text-text">
      <div className="flex h-fit w-full flex-col items-center justify-normal gap-4">
        <SearchBar
          placeholder="Search for OWASP projects..."
          searchEndpoint={`${API_URL}/owasp/search/project`}
          onSearchResult={setProjectData}
          defaultResults={defaultProjects}
          currentPage={currentPage}
        />
        {projectData &&
          projectData?.projects?.map((project, index) => {
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
                key={project.objectID || `project-${index}`}
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
      <Pagination
        currentPage={currentPage}
        totalPages={totalPages}
        isLoaded={isLoaded}
        onPageChange={handlePageChange}
      />
    </div>
  )
}
