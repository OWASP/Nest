import { useQuery } from '@apollo/client'
import { GET_PROJECT_DATA } from 'api/queries/projectQueries'
import { toast } from 'hooks/useToast'
import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { ProjectTypeGraphql } from 'types/project'
import { formatDate } from 'utils/dateFormatter'
import { ErrorDisplay } from 'wrappers/ErrorWrapper'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'

const ProjectDetailsPage = () => {
  const { projectKey } = useParams()
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [project, setProject] = useState<ProjectTypeGraphql>(null)

  const { data, error: graphQLRequestError } = useQuery(GET_PROJECT_DATA, {
    variables: { key: projectKey },
  })

  useEffect(() => {
    if (data) {
      setProject(data?.project)
      setIsLoading(false)
    }
    if (graphQLRequestError) {
      toast({
        description: 'Unable to complete the requested operation.',
        title: 'GraphQL Request Failed',
        variant: 'destructive',
      })
      setIsLoading(false)
    }
  }, [data, graphQLRequestError, projectKey])

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner imageUrl="/img/owasp_icon_white_sm.png" />
      </div>
    )
  }

  if (!project)
    return (
      <ErrorDisplay
        statusCode={404}
        title="Project not found"
        message="Sorry, the project you're looking for doesn't exist"
      />
    )
  const projectDetails = [
    { label: 'Last Updated', value: formatDate(project.updatedAt) },
    { label: 'Level', value: project.level[0].toUpperCase() + project.level.slice(1) },
    { label: 'Project Leaders', value: project.leaders.join(', ') },
    { label: 'Type', value: project.type[0].toUpperCase() + project.type.slice(1) },
    {
      label: 'URL',
      value: (
        <a href={project.url} className="hover:underline dark:text-sky-600">
          {project.url}
        </a>
      ),
    },
  ]

  const projectStats = {
    contributors: project.contributorsCount,
    forks: project.forksCount,
    issues: project.issuesCount,
    repositories: project.repositoriesCount,
    stars: project.starsCount,
  }
  return (
    <DetailsCard
      title={project.name}
      details={projectDetails}
      is_active={project.isActive}
      summary={project.summary}
      projectStats={projectStats}
      type="project"
      topContributors={project.topContributors}
      languages={project.languages}
      topics={project.topics}
      recentReleases={project.recentReleases}
      recentIssues={project.recentIssues}
      repositories={project.repositories}
    />
  )
}

export default ProjectDetailsPage
