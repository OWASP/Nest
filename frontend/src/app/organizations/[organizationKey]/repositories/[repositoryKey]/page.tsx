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
import Contributors from 'components/cards/Contributors'
import Header from 'components/cards/Header'
import IssuesMilestones from 'components/cards/IssuesMilestones'
import Metadata from 'components/cards/Metadata'
import PageWrapper from 'components/cards/PageWrapper'
import Summary from 'components/cards/Summary'
import Tags from 'components/cards/Tags'
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
  const recentIssues = repository?.recentIssues?.map((issue) => ({
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
    <PageWrapper>
      <Header
        title={repository.name}
        isActive={!repository.isArchived}
        isArchived={repository.isArchived}
        showArchivedBadge={true}
      />

      <Summary summary={repository.description} />

      <Metadata
        details={repositoryDetails}
        stats={RepositoryStats}
        detailsTitle="Repository Details"
      />

      <Tags languages={repository.languages} topics={repository.topics} />

      <Contributors topContributors={topContributors} />

      <IssuesMilestones
        recentIssues={recentIssues ?? []}
        recentMilestones={repository.recentMilestones ?? []}
        pullRequests={recentPullRequests ?? []}
        recentReleases={repository.recentReleases ?? []}
        showAvatar={true}
      />

      {repository.project?.key && repository.project?.name && (
        <SponsorCard
          target={repository.project.key}
          title={repository.project.name}
          type="project"
        />
      )}
    </PageWrapper>
  )
}
export default RepositoryDetailsPage
