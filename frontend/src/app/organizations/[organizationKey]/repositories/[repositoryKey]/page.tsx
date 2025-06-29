'use client'

import { useQuery } from '@apollo/client'
import {
  faCodeCommit,
  faCodeFork,
  faExclamationCircle,
  faStar,
  faUsers,
} from '@fortawesome/free-solid-svg-icons'
import _ from 'lodash'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { handleAppError, ErrorDisplay } from 'app/global-error'
import { GET_ORGANIZATION_METADATA } from 'server/queries/organizationQueries'
import { GET_REPOSITORY_DATA } from 'server/queries/repositoryQueries'
import type { Contributor } from 'types/contributor'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'
import PageLayout from 'components/PageLayout'

const RepositoryDetailsPage = () => {
  const { repositoryKey, organizationKey } = useParams()
  const [repository, setRepository] = useState(null)
  const [topContributors, setTopContributors] = useState<Contributor[]>([])
  const [recentPullRequests, setRecentPullRequests] = useState(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [organizationMetaData, setOrganizationMetaData] = useState(null)
  const { data, error: graphQLRequestError } = useQuery(GET_REPOSITORY_DATA, {
    variables: { repositoryKey: repositoryKey, organizationKey: organizationKey },
  })
  const { data: organizationData } = useQuery(GET_ORGANIZATION_METADATA, {
    variables: { login: organizationKey },
  })

  useEffect(() => {
    if (data) {
      setRepository(data.repository)
      setTopContributors(data.topContributors)
      setRecentPullRequests(data.recentPullRequests)
      setIsLoading(false)
    }
    if (organizationData) {
      setOrganizationMetaData(organizationData)
    }
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
      setIsLoading(false)
    }
  }, [data, graphQLRequestError, repositoryKey, organizationData])

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
    <PageLayout
      breadcrumbItems={[
        { title: 'Organizations' },
        { title: _.get(organizationMetaData, 'organization.name', organizationKey) },
        { title: 'Repositories' },
        { title: _.get(repository, 'name', repositoryKey) },
      ]}
    >
      <DetailsCard
        details={repositoryDetails}
        languages={repository.languages}
        pullRequests={recentPullRequests}
        recentIssues={repository.issues}
        recentReleases={repository.releases}
        stats={RepositoryStats}
        summary={repository.description}
        title={repository.name}
        topContributors={topContributors}
        topics={repository.topics}
        recentMilestones={repository.recentMilestones}
        type="repository"
      />
    </PageLayout>
  )
}
export default RepositoryDetailsPage
