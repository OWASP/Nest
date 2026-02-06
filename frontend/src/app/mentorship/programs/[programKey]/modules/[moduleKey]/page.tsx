'use client'

import { useQuery } from '@apollo/client/react'
import capitalize from 'lodash/capitalize'
import { useParams } from 'next/navigation'
import { useEffect } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GetProgramAdminsAndModulesDocument } from 'types/__generated__/moduleQueries.generated'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import MentorshipPageSkeleton from 'components/skeletons/MentorshipPageSkeleton'
import { getSimpleDuration } from 'components/ModuleCard'

const ModuleDetailsPage = () => {
  const { programKey, moduleKey } = useParams<{ programKey: string; moduleKey: string }>()

  const {
    data,
    error,
    loading: isLoading,
  } = useQuery(GetProgramAdminsAndModulesDocument, {
    fetchPolicy: 'cache-and-network',
    variables: {
      programKey,
      moduleKey,
    },
  })

  const programModule = data?.getModule
  const admins = data?.getProgram?.admins

  useEffect(() => {
    if (error) {
      handleAppError(error)
    }
  }, [error])

  if (isLoading && !data) return <MentorshipPageSkeleton type="modules" />

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
      pullRequests={programModule.recentPullRequests || []}
      summary={programModule.description}
      tags={programModule.tags}
      title={programModule.name}
      type="module"
    />
  )
}

export default ModuleDetailsPage
