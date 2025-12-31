'use client'

import { useQuery } from '@apollo/client/react'
import { useParams, useSearchParams, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { ErrorDisplay } from 'app/global-error'
import { GetProgramAndModulesDocument } from 'types/__generated__/programsQueries.generated'

import type { Module, Program } from 'types/mentorship'
import { titleCaseWord } from 'utils/capitalize'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'

const ProgramDetailsPage = () => {
  const { programKey } = useParams<{ programKey: string }>()
  const searchParams = useSearchParams()
  const router = useRouter()
  const shouldRefresh = searchParams.get('refresh') === 'true'
  const {
    data,
    error,
    refetch,
    loading: isQueryLoading,
  } = useQuery(GetProgramAndModulesDocument, {
    variables: { programKey },
    skip: !programKey,
    notifyOnNetworkStatusChange: true,
  })

  const [program, setProgram] = useState<Program | null>(null)
  const [modules, setModules] = useState<Module[]>([])
  const [isRefetching, setIsRefetching] = useState(false)
  const [hasError, setHasError] = useState(false)
  const [hasAttemptedLoad, setHasAttemptedLoad] = useState(false)

  const isLoading = isQueryLoading || isRefetching

  useEffect(() => {
    const processResult = async () => {
      if (shouldRefresh) {
        setIsRefetching(true)
        try {
          await refetch()
        } finally {
          setIsRefetching(false)

          const params = new URLSearchParams(searchParams.toString())
          params.delete('refresh')
          const cleaned = params.toString()
          router.replace(cleaned ? `?${cleaned}` : globalThis.location.pathname, { scroll: false })
        }
      }

      if (error) {
        setHasError(true)
        setProgram(null)
        setModules([])
        setHasAttemptedLoad(true)
        return
      }

      if (data?.getProgram) {
        setProgram(data.getProgram)
        setModules(data.getProgramModules || [])
        setHasError(false)
        setHasAttemptedLoad(true)
      } else if (data && !data.getProgram) {
        setHasError(true)
        setProgram(null)
        setModules([])
        setHasAttemptedLoad(true)
      }
    }

    processResult()
  }, [shouldRefresh, data, error, refetch, router, searchParams, programKey])

  if (isLoading || !hasAttemptedLoad) {
    return <LoadingSpinner />
  }

  if (hasError || !program) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Program Not Found"
        message="Sorry, the program you're looking for doesn't exist or is not available."
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
