'use client'

import { useQuery } from '@apollo/client'
import { useUpdateProgramStatus } from 'hooks/useUpdateProgramStatus'
import upperFirst from 'lodash/upperFirst'
import { useParams, useSearchParams, useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { useEffect, useMemo, useState } from 'react'
import { ErrorDisplay } from 'app/global-error'
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
  const searchParams = useSearchParams()
  const router = useRouter()
  const shouldRefresh = searchParams.get('refresh') === 'true'

  const { data: session } = useSession()
  const username = (session as ExtendedSession)?.user?.login

  const [program, setProgram] = useState<Program | null>(null)
  const [modules, setModules] = useState<Module[]>([])
  const [isRefetching, setIsRefetching] = useState(false)

  const {
    data,
    refetch,
    loading: isQueryLoading,
  } = useQuery(GET_PROGRAM_AND_MODULES, {
    variables: { programKey },
    skip: !programKey,
    notifyOnNetworkStatusChange: true,
  })

  const isLoading = isQueryLoading || isRefetching

  const isAdmin = useMemo(
    () => !!program?.admins?.some((admin) => admin.login === username),
    [program, username]
  )

  const canUpdateStatus = useMemo(() => {
    if (!isAdmin || !program?.status) return false
    return true
  }, [isAdmin, program])

  const { updateProgramStatus } = useUpdateProgramStatus({
    programKey,
    programName: program?.name || '',
    isAdmin,
    refetchQueries: [{ query: GET_PROGRAM_AND_MODULES, variables: { programKey } }],
  })

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
          router.replace(cleaned ? `?${cleaned}` : window.location.pathname, { scroll: false })
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
      setStatus={updateProgramStatus}
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
