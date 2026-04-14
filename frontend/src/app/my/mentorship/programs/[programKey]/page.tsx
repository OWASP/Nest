'use client'
import { useMutation, useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { BreadcrumbStyleProvider } from 'contexts/BreadcrumbContext'
import { capitalize } from 'lodash'
import { useParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { useMemo } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { ProgramStatusEnum } from 'types/__generated__/graphql'
import { UpdateProgramStatusDocument } from 'types/__generated__/programsMutations.generated'
import { GetProgramAndModulesDocument } from 'types/__generated__/programsQueries.generated'
import type { ExtendedSession } from 'types/auth'
import { titleCaseWord } from 'utils/capitalize'
import { formatDate } from 'utils/dateFormatter'
import CardDetailsHeader from 'components/CardDetailsPage/CardDetailsHeader'
import CardDetailsMetadata from 'components/CardDetailsPage/CardDetailsMetadata'
import CardDetailsPageWrapper from 'components/CardDetailsPage/CardDetailsPageWrapper'
import CardDetailsRepositoriesModules from 'components/CardDetailsPage/CardDetailsRepositoriesModules'
import CardDetailsSummary from 'components/CardDetailsPage/CardDetailsSummary'
import CardDetailsTags from 'components/CardDetailsPage/CardDetailsTags'
import LoadingSpinner from 'components/LoadingSpinner'

const ProgramDetailsPage = () => {
  const { programKey } = useParams<{ programKey: string }>()

  const { data: session } = useSession()
  const username = (session as ExtendedSession)?.user?.login

  const [updateProgram] = useMutation(UpdateProgramStatusDocument, {
    onError: handleAppError,
  })

  const { data, loading: isQueryLoading } = useQuery(GetProgramAndModulesDocument, {
    variables: { programKey },
    skip: !programKey,
    fetchPolicy: 'cache-and-network',
    notifyOnNetworkStatusChange: true,
  })

  const isLoading = isQueryLoading
  const program = data?.getProgram ?? null
  const modules = data?.getProgramModules ?? []

  const isAdmin = useMemo(
    () => !!program?.admins?.some((admin) => admin.login === username),
    [program, username]
  )

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
    { label: 'Mentees Limit', value: String(program?.menteesLimit ?? 0) },
    {
      label: 'Experience Levels',
      value: program?.experienceLevels?.map((level) => titleCaseWord(level)).join(', ') || 'N/A',
    },
  ]

  return (
    <BreadcrumbStyleProvider className="bg-white dark:bg-[#212529]">
      <CardDetailsPageWrapper>
        <CardDetailsHeader
          title={program?.name ?? ''}
          status={program?.status ?? ''}
          setStatus={updateStatus}
          canUpdateStatus={canUpdateStatus}
          programKey={program?.key ?? ''}
          entityKey={program?.key ?? ''}
          admins={program?.admins ?? undefined}
          isActive={true}
          isArchived={false}
          showProgramActions={true}
        />

        <CardDetailsSummary summary={program?.description ?? ''} />

        <CardDetailsMetadata details={programDetails} detailsTitle="Program Details" />

        <CardDetailsTags
          tags={program?.tags ?? undefined}
          domains={program?.domains ?? undefined}
        />

        <CardDetailsRepositoriesModules
          programKey={program?.key ?? ''}
          accessLevel={isAdmin ? 'admin' : 'user'}
          modules={modules}
        />
      </CardDetailsPageWrapper>
    </BreadcrumbStyleProvider>
  )
}

export default ProgramDetailsPage
