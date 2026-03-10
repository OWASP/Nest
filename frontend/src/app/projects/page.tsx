'use client'
import { useSearchPage } from 'hooks/useSearchPage'
import { formatCategoryOptions, useProjectCategories } from 'hooks/useProjectCategories'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { FaRightToBracket } from 'react-icons/fa6'
import type { Project } from 'types/project'
import { getSearchBackendPreference, type SearchBackend } from 'utils/backendConfig'
import { level } from 'utils/data'
import { sortOptionsProject } from 'utils/sortingOptions'
import { getFilteredIcons } from 'utils/utility'
import Card from 'components/Card'
import UnifiedSearchBar from 'components/UnifiedSearchBar'

const ProjectsPage = () => {
  const [backend] = useState<SearchBackend>(() => getSearchBackendPreference())
  const { categories } = useProjectCategories()
  const categoryOptions = formatCategoryOptions(categories)

  const {
    items: projects,
    isLoaded,
    currentPage,
    totalPages,
    searchQuery,
    sortBy,
    order,
    category,
    handleSearch,
    handlePageChange,
    handleSortChange,
    handleOrderChange,
    handleCategoryChange,
  } = useSearchPage<Project>({
    indexName: 'projects',
    pageTitle: 'OWASP Projects',
    defaultSortBy: 'default',
    defaultOrder: 'desc',
    defaultCategory: '',
    useBackend: backend, // Use the selected backend
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
      icon: <FaRightToBracket className="h-4 w-4" />,
      onclick: handleButtonClick,
    }

    return (
      <Card
        button={submitButton}
        cardKey={project.key ?? ''}
        icons={filteredIcons}
        key={project.key ?? project.name}
        level={level[`${project.level as keyof typeof level}`]}
        summary={project.summary ?? ''}
        title={project.name}
        topContributors={project.topContributors}
        url={`/projects/${project.key}`}
      />
    )
  }

  return (
    <UnifiedSearchBar
      currentPage={currentPage}
      empty="No projects found"
      indexName="projects"
      isLoaded={isLoaded}
      onPageChange={handlePageChange}
      onSearch={handleSearch}
      searchPlaceholder="Search for projects..."
      searchQuery={searchQuery}
      sortBy={sortBy}
      order={order}
      category={category}
      sortOptions={sortOptionsProject}
      categoryOptions={categoryOptions}
      categories={categories}
      onOrderChange={handleOrderChange}
      onSortChange={handleSortChange}
      onCategoryChange={handleCategoryChange}
      totalPages={totalPages}
    >
      {projects?.filter((project) => project.isActive).map(renderProjectCard)}
    </UnifiedSearchBar>
  )
}

export default ProjectsPage
