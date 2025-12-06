'use client'
import { useQuery } from '@apollo/client/react'
import { capitalize } from 'lodash'
import { useParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GetProgramAdminsAndModulesDocument } from 'types/__generated__/moduleQueries.generated'
import { Module } from 'types/mentorship'
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
      accessLevel="admin"
      admins={admins}
      details={moduleDetails}
      domains={module.domains}
      entityKey={moduleKey}
      labels={module.labels}
      mentees={module.mentees}
      mentors={module.mentors}
      programKey={programKey}
      summary={module.description}
      tags={module.tags}
      title={module.name}
      type="module"
    />
  )
}

export default ModuleDetailsPage
