'use client'
import { useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { FaExclamationCircle } from 'react-icons/fa'
import { FaCodeCommit, FaCodeFork, FaStar } from 'react-icons/fa6'
import { HiUserGroup } from 'react-icons/hi'
import { handleAppError, ErrorDisplay } from 'app/global-error'
import type { Contributor } from 'types/contributor'
import type { Issue } from 'types/issue'
import type { PullRequest } from 'types/pullRequest'
import { GetRepositoryDataDocument, GetRepositoryDataQuery } from 'types/__generated__/repositoryQueries.generated'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'

const RepositoryDetailsPage = () => {
  const { repositoryKey, organizationKey } = useParams<{
    repositoryKey: string
    organizationKey: string
  }>()
  const [repository, setRepository] = useState<GetRepositoryDataQuery['repository'] | null>(null)
  const [topContributors, setTopContributors] = useState<Contributor[]>([])
  const [recentPullRequests, setRecentPullRequests] = useState<GetRepositoryDataQuery['recentPullRequests'] | null>(
    null
  )
  const {
    data,
    error: graphQLRequestError,
    loading: isLoading,
  } = useQuery(GetRepositoryDataDocument, {
    variables: { repositoryKey: repositoryKey, organizationKey: organizationKey },
  })
  useEffect(() => {
    if (data) {
      setRepository(data.repository)
      setTopContributors((data.topContributors as Contributor[]) || [])
      setRecentPullRequests(data.recentPullRequests)
    }
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
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
      value: formatDate(repository?.updatedAt),
    },
    {
      label: 'License',
      value: repository?.license,
    },
    {
      label: 'Size',
      value: repository?.size != null ? `${repository.size} KB` : '',
    },
    {
      label: 'URL',
      value: repository?.url ? (
        <Link href={repository?.url || '#'} className="text-blue-400 hover:underline">
          {repository.url}
        </Link>
      ) : '',
    },
  ]

  const RepositoryStats = [
    {
      icon: FaStar,
      value: repository?.starsCount,
      unit: 'Star',
    },
    {
      icon: FaCodeFork,
      value: repository?.forksCount,
      unit: 'Fork',
    },
    {
      icon: HiUserGroup,
      value: repository?.contributorsCount,
      unit: 'Contributor',
    },
    {
      icon: FaExclamationCircle,
      value: repository?.openIssuesCount,
      unit: 'Issue',
    },
    {
      icon: FaCodeCommit,
      value: repository?.commitsCount,
      unit: 'Commit',
    },
  ]
  return (
    <DetailsCard
      details={repositoryDetails.map((d) => ({ ...d, value: d.value || '' }))}
      entityKey={repository?.project?.key}
      isArchived={repository?.isArchived}
      languages={repository?.languages || []}
      projectName={repository?.project?.name}
      pullRequests={
        recentPullRequests?.map((pr) => ({
          ...pr,
          author: pr.author ? { ...pr.author } : undefined,
        })) as PullRequest[] | undefined
      }
      recentIssues={
        repository?.issues?.map((issue) => ({
          ...issue,
          url: issue.url || '',
          author: issue.author ? { ...issue.author } : undefined,
        })) as Issue[] | undefined
      }
      recentMilestones={repository?.recentMilestones || undefined}
      recentReleases={repository?.releases || undefined}
      stats={RepositoryStats.map((s) => ({ ...s, value: s.value || 0 }))}
      summary={repository?.description}
      title={repository?.name}
      topContributors={topContributors}
      topics={repository?.topics || []}
      type="repository"
    />
  )
}
export default RepositoryDetailsPage
