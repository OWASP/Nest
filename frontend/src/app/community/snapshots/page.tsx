'use client'
import { useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { useRouter } from 'next/navigation'
import React, { useState, useEffect } from 'react'
import { FaRightToBracket } from 'react-icons/fa6'
import { GetCommunitySnapshotsDocument } from 'types/__generated__/snapshotQueries.generated'
import type { Snapshot } from 'types/snapshot'
import SnapshotSkeleton from 'components/skeletons/SnapshotSkeleton'
import SnapshotCard from 'components/SnapshotCard'

const SnapshotsPage: React.FC = () => {
  const [snapshots, setSnapshots] = useState<Snapshot[] | null>(null)

  const {
    data: graphQLData,
    error: graphQLRequestError,
    loading: isLoading,
  } = useQuery(GetCommunitySnapshotsDocument)

  useEffect(() => {
    if (graphQLData) {
      setSnapshots(graphQLData.snapshots)
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
    }
  }, [graphQLData, graphQLRequestError])

  const router = useRouter()

  const handleButtonClick = (snapshot: Snapshot) => {
    router.push(`/community/snapshots/${snapshot.key}`)
  }

  const renderSnapshotCard = (snapshot: Snapshot) => {
    const SubmitButton = {
      label: 'View Details',
      icon: <FaRightToBracket className="h-4 w-4" />,
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
    <div className="min-h-screen p-8 text-gray-800 dark:bg-[#212529] dark:text-gray-300">
      <div className="text-text flex min-h-screen w-full flex-col items-center justify-normal p-5">
        {isLoading ? (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {Array.from({ length: 12 }, (_, index) => (
              <SnapshotSkeleton key={`snapshot-skeleton-${index}`} />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {snapshots?.length ? (
              snapshots.map((snapshot: Snapshot) => (
                <div key={snapshot.key}>{renderSnapshotCard(snapshot)}</div>
              ))
            ) : (
              <div className="col-span-full py-8 text-center">No Snapshots found</div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default SnapshotsPage
