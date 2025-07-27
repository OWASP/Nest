'use client'

import { useQuery } from '@apollo/client'
import {
  faPlus,
  faEye,
  faEdit,
  faGraduationCap,
  faExclamationTriangle,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Button } from '@heroui/button'
import { addToast } from '@heroui/toast'
import { useUserRoles } from 'hooks/useUserRoles'
import { useRouter, useSearchParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import React, { useEffect, useMemo, useState } from 'react'

import { GET_MY_PROGRAMS } from 'server/queries/programsQueries'
import type { ExtendedSession } from 'types/auth'
import type { Program } from 'types/mentorship'

import LoadingSpinner from 'components/LoadingSpinner'
import SearchPageLayout from 'components/SearchPageLayout'

// =========================
// Compact Program Card
// =========================
const CompactProgramCard: React.FC<{
  program: Program & { userRole: string }
  onEdit: (key: string) => void
  onView: (key: string) => void
}> = ({ program, onEdit, onView }) => {
  const formatDate = (dateString: string) =>
    new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })

  const truncate = (text: string, max = 100) =>
    !text || text.length <= max ? text : `${text.substring(0, max).trim()}...`

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'admin':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
      case 'mentor':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
    }
  }

  return (
    <div className="flex h-full flex-col rounded-lg border border-gray-200 bg-white p-4 transition duration-200 hover:shadow-md dark:border-gray-700 dark:bg-gray-800">
      <div className="mb-3 flex items-start justify-between">
        <h3 className="mr-2 line-clamp-2 flex-1 text-base font-semibold text-gray-900 dark:text-white">
          {program.name}
        </h3>
        <span
          className={`rounded-full px-2 py-1 text-xs font-medium capitalize ${getRoleBadgeColor(
            program.userRole
          )}`}
        >
          {program.userRole}
        </span>
      </div>

      <div className="mb-3 text-xs text-gray-600 dark:text-gray-400">
        {program.startedAt && program.endedAt
          ? `${formatDate(program.startedAt)} - ${formatDate(program.endedAt)}`
          : program.startedAt
            ? `Started: ${formatDate(program.startedAt)}`
            : 'No dates set'}
      </div>

      <p className="mb-4 line-clamp-3 flex-grow text-sm text-gray-700 dark:text-gray-300">
        {truncate(program.description || 'No description available.')}
      </p>

      <div className="mt-auto flex gap-2">
        <Button
          size="sm"
          variant="shadow"
          className="flex-1 text-xs"
          onPress={() => onView(program.key)}
        >
          <FontAwesomeIcon icon={faEye} className="mr-1" />
          View
        </Button>
        <Button
          size="sm"
          color="primary"
          className="flex-1 text-xs"
          onPress={() => onEdit(program.key)}
        >
          <FontAwesomeIcon icon={faEdit} className="mr-1" />
          Edit
        </Button>
      </div>
    </div>
  )
}

// =========================
// Main Page
// =========================
const MyMentorshipPage: React.FC = () => {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { data: session } = useSession()
  const { roles, isLoadingRoles } = useUserRoles()

  const username = (session as ExtendedSession)?.user?.login
  const initialQuery = searchParams.get('q') || ''
  const [searchQuery, setSearchQuery] = useState(initialQuery)
  const [programs, setPrograms] = useState<Program[]>([])

  const { data, loading, error } = useQuery(GET_MY_PROGRAMS, {
    variables: { username, search: searchQuery },
    skip: !username,
    fetchPolicy: 'cache-and-network',
    errorPolicy: 'all',
  })

  useEffect(() => {
    if (data?.myPrograms) {
      setPrograms(data.myPrograms)
    }
  }, [data])

  useEffect(() => {
    if (error) {
      addToast({
        description: 'Unable to fetch your programs',
        title: 'Error',
        timeout: 3000,
        color: 'danger',
        variant: 'solid',
      })
    }
  }, [error])

  const hasAdminRole = useMemo(() => programs.some((p) => p.userRole === 'admin'), [programs])

  const handleCreateProgram = () => router.push('/mentorship/programs/create')
  const handleViewProgram = (key: string) => router.push(`/mentorship/programs/${key}`)
  const handleEditProgram = (key: string) => router.push(`/mentorship/programs/${key}/edit`)

  if (!isLoadingRoles && !roles.includes('mentor')) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex h-64 flex-col items-center justify-center">
          <FontAwesomeIcon icon={faExclamationTriangle} className="mb-4 text-6xl text-red-400" />
          <h2 className="mb-2 text-2xl font-bold text-gray-900 dark:text-white">Access Denied</h2>
          <p className="mb-6 text-lg text-gray-600 dark:text-gray-400">
            You are not a mentor. Only mentors can access this page.
          </p>
        </div>
      </div>
    )
  }

  if (loading || isLoadingRoles) {
    return <LoadingSpinner />
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header Section */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="mb-1 text-3xl font-bold text-gray-900 dark:text-white">My Mentorship</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Manage your mentorship programs and participation
          </p>
        </div>
        {hasAdminRole && (
          <Button color="primary" onPress={handleCreateProgram}>
            <FontAwesomeIcon icon={faPlus} className="mr-2" />
            Create Program
          </Button>
        )}
      </div>

      {/* Search & Programs */}
      <SearchPageLayout
        isLoaded={!loading}
        totalPages={1}
        currentPage={1}
        onPageChange={() => {}}
        onSearch={(q) => setSearchQuery(q)}
        searchQuery={searchQuery}
        searchPlaceholder="Search my programs"
        indexName="my-programs"
      >
        {programs.length === 0 ? (
          <div className="py-16 text-center">
            <FontAwesomeIcon
              icon={faGraduationCap}
              className="mb-4 text-6xl text-gray-300 dark:text-gray-600"
            />
            <h3 className="mb-2 text-xl font-medium text-gray-900 dark:text-white">
              {searchQuery ? 'No programs found' : 'No programs yet'}
            </h3>
            <p className="mb-6 text-gray-600 dark:text-gray-400">
              {searchQuery
                ? 'Try adjusting your search.'
                : "You haven't created or joined any programs yet."}
            </p>
            {!searchQuery && hasAdminRole && (
              <Button color="primary" onPress={handleCreateProgram}>
                <FontAwesomeIcon icon={faPlus} className="mr-2" />
                Create Your First Program
              </Button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {programs.map((program) => (
              <CompactProgramCard
                key={program.id}
                program={program}
                onEdit={handleEditProgram}
                onView={handleViewProgram}
              />
            ))}
          </div>
        )}
      </SearchPageLayout>
    </div>
  )
}

export default MyMentorshipPage
