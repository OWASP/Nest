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
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
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
      <div data-testid="org-loading-skeleton">
        <OrganizationDetailsPageSkeleton />
      </div>
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
    <DetailsCard
      details={organizationDetails}
      recentIssues={recentIssues}
      recentReleases={recentReleases}
      recentMilestones={recentMilestones}
      pullRequests={recentPullRequests}
      repositories={repositories}
      stats={organizationStats}
      summary={organization.description}
      title={organization.name}
      topContributors={topContributors}
      type="organization"
    />
  )
}

export default OrganizationDetailsPage
