'use client'

import { useQuery, useMutation } from '@apollo/client'
import { addToast } from '@heroui/toast'
import { useParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { useEffect, useMemo, useState } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import {
  GET_PROGRAM_AND_MODULES,
  UPDATE_PROGRAM_STATUS_MUTATION,
} from 'server/queries/programsQueries'
import { Module, type Program, ProgramStatusEnum, SessionWithRole } from 'types/program'
import { capitalize } from 'utils/capitalize'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'

const ProgramDetailsPage = () => {
  const { programId } = useParams() as { programId: string }
  const { data: session } = useSession()
  const [isLoading, setIsLoading] = useState(true)
  const [program, setProgram] = useState<Program | null>(null)
  const [modules, setModules] = useState<Module[]>([])

  const { data, error } = useQuery(GET_PROGRAM_AND_MODULES, {
    variables: { programId },
    skip: !programId,
  })

  const [updateProgram] = useMutation(UPDATE_PROGRAM_STATUS_MUTATION, {
    onCompleted: (data) => {
      setProgram((prev) => (prev ? { ...prev, status: data.updateProgram.status } : null))
      addToast({
        title: 'Program Published',
        description: 'The program is now live.',
        variant: 'solid',
        color: 'success',
        timeout: 3000,
      })
    },
    onError: (error) => {
      handleAppError(error)
    },
  })

  const username = (session as SessionWithRole)?.user?.username
  const isAdmin = useMemo(
    () => !!program?.admins?.some((admin) => admin.login === username),
    [program, username]
  )

  const canPublish = useMemo(
    () => isAdmin && program?.status?.toLowerCase() === ProgramStatusEnum.DRAFT,
    [isAdmin, program]
  )

  const setPublish = async () => {
    if (!program) return

    if (!isAdmin) {
      addToast({
        title: 'Permission Denied',
        description: 'Only admins can publish this program.',
        variant: 'solid',
        color: 'danger',
        timeout: 3000,
      })
      return
    }

    await updateProgram({
      variables: {
        inputData: {
          id: program.id,
          status: 'PUBLISHED',
        },
      },
    })
  }

  useEffect(() => {
    if (data?.program) {
      setProgram(data.program)
      setModules(data.modulesByProgram || [])
    } else if (error) {
      handleAppError(error)
    }

    if (data || error) {
      setIsLoading(false)
    }
  }, [data, error])

  if (isLoading) return <LoadingSpinner />

  if (!program) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Program Not Found"
        message="Sorry, the program you're looking for doesn't exist."
      />
    )
  }

  const programDetails = [
    { label: 'Status', value: capitalize(program.status) },
    { label: 'Start Date', value: formatDate(program.startedAt) },
    { label: 'End Date', value: formatDate(program.endedAt) },
    { label: 'Mentees Limit', value: String(program.menteesLimit) },
    {
      label: 'Experience Levels',
      value: program.experienceLevels?.join(', ') || 'N/A',
    },
  ]

  return (
    <DetailsCard
      modules={modules}
      isDraft={canPublish}
      setPublish={setPublish}
      details={programDetails}
      admins={program.admins}
      tags={program.tags}
      domains={program.domains}
      summary={program.description}
      title={program.name}
      type="program"
    />
  )
}

export default ProgramDetailsPage
