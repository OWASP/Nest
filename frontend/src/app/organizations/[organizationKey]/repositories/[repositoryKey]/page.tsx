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
import { formatDate } from 'utils/dateFormatter'
import CardDetailsContributors from 'components/CardDetailsPage/CardDetailsContributors'
import CardDetailsHeader from 'components/CardDetailsPage/CardDetailsHeader'
import CardDetailsIssuesMilestones from 'components/CardDetailsPage/CardDetailsIssuesMilestones'
import CardDetailsMetadata from 'components/CardDetailsPage/CardDetailsMetadata'
import CardDetailsPageWrapper from 'components/CardDetailsPage/CardDetailsPageWrapper'
import CardDetailsSummary from 'components/CardDetailsPage/CardDetailsSummary'
import CardDetailsTags from 'components/CardDetailsPage/CardDetailsTags'
import LoadingSpinner from 'components/LoadingSpinner'
import SponsorCard from 'components/SponsorCard'

const RepositoryDetailsPage = () => {
  const { repositoryKey, organizationKey } = useParams<{
    repositoryKey: string
    organizationKey: string
  }>()
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
  const recentIssues = repository?.issues?.map((issue) => ({
    ...issue,
    author: issue.author ?? undefined,
  }))

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
    <CardDetailsPageWrapper>
      <CardDetailsHeader
        title={repository.name}
        isActive={!repository.isArchived}
        isArchived={repository.isArchived}
        showArchivedBadge={true}
      />

      <CardDetailsSummary summary={repository.description} />

      <CardDetailsMetadata
        details={repositoryDetails}
        stats={RepositoryStats}
        detailsTitle="Repository Details"
      />

      <CardDetailsTags languages={repository.languages} topics={repository.topics} />

      <CardDetailsContributors topContributors={topContributors} />

      <CardDetailsIssuesMilestones
        recentIssues={recentIssues ?? []}
        recentMilestones={repository.recentMilestones ?? []}
        pullRequests={recentPullRequests ?? []}
        recentReleases={repository.releases ?? []}
        showAvatar={true}
      />

      {repository.project?.key && repository.project?.name && (
        <SponsorCard
          target={repository.project.key}
          title={repository.project.name}
          type="project"
        />
      )}
    </CardDetailsPageWrapper>
  )
}
export default RepositoryDetailsPage
