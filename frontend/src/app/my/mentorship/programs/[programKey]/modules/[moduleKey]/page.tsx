'use client'
import { useQuery } from '@apollo/client/react'
import { capitalize } from 'lodash'
import { useParams } from 'next/navigation'
import { useEffect } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GetProgramAdminsAndModulesDocument } from 'types/__generated__/moduleQueries.generated'
import { Module } from 'types/mentorship'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'
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

  useEffect(() => {
    if (error) {
      handleAppError(error)
    }
  }, [error])

  const mentorshipModule: Module | null | undefined = data?.getModule
  const admins = data?.getProgram?.admins

  if (isLoading && !mentorshipModule) return <LoadingSpinner />

  if (!mentorshipModule) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Module Not Found"
        message="Sorry, the module you're looking for doesn't exist."
      />
    )
  }

  const moduleDetails = [
    { label: 'Experience Level', value: capitalize(mentorshipModule.experienceLevel) },
    { label: 'Start Date', value: formatDate(mentorshipModule.startedAt) },
    { label: 'End Date', value: formatDate(mentorshipModule.endedAt) },
    {
      label: 'Duration',
      value: getSimpleDuration(mentorshipModule.startedAt, mentorshipModule.endedAt),
    },
  ]

  return (
    <DetailsCard
      accessLevel="admin"
      admins={admins}
      details={moduleDetails}
      domains={mentorshipModule.domains}
      entityKey={moduleKey}
      labels={mentorshipModule.labels}
      mentees={mentorshipModule.mentees}
      mentors={mentorshipModule.mentors}
      programKey={programKey}
      summary={mentorshipModule.description}
      tags={mentorshipModule.tags}
      title={mentorshipModule.name}
      type="module"
    />
  )
}

export default ModuleDetailsPage
