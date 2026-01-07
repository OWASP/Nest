'use client'
import { useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { FaExclamationCircle } from 'react-icons/fa'
import { FaCodeCommit, FaCodeFork, FaStar } from 'react-icons/fa6'
import { HiUserGroup } from 'react-icons/hi'
import { handleAppError, ErrorDisplay } from 'app/global-error'
import { GetRepositoryDataDocument } from 'types/__generated__/repositoryQueries.generated'
import type { Contributor } from 'types/contributor'
import type { Issue } from 'types/issue'
import type { Milestone } from 'types/milestone'
import type { PullRequest } from 'types/pullRequest'
import type { Release } from 'types/release'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'

interface RepositoryData {
  updatedAt?: string | number
  license?: string
  size?: number
  url: string
  starsCount?: number
  forksCount?: number
  contributorsCount?: number
  openIssuesCount?: number
  commitsCount?: number
  isArchived?: boolean
  languages?: string[]
  description?: string
  name: string
  topics?: string[]
  project?: {
    key: string
    name: string
  }
  issues?: Issue[]
  recentMilestones?: Milestone[]
  releases?: Release[]
}

const RepositoryDetailsPage = () => {
  const { repositoryKey, organizationKey } = useParams<{
    repositoryKey: string
    organizationKey: string
  }>()
  const [repository, setRepository] = useState<RepositoryData | null>(null)
  const [topContributors, setTopContributors] = useState<Contributor[]>([])
  const [recentPullRequests, setRecentPullRequests] = useState<PullRequest[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(true)

  const { data, error: graphQLRequestError } = useQuery(GetRepositoryDataDocument, {
    variables: { repositoryKey: repositoryKey, organizationKey: organizationKey },
  })

  useEffect(() => {
    if (data) {
      setRepository(data.repository as unknown as RepositoryData)
      setTopContributors((data.topContributors as Contributor[]) || [])
      setRecentPullRequests((data.recentPullRequests as PullRequest[]) || [])
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

  if (!repository) {
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
      value: formatDate(repository.updatedAt ?? ''),
    },
    {
      label: 'License',
      value: repository.license || 'N/A',
    },
    {
      label: 'Size',
      value: `${repository.size ?? 0} KB`,
    },
    {
      label: 'URL',
      value: (
        <Link href={repository.url || '#'} className="text-blue-400 hover:underline">
          {repository.url || ''}
        </Link>
      ),
    },
  ]

  const RepositoryStats = [
    {
      icon: FaStar,
      value: repository.starsCount ?? 0,
      unit: 'Star',
    },
    {
      icon: FaCodeFork,
      value: repository.forksCount ?? 0,
      unit: 'Fork',
    },
    {
      icon: HiUserGroup,
      value: repository.contributorsCount ?? 0,
      unit: 'Contributor',
    },
    {
      icon: FaExclamationCircle,
      value: repository.openIssuesCount ?? 0,
      unit: 'Issue',
    },
    {
      icon: FaCodeCommit,
      value: repository.commitsCount ?? 0,
      unit: 'Commit',
    },
  ]

  return (
    <DetailsCard
      details={repositoryDetails}
      entityKey={repository.project?.key || ''}
      isArchived={repository.isArchived ?? false}
      languages={repository.languages || []}
      projectName={repository.project?.name || ''}
      pullRequests={recentPullRequests}
      recentIssues={repository.issues || []}
      recentMilestones={repository.recentMilestones || []}
      recentReleases={repository.releases || []}
      stats={RepositoryStats}
      summary={repository.description || ''}
      title={repository.name || ''}
      topContributors={topContributors}
      topics={repository.topics || []}
      type="repository"
    />
  )
}

export default RepositoryDetailsPage