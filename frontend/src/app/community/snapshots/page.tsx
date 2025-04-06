'use client'
import { useQuery } from '@apollo/client'
import { addToast } from '@heroui/toast'
import { useRouter } from 'next/navigation'
import React, { useState, useEffect } from 'react'
import { GET_COMMUNITY_SNAPSHOTS } from 'server/queries/snapshotQueries'
import { Snapshots } from 'types/snapshot'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import LoadingSpinner from 'components/LoadingSpinner'
import SnapshotCard from 'components/SnapshotCard'

const SnapshotsPage: React.FC = () => {
  const [snapshots, setSnapshots] = useState<Snapshots[] | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)

  const { data: graphQLData, error: graphQLRequestError } = useQuery(GET_COMMUNITY_SNAPSHOTS)

  useEffect(() => {
    if (graphQLData) {
      setSnapshots(graphQLData?.snapshots)
      setIsLoading(false)
    }
    if (graphQLRequestError) {
      addToast({
        description: 'Unable to complete the requested operation.',
        title: 'GraphQL Request Failed',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'danger',
        variant: 'solid',
      })
      setIsLoading(false)
    }
  }, [graphQLData, graphQLRequestError])

  const router = useRouter()

  const handleButtonClick = (snapshot: Snapshots) => {
    router.push(`/community/snapshots/${snapshot.key}`)
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
    return <LoadingSpinner />
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
