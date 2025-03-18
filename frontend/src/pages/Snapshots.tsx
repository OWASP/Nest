import { useQuery } from '@apollo/client'
import { GET_COMMUNITY_SNAPSHOTS } from 'api/queries/snapshotQueries'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Snapshots } from 'types/snapshot'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import SnapshotCard from 'components/SnapshotCard'
import LoadingSpinner from 'components/LoadingSpinner'
import { toaster } from 'components/ui/toaster'

const SnapshotsPage = () => {
  const [snapshots, setSnapshots] = useState<Snapshots[] | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const { data: graphQLData, error: graphQLRequestError } = useQuery(GET_COMMUNITY_SNAPSHOTS)

  useEffect(() => {
    if (graphQLData) {
      setSnapshots(graphQLData.snapshots)
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
  }, [graphQLData, graphQLRequestError])

  const navigate = useNavigate()

  const handleButtonClick = (snapshot: Snapshots) => {
    navigate(`/community/snapshots/${snapshot.key}`)
  }

  const renderSnapshotCard = (snapshot: Snapshots) => {
    const SubmitButton = {
      label: 'View Details',
      icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
      onclick: () => handleButtonClick(snapshot),
    }

    return (
      <SnapshotCard
        key={snapshot.key}
        title={snapshot.title}
        button={SubmitButton}
        startAt={snapshot.startAt}
        endAt={snapshot.endAt}
      />
    )
  }

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner imageUrl="/img/owasp_icon_white_sm.png" />
      </div>
    )
  }

  return (
    <div className="mt-16 min-h-screen p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mt-16 flex min-h-screen w-full flex-col items-center justify-normal p-5 text-text">
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {!snapshots?.length ? (
            <div className="col-span-full py-8 text-center">No Snapshots found</div>
          ) : (
            snapshots.map((snapshot: Snapshots) => (
              <div key={snapshot.key}>{renderSnapshotCard(snapshot)}</div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default SnapshotsPage
