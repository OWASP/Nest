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
import type { HealthMetricsProps } from 'types/healthMetrics'
import type { Issue } from 'types/issue'
import type { Milestone } from 'types/milestone'
import type { RepositoryCardProps } from 'types/project'
import type { PullRequest } from 'types/pullRequest'
import type { Release } from 'types/release'
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
  const slackChannelUrl = (slackChannelId: string) =>
    `https://owasp.slack.com/archives/${slackChannelId}`

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
        <Link href={project.url} className="text-blue-400 hover:underline">
          {project.url}
        </Link>
      ),
    },
    ...(project.entityChannels && project.entityChannels.length > 0
      ? [
        {
          label: 'Slack',
          value: (
            <div className="inline-flex flex-wrap gap-3">
              {project.entityChannels.map((ch) => (
                <Link
                  key={ch.slackChannelId}
                  href={slackChannelUrl(ch.slackChannelId)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 hover:underline"
                >
                  #{ch.name}
                </Link>
              ))}
            </div>
          ),
        },
      ]
      : []),
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
      healthMetricsData={project.healthMetricsList as unknown as HealthMetricsProps[]}
      isActive={project.isActive}
      languages={project.languages}
      pullRequests={project.recentPullRequests as unknown as PullRequest[]}
      recentIssues={project.recentIssues as unknown as Issue[]}
      recentMilestones={project.recentMilestones as unknown as Milestone[]}
      recentReleases={project.recentReleases as unknown as Release[]}
      repositories={project.repositories as unknown as RepositoryCardProps[]}
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
