import { useSearchPage } from 'hooks/useSearchPage'
import { useNavigate } from 'react-router-dom'
import { project } from 'types/project'
import { level } from 'utils/data'
import { getFilteredIcons } from 'utils/utility'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import Card from 'components/Card'
import SearchPageLayout from 'components/SearchPageLayout'

const ProjectsPage = () => {
  const {
    items: projects,
    isLoaded,
    currentPage,
    totalPages,
    searchQuery,
    handleSearch,
    handlePageChange,
  } = useSearchPage<project>({
    indexName: 'projects',
    pageTitle: 'OWASP Projects',
  })
  const navigate = useNavigate()
  const renderProjectCard = (project: project, index: number) => {
    const params: string[] = [
      'idx_updated_at',
      'idx_forks_count',
      'idx_stars_count',
      'idx_contributors_count',
    ]
    const filteredIcons = getFilteredIcons(project, params)

    const handleButtonClick = () => {
      navigate(`/projects/${project.idx_key}`)
    }

    const SubmitButton = {
      label: 'View Details',
      icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
      onclick: handleButtonClick,
    }

    return (
      <Card
        key={project.objectID || `project-${index}`}
        title={project.idx_name}
        url={`projects/${project.idx_key}`}
        summary={project.idx_summary}
        level={level[`${project.idx_level as keyof typeof level}`]}
        icons={filteredIcons}
        topContributors={project.idx_top_contributors}
        button={SubmitButton}
      />
    )
  }

  return (
    <SearchPageLayout
      isLoaded={isLoaded}
      totalPages={totalPages}
      currentPage={currentPage}
      searchQuery={searchQuery}
      indexName="projects"
      onSearch={handleSearch}
      onPageChange={handlePageChange}
      empty="No projects found"
      searchPlaceholder="Search for OWASP projects..."
    >
      {projects && projects.map(renderProjectCard)}
    </SearchPageLayout>
  )
}

export default ProjectsPage
