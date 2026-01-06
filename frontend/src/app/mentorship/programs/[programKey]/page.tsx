'use client'

import { useQuery } from '@apollo/client/react'
import { useParams } from 'next/navigation'
import { ErrorDisplay } from 'app/global-error'
import { GetProgramAndModulesDocument } from 'types/__generated__/programsQueries.generated'

import { titleCaseWord } from 'utils/capitalize'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'

const ProgramDetailsPage = () => {
  const { programKey } = useParams<{ programKey: string }>()
  const { data, loading: isLoading } = useQuery(GetProgramAndModulesDocument, {
    variables: { programKey },
    skip: !programKey,
  })

  const program = data?.getProgram
  const modules = data?.getProgramModules || []

  if (isLoading) return <LoadingSpinner />

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
      details={programDetails}
      domains={program.domains}
      modules={modules}
      summary={program.description}
      tags={program.tags}
      title={program.name}
      type="program"
    />
  )
}

export default ProgramDetailsPage
