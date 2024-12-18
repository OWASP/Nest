import { useState, useEffect } from 'react'

import Card from '../components/Card'
import { level } from '../components/data'
import LoadingSpinner from '../components/Loader'
import Pagination from '../components/Pagination'
import SearchBar from '../components/Search'
import { loadData } from '../lib/api'
import FontAwesomeIconWrapper from '../lib/FontAwesomeIconWrapper'
import { project, ProjectDataType } from '../lib/types'
import { getFilteredIcons } from '../lib/utils'

const ProjectsPage = () => {
  const [projects, setProjects] = useState<project[]>([])
  const [currentPage, setCurrentPage] = useState<number>(1)
  const [totalPages, setTotalPages] = useState<number>(0)
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [isLoaded, setIsLoaded] = useState<boolean>(false)

  useEffect(() => {
    document.title = 'OWASP Projects'
    setIsLoaded(false)
    const fetchData = async () => {
      try {
        const data = await loadData<ProjectDataType>(
          'owasp/search/project',
          searchQuery,
          currentPage
        )
        setProjects(data.projects)
        setTotalPages(data.total_pages)
      } catch (error) {
        console.error(error)
      }
      setIsLoaded(true)
    }
    fetchData()
  }, [currentPage, searchQuery])

  const handleSearch = (query: string) => {
    setSearchQuery(query)
    setCurrentPage(1)
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
    window.scrollTo({
      top: 0,
      behavior: 'auto',
    })
  }

  return (
    <div className="flex min-h-screen w-full flex-col items-center justify-normal p-4">
      <SearchBar onSearch={handleSearch} placeholder="Search for OWASP projects..." />
      {!isLoaded ? (
        <div className="bg-background/50 fixed inset-0 flex items-center justify-center">
          <LoadingSpinner imageUrl="../public/img/owasp_icon_white_sm.png" />
        </div>
      ) : (
        <div className="flex h-fit w-full flex-col items-center justify-normal gap-4">
          {totalPages === 0 && (
            <div className="text bg:text-white m-4 text-xl"> No projects found </div>
          )}
          {projects &&
            projects?.map((project, index) => {
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
      )}
      <Pagination
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={handlePageChange}
        isLoaded={isLoaded}
      />
    </div>
  )
}

export default ProjectsPage
