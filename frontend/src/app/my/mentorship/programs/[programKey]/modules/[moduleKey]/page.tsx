'use client'
import { useQuery } from '@apollo/client/react'
import { BreadcrumbStyleProvider } from 'contexts/BreadcrumbContext'
import { capitalize } from 'lodash'
import { useParams } from 'next/navigation'
import { useEffect } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GetProgramAdminsAndModulesDocument } from 'types/__generated__/moduleQueries.generated'
import { Module } from 'types/mentorship'
import { formatDate } from 'utils/dateFormatter'
import CardDetailsContributors from 'components/CardDetailsPage/CardDetailsContributors'
import CardDetailsHeader from 'components/CardDetailsPage/CardDetailsHeader'
import CardDetailsMetadata from 'components/CardDetailsPage/CardDetailsMetadata'
import CardDetailsPageWrapper from 'components/CardDetailsPage/CardDetailsPageWrapper'
import CardDetailsSummary from 'components/CardDetailsPage/CardDetailsSummary'
import CardDetailsTags from 'components/CardDetailsPage/CardDetailsTags'
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
    { label: 'Start Date', value: formatDate(String(mentorshipModule.startedAt)) },
    { label: 'End Date', value: formatDate(String(mentorshipModule.endedAt)) },
    {
      label: 'Duration',
      value: getSimpleDuration(
        String(mentorshipModule.startedAt),
        String(mentorshipModule.endedAt)
      ),
    },
  ]

  return (
    <BreadcrumbStyleProvider className="bg-white dark:bg-[#212529]">
      <CardDetailsPageWrapper>
        <CardDetailsHeader
          title={mentorshipModule.name}
          programKey={programKey}
          moduleKey={moduleKey}
          entityKey={moduleKey}
          accessLevel="admin"
          admins={admins ?? undefined}
          mentors={mentorshipModule.mentors ?? undefined}
          isActive={true}
          isArchived={false}
          showModuleActions={true}
        />

        <CardDetailsSummary summary={mentorshipModule.description} />

        <CardDetailsMetadata details={moduleDetails} detailsTitle="Module Details" />

        <CardDetailsTags
          entityKey={moduleKey}
          tags={mentorshipModule.tags ?? undefined}
          domains={mentorshipModule.domains ?? undefined}
          labels={mentorshipModule.labels ?? undefined}
        />

        <CardDetailsContributors
          entityKey={moduleKey}
          programKey={programKey}
          admins={admins ?? undefined}
          mentors={mentorshipModule.mentors ?? undefined}
          mentees={mentorshipModule.mentees ?? undefined}
        />
      </CardDetailsPageWrapper>
    </BreadcrumbStyleProvider>
  )
}

export default ModuleDetailsPage
