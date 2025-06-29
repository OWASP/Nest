'use client'
import { useSearchPage } from 'hooks/useSearchPage'
import { useRouter } from 'next/navigation'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import type { Project } from 'types/project'
import { level } from 'utils/data'
import { sortOptionsProject } from 'utils/sortingOptions'
import { getFilteredIcons } from 'utils/utility'
import Card from 'components/Card'
import PageLayout from 'components/PageLayout'
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
  } = useSearchPage<Project>({
    indexName: 'projects',
    pageTitle: 'OWASP Projects',
    defaultSortBy: 'default',
    defaultOrder: 'desc',
  })

  const router = useRouter()
  const renderProjectCard = (project: Project) => {
    const params: string[] = ['forksCount', 'starsCount', 'contributorsCount']
    const filteredIcons = getFilteredIcons(project, params)
    const handleButtonClick = () => {
      router.push(`/projects/${project.key}`)
    }

    const submitButton = {
      label: 'View Details',
      icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
      onclick: handleButtonClick,
    }

    return (
      <Card
        button={submitButton}
        icons={filteredIcons}
        key={project.key}
        level={level[`${project.level as keyof typeof level}`]}
        summary={project.summary}
        title={project.name}
        topContributors={project.topContributors}
        url={`/projects/${project.key}`}
      />
    )
  }

  return (
    <PageLayout>
      <SearchPageLayout
        currentPage={currentPage}
        empty="No projects found"
        indexName="projects"
        isLoaded={isLoaded}
        onPageChange={handlePageChange}
        onSearch={handleSearch}
        searchPlaceholder="Search for projects..."
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
        {projects && projects.filter((project) => project.isActive).map(renderProjectCard)}
      </SearchPageLayout>
    </PageLayout>
  )
}

export default ProjectsPage
