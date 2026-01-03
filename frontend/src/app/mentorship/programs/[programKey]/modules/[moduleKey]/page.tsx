'use client'

import { useQuery } from '@apollo/client/react'
import capitalize from 'lodash/capitalize'
import { useParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GetProgramAdminsAndModulesDocument } from 'types/__generated__/moduleQueries.generated'
import type { Module } from 'types/mentorship'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'
import { getSimpleDuration } from 'components/ModuleCard'

const ModuleDetailsPage = () => {
  const { programKey, moduleKey } = useParams<{ programKey: string; moduleKey: string }>()
  const [module, setModule] = useState<Module | null>(null)
  const [admins, setAdmins] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)

  const { data, error } = useQuery(GetProgramAdminsAndModulesDocument, {
    variables: {
      programKey,
      moduleKey,
    },
  })

  useEffect(() => {
    if (error) {
      handleAppError(error)
      setHasError(true)
      setModule(null)
      setAdmins(null)
      setIsLoading(false)
      return
    }

    if (data?.getModule) {
      setModule(data.getModule)
      setAdmins(data.getProgram?.admins || null)
      setHasError(false)
      setIsLoading(false)
    } else if (data && !data.getModule) {
      setHasError(true)
      setModule(null)
      setAdmins(null)
      setIsLoading(false)
    }
  }, [data, error, moduleKey, programKey])

  if (isLoading) return <LoadingSpinner />

  if (hasError || !module) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Module Not Found"
        message="Sorry, the module you're looking for doesn't exist or is not available."
      />
    )
  }

  const moduleDetails = [
    { label: 'Experience Level', value: capitalize(module.experienceLevel) },
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
