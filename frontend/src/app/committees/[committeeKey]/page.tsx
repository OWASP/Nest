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
import type { Committee } from 'types/committee'
import type { Contributor } from 'types/contributor'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'

export default function CommitteeDetailsPage() {
  const { committeeKey } = useParams<{ committeeKey: string }>()
  const { data, loading, error: graphQLRequestError } = useQuery(GetCommitteeDataDocument, {
    variables: { key: committeeKey },
  })

  useEffect(() => {
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
    }
  }, [graphQLRequestError, committeeKey])

  if (loading) {
    return <LoadingSpinner />
  }

  if (!data?.committee && !loading)
    return (
      <ErrorDisplay
        statusCode={404}
        title="Committee not found"
        message="Sorry, the committee you're looking for doesn't exist"
      />
    )

  const committee = data.committee
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
    <DetailsCard
      details={details}
      socialLinks={committee.relatedUrls}
      stats={committeeStats}
      summary={committee.summary}
      title={committee.name}
      topContributors={data.topContributors}
      type="committee"
    />
  )
}
