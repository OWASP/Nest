'use client'
import { useSearchPage } from 'hooks/useSearchPage'
import { useRouter } from 'next/navigation'
import { ProjectTypeAlgolia } from 'types/project'
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
  } = useSearchPage<ProjectTypeAlgolia>({
    indexName: 'projects',
    pageTitle: 'OWASP Projects',
    defaultSortBy: 'default',
    defaultOrder: 'desc',
  })

  const router = useRouter()
  const renderProjectCard = (project: ProjectTypeAlgolia) => {
    const params: string[] = ['forks_count', 'stars_count', 'contributors_count']
    const filteredIcons = getFilteredIcons(project, params)
    const handleButtonClick = () => {
      router.push(`/projects/${project.key}`)
    }

    const SubmitButton = {
      label: 'View Details',
      icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
      onclick: handleButtonClick,
    }

    return (
      <Card
        button={SubmitButton}
        icons={filteredIcons}
        key={project.objectID}
        level={level[`${project.level as keyof typeof level}`]}
        summary={project.summary}
        title={project.name}
        topContributors={project.top_contributors}
        url={`/projects/${project.key}`}
      />
    )
  }

  return (
    <SearchPageLayout
      currentPage={currentPage}
      empty="No projects found"
      indexName="projects"
      isLoaded={isLoaded}
      onPageChange={handlePageChange}
      onSearch={handleSearch}
      searchPlaceholder="Search for OWASP projects..."
      searchQuery={searchQuery}
      sortChildren={
        <SortBy
          onOrderChange={handleOrderChange}
          onSortChange={handleSortChange}
          selectedOrder={order}
          selectedSortOption={sortBy}
          sortOptions={sortOptionsProject}
        />
      }
      totalPages={totalPages}
    >
      {projects && projects.filter((project) => project.is_active).map(renderProjectCard)}
    </SearchPageLayout>
  )
}

export default ProjectsPage
