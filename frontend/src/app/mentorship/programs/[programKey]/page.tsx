'use client'
import { useQuery } from '@apollo/client/react'
import { capitalize } from 'lodash'
import { useParams, useSearchParams, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { ErrorDisplay } from 'app/global-error'
import { GetProgramAndModulesDocument } from 'types/__generated__/programsQueries.generated'
import type { Program, Module } from 'types/mentorship'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'

const ProgramDetailsPage = () => {
  const { programKey } = useParams() as { programKey: string }
  const searchParams = useSearchParams()
  const router = useRouter()
  const shouldRefresh = searchParams.get('refresh') === 'true'
  const {
    data,
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

      if (data?.getProgram) {
        setProgram(data.getProgram)
        setModules(data.getProgramModules || [])
      }
    }

    processResult()
  }, [shouldRefresh, data, refetch, router, searchParams])

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
      details={programDetails}
      tags={program.tags}
      domains={program.domains}
      summary={program.description}
      title={program.name}
      type="program"
    />
  )
}

export default ProgramDetailsPage
