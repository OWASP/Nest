'use client'

import { useQuery, useMutation } from '@apollo/client'
import { addToast } from '@heroui/toast'
import { useParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import {
  GET_PROGRAM_AND_MODULES,
  UPDATE_PROGRAM_STATUS_MUTATION,
} from 'server/queries/getProgramsQueries'
import { Module, type Program } from 'types/program'
import { capitalize } from 'utils/capitalize'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'

const ProgramDetailsPage = () => {
  const { programId } = useParams()
  const [isLoading, setIsLoading] = useState(true)
  const [program, setProgram] = useState<Program | null>(null)
  const [modules, setModules] = useState<Module[]>(null)

  const { data, error } = useQuery(GET_PROGRAM_AND_MODULES, {
    variables: { programId: programId },
  })

  const [updateProgram, { loading: publishLoading }] = useMutation(UPDATE_PROGRAM_STATUS_MUTATION, {
    onCompleted: (data) => {
      setProgram((prev) => (prev ? { ...prev, status: data.updateProgram.status } : null))
      addToast({
        title: 'Program published',
        description: 'The program is published right now.',
        variant: 'solid',
        color: 'success',
        timeout: 3000,
      })
    },
    onError: (error) => {
      handleAppError(error)
    },
  })

  const setPublish = async () => {
    if (!program) return
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
      setModules(data?.modulesByProgram)
      setProgram(data.program)
      setIsLoading(false)
    } else if (error) {
      handleAppError(error)
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
  console.log(program.status)
  return (
    <DetailsCard
      modules={modules}
      isDraft={program.status === 'DRAFT'}
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
