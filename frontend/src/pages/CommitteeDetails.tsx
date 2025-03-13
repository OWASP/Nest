import { useQuery } from '@apollo/client'
import {
  faCode,
  faCodeFork,
  faExclamationCircle,
  faStar,
  faUsers,
} from '@fortawesome/free-solid-svg-icons'
import { GET_COMMITTEE_DATA } from 'api/queries/committeeQueries'
import { toaster } from 'components/ui/toaster'
import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import type { CommitteeDetailsTypeGraphQL } from 'types/committee'
import { formatDate } from 'utils/dateFormatter'
import { ErrorDisplay } from 'wrappers/ErrorWrapper'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'
import MetadataManager from 'components/MetadataManager'

export default function CommitteeDetailsPage() {
  const { committeeKey } = useParams<{ committeeKey: string }>()
  const [committee, setCommittee] = useState<CommitteeDetailsTypeGraphQL | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)

  const { data, error: graphQLRequestError } = useQuery<{ committee: CommitteeDetailsTypeGraphQL }>(
    GET_COMMITTEE_DATA,
    {
      variables: { key: committeeKey },
    }
  )

  useEffect(() => {
    if (data?.committee) {
      setCommittee(data.committee)
      setIsLoading(false)
    }
    if (graphQLRequestError) {
      toaster.create({
        description: 'Unable to complete the requested operation.',
        title: 'GraphQL Request Failed',
        type: 'error',
      })
      setIsLoading(false)
    }
  }, [data, graphQLRequestError, committeeKey])

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner imageUrl="/img/owasp_icon_white_sm.png" />
      </div>
    )
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
        <a href={committee.url} className="hover:underline dark:text-sky-600">
          {committee.url}
        </a>
      ),
    },
  ]

  const committeeStats = [
    { icon: faUsers, value: `${committee?.contributorsCount || 'No'} Contributors` },
    { icon: faCodeFork, value: `${committee?.forksCount || 'No'} Forks` },
    { icon: faStar, value: `${committee?.starsCount || 'No'} Stars` },
    { icon: faCode, value: `${committee?.repositoriesCount || 'No'} Repositories` },
    { icon: faExclamationCircle, value: `${committee?.issuesCount || 'No'} Issues` },
  ]

  return (
    <MetadataManager pageTitle={committee.name} description={committee.summary} url={committee.url}>
      <DetailsCard
        details={details}
        socialLinks={committee.relatedUrls}
        stats={committeeStats}
        summary={committee.summary}
        title={committee.name}
        topContributors={committee.topContributors}
        type="committee"
      />
    </MetadataManager>
  )
}
