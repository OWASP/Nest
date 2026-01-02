'use client'
import { useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useEffect } from 'react'
import { FaExclamationCircle } from 'react-icons/fa'
import { FaCodeCommit, FaCodeFork, FaStar } from 'react-icons/fa6'
import { HiUserGroup } from 'react-icons/hi'
import { handleAppError, ErrorDisplay } from 'app/global-error'
import { GetRepositoryDataDocument } from 'types/__generated__/repositoryQueries.generated'
import type { Contributor } from 'types/contributor'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'

const RepositoryDetailsPage = () => {
  const { repositoryKey, organizationKey } = useParams<{
    repositoryKey: string
    organizationKey: string
  }>()
  const { data, loading, error: graphQLRequestError } = useQuery(GetRepositoryDataDocument, {
    variables: { repositoryKey: repositoryKey, organizationKey: organizationKey },
  })
  useEffect(() => {
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
    }
  }, [graphQLRequestError, repositoryKey])

  if (loading) {
    return <LoadingSpinner />
  }

  if (!loading && !data?.repository) {
    return (
      <ErrorDisplay
        message="Sorry, the Repository you're looking for doesn't exist"
        statusCode={404}
        title="Repository not found"
      />
    )
  }

  const repository = data.repository
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
      icon: FaStar,
      value: repository.starsCount,
      unit: 'Star',
    },
    {
      icon: FaCodeFork,
      value: repository.forksCount,
      unit: 'Fork',
    },
    {
      icon: HiUserGroup,
      value: repository.contributorsCount,
      unit: 'Contributor',
    },
    {
      icon: FaExclamationCircle,
      value: repository.openIssuesCount,
      unit: 'Issue',
    },
    {
      icon: FaCodeCommit,
      value: repository.commitsCount,
      unit: 'Commit',
    },
  ]
  return (
    <DetailsCard
      details={repositoryDetails}
      entityKey={repository.project?.key}
      isArchived={repository.isArchived}
      languages={repository.languages}
      projectName={repository.project?.name}
      pullRequests={data.recentPullRequests}
      recentIssues={repository.issues}
      recentMilestones={repository.recentMilestones}
      recentReleases={repository.releases}
      stats={RepositoryStats}
      summary={repository.description}
      title={repository.name}
      topContributors={data.topContributors}
      topics={repository.topics}
      type="repository"
    />
  )
}
export default RepositoryDetailsPage
