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
import { IS_PROJECT_HEALTH_ENABLED } from 'utils/env.client'
import CardDetailsContributions from 'components/CardDetailsPage/CardDetailsContributions'
import CardDetailsContributors from 'components/CardDetailsPage/CardDetailsContributors'
import CardDetailsHeader from 'components/CardDetailsPage/CardDetailsHeader'
import CardDetailsIssuesMilestones from 'components/CardDetailsPage/CardDetailsIssuesMilestones'
import CardDetailsLeaders from 'components/CardDetailsPage/CardDetailsLeaders'
import CardDetailsMetadata from 'components/CardDetailsPage/CardDetailsMetadata'
import CardDetailsPageWrapper from 'components/CardDetailsPage/CardDetailsPageWrapper'
import CardDetailsRepositoriesModules from 'components/CardDetailsPage/CardDetailsRepositoriesModules'
import CardDetailsSummary from 'components/CardDetailsPage/CardDetailsSummary'
import CardDetailsTags from 'components/CardDetailsPage/CardDetailsTags'
import HealthMetrics from 'components/HealthMetrics'
import LoadingSpinner from 'components/LoadingSpinner'
import SponsorCard from 'components/SponsorCard'

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
    <CardDetailsPageWrapper>
      <CardDetailsHeader
        title={project.name}
        isActive={project.isActive}
        isArchived={false}
        showHealthMetrics={true}
      />

      <CardDetailsSummary summary={project.summary} />

      <CardDetailsMetadata
        details={projectDetails}
        stats={projectStats}
        detailsTitle="Project Details"
      />

      <CardDetailsTags languages={project.languages} topics={project.topics} />

      <CardDetailsLeaders entityLeaders={project.entityLeaders} />

      <CardDetailsContributions
        hasContributions={
          !!(
            (contributionStats && contributionStats.total > 0) ||
            (project.contributionData && Object.keys(project.contributionData).length > 0)
          )
        }
        contributionStats={contributionStats}
        contributionData={project.contributionData}
        startDate={startDate}
        endDate={endDate}
        title="Project Contribution Activity"
      />

      <CardDetailsContributors topContributors={topContributors} />

      <CardDetailsIssuesMilestones
        recentIssues={project.recentIssues as unknown as Issue[]}
        recentMilestones={project.recentMilestones as unknown as Milestone[]}
        pullRequests={project.recentPullRequests as unknown as PullRequest[]}
        recentReleases={project.recentReleases as unknown as Release[]}
        showAvatar={true}
      />

      <CardDetailsRepositoriesModules
        repositories={project.repositories as unknown as RepositoryCardProps[]}
      />

      {IS_PROJECT_HEALTH_ENABLED &&
        project.healthMetricsList &&
        project.healthMetricsList.length > 0 && (
          <HealthMetrics data={project.healthMetricsList as unknown as HealthMetricsProps[]} />
        )}

      {project.key && project.name && (
        <SponsorCard target={project.key} title={project.name} type="project" />
      )}
    </CardDetailsPageWrapper>
  )
}

export default ProjectDetailsPage
