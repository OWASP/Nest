import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { fetchAlgoliaData } from 'lib/api'
import FontAwesomeIconWrapper from 'lib/FontAwesomeIconWrapper'
import { getFilteredIcons } from 'lib/utils'
import Card from 'components/Card'
import { level } from 'components/data'
import LoadingSpinner from 'components/LoadingSpinner'

const ProjectDetailsPage = () => {
  const { projectKey } = useParams()
  const [project, setProject] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchProjectData = async () => {
      setIsLoading(true)
      const { hits } = await fetchAlgoliaData('projects', projectKey, 1, projectKey)
      if (hits && hits.length > 0) {
        setProject(hits[0])
      }
      setIsLoading(false)
    }

    fetchProjectData()
  }, [projectKey])

  if (isLoading)
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner imageUrl="/img/owasp_icon_white_sm.png" />
      </div>
    )

  if (!project)
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <p className="text-lg font-medium text-muted-foreground">No project details found.</p>
      </div>
    )
  const params = ['idx_updated_at', 'idx_forks_count', 'idx_stars_count', 'idx_contributors_count']
  const filteredIcons = getFilteredIcons(project, params)

  const handleButtonClick = () => {
    window.open(`/projects/contribute?q=${project.idx_name}`)
  }

  const SubmitButton = {
    label: 'Contribute',
    icon: <FontAwesomeIconWrapper icon="fa-solid fa-code-fork" />,
    onclick: handleButtonClick,
  }

  return (
    <div className="container mx-auto pb-16 pt-24 xl:max-w-full">
      <div className="flex justify-center">
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
      </div>
    </div>
  )
}
export default ProjectDetailsPage
