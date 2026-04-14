'use client'

import { useQuery } from '@apollo/client/react'
import { BreadcrumbStyleProvider } from 'contexts/BreadcrumbContext'
import { useParams } from 'next/navigation'
import { useEffect } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GetProgramAndModulesDocument } from 'types/__generated__/programsQueries.generated'

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
    <BreadcrumbStyleProvider className="bg-white dark:bg-[#212529]">
      <CardDetailsPageWrapper>
        <CardDetailsHeader
          title={program.name}
          admins={program.admins ?? undefined}
          isActive={true}
          isArchived={false}
          showProgramActions={true}
        />

        <CardDetailsSummary summary={program.description} />

        <CardDetailsMetadata details={programDetails} detailsTitle="Program Details" />

        <CardDetailsTags tags={program.tags ?? undefined} domains={program.domains ?? undefined} />

        <CardDetailsRepositoriesModules modules={modules} />
      </CardDetailsPageWrapper>
    </BreadcrumbStyleProvider>
  )
}

export default ProgramDetailsPage
