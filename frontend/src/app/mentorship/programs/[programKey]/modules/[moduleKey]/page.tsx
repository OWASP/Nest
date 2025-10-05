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
import LoadingSpinner from 'components/LoadingSpinner'
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
    { label: 'Experience Level', value: upperFirst(module.experienceLevel) },
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
      admins={admins}
      tags={module.tags}
      domains={module.domains}
      summary={module.description}
      mentors={module.mentors}
      type="module"
    />
  )
}

export default ModuleDetailsPage
