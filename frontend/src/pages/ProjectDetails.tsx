import { useQuery } from '@apollo/client'
import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { GET_PROJECT_DATA } from 'api/queries/projectQueries'
import { toast } from 'hooks/useToast'
import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { formatDate } from 'utils/dateFormatter'
import { ErrorDisplay } from 'wrappers/ErrorWrapper'
import LoadingSpinner from 'components/LoadingSpinner'
import GenericDetails from './CardDetailsPage'

const ProjectDetailsPage = () => {
  const { projectKey } = useParams()
  const [project, setProject] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [recentReleases, setRecentReleases] = useState([])
  const [recentIssues, setRecentIssues] = useState([])

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
        setProject(hits[0])
      }
      setIsLoading(false)
    }

    fetchProjectData()
  }, [projectKey])

  useEffect(() => {
    if (data) {
      setRecentReleases(data?.project?.recentReleases)
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
  const details = [
    { label: 'Type', value: project.type[0].toUpperCase() + project.type.slice(1) },
    { label: 'Level', value: project.level[0].toUpperCase() + project.level.slice(1) },
    { label: 'Organization', value: project.organizations },
    { label: 'Project Leaders', value: project.leaders.join(', ') },
    { label: 'Last Updated', value: formatDate(project.updated_at) },
    {
      label: 'URL',
      value: (
        <a href={project.url} className="hover:underline dark:text-sky-600">
          {project.url}
        </a>
      ),
    },
  ]
  return (
    <GenericDetails
      title={project.name}
      details={details}
      is_active={project.is_active}
      summary={project.summary}
      data={project}
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
