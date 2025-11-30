'use client'
import { useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { useRouter } from 'next/navigation'
import React, { useState, useEffect } from 'react'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import { GetCommunitySnapshotsDocument } from 'types/__generated__/snapshotQueries.generated'
import type { Snapshot } from 'types/snapshot'
import SnapshotSkeleton from 'components/skeletons/SnapshotSkeleton'
import SnapshotCard from 'components/SnapshotCard'

const SnapshotsPage: React.FC = () => {
  const [snapshots, setSnapshots] = useState<Snapshot[] | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)

  const { data: graphQLData, error: graphQLRequestError } = useQuery(GetCommunitySnapshotsDocument)

  useEffect(() => {
    if (graphQLData) {
      setSnapshots(graphQLData.snapshots)
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

  const handleButtonClick = (snapshot: Snapshot) => {
    router.push(`/snapshots/${snapshot.key}`)
  }

  const renderSnapshotCard = (snapshot: Snapshot) => {
    const SubmitButton = {
      label: 'View Snapshot',
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

  return (
    <div className="min-h-screen p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="text-text flex min-h-screen w-full flex-col items-center justify-normal p-5">
        {isLoading ? (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {Array.from({ length: 12 }).map((_, index) => (
              <SnapshotSkeleton key={index} />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {!snapshots?.length ? (
              <div className="col-span-full py-8 text-center">No Snapshots found</div>
            ) : (
              snapshots.map((snapshot: Snapshot) => (
                <div key={snapshot.key}>{renderSnapshotCard(snapshot)}</div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default SnapshotsPage
