'use client'
import { useQuery } from '@apollo/client'
import {
  faCode,
  faCodeFork,
  faExclamationCircle,
  faStar,
  faUsers,
} from '@fortawesome/free-solid-svg-icons'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useState, useEffect } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GET_COMMITTEE_DATA } from 'server/queries/committeeQueries'
import type { Committee } from 'types/committee'
import type { Contributor } from 'types/contributor'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'
import PageLayout from 'components/PageLayout'
export default function CommitteeDetailsPage() {
  const { committeeKey } = useParams<{ committeeKey: string }>()
  const [committee, setCommittee] = useState<Committee | null>(null)
  const [topContributors, setTopContributors] = useState<Contributor[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(true)

  const { data, error: graphQLRequestError } = useQuery(GET_COMMITTEE_DATA, {
    variables: { key: committeeKey },
  })

  useEffect(() => {
    if (data?.committee) {
      setCommittee(data.committee)
      setTopContributors(data.topContributors)
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
    { icon: faUsers, value: committee.contributorsCount, unit: 'Contributor' },
    { icon: faCodeFork, value: committee.forksCount, unit: 'Fork' },
    { icon: faStar, value: committee.starsCount, unit: 'Star' },
    {
      icon: faCode,
      value: committee.repositoriesCount,
      unit: 'Repository',
      pluralizedName: 'Repositories',
    },
    { icon: faExclamationCircle, value: committee.issuesCount, unit: 'Issue' },
  ]

  return (
    <PageLayout breadcrumbItems={{ title: committee.name }}>
      <DetailsCard
        details={details}
        socialLinks={committee.relatedUrls}
        stats={committeeStats}
        summary={committee.summary}
        title={committee.name}
        topContributors={topContributors}
        type="committee"
      />
    </PageLayout>
  )
}
