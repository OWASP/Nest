'use client'
import { useMutation, useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { BreadcrumbStyleProvider } from 'contexts/BreadcrumbContext'
import { capitalize } from 'lodash'
import { useParams } from 'next/navigation'
import { useMemo } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { ProgramStatusEnum } from 'types/__generated__/graphql'
import { UpdateProgramStatusDocument } from 'types/__generated__/programsMutations.generated'
import { GetManagementProgramAndModulesDocument } from 'types/__generated__/programsQueries.generated'
import { titleCaseWord } from 'utils/capitalize'
import { formatDate } from 'utils/dateFormatter'
import { isForbiddenGraphQLError } from 'utils/helpers/handleGraphQLError'
import Contributors from 'components/cards/Contributors'
import Header from 'components/cards/Header'
import Metadata from 'components/cards/Metadata'
import PageWrapper from 'components/cards/PageWrapper'
import RepositoriesModules from 'components/cards/RepositoriesModules'
import Summary from 'components/cards/Summary'
import Tags from 'components/cards/Tags'
import LoadingSpinner from 'components/LoadingSpinner'

const ProgramDetailsPage = () => {
  const { programKey } = useParams<{ programKey: string }>()

  const [updateProgram] = useMutation(UpdateProgramStatusDocument, {
    onError: handleAppError,
  })

  const {
    data,
    loading: isLoading,
    error: queryError,
  } = useQuery(GetManagementProgramAndModulesDocument, {
    variables: { programKey },
    skip: !programKey,
    fetchPolicy: 'cache-and-network',
    notifyOnNetworkStatusChange: true,
  })

  const program = data?.managementProgram ?? null
  const modules = data?.managementProgramModules ?? []

  // Role comes straight from the backend, so we never rely on a failing request
  // to tell an admin/mentor apart from a mentee.
  const userRole = program?.userRole ?? null
  const isAdmin = userRole === 'admin'
  // Admins and mentors share the full management view; mentees get a read-only one.
  const isPrivileged = isAdmin || userRole === 'mentor'

  const canUpdateStatus = useMemo(() => {
    if (!isAdmin || !program?.status) return false
    return true
  }, [isAdmin, program])

  const updateStatus = async (newStatus: string) => {
    if (!Object.values(ProgramStatusEnum).includes(newStatus as ProgramStatusEnum)) {
      addToast({
        color: 'danger',
        description: 'The provided status is not valid.',
        timeout: 3000,
        title: 'Invalid Status',
        variant: 'solid',
      })
      return
    }

    if (!program || !isAdmin) {
      addToast({
        color: 'danger',
        description: 'Only admins can update the program status.',
        timeout: 3000,
        title: 'Permission Denied',
        variant: 'solid',
      })
      return
    }

    try {
      await updateProgram({
        variables: {
          inputData: {
            key: program.key,
            name: program.name,
            status: newStatus as ProgramStatusEnum,
          },
        },
        refetchQueries: [
          {
            query: GetManagementProgramAndModulesDocument,
            variables: { programKey },
          },
        ],
      })

      addToast({
        title: `Program status updated to ${capitalize(newStatus)}`,
        description: 'The status has been successfully updated.',
        variant: 'solid',
        color: 'success',
        timeout: 3000,
      })
    } catch (err) {
      handleAppError(err)
    }
  }

  if (queryError && isForbiddenGraphQLError(queryError)) {
    return (
      <ErrorDisplay
        statusCode={403}
        title="Access Denied"
        message="You do not have permission to manage this program."
      />
    )
  }

  if (isLoading && !data) return <LoadingSpinner />

  if (!program && !isLoading) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Program Not Found"
        message="Sorry, the program you're looking for doesn't exist."
      />
    )
  }

  const programDetails = [
    { label: 'Status', value: titleCaseWord(program?.status ?? '') },
    { label: 'Start Date', value: formatDate(program?.startedAt ?? '') },
    { label: 'End Date', value: formatDate(program?.endedAt ?? '') },
    // Full program configuration is only shown to admins and mentors, not mentees.
    ...(isPrivileged
      ? [
          { label: 'Mentees Limit', value: String(program?.menteesLimit ?? 0) },
          {
            label: 'Experience Levels',
            value:
              program?.experienceLevels?.map((level) => titleCaseWord(level)).join(', ') || 'N/A',
          },
        ]
      : []),
  ]

  return (
    <BreadcrumbStyleProvider className="bg-white dark:bg-[#212529]">
      <PageWrapper>
        <Header
          title={program?.name ?? ''}
          status={program?.status ?? ''}
          setStatus={updateStatus}
          canUpdateStatus={canUpdateStatus}
          programKey={program?.key ?? ''}
          entityKey={program?.key ?? ''}
          admins={program?.admins ?? undefined}
          isActive={true}
          isArchived={false}
          showProgramActions={isPrivileged}
        />

        <Summary summary={program?.description ?? ''} />

        <Metadata details={programDetails} detailsTitle="Program Details" />

        <Tags tags={program?.tags ?? undefined} domains={program?.domains ?? undefined} />

        {isPrivileged && (
          <Contributors
            entityKey={program?.key ?? ''}
            programKey={programKey}
            admins={program?.admins ?? undefined}
          />
        )}

        <RepositoriesModules
          programKey={program?.key ?? ''}
          accessLevel={isAdmin ? 'admin' : 'user'}
          modules={modules}
        />
      </PageWrapper>
    </BreadcrumbStyleProvider>
  )
}

export default ProgramDetailsPage
