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
import millify from 'millify'
import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { ProjectTypeGraphql } from 'types/project'
import { capitalize } from 'utils/capitalize'
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
    {
      label: 'Level',
      value: capitalize(project.level),
    },
    { label: 'Project Leaders', value: project.leaders.join(', ') },
    { label: 'Type', value: capitalize(project.type) },
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
      icon: faStar,
      value: `${project.starsCount ? millify(project.starsCount, { precision: 1 }) : 'No'}
        ${pluralize(project.starsCount, 'Star')}`,
    },
    {
      icon: faCodeFork,
      value: `${project.forksCount ? millify(project.forksCount, { precision: 1 }) : 'No'}
        ${pluralize(project.forksCount, 'Fork')}`,
    },
    {
      icon: faUsers,
      value: `${
        project.contributorsCount ? millify(project.contributorsCount, { precision: 1 }) : 'No'
      }
        ${pluralize(project.contributorsCount, 'Contributor')}`,
    },
    {
      icon: faExclamationCircle,
      value: `${project.issuesCount ? millify(project.issuesCount, { precision: 1 }) : 'No'}
        ${pluralize(project.issuesCount, 'Issue')}`,
    },
    {
      icon: faCode,
      value: `${
        project.repositoriesCount ? millify(project.repositoriesCount, { precision: 1 }) : 'No'
      }
        ${pluralize(project.repositoriesCount, 'Repository', 'Repositories')}`,
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
