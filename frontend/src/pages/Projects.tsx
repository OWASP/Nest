import FontAwesomeIconWrapper from 'lib/FontAwesomeIconWrapper'
import { useSearchPage } from 'lib/hooks/useSearchPage'
import { project } from 'lib/types'
import { getFilteredIcons } from 'lib/utils'

import Card from 'components/Card'
import { level } from 'components/data'
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

  const renderProjectCard = (project: project, index: number) => {
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
  }

  return (
    <SearchPageLayout
      isLoaded={isLoaded}
      totalPages={totalPages}
      currentPage={currentPage}
      searchQuery={searchQuery}
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
