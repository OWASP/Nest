'use client'

import { useQuery } from '@apollo/client'
import {
  faCodeCommit,
  faCodeFork,
  faExclamationCircle,
  faStar,
  faUsers,
} from '@fortawesome/free-solid-svg-icons'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { GET_REPOSITORY_DATA } from 'server/queries/repositoryQueries'
import { TopContributorsTypeGraphql } from 'types/contributor'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'
import { handleAppError, ErrorDisplay } from 'app/global-error'
import SponsorBanner from 'components/SponsorBanner'
import SecondaryCard from 'components/SecondaryCard'

const RepositoryDetailsPage = () => {
  const { repositoryKey, organizationKey } = useParams()
  const [repository, setRepository] = useState(null)
  const [topContributors, setTopContributors] = useState<TopContributorsTypeGraphql[]>([])
  const [recentPullRequests, setRecentPullRequests] = useState(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const { data, error: graphQLRequestError } = useQuery(GET_REPOSITORY_DATA, {
    variables: { repositoryKey: repositoryKey, organizationKey: organizationKey },
  })
  useEffect(() => {
    if (data) {
      setRepository(data?.repository)
      setTopContributors(data?.topContributors)
      setRecentPullRequests(data?.recentPullRequests)
      setIsLoading(false)
    }
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
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
      icon: faCodeCommit,
      value: repository.commitsCount,
      unit: 'Commit',
    },
  ]
  return (
    <>
      <DetailsCard
        details={repositoryDetails}
        languages={repository.languages}
        pullRequests={recentPullRequests}
        recentIssues={repository.issues}
        recentReleases={repository.releases}
        stats={RepositoryStats}
        summary={repository.description}
        title={repository.name}
        topContributors={repository.topContributors}
        topics={repository.topics}
        type="repository"
      />
      <div className="mt-8 max-w-6xl mx-auto">
        <SecondaryCard>
          <SponsorBanner
            entityType="repository"
            entityKey={repositoryKey as string}
            entityName={repository.name}
          />
        </SecondaryCard>
      </div>
    </>
  )
}
export default RepositoryDetailsPage
