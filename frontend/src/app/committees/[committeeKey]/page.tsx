'use client'
import { useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useEffect } from 'react'
import { FaExclamationCircle } from 'react-icons/fa'
import { FaCode, FaCodeFork, FaStar } from 'react-icons/fa6'
import { HiUserGroup } from 'react-icons/hi'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GetCommitteeDataDocument } from 'types/__generated__/committeeQueries.generated'
import { formatDate } from 'utils/dateFormatter'
import Contributors from 'components/cards/Contributors'
import Header from 'components/cards/Header'
import Metadata from 'components/cards/Metadata'
import PageWrapper from 'components/cards/PageWrapper'
import Summary from 'components/cards/Summary'
import LoadingSpinner from 'components/LoadingSpinner'

export default function CommitteeDetailsPage() {
  const { committeeKey } = useParams<{ committeeKey: string }>()

  const {
    data,
    error: graphQLRequestError,
    loading: isLoading,
  } = useQuery(GetCommitteeDataDocument, {
    variables: { key: committeeKey },
  })

  const committee = data?.committee
  const topContributors = data?.topContributors || []

  useEffect(() => {
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
    }
  }, [graphQLRequestError, committeeKey])

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (graphQLRequestError) {
    return (
      <ErrorDisplay
        statusCode={500}
        title="Error loading committee"
        message="An error occurred while loading the committee data"
      />
    )
  }

  if (!data || !committee) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Committee not found"
        message="Sorry, the committee you're looking for doesn't exist"
      />
    )
  }

  const details = [
    { label: 'Last Updated', value: formatDate(committee.updatedAt) },
    { label: 'Leaders', value: committee.leaders.join(', ') },
    {
      label: 'URL',
      value: (
        <Link href={committee.url} className="text-blue-400 hover:underline">
          {committee.url}
        </Link>
      ),
    },
  ]

  const committeeStats = [
    { icon: HiUserGroup, value: committee.contributorsCount, unit: 'Contributor' },
    { icon: FaCodeFork, value: committee.forksCount, unit: 'Fork' },
    { icon: FaStar, value: committee.starsCount, unit: 'Star' },
    {
      icon: FaCode,
      value: committee.repositoriesCount,
      unit: 'Repository',
      pluralizedName: 'Repositories',
    },
    { icon: FaExclamationCircle, value: committee.issuesCount, unit: 'Issue' },
  ]

  return (
    <PageWrapper>
      <Header title={committee.name} />

      <Summary summary={committee.summary} />

      <Metadata
        details={details}
        stats={committeeStats}
        socialLinks={committee.relatedUrls}
        showSocialLinks={true}
        detailsTitle="Committee Details"
      />

      <Contributors topContributors={topContributors} />
    </PageWrapper>
  )
}
