'use client'
import { useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useState, useEffect } from 'react'
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
  const [committee, setCommittee] = useState<Committee | null>(null)
  const [topContributors, setTopContributors] = useState<Contributor[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(true)

  const { data, error: graphQLRequestError } = useQuery(GetCommitteeDataDocument, {
    variables: { key: committeeKey },
  })

  useEffect(() => {
    if (data?.committee) {
      setCommittee(data.committee as Committee)
      setTopContributors((data.topContributors as Contributor[]) || [])
      setIsLoading(false)
    }
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
      setIsLoading(false)
    }
  }, [data, graphQLRequestError, committeeKey])

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (!committee && !isLoading)
    return (
      <ErrorDisplay
        statusCode={404}
        title="Committee not found"
        message="Sorry, the committee you're looking for doesn't exist"
      />
    )

  // Ensure committee is defined for strict type checks below
  if (!committee) return null

  const details = [
    { label: 'Last Updated', value: formatDate(committee.updatedAt) },
    { label: 'Leaders', value: (committee.leaders || []).join(', ') },
    {
      label: 'URL',
      value: (
        <Link href={committee.url || '#'} className="text-blue-400 hover:underline">
          {committee.url || ''}
        </Link>
      ),
    },
  ]

  const committeeStats = [
    { icon: HiUserGroup, value: committee.contributorsCount ?? 0, unit: 'Contributor' },
    { icon: FaCodeFork, value: committee.forksCount ?? 0, unit: 'Fork' },
    { icon: FaStar, value: committee.starsCount ?? 0, unit: 'Star' },
    {
      icon: FaCode,
      value: committee.repositoriesCount ?? 0,
      unit: 'Repository',
      pluralizedName: 'Repositories',
    },
    { icon: FaExclamationCircle, value: committee.issuesCount ?? 0, unit: 'Issue' },
  ]

  return (
    <DetailsCard
      details={details}
      socialLinks={committee.relatedUrls || []}
      stats={committeeStats}
      summary={committee.summary || ''}
      title={committee.name || ''}
      topContributors={topContributors}
      type="committee"
    />
  )
}