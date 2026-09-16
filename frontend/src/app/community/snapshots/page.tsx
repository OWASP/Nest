'use client'
import { useQuery } from '@apollo/client/react'
import { Input } from '@heroui/react'
import { addToast } from '@heroui/toast'
import { useRouter } from 'next/navigation'
import React, { useState, useEffect } from 'react'
import { FaRightToBracket, FaXmark } from 'react-icons/fa6'
import { GetCommunitySnapshotsDocument } from 'types/__generated__/snapshotQueries.generated'
import type { Snapshot } from 'types/snapshot'
import Pagination from 'components/Pagination'
import SnapshotSkeleton from 'components/skeletons/SnapshotSkeleton'
import SnapshotCard from 'components/SnapshotCard'

const SNAPSHOTS_PER_PAGE = 12

const getLocalToday = () => {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
}

const SnapshotsPage: React.FC = () => {
  const [snapshots, setSnapshots] = useState<Snapshot[] | null>(null)
  const [totalCount, setTotalCount] = useState(0)
  const [currentPage, setCurrentPage] = useState(1)
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  const filterVariables = (() => {
    const vars: Record<string, string> = {}
    if (startDate) {
      vars.startAtGte = `${startDate}T00:00:00`
    }
    if (endDate) {
      vars.startAtLte = `${endDate}T23:59:59`
    }
    return vars
  })()

  const {
    data: graphQLData,
    error: graphQLRequestError,
    loading: isLoading,
  } = useQuery(GetCommunitySnapshotsDocument, {
    variables: {
      limit: SNAPSHOTS_PER_PAGE,
      offset: (currentPage - 1) * SNAPSHOTS_PER_PAGE,
      ...filterVariables,
    },
  })

  useEffect(() => {
    if (graphQLData) {
      setSnapshots(graphQLData.snapshots)
      setTotalCount(graphQLData.snapshotsCount)
    }
    if (graphQLRequestError) {
      setSnapshots(null)
      setTotalCount(0)
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

  const totalPages = Math.ceil(totalCount / SNAPSHOTS_PER_PAGE)

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleStartDateChange = (value: string) => {
    setStartDate(value)
    setCurrentPage(1)
  }

  const handleEndDateChange = (value: string) => {
    setEndDate(value)
    setCurrentPage(1)
  }

  const clearFilters = () => {
    setStartDate('')
    setEndDate('')
    setCurrentPage(1)
  }

  const hasFilters = startDate || endDate

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
    <div className="p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="text-text flex w-full flex-col items-center justify-normal p-5">
        <div className="mb-6 flex w-full flex-wrap items-center justify-center gap-3">
          <Input
            aria-label="Start date"
            classNames={{
              base: 'w-auto max-w-44',
              inputWrapper:
                'h-12 rounded-lg border border-gray-300 bg-white shadow-none hover:bg-white data-[hover=true]:bg-white dark:border-gray-600 dark:bg-gray-800 dark:hover:bg-gray-800 dark:data-[hover=true]:bg-gray-800',
              input: 'text-sm font-medium text-gray-800 dark:text-gray-200',
            }}
            max={endDate || getLocalToday()}
            onValueChange={handleStartDateChange}
            placeholder="Start date"
            type="date"
            value={startDate}
          />
          <span className="text-sm text-gray-500 dark:text-gray-400">to</span>
          <Input
            aria-label="End date"
            classNames={{
              base: 'w-auto max-w-44',
              inputWrapper:
                'h-12 rounded-lg border border-gray-300 bg-white shadow-none hover:bg-white data-[hover=true]:bg-white dark:border-gray-600 dark:bg-gray-800 dark:hover:bg-gray-800 dark:data-[hover=true]:bg-gray-800',
              input: 'text-sm font-medium text-gray-800 dark:text-gray-200',
            }}
            max={getLocalToday()}
            min={startDate || undefined}
            onValueChange={handleEndDateChange}
            placeholder="End date"
            type="date"
            value={endDate}
          />
          {hasFilters && (
            <button
              aria-label="Clear date filters"
              className="inline-flex h-12 items-center gap-1.5 rounded-lg border border-gray-300 bg-white px-3 text-sm font-medium text-gray-600 shadow-none transition-colors hover:bg-gray-100 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700"
              onClick={clearFilters}
              type="button"
            >
              <FaXmark className="h-3.5 w-3.5" />
              Clear
            </button>
          )}
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {Array.from({ length: SNAPSHOTS_PER_PAGE }, (_, index) => (
              <SnapshotSkeleton key={`snapshot-skeleton-${index}`} />
            ))}
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {snapshots?.length ? (
                snapshots.map((snapshot: Snapshot) => (
                  <div key={snapshot.key}>{renderSnapshotCard(snapshot)}</div>
                ))
              ) : (
                <div className="col-span-full py-8 text-center">No Snapshots found</div>
              )}
            </div>
            {totalPages > 1 && (
              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={handlePageChange}
                isLoaded={!isLoading}
              />
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default SnapshotsPage
