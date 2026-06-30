'use client'
import { useQuery } from '@apollo/client/react'
import { BreadcrumbStyleProvider } from 'contexts/BreadcrumbContext'
import { capitalize } from 'lodash'
import { useParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { useEffect } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import {
  GetManagementProgramAdminsAndModulesDocument,
  GetModuleByIdDocument,
} from 'types/__generated__/moduleQueries.generated'
import { hasExtendedUser } from 'types/auth'
import { Module } from 'types/mentorship'
import { formatDate } from 'utils/dateFormatter'
import { isForbiddenGraphQLError } from 'utils/helpers/handleGraphQLError'
import Contributors from 'components/cards/Contributors'
import Header from 'components/cards/Header'
import Metadata from 'components/cards/Metadata'
import PageWrapper from 'components/cards/PageWrapper'
import Summary from 'components/cards/Summary'
import Tags from 'components/cards/Tags'
import LoadingSpinner from 'components/LoadingSpinner'
import { getSimpleDuration } from 'components/ModuleCard'

const ModuleDetailsPage = () => {
  const { programKey, moduleKey } = useParams<{ programKey: string; moduleKey: string }>()

  const { data: session, status: sessionStatus } = useSession()
  const isProjectLeader = hasExtendedUser(session) ? session.user.isLeader : false
  const isMentor = hasExtendedUser(session) ? session.user.isMentor : false
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

  const isMenteeUser =
    sessionStatus === 'authenticated' && !isProjectLeader && isForbiddenGraphQLError(error)

  const { data: menteeModuleData, loading: isMenteeModuleLoading } = useQuery(
    GetModuleByIdDocument,
    {
      fetchPolicy: 'cache-and-network',
      skip: !isMenteeUser,
      variables: {
        programKey,
        moduleKey,
      },
    }
  )

  useEffect(() => {
    if (error && !isForbiddenGraphQLError(error)) {
      handleAppError(error)
    }
  }, [error])

  const mentorshipModule: Module | null | undefined = data?.managementModule
  const admins = data?.managementProgram?.admins

  if (isMenteeUser) {
    if (isMenteeModuleLoading && !menteeModuleData) return <LoadingSpinner />

    const menteeModule = menteeModuleData?.getModule ?? null

    if (!menteeModule) {
      return (
        <ErrorDisplay
          statusCode={404}
          title="Module Not Found"
          message="Sorry, the module you're looking for doesn't exist or you are not enrolled."
        />
      )
    }

    const menteeModuleDetails = [
      { label: 'Experience Level', value: capitalize(menteeModule.experienceLevel) },
      { label: 'Start Date', value: formatDate(String(menteeModule.startedAt)) },
      { label: 'End Date', value: formatDate(String(menteeModule.endedAt)) },
      {
        label: 'Duration',
        value: getSimpleDuration(String(menteeModule.startedAt), String(menteeModule.endedAt)),
      },
    ]

    return (
      <BreadcrumbStyleProvider className="bg-white dark:bg-[#212529]">
        <PageWrapper>
          <Header
            title={menteeModule.name}
            programKey={programKey}
            moduleKey={moduleKey}
            entityKey={moduleKey}
            accessLevel="user"
            isActive={true}
            isArchived={false}
            showModuleActions={false}
          />
          <Summary summary={menteeModule.description} />
          <Metadata details={menteeModuleDetails} detailsTitle="Module Details" />
          <Tags
            entityKey={moduleKey}
            tags={menteeModule.tags ?? undefined}
            domains={menteeModule.domains ?? undefined}
          />
          <Contributors
            entityKey={moduleKey}
            programKey={programKey}
            mentors={menteeModule.mentors ?? undefined}
            mentees={menteeModule.mentees ?? undefined}
          />
        </PageWrapper>
      </BreadcrumbStyleProvider>
    )
  }

  if (error && isForbiddenGraphQLError(error)) {
    return (
      <ErrorDisplay
        statusCode={403}
        title="Access Denied"
        message="You do not have permission to manage this module."
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

  return (
    <BreadcrumbStyleProvider className="bg-white dark:bg-[#212529]">
      <PageWrapper>
        <Header
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

        <Summary summary={mentorshipModule.description} />

        <Metadata details={moduleDetails} detailsTitle="Module Details" />

        <Tags
          entityKey={moduleKey}
          tags={mentorshipModule.tags ?? undefined}
          domains={mentorshipModule.domains ?? undefined}
          labels={mentorshipModule.labels ?? undefined}
        />

        <Contributors
          entityKey={moduleKey}
          programKey={programKey}
          mentors={mentorshipModule.mentors ?? undefined}
          mentees={mentorshipModule.mentees ?? undefined}
        />
      </PageWrapper>
    </BreadcrumbStyleProvider>
  )
}

export default ModuleDetailsPage
