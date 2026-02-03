'use client'

import { useQuery } from '@apollo/client/react'
import capitalize from 'lodash/capitalize'
import { useParams } from 'next/navigation'
import { useState, useEffect } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GetProgramAdminsAndModulesDocument } from 'types/__generated__/moduleQueries.generated'
import { Module } from 'types/mentorship'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'
import { getSimpleDuration } from 'components/ModuleCard'

const ModuleDetailsPage = () => {
  const { programKey, moduleKey } = useParams<{ programKey: string; moduleKey: string }>()
  const [hasMorePRs, setHasMorePRs] = useState(true)
  const [visibleCount, setVisibleCount] = useState(4)
  const [isFetchingMore, setIsFetchingMore] = useState(false)
  const limit = 4

  const {
    data,
    error,
    loading: isLoading,
    fetchMore,
  } = useQuery(GetProgramAdminsAndModulesDocument, {
    fetchPolicy: 'cache-and-network',
    variables: {
      programKey,
      moduleKey,
      limit,
      offset: 0,
    },
  })

  useEffect(() => {
    const prCount = data?.getModule?.recentPullRequests?.length
    if (prCount == null) return
    if (prCount <= limit) {
      setHasMorePRs(prCount >= limit)
    }
  }, [data, limit])

  const programModule = data?.getModule as Module
  const admins = data?.getProgram?.admins

  useEffect(() => {
    if (error) {
      handleAppError(error)
    }
  }, [error])

  if (isLoading && !data) return <LoadingSpinner />

  if (error) {
    return (
      <ErrorDisplay
        statusCode={500}
        title="Error loading module"
        message="An error occurred while loading the module data"
      />
    )
  }

  if (!data || !programModule) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Module Not Found"
        message="Sorry, the module you're looking for doesn't exist."
      />
    )
  }

  const moduleDetails = [
    { label: 'Experience Level', value: capitalize(programModule.experienceLevel) },
    { label: 'Start Date', value: formatDate(programModule.startedAt) },
    { label: 'End Date', value: formatDate(programModule.endedAt) },
    {
      label: 'Duration',
      value: getSimpleDuration(programModule.startedAt, programModule.endedAt),
    },
  ]

  return (
    <DetailsCard
      admins={admins}
      details={moduleDetails}
      domains={programModule.domains}
      mentors={programModule.mentors}
      pullRequests={(programModule.recentPullRequests || []).slice(0, visibleCount)}
      summary={programModule.description}
      tags={programModule.tags}
      title={programModule.name}
      type="module"
      onLoadMorePullRequests={
        hasMorePRs || (programModule.recentPullRequests || []).length > visibleCount
          ? () => {
              if (isFetchingMore) return
              const currentLength = programModule.recentPullRequests?.length || 0
              if (hasMorePRs && currentLength < visibleCount + limit) {
                setIsFetchingMore(true)
                fetchMore({
                  variables: {
                    programKey,
                    moduleKey,
                    offset: currentLength,
                    limit,
                  },
                  updateQuery: (prevResult, { fetchMoreResult }) => {
                    if (!fetchMoreResult) return prevResult
                    const newPRs = fetchMoreResult.getModule?.recentPullRequests || []
                    if (newPRs.length < limit) setHasMorePRs(false)
                    if (newPRs.length === 0) return prevResult
                    return {
                      ...prevResult,
                      getModule: {
                        ...prevResult.getModule,
                        recentPullRequests: [
                          ...(prevResult.getModule?.recentPullRequests || []),
                          ...newPRs,
                        ],
                      },
                    }
                  },
                }).finally(() => setIsFetchingMore(false))
              }
              setVisibleCount((prev) => prev + limit)
            }
          : undefined
      }
      onResetPullRequests={
        visibleCount > limit && (programModule.recentPullRequests || []).length > limit
          ? () => setVisibleCount(limit)
          : undefined
      }
    />
  )
}

export default ModuleDetailsPage
