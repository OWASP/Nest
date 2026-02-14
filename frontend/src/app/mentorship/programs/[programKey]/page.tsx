'use client'

import { useQuery } from '@apollo/client/react'
import { useParams } from 'next/navigation'
import { useEffect } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GetProgramAndModulesDocument } from 'types/__generated__/programsQueries.generated'

import { titleCaseWord } from 'utils/capitalize'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'

const ProgramDetailsPage = () => {
  const { programKey } = useParams<{ programKey: string }>()
  const {
    data,
    error: graphQLRequestError,
    loading: isLoading,
  } = useQuery(GetProgramAndModulesDocument, {
    fetchPolicy: 'cache-and-network',
    skip: !programKey,
    variables: { programKey },
  })

  const program = data?.getProgram
  const modules = data?.getProgramModules || []

  useEffect(() => {
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
    }
  }, [graphQLRequestError])

  if (isLoading && !data) return <LoadingSpinner />

  if (graphQLRequestError) {
    return (
      <ErrorDisplay
        statusCode={500}
        title="Error loading program"
        message="An error occurred while loading the program data"
      />
    )
  }

  if (!data || !program) {
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
      admins={program.admins ?? undefined}
      details={programDetails}
      domains={program.domains ?? undefined}
      modules={modules}
      recentMilestones={
        (program.recentMilestones as unknown as import('types/milestone').Milestone[]) ?? undefined
      }
      summary={program.description}
      tags={program.tags ?? undefined}
      title={program.name}
      type="program"
    />
  )
}

export default ProgramDetailsPage
