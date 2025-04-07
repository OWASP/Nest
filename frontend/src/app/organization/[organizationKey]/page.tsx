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
import { useParams } from 'next/navigation'
import { useState, useEffect } from 'react'
import { GET_ORGANIZATION_DATA } from 'server/queries/organizationQueries'
import { formatDate } from 'utils/dateFormatter'
import { ErrorDisplay } from 'wrappers/ErrorWrapper'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'

const OrganizationDetailsPage = () => {
  const { organizationKey } = useParams()
  const [organization, setOrganization] = useState(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const { data, error: graphQLRequestError } = useQuery(GET_ORGANIZATION_DATA, {
    variables: { login: organizationKey },
  })

  useEffect(() => {
    if (data && data.organization) {
      setOrganization(data.organization)
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
  }, [data, graphQLRequestError, organizationKey])

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (!isLoading && !organization) {
    return (
      <ErrorDisplay
        message="Sorry, the Organization you're looking for doesn't exist"
        statusCode={404}
        title="Organization not found"
      />
    )
  }

  const organizationDetails = [
    {
      label: 'GitHub Profile',
      value: (
        <a href={organization.url} className="text-blue-400 hover:underline">
          @{organization.login}
        </a>
      ),
    },
    {
      label: 'Joined',
      value: formatDate(organization.createdAt),
    },
    {
      label: 'Followers',
      value: organization.followersCount,
    },
    {
      label: 'Location',
      value: organization.location || 'Not provided',
    },
  ]

  const organizationStats = [
    {
      icon: faStar,
      value: organization.stats.totalStars,
      unit: 'Star',
    },
    {
      icon: faCodeFork,
      value: organization.stats.totalForks,
      unit: 'Fork',
    },
    {
      icon: faUsers,
      value: organization.stats.totalContributors,
      unit: 'Contributor',
    },
    {
      icon: faExclamationCircle,
      value: organization.stats.totalIssues,
      unit: 'Issue',
    },
    {
      icon: faCode,
      value: organization.stats.totalRepositories,
      unit: 'Repository',
      pluralizedName: 'Repositories',
    },
  ]

  return (
    <DetailsCard
      details={organizationDetails}
      recentIssues={organization.issues}
      recentReleases={organization.releases}
      repositories={organization.repositories}
      stats={organizationStats}
      summary={organization.description}
      title={organization.name}
      topContributors={organization.topContributors}
      type="organization"
    />
  )
}

export default OrganizationDetailsPage
