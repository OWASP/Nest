'use client'

import { useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useEffect } from 'react'
import { FaExclamationCircle } from 'react-icons/fa'
import { FaCodeFork, FaFolderOpen, FaStar } from 'react-icons/fa6'
import { HiUserGroup } from 'react-icons/hi'
import { handleAppError, ErrorDisplay } from 'app/global-error'
import { GetOrganizationDataDocument } from 'types/__generated__/organizationQueries.generated'
import type { Issue } from 'types/issue'
import type { Milestone } from 'types/milestone'
import type { RepositoryCardProps } from 'types/project'
import type { PullRequest } from 'types/pullRequest'
import type { Release } from 'types/release'
import { formatDate } from 'utils/dateFormatter'
import CardDetailsContributors from 'components/CardDetailsPage/CardDetailsContributors'
import CardDetailsHeader from 'components/CardDetailsPage/CardDetailsHeader'
import CardDetailsIssuesMilestones from 'components/CardDetailsPage/CardDetailsIssuesMilestones'
import CardDetailsMetadata from 'components/CardDetailsPage/CardDetailsMetadata'
import CardDetailsPageWrapper from 'components/CardDetailsPage/CardDetailsPageWrapper'
import CardDetailsRepositoriesModules from 'components/CardDetailsPage/CardDetailsRepositoriesModules'
import CardDetailsSummary from 'components/CardDetailsPage/CardDetailsSummary'
import OrganizationDetailsPageSkeleton from 'components/skeletons/OrganizationDetailsPageSkeleton'
const OrganizationDetailsPage = () => {
  const { organizationKey } = useParams<{ organizationKey: string }>()
  const {
    data: graphQLData,
    error: graphQLRequestError,
    loading: isLoading,
  } = useQuery(GetOrganizationDataDocument, {
    variables: { login: organizationKey },
  })

  useEffect(() => {
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
    }
  }, [graphQLRequestError, organizationKey])

  if (isLoading) {
    return (
      <output>
        <OrganizationDetailsPageSkeleton />
      </output>
    )
  }

  const {
    organization,
    recentIssues,
    recentMilestones,
    recentPullRequests,
    recentReleases,
    repositories,
    topContributors,
  } = graphQLData ?? {}

  if (!organization) {
    return (
      <ErrorDisplay
        message="Sorry, the organization you're looking for doesn't exist"
        statusCode={404}
        title="Organization not found"
      />
    )
  }

  const organizationDetails = [
    {
      label: 'GitHub Profile',
      value: (
        <Link href={organization.url} className="text-blue-400 hover:underline">
          @{organization.login}
        </Link>
      ),
    },
    {
      label: 'Created',
      value: formatDate(organization.createdAt),
    },
    {
      label: 'Followers',
      value: String(organization.followersCount),
    },
    {
      label: 'Location',
      value: organization.location,
    },
  ]

  const organizationStats = [
    {
      icon: FaStar,
      value: organization.stats.totalStars,
      unit: 'Star',
    },
    {
      icon: FaCodeFork,
      value: organization.stats.totalForks,
      unit: 'Fork',
    },
    {
      icon: HiUserGroup,
      value: organization.stats.totalContributors,
      unit: 'Contributor',
    },
    {
      icon: FaExclamationCircle,
      value: organization.stats.totalIssues,
      unit: 'Issue',
    },
    {
      icon: FaFolderOpen,
      value: organization.stats.totalRepositories,
      unit: 'Repository',
      pluralizedName: 'Repositories',
    },
  ]

  return (
    <CardDetailsPageWrapper>
      <CardDetailsHeader title={organization.name} isActive={true} isArchived={false} />

      <CardDetailsSummary summary={organization.description} />

      <CardDetailsMetadata
        details={organizationDetails}
        stats={organizationStats}
        detailsTitle="Organization Details"
      />

      <CardDetailsContributors topContributors={topContributors} />

      <CardDetailsIssuesMilestones
        recentIssues={recentIssues as Issue[]}
        recentMilestones={recentMilestones as Milestone[]}
        pullRequests={recentPullRequests as PullRequest[]}
        recentReleases={
          recentReleases?.map((release) => ({
            ...release,
            publishedAt: release.publishedAt as string,
          })) as Release[]
        }
        showAvatar={true}
      />

      <CardDetailsRepositoriesModules
        repositories={
          repositories?.map((repo) => ({
            ...repo,
            organization: repo.organization ? { login: repo.organization.login } : undefined,
          })) as RepositoryCardProps[]
        }
      />
    </CardDetailsPageWrapper>
  )
}

export default OrganizationDetailsPage
