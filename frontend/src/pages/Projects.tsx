import { useSearchPage } from 'hooks/useSearchPage'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { project } from 'types/project'
import { level } from 'utils/data'
import { sortOptionsProject } from 'utils/sortingoptions'
import { getFilteredIcons } from 'utils/utility'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import Card from 'components/Card'
import SearchPageLayout from 'components/SearchPageLayout'
import SortBy from 'components/SortBy'
const ProjectsPage = () => {
  const [sortBy, setSortBy] = useState('projects')

  const handleSortChange = (val: string) => {
    setSortBy(val)
  }

  const {
    items: projects,
    isLoaded,
    currentPage,
    totalPages,
    searchQuery,
    handleSearch,
    handlePageChange,
  } = useSearchPage<project>({
    indexName: sortBy,
    pageTitle: 'OWASP Projects',
  })
  const navigate = useNavigate()
  const renderProjectCard = (project: project, index: number) => {
    const params: string[] = ['updated_at', 'forks_count', 'stars_count', 'contributors_count']
    const filteredIcons = getFilteredIcons(project, params)

    const handleButtonClick = () => {
      navigate(`/projects/${project.key}`)
    }

    const SubmitButton = {
      label: 'View Details',
      icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
      onclick: handleButtonClick,
    }

    return (
      <Card
        key={project.objectID || `project-${index}`}
        title={project.name}
        url={`projects/${project.key}`}
        summary={project.summary}
        level={level[`${project.level as keyof typeof level}`]}
        icons={filteredIcons}
        leaders={project.leaders}
        topContributors={project.top_contributors}
        topics={project.topics}
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
      sortChildren={
        <SortBy
          options={sortOptionsProject}
          selectedOption={sortBy}
          onSortChange={handleSortChange}
        />
      }
    >
      {projects && projects.map(renderProjectCard)}
    </SearchPageLayout>
  )
}

export default ProjectsPage
