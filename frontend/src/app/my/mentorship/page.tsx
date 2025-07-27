'use client'

import { useQuery } from '@apollo/client'
import { faPlus, faGraduationCap, faEye, faEdit } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { addToast } from '@heroui/toast'
import { useUserRoles } from 'hooks/useUserRoles'
import { debounce } from 'lodash'
import { useRouter, useSearchParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import React, { useEffect, useMemo, useState } from 'react'

import { GET_MY_PROGRAMS } from 'server/queries/programsQueries'
import type { ExtendedSession } from 'types/auth'
import type { Program } from 'types/mentorship'

import ActionButton from 'components/ActionButton'
import SearchPageLayout from 'components/SearchPageLayout'

// ------------------- CompactProgramCard -------------------
const CompactProgramCard: React.FC<{
  program: Program
  onEdit: (key: string) => void
  onView: (key: string) => void
}> = ({ program, onEdit, onView }) => {
  const formatDate = (d: string) =>
    new Date(d).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })

  const roleClass = {
    admin: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    mentor: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    default: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200',
  }

  const isMentor = program.userRole === 'mentor'
  const description =
    program.description?.length > 100
      ? `${program.description.slice(0, 100)}...`
      : program.description || 'No description available.'

  return (
    <div className="h-64 w-80 rounded-[5px] border border-gray-400 bg-white p-6 text-left transition-transform duration-300 hover:scale-[1.02] hover:brightness-105 dark:border-gray-600 dark:bg-gray-800">
      <div className="flex h-full flex-col justify-between">
        <div>
          <div className="mb-2 flex items-start justify-between">
            <h3 className="line-clamp-2 text-base font-semibold text-gray-600 dark:text-white">
              {program.name}
            </h3>
            <span
              className={`rounded-full px-2 py-1 text-xs font-medium capitalize ${
                roleClass[program.userRole] ?? roleClass.default
              }`}
            >
              {program.userRole}
            </span>
          </div>

          <div className="mb-2 text-xs text-gray-600 dark:text-gray-400">
            {program.startedAt && program.endedAt
              ? `${formatDate(program.startedAt)} – ${formatDate(program.endedAt)}`
              : program.startedAt
                ? `Started: ${formatDate(program.startedAt)}`
                : 'No dates set'}
          </div>

          <p className="mb-4 text-sm text-gray-700 dark:text-gray-300">{description}</p>
        </div>

        <div className="mt-auto flex gap-2">
          <ActionButton onClick={() => onView(program.key)}>
            <FontAwesomeIcon icon={faEye} className="mr-1" />
            View
          </ActionButton>
          {!isMentor && (
            <ActionButton onClick={() => onEdit(program.key)}>
              <FontAwesomeIcon icon={faEdit} className="mr-1" />
              Edit
            </ActionButton>
          )}
        </div>
      </div>
    </div>
  )
}

// ------------------- MyMentorshipPage -------------------
const MyMentorshipPage: React.FC = () => {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { data: session } = useSession()
  const { roles, isLoadingRoles } = useUserRoles()

  const username = (session as ExtendedSession)?.user?.login
  const initialQuery = searchParams.get('q') || ''
  const initialPage = parseInt(searchParams.get('page') || '1', 10)

  const [searchQuery, setSearchQuery] = useState(initialQuery)
  const [debouncedQuery, setDebouncedQuery] = useState(initialQuery)
  const [page, setPage] = useState(initialPage)
  const [programs, setPrograms] = useState<Program[]>([])

  const debounceSearch = useMemo(() => debounce((q) => setDebouncedQuery(q), 400), [])

  useEffect(() => {
    debounceSearch(searchQuery)
    return () => debounceSearch.cancel()
  }, [searchQuery])

  useEffect(() => {
    const params = new URLSearchParams()
    if (searchQuery) params.set('q', searchQuery)
    if (page > 1) params.set('page', String(page))
    const nextUrl = params.toString() ? `?${params}` : window.location.pathname
    if (window.location.search !== `?${params}`) {
      router.push(nextUrl, { scroll: false })
    }
  }, [searchQuery, page, router])

  const { data, loading, error } = useQuery(GET_MY_PROGRAMS, {
    variables: { username, search: debouncedQuery },
    skip: !username,
    fetchPolicy: 'cache-and-network',
    errorPolicy: 'all',
  })

  useEffect(() => {
    if (data?.myPrograms) setPrograms(data.myPrograms)
  }, [data])

  useEffect(() => {
    if (error) {
      addToast({
        title: 'GraphQL Error',
        description: 'Failed to fetch your programs',
        color: 'danger',
        timeout: 3000,
        variant: 'solid',
      })
    }
  }, [error])

  const handleCreate = () => router.push('/mentorship/programs/create')
  const handleView = (key: string) => router.push(`/mentorship/programs/${key}`)
  const handleEdit = (key: string) => router.push(`/mentorship/programs/${key}/edit`)

  const canCreateProgram = roles.includes('mentor')

  if (!isLoadingRoles && !canCreateProgram) {
    return (
      <div className="flex h-80 flex-col items-center justify-center px-4 text-center">
        <FontAwesomeIcon icon={faGraduationCap} className="mb-4 text-6xl text-red-400" />
        <h2 className="mb-2 text-2xl font-bold text-gray-600 dark:text-white">Access Denied</h2>
        <p className="text-gray-600 dark:text-gray-400">Only mentors can access this page.</p>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8 dark:bg-[#212529]">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-600 dark:text-white">My Mentorship</h1>
          <p className="text-gray-600 dark:text-gray-400">Programs you’ve created or joined</p>
        </div>
        {canCreateProgram && (
          <ActionButton onClick={handleCreate}>
            <FontAwesomeIcon icon={faPlus} className="mr-2" />
            Create Program
          </ActionButton>
        )}
      </div>

      <SearchPageLayout
        isLoaded={!loading}
        totalPages={1}
        currentPage={page}
        onPageChange={(p) => {
          setPage(p)
          window.scrollTo({ top: 0, behavior: 'smooth' })
        }}
        onSearch={(q) => {
          setSearchQuery(q)
          setPage(1)
        }}
        searchQuery={searchQuery}
        searchPlaceholder="Search your programs"
        indexName="my-programs"
      >
        {
          <div className="mt-16 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {programs.map((p) => (
              <CompactProgramCard key={p.id} program={p} onEdit={handleEdit} onView={handleView} />
            ))}
          </div>
        }
      </SearchPageLayout>
    </div>
  )
}

export default MyMentorshipPage
