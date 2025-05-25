'use client'
import { useQuery } from '@apollo/client'
import {
  faCodeFork,
  faExclamationCircle,
  faFolderOpen,
  faStar,
  faUsers,
} from '@fortawesome/free-solid-svg-icons'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useState, useEffect } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GET_PROJECT_DATA } from 'server/queries/projectQueries'
import { TopContributorsTypeGraphql } from 'types/contributor'
import { ProjectTypeGraphql } from 'types/project'
import { capitalize } from 'utils/capitalize'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'
import PageLayout from 'components/PageLayout'
const ProjectDetailsPage = () => {
  const { projectKey } = useParams()
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [project, setProject] = useState<ProjectTypeGraphql | null>(null)
  const [topContributors, setTopContributors] = useState<TopContributorsTypeGraphql[]>([])
  const { data, error: graphQLRequestError } = useQuery(GET_PROJECT_DATA, {
    variables: { key: projectKey },
  })

  useEffect(() => {
    if (data) {
      setProject(data.project)
      setTopContributors(data.topContributors)
      setIsLoading(false)
    }
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
      setIsLoading(false)
    }
  }, [data, graphQLRequestError, projectKey])

  if (isLoading) {
    return <LoadingSpinner />
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
    { icon: faStar, value: project.starsCount, unit: 'Star' },
    { icon: faCodeFork, value: project.forksCount, unit: 'Fork' },
    {
      icon: faUsers,
      value: project.contributorsCount,
      unit: 'Contributor',
    },
    {
      icon: faExclamationCircle,
      value: project.issuesCount,
      unit: 'Issue',
    },
    {
      icon: faFolderOpen,
      value: project.repositoriesCount,
      unit: 'Repository',
      pluralizedName: 'Repositories',
    },
  ]
  return (
    <PageLayout
      bcItems={[
        { title: 'Projects', href: '/projects' },
        { title: project.name, href: `/projects/${project.key}` },
      ]}
    >
      <DetailsCard
        details={projectDetails}
        is_active={project.isActive}
        languages={project.languages}
        pullRequests={project.recentPullRequests}
        recentIssues={project.recentIssues}
        recentReleases={project.recentReleases}
        repositories={project.repositories}
        stats={projectStats}
        summary={project.summary}
        title={project.name}
        recentMilestones={project.recentMilestones}
        topContributors={topContributors}
        topics={project.topics}
        type="project"
      />
    </PageLayout>
  )
}

export default ProjectDetailsPage
