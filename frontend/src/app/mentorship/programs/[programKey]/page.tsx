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
import { titleCaseWord } from 'utils/capitalize'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'

const ProgramDetailsPage = () => {
  const { programKey } = useParams() as { programKey: string }
  const { data: session } = useSession()
  const [isLoading, setIsLoading] = useState(true)
  const [program, setProgram] = useState<Program | null>(null)
  const [modules, setModules] = useState<Module[]>([])

  const { data, error } = useQuery(GET_PROGRAM_AND_MODULES, {
    variables: { programKey },
    skip: !programKey,
  })

  const [updateProgram] = useMutation(UPDATE_PROGRAM_STATUS_MUTATION, {
    onError: (error) => {
      handleAppError(error)
    },
  })

  const username = (session as SessionWithRole)?.user?.login
  const isAdmin = useMemo(
    () => !!program?.admins?.some((admin) => admin.login === username),
    [program, username]
  )
  const canPublish = useMemo(
    () => isAdmin && program?.status?.toLowerCase() === ProgramStatusEnum.DRAFT,
    [isAdmin, program]
  )

  const setPublish = async () => {
    if (!program || !isAdmin) {
      addToast({
        title: 'Permission Denied',
        description: 'Only admins can publish this program.',
        variant: 'solid',
        color: 'danger',
        timeout: 3000,
      })
      return
    }

    addToast({
      title: 'Program Published',
      description: 'The program is now live and the page will refresh.',
      variant: 'solid',
      color: 'success',
      timeout: 3000,
    })

    await updateProgram({
      variables: {
        inputData: {
          key: program.key,
          name: program.name,
          status: 'PUBLISHED',
        },
      },
      refetchQueries: [{ query: GET_PROGRAM_AND_MODULES, variables: { programKey } }],
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
    { label: 'Status', value: titleCaseWord(program.status) },
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
