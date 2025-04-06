'use client'

import { useQuery } from '@apollo/client'
import {
  faCodeFork,
  faExclamationCircle,
  faHistory,
  faStar,
  faUsers,
} from '@fortawesome/free-solid-svg-icons'
import { addToast } from '@heroui/toast'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { GET_REPOSITORY_DATA } from 'server/queries/repositoryQueries'
import { formatDate } from 'utils/dateFormatter'
import { ErrorDisplay } from 'wrappers/ErrorWrapper'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'

const RepositoryDetailsPage = () => {
  const { repositoryKey } = useParams()
  const [repository, setRepository] = useState(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const { data, error: graphQLRequestError } = useQuery(GET_REPOSITORY_DATA, {
    variables: { repositoryKey: repositoryKey },
  })
  useEffect(() => {
    if (data) {
      setRepository(data?.repository)
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
  }, [data, graphQLRequestError, repositoryKey])

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (!isLoading && !repository) {
    return (
      <ErrorDisplay
        message="Sorry, the Repository you're looking for doesn't exist"
        statusCode={404}
        title="Repository not found"
      />
    )
  }

  const repositoryDetails = [
    {
      label: 'Last Updated',
      value: formatDate(repository.updatedAt),
    },
    {
      label: 'License',
      value: repository.license,
    },
    {
      label: 'Size',
      value: `${repository.size} KB`,
    },
    {
      label: 'URL',
      value: (
        <Link href={repository.url} className="text-blue-400 hover:underline">
          {repository.url}
        </Link>
      ),
    },
  ]

  const RepositoryStats = [
    {
      icon: faStar,
      value: repository.starsCount,
      unit: 'Star',
    },
    {
      icon: faCodeFork,
      value: repository.forksCount,
      unit: 'Fork',
    },
    {
      icon: faUsers,
      value: repository.contributorsCount,
      unit: 'Contributor',
    },

    {
      icon: faExclamationCircle,
      value: repository.openIssuesCount,
      unit: 'Issue',
    },
    {
      icon: faHistory,
      value: repository.commitsCount,
      unit: 'Commit',
    },
  ]
  return (
    <DetailsCard
      details={repositoryDetails}
      languages={repository.languages}
      recentIssues={repository.issues}
      recentReleases={repository.releases}
      stats={RepositoryStats}
      summary={repository.description}
      title={repository.name}
      topContributors={repository.topContributors}
      topics={repository.topics}
      type="repository"
    />
  )
}
export default RepositoryDetailsPage
