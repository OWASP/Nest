'use client'
import { useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useState, useEffect } from 'react'
import { FaExclamationCircle } from 'react-icons/fa'
import { FaCodeFork, FaFolderOpen, FaStar } from 'react-icons/fa6'
import { HiUserGroup } from 'react-icons/hi'
import { handleAppError, ErrorDisplay } from 'app/global-error'
import { GetOrganizationDataDocument } from 'types/__generated__/organizationQueries.generated'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'
const OrganizationDetailsPage = () => {
  const { organizationKey } = useParams<{ organizationKey: string }>()
  const [organization, setOrganization] = useState(null)
  const [issues, setIssues] = useState(null)
  const [milestones, setMilestones] = useState(null)
  const [pullRequests, setPullRequests] = useState(null)
  const [releases, setReleases] = useState(null)
  const [repositories, setRepositories] = useState(null)
  const [topContributors, setTopContributors] = useState(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const { data: graphQLData, error: graphQLRequestError } = useQuery(GetOrganizationDataDocument, {
    variables: { login: organizationKey },
  })

  useEffect(() => {
    if (graphQLData) {
      setMilestones(graphQLData.recentMilestones)
      setOrganization(graphQLData.organization)
      setIssues(graphQLData.recentIssues)
      setPullRequests(graphQLData.recentPullRequests)
      setReleases(graphQLData.recentReleases)
      setRepositories(graphQLData.repositories)
      setTopContributors(graphQLData.topContributors)
      setIsLoading(false)
    }
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
      setIsLoading(false)
    }
  }, [graphQLData, graphQLRequestError, organizationKey])

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (!isLoading && !graphQLData?.organization) {
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
      value: organization.followersCount,
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
      recentIssues={issues}
      recentReleases={releases}
      recentMilestones={milestones}
      pullRequests={pullRequests}
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
