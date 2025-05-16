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
import { GET_PROJECT_DATA } from 'server/queries/projectQueries'
import { TopContributorsTypeGraphql } from 'types/contributor'
import { ProjectTypeGraphql } from 'types/project'
import { capitalize } from 'utils/capitalize'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import SponsorBanner from 'components/SponsorBanner'
import SecondaryCard from 'components/SecondaryCard'

const ProjectDetailsPage = () => {
  const { projectKey } = useParams()
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [project, setProject] = useState<ProjectTypeGraphql | null>(null)
  const [topContributors, setTopContributors] = useState<TopContributorsTypeGraphql[]>([])
  const [recentPullRequests, setRecentPullRequests] = useState(null)

  const { data, error: graphQLRequestError } = useQuery(GET_PROJECT_DATA, {
    variables: { key: projectKey },
  })

  useEffect(() => {
    if (data) {
      setProject(data?.project)
      setTopContributors(data?.topContributors)
      setRecentPullRequests(data.recentPullRequests)
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
    <>
      <DetailsCard
        details={projectDetails}
        is_active={project.isActive}
        languages={project.languages}
        pullRequests={recentPullRequests}
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
      <div className="mt-8 max-w-6xl mx-auto">
        <SecondaryCard>
          <SponsorBanner
            entityType="project"
            entityKey={projectKey as string}
            entityName={project.name}
          />
        </SecondaryCard>
      </div>
    </>
  )
}

export default ProjectDetailsPage
