'use client'
import { useQuery } from '@apollo/client'
import {
  faCode,
  faCodeFork,
  faExclamationCircle,
  faStar,
  faUsers,
} from '@fortawesome/free-solid-svg-icons'
import { addToast } from '@heroui/toast'
import millify from 'millify'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useState, useEffect } from 'react'
import { GET_PROJECT_DATA } from 'server/queries/projectQueries'
import { ProjectTypeGraphql } from 'types/project'
import { capitalize } from 'utils/capitalize'
import { formatDate } from 'utils/dateFormatter'
import { pluralize } from 'utils/pluralize'
import { ErrorDisplay } from 'wrappers/ErrorWrapper'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'
const ProjectDetailsPage = () => {
  const { projectKey } = useParams()
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [project, setProject] = useState<ProjectTypeGraphql | null>(null)

  const { data, error: graphQLRequestError } = useQuery(GET_PROJECT_DATA, {
    variables: { key: projectKey },
  })

  useEffect(() => {
    if (data) {
      setProject(data?.project)
      setIsLoading(false)
    }
    if (graphQLRequestError) {
      addToast({
        description: 'Unable to complete the requested operation.',
        title: 'GraphQL Request Failed',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'danger',
        variant: 'solid',
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
    { label: 'Leaders', value: project.leaders.join(', ') },
    {
      label: 'Level',
      value: capitalize(project.level),
    },
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
  )
}

export default ProjectDetailsPage
