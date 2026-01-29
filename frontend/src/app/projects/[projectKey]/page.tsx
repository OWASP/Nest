'use client'
import { useQuery } from '@apollo/client/react'
import upperFirst from 'lodash/upperFirst'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useEffect } from 'react'
import { FaExclamationCircle } from 'react-icons/fa'
import { FaCodeFork, FaFolderOpen, FaStar } from 'react-icons/fa6'
import { HiUserGroup } from 'react-icons/hi'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GetProjectDocument } from 'types/__generated__/projectQueries.generated'
import { getContributionStats } from 'utils/contributionDataUtils'
import { formatDate, getDateRange } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'

const ProjectDetailsPage = () => {
  const { projectKey } = useParams<{ projectKey: string }>()
  const {
    data,
    error: graphQLRequestError,
    loading: isLoading,
  } = useQuery(GetProjectDocument, {
    variables: { key: projectKey },
  })

  const project = data?.project
  const topContributors = data?.topContributors || []

  useEffect(() => {
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
    }
  }, [graphQLRequestError])

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (graphQLRequestError) {
    return (
      <ErrorDisplay
        statusCode={500}
        title="Error loading project"
        message="An error occurred while loading the project data"
      />
    )
  }

  if (!data || !project) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Project not found"
        message="Sorry, the project you're looking for doesn't exist"
      />
    )
  }
  const projectDetails = [
    { label: 'Last Updated', value: formatDate(project.updatedAt) },
    { label: 'Leaders', value: project.leaders.join(', ') },
    {
      label: 'Level',
      value: upperFirst(project.level),
    },
    { label: 'Type', value: upperFirst(project.type) },
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
    { icon: FaStar, value: project.starsCount, unit: 'Star' },
    { icon: FaCodeFork, value: project.forksCount, unit: 'Fork' },
    {
      icon: HiUserGroup,
      value: project.contributorsCount,
      unit: 'Contributor',
    },
    {
      icon: FaExclamationCircle,
      value: project.issuesCount,
      unit: 'Issue',
    },
    {
      icon: FaFolderOpen,
      value: project.repositoriesCount,
      unit: 'Repository',
      pluralizedName: 'Repositories',
    },
  ]

  const { startDate, endDate } = getDateRange({ years: 1 })

  const contributionStats = getContributionStats(
    project.contributionStats,
    project.contributionData
  )

  return (
    <DetailsCard
      contributionData={project.contributionData}
      contributionStats={contributionStats}
      details={projectDetails}
      endDate={endDate}
      entityKey={project.key}
      entityLeaders={project.entityLeaders}
      healthMetricsData={project.healthMetricsList}
      isActive={project.isActive}
      languages={project.languages}
      pullRequests={
        project.recentPullRequests?.map((pr) => ({
          ...pr,
          author: pr.author || undefined,
        })) || []
      }
      recentIssues={
        project.recentIssues?.map((issue) => ({
          ...issue,
          author: issue.author || undefined,
        })) || []
      }
      recentMilestones={project.recentMilestones || undefined}
      recentReleases={
        project.recentReleases?.map((release) => ({
          ...release,
          author: release.author || undefined,
        })) || []
      }
      repositories={
        project.repositories?.map((repo) => ({
          ...repo,
          organization: repo.organization || undefined,
        })) || []
      }
      startDate={startDate}
      stats={projectStats}
      summary={project.summary}
      title={project.name}
      topContributors={topContributors}
      topics={project.topics}
      type="project"
    />
  )
}

export default ProjectDetailsPage
