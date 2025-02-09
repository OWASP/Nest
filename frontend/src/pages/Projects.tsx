import { useSearchPage } from 'hooks/useSearchPage'
import { useNavigate } from 'react-router-dom'
import { project } from 'types/project'
import { level } from 'utils/data'
import { sortOptionsProject } from 'utils/sortingOptions'
import { getFilteredIcons } from 'utils/utility'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import Card from 'components/Card'
import SearchPageLayout from 'components/SearchPageLayout'
import SortBy from 'components/SortBy'
const ProjectsPage = () => {
  const {
    items: projects,
    isLoaded,
    currentPage,
    totalPages,
    searchQuery,
    sortBy,
    order,
    handleSearch,
    handlePageChange,
    handleSortChange,
    handleOrderChange,
  } = useSearchPage<project>({
    indexName: 'projects',
    pageTitle: 'OWASP Projects',
    defaultSortBy: 'default',
    defaultOrder: 'asc',
  })

  const navigate = useNavigate()
  const renderProjectCard = (project: project) => {
    const params: string[] = ['forks_count', 'stars_count', 'contributors_count']
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
        key={project.objectID}
        title={project.name}
        url={`/projects/${project.key}`}
        summary={project.summary}
        level={level[`${project.level as keyof typeof level}`]}
        icons={filteredIcons}
        topContributors={project.top_contributors}
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
          sortOptions={sortOptionsProject}
          selectedSortOption={sortBy}
          onSortChange={handleSortChange}
          selectedOrder={order}
          onOrderChange={handleOrderChange}
        />
      }
    >
      {projects && projects.filter((project) => project.is_active).map(renderProjectCard)}
    </SearchPageLayout>
  )
}

export default ProjectsPage
