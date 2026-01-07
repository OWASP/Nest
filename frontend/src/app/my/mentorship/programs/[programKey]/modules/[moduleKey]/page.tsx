'use client'

import { useQuery } from '@apollo/client/react'
import { capitalize } from 'lodash'
import { useParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
// Importing the specific Query type for strict typing of the 'data' response
import { 
  GetProgramAdminsAndModulesDocument
} from 'types/__generated__/moduleQueries.generated'
import { Contributor } from 'types/contributor'
import { Module } from 'types/mentorship'
import { formatDate } from 'utils/dateFormatter'
import DetailsCard from 'components/CardDetailsPage'
import LoadingSpinner from 'components/LoadingSpinner'
import { getSimpleDuration } from 'components/ModuleCard'

/**
 * ModuleDetailsPage Component
 * Fetches and displays detailed information about a specific mentorship module.
 */
const ModuleDetailsPage = () => {
  // Extracting keys from URL parameters with explicit types
  const { programKey, moduleKey } = useParams<{ programKey: string; moduleKey: string }>()
  
  // State management for module data and admins list
  const [module, setModule] = useState<Module | null>(null)
  const [admins, setAdmins] = useState<Contributor[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // Apollo useQuery hook using the generated document for type safety
  const { data, error } = useQuery(GetProgramAdminsAndModulesDocument, {
    variables: {
      programKey,
      moduleKey,
    },
  })

  useEffect(() => {
    // Check if the required data has been successfully fetched
    if (data?.getModule && data?.getProgram) {
      setModule(data.getModule as Module)

      // Accessing the admin list from the program data
      // Using a local variable to help TypeScript infer types from the generated query
      const programAdmins = data.getProgram.admins ?? []

      // Mapping raw GraphQL data to our internal Contributor interface
      // Removing 'any' by letting TypeScript infer the type from GetProgramAdminsAndModulesQuery
      const formattedAdmins: Contributor[] = programAdmins.map((admin) => ({
        ...admin,
        // Ensure avatarUrl is always a string (fallback to empty string) to prevent Type errors in DetailsCard
        avatarUrl: admin.avatarUrl ?? '', 
      }))

      setAdmins(formattedAdmins)
      setIsLoading(false)
    } else if (error) {
      // Global error handler for API/Network failures
      handleAppError(error)
      setIsLoading(false)
    }
  }, [data, error])

  // Display a loading state while fetching data
  if (isLoading) return <LoadingSpinner />

  // Handle cases where the API returns null or the module is not found
  if (!module) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Module Not Found"
        message="Sorry, the module you're looking for doesn't exist."
      />
    )
  }

  // Formatting specific module details for the DetailsCard component
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
      admins={admins} // Strict Contributor[] type ensured by the map function above
      details={moduleDetails}
      domains={module.domains || []} // Fallback to empty array for optional props
      entityKey={moduleKey}
      labels={module.labels || []}
      mentees={module.mentees || []}
      mentors={module.mentors || []}
      programKey={programKey}
      summary={module.description || ''} // Handle potentially null description
      tags={module.tags || []}
      title={module.name || 'Untitled Module'}
      type="module"
    />
  )
}

export default ModuleDetailsPage