import { useQuery } from '@apollo/client'
import { Link } from '@chakra-ui/react'
import {
  faCode,
  faCodeFork,
  faExclamationCircle,
  faStar,
  faUsers,
} from '@fortawesome/free-solid-svg-icons'
import { GET_PROJECT_DATA } from 'api/queries/projectQueries'
import { toast } from 'hooks/useToast'
import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { ProjectTypeGraphql } from 'types/project'
import { formatDate } from 'utils/dateFormatter'
import { pluralize } from 'utils/pluralize'
import { ErrorDisplay } from 'wrappers/ErrorWrapper'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'
import MetadataManager from 'components/MetadataManager'

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
        <Link href={project.url} className="hover:underline dark:text-sky-600">
          {project.url}
        </Link>
      ),
    },
  ]
  const projectStats = [
    {
      icon: faUsers,
      value: `${project?.contributorsCount || 'No'} ${pluralize(project.contributorsCount, 'Contributor')}`,
    },
    {
      icon: faCodeFork,
      value: `${project?.forksCount || 'No'} ${pluralize(project.forksCount, 'Fork')}`,
    },
    {
      icon: faStar,
      value: `${project?.starsCount || 'No'} ${pluralize(project.starsCount, 'Star')}`,
    },
    {
      icon: faCode,
      value: `${project?.repositoriesCount || 'No'} ${pluralize(project.repositoriesCount, 'Repository', 'Repositories')}`,
    },
    {
      icon: faExclamationCircle,
      value: `${project?.issuesCount || 'No'} ${pluralize(project.issuesCount, 'Issue')}`,
    },
  ]
  return (
    <MetadataManager
      description={project.summary}
      keywords={project.topics}
      pageTitle={project.name || projectKey}
      type={project.type}
      url={project.url}
    >
      <DetailsCard
        details={projectDetails}
        is_active={project.isActive}
        languages={project.languages}
        recentIssues={project.recentIssues}
        recentReleases={project.recentReleases}
        repositories={project.repositories}
        stats={projectStats}
        summary={project.summary}
        title={project.name}
        topContributors={project.topContributors}
        topics={project.topics}
        type="project"
      />
    </MetadataManager>
  )
}

export default ProjectDetailsPage
