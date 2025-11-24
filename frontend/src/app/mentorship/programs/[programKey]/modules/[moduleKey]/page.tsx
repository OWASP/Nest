'use client'

import { useQuery } from '@apollo/client/react'
import upperFirst from 'lodash/upperFirst'
import { useParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GetProgramAdminsAndModulesDocument } from 'types/__generated__/moduleQueries.generated'
import type { Module } from 'types/mentorship'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import DetailsCardSkeleton from 'components/DetailsCardSkeleton'
import { getSimpleDuration } from 'components/ModuleCard'

const ModuleDetailsPage = () => {
  const { programKey, moduleKey } = useParams<{ programKey: string; moduleKey: string }>()
  const [module, setModule] = useState<Module | null>(null)
  const [admins, setAdmins] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  const { data, error } = useQuery(GetProgramAdminsAndModulesDocument, {
    variables: {
      programKey,
      moduleKey,
    },
  })

  useEffect(() => {
    if (data?.getModule) {
      setModule(data.getModule)
      setAdmins(data.getProgram.admins)
      setIsLoading(false)
    } else if (error) {
      handleAppError(error)
      setIsLoading(false)
    }
  }, [data, error])

  if (isLoading) return <DetailsCardSkeleton />

  if (!module) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Module Not Found"
        message="Sorry, the module you're looking for doesn't exist."
      />
    )
  }

  // @ts-ignore
  if (data?.getProgram?.status !== 'PUBLISHED') {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Program Not Found"
        message="Sorry, the program for this module is not published."
      />
    )
  }

  const moduleDetails = [
    { label: 'Experience Level', value: upperFirst(module.experienceLevel.toLowerCase()) },
    { label: 'Start Date', value: formatDate(module.startedAt) },
    { label: 'End Date', value: formatDate(module.endedAt) },
    {
      label: 'Duration',
      value: getSimpleDuration(module.startedAt, module.endedAt),
    },
  ]

  return (
    <DetailsCard
      admins={admins}
      details={moduleDetails}
      domains={module.domains}
      mentors={module.mentors}
      summary={module.description}
      tags={module.tags}
      title={module.name}
      type="module"
    />
  )
}

export default ModuleDetailsPage
