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
import type { GetRepositoryDataQuery } from 'types/__generated__/repositoryQueries.generated'
import type { Contributor } from 'types/contributor'
import type { Issue } from 'types/issue'
import type { Milestone } from 'types/milestone'
import type { PullRequest } from 'types/pullRequest'
import type { Release } from 'types/release'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'

const RepositoryDetailsPage = () => {
  const { repositoryKey, organizationKey } = useParams<{
    repositoryKey: string
    organizationKey: string
  }>()
<<<<<<< enable-strict-mode
  const [repository, setRepository] = useState<GetRepositoryDataQuery['repository']>(null)
  const [topContributors, setTopContributors] = useState<Contributor[]>([])
  const [recentPullRequests, setRecentPullRequests] = useState<
    GetRepositoryDataQuery['recentPullRequests']
  >([])
=======
>>>>>>> main
  const {
    data,
    error: graphQLRequestError,
    loading: isLoading,
  } = useQuery(GetRepositoryDataDocument, {
    variables: { repositoryKey: repositoryKey, organizationKey: organizationKey },
  })

  const repository = data?.repository
  const topContributors = data?.topContributors ?? []
  const recentPullRequests = data?.recentPullRequests

  useEffect(() => {
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
    }
  }, [graphQLRequestError])

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
      pullRequests={recentPullRequests as unknown as PullRequest[]}
      recentIssues={repository.issues as unknown as Issue[]}
      recentMilestones={repository.recentMilestones as unknown as Milestone[]}
      recentReleases={repository.releases as unknown as Release[]}
      stats={RepositoryStats}
      summary={repository.description}
      title={repository.name}
      topContributors={topContributors}
      topics={repository.topics}
      type="repository"
    />
  )
}
export default RepositoryDetailsPage
