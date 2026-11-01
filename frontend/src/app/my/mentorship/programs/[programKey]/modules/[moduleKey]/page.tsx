'use client'
import { useQuery } from '@apollo/client/react'
import { BreadcrumbStyleProvider } from 'contexts/BreadcrumbContext'
import { capitalize } from 'lodash'
import { useParams } from 'next/navigation'
import { useEffect } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GetManagementProgramAdminsAndModulesDocument } from 'types/__generated__/moduleQueries.generated'
import { Module } from 'types/mentorship'
import { formatDate } from 'utils/dateFormatter'
import { isForbiddenGraphQLError } from 'utils/helpers/handleGraphQLError'
import Contributors from 'components/cards/Contributors'
import Header from 'components/cards/Header'
import Metadata from 'components/cards/Metadata'
import ModuleIssues from 'components/cards/ModuleIssues'
import PageWrapper from 'components/cards/PageWrapper'
import Summary from 'components/cards/Summary'
import Tags from 'components/cards/Tags'
import LoadingSpinner from 'components/LoadingSpinner'
import { getSimpleDuration } from 'components/ModuleCard'

const ModuleDetailsPage = () => {
  const { programKey, moduleKey } = useParams<{ programKey: string; moduleKey: string }>()

  const {
    data,
    error,
    loading: isLoading,
  } = useQuery(GetManagementProgramAdminsAndModulesDocument, {
    fetchPolicy: 'cache-and-network',
    variables: {
      programKey,
      moduleKey,
    },
  })

  useEffect(() => {
    if (error && !isForbiddenGraphQLError(error)) {
      handleAppError(error)
    }
  }, [error])

  const mentorshipModule: Module | null | undefined = data?.managementModule
  const admins = data?.managementProgram?.admins

  // Role comes straight from the backend; admins and mentors get the full
  // management view, mentees a read-only one.
  const isPrivileged =
    mentorshipModule?.userRole === 'admin' || mentorshipModule?.userRole === 'mentor'

  if (error && isForbiddenGraphQLError(error)) {
    return (
      <ErrorDisplay
        statusCode={403}
        title="Access Denied"
        message="You do not have permission to view this module."
      />
    )
  }

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

  const summaryDetailsGridClass = mentorshipModule.description
    ? 'grid grid-cols-1 gap-x-6 md:grid-cols-3'
    : 'grid grid-cols-1 gap-x-6'

  return (
    <BreadcrumbStyleProvider className="bg-white dark:bg-[#212529]">
      <PageWrapper>
        <Header
          title={mentorshipModule.name}
          programKey={programKey}
          moduleKey={moduleKey}
          entityKey={moduleKey}
          accessLevel={isPrivileged ? 'admin' : 'user'}
          admins={admins ?? undefined}
          mentors={mentorshipModule.mentors ?? undefined}
          isActive={true}
          isArchived={false}
          showModuleActions={true}
        />

        <div className={summaryDetailsGridClass}>
          <Summary summary={mentorshipModule.description} className="md:col-span-2" />

          <Metadata
            details={moduleDetails}
            detailsTitle="Module Details"
            className="md:col-span-1"
          />
        </div>

        <Tags
          entityKey={moduleKey}
          tags={mentorshipModule.tags ?? undefined}
          domains={mentorshipModule.domains ?? undefined}
        />

        <Contributors
          entityKey={moduleKey}
          programKey={programKey}
          mentors={mentorshipModule.mentors ?? undefined}
          mentees={mentorshipModule.mentees ?? undefined}
        />

        <ModuleIssues programKey={programKey} moduleKey={moduleKey} />
      </PageWrapper>
    </BreadcrumbStyleProvider>
  )
}

export default ModuleDetailsPage
