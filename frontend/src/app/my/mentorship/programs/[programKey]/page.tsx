'use client'

import { useQuery, useMutation } from '@apollo/client'
import { addToast } from '@heroui/toast'
import upperFirst from 'lodash/upperFirst'
import { useParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { useEffect, useMemo, useState } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { UPDATE_PROGRAM_STATUS_MUTATION } from 'server/mutations/programsMutations'
import { GET_PROGRAM_AND_MODULES } from 'server/queries/programsQueries'
import type { ExtendedSession } from 'types/auth'
import type { Module, Program } from 'types/mentorship'
import { ProgramStatusEnum } from 'types/mentorship'
import { titleCaseWord } from 'utils/capitalize'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'

const ProgramDetailsPage = () => {
  const { programKey } = useParams() as { programKey: string }

  const { data: session } = useSession()
  const username = (session as ExtendedSession)?.user?.login

  const [program, setProgram] = useState<Program | null>(null)
  const [modules, setModules] = useState<Module[]>([])

  const [updateProgram] = useMutation(UPDATE_PROGRAM_STATUS_MUTATION, {
    onError: handleAppError,
  })

  const { data, loading: isQueryLoading } = useQuery(GET_PROGRAM_AND_MODULES, {
    variables: { programKey },
    skip: !programKey,
    notifyOnNetworkStatusChange: true,
  })

  const isLoading = isQueryLoading

  const isAdmin = useMemo(
    () => !!program?.admins?.some((admin) => admin.login === username),
    [program, username]
  )

  const canUpdateStatus = useMemo(() => {
    if (!isAdmin || !program?.status) return false
    return true
  }, [isAdmin, program])

  const updateStatus = async (newStatus: ProgramStatusEnum) => {
    if (!program || !isAdmin) {
      addToast({
        title: 'Permission Denied',
        description: 'Only admins can update the program status.',
        variant: 'solid',
        color: 'danger',
        timeout: 3000,
      })
      return
    }

    try {
      await updateProgram({
        variables: {
          inputData: {
            key: program.key,
            name: program.name,
            status: newStatus,
          },
        },
      })

      addToast({
        title: `Program status updated to ${upperFirst(newStatus)}`,
        description: 'The status has been successfully updated.',
        variant: 'solid',
        color: 'success',
        timeout: 3000,
      })
    } catch (err) {
      handleAppError(err)
    }
  }

  useEffect(() => {
    if (data?.getProgram) {
      setProgram(data.getProgram)
      setModules(data.getProgramModules || [])
    }
  }, [data])

  if (isLoading) return <LoadingSpinner />

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
    { label: 'Status', value: titleCaseWord(program.status) },
    { label: 'Start Date', value: formatDate(program.startedAt) },
    { label: 'End Date', value: formatDate(program.endedAt) },
    { label: 'Mentees Limit', value: String(program.menteesLimit) },
    {
      label: 'Experience Levels',
      value: program.experienceLevels?.map((level) => titleCaseWord(level)).join(', ') || 'N/A',
    },
  ]

  return (
    <DetailsCard
      programKey={program.key}
      modules={modules}
      status={program.status}
      setStatus={updateStatus}
      canUpdateStatus={canUpdateStatus}
      details={programDetails}
      admins={program.admins}
      tags={program.tags}
      domains={program.domains}
      summary={program.description}
      title={program.name}
      accessLevel="admin"
      type="program"
    />
  )
}

export default ProgramDetailsPage
