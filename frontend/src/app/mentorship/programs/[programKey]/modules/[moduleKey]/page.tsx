'use client'

import { useQuery } from '@apollo/client'
import { useParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GET_PROGRAM_ADMINS_AND_MODULES } from 'server/queries/moduleQueries'
import type { Module } from 'types/program'
import { titleCaseWord } from 'utils/capitalize'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'
import { getSimpleDuration } from 'components/ModuleCard'

const ModuleDetailsPage = () => {
  const { programKey, moduleKey } = useParams()
  const [module, setModule] = useState<Module | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const { data, error } = useQuery(GET_PROGRAM_ADMINS_AND_MODULES, {
    variables: {
      programKey,
      moduleKey,
    },
  })

  useEffect(() => {
    if (data?.getModule) {
      setModule(data.getModule)
      setIsLoading(false)
    } else if (error) {
      handleAppError(error)
      setIsLoading(false)
    }
  }, [data, error])

  if (isLoading) return <LoadingSpinner />

  if (!module) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Module Not Found"
        message="Sorry, the module you're looking for doesn't exist."
      />
    )
  }

  const moduleDetails = [
    { label: 'Experience Level', value: titleCaseWord(module.experienceLevel) },
    { label: 'Start Date', value: formatDate(module.startedAt) },
    { label: 'End Date', value: formatDate(module.endedAt) },
    {
      label: 'Duration',
      value: getSimpleDuration(module.startedAt, module.endedAt),
    },
  ]

  return (
    <DetailsCard
      details={moduleDetails}
      title={module.name}
      tags={module.tags}
      domains={module.domains}
      summary={module.description}
      mentors={module.mentors}
      type="module"
    />
  )
}

export default ModuleDetailsPage
