import { useQuery } from '@apollo/client'
import { Link } from '@chakra-ui/react'
import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { GET_PROJECT_DATA } from 'api/queries/projectQueries'
import { toast } from 'hooks/useToast'
import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { project, ProjectIssuesType, ProjectReleaseType } from 'types/project'
import { formatDate } from 'utils/dateFormatter'
import { ErrorDisplay } from 'wrappers/ErrorWrapper'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'

const ProjectDetailsPage = () => {
  const { projectKey } = useParams()
  const [project, setProject] = useState<project>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [recentReleases, setRecentReleases] = useState<ProjectReleaseType[]>([])
  const [recentIssues, setRecentIssues] = useState<ProjectIssuesType[]>([])

  const {
    data,
    loading: isGraphQlDataLoading,
    error: graphQLRequestError,
  } = useQuery(GET_PROJECT_DATA, {
    variables: { key: 'www-project-' + projectKey },
  })

  useEffect(() => {
    const fetchProjectData = async () => {
      setIsLoading(true)
      const { hits } = await fetchAlgoliaData('projects', projectKey, 1, projectKey)
      if (hits && hits.length > 0) {
        setProject(hits[0] as project)
      }
      setIsLoading(false)
    }

    fetchProjectData()
  }, [projectKey])

  useEffect(() => {
    if (data) {
      setRecentReleases(data?.project?.recentReleases || [])
      setRecentIssues(data?.project?.recentIssues)
    }
    if (graphQLRequestError && !isLoading) {
      toast({
        variant: 'destructive',
        title: 'GraphQL Request Failed',
        description: 'Unable to complete the requested operation.',
      })
    }
  }, [data, graphQLRequestError, isLoading])

  if (isLoading || isGraphQlDataLoading)
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner imageUrl="/img/owasp_icon_white_sm.png" />
      </div>
    )

  if (!project)
    return (
      <ErrorDisplay
        statusCode={404}
        title="Project not found"
        message="Sorry, the project you're looking for doesn't exist"
      />
    )
  const projectDetails = [
    { label: 'Last Updated', value: formatDate(project.updated_at) },
    { label: 'Level', value: project.level[0].toUpperCase() + project.level.slice(1) },
    { label: 'Project Leaders', value: project.leaders.join(', ') },
    { label: 'Type', value: project.type[0].toUpperCase() + project.type.slice(1) },
    {
      label: 'URL',
      value: (
        <Link href={project.url} className="hover:underline dark:text-sky-600">
          {project.url}
        </Link>
      ),
    },
  ]

  const projectStats = {
    contributors: project.contributors_count,
    forks: project.forks_count,
    issues: project.issues_count,
    repositories: project.repositories_count,
    stars: project.stars_count,
  }
  return (
    <DetailsCard
      title={project.name}
      description={project.description}
      details={projectDetails}
      is_active={project.is_active}
      summary={project.summary}
      projectStats={projectStats}
      type="project"
      topContributors={project.top_contributors}
      languages={project.languages}
      topics={project.topics}
      recentReleases={recentReleases}
      recentIssues={recentIssues}
    />
  )
}

export default ProjectDetailsPage
