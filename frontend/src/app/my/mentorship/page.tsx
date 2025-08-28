'use client'

import { useQuery } from '@apollo/client'
import { faPlus, faGraduationCap } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { addToast } from '@heroui/toast'
import { debounce } from 'lodash'
import { useRouter, useSearchParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import React, { useEffect, useMemo, useState } from 'react'

import { GET_MY_PROGRAMS } from 'server/queries/programsQueries'
import type { ExtendedSession } from 'types/auth'
import type { Program } from 'types/mentorship'

import ActionButton from 'components/ActionButton'
import LoadingSpinner from 'components/LoadingSpinner'
import ProgramCard from 'components/ProgramCard'
import SearchPageLayout from 'components/SearchPageLayout'

const MyMentorshipPage: React.FC = () => {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { data: session } = useSession()
  const username = (session as ExtendedSession)?.user?.login

  const initialQuery = searchParams.get('q') || ''
  const initialPage = parseInt(searchParams.get('page') || '1', 10)

  const [searchQuery, setSearchQuery] = useState(initialQuery)
  const [debouncedQuery, setDebouncedQuery] = useState(initialQuery)
  const [page, setPage] = useState(initialPage)
  const [programs, setPrograms] = useState<Program[]>([])
  const [totalPages, setTotalPages] = useState(1)

  const debounceSearch = useMemo(() => debounce((q) => setDebouncedQuery(q), 400), [])

  useEffect(() => {
    debounceSearch(searchQuery)
    return () => debounceSearch.cancel()
  }, [debounceSearch, searchQuery])

  useEffect(() => {
    const params = new URLSearchParams()
    if (searchQuery) params.set('q', searchQuery)
    if (page > 1) params.set('page', String(page))
    const nextUrl = params.toString() ? `?${params}` : window.location.pathname
    if (window.location.search !== `?${params}`) {
      router.push(nextUrl, { scroll: false })
    }
  }, [searchQuery, page, router])

  const {
    data: programData,
    loading: loadingPrograms,
    error,
  } = useQuery(GET_MY_PROGRAMS, {
    variables: { search: debouncedQuery, page, limit: 24 },
    fetchPolicy: 'cache-and-network',
    errorPolicy: 'all',
  })
  const isProjectLeader = (session as ExtendedSession)?.user.isLeader

  useEffect(() => {
    if (programData?.myPrograms) {
      setPrograms(programData.myPrograms.programs)
      setTotalPages(programData.myPrograms.totalPages || 1)
    }
  }, [programData])

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

  const handleCreate = () => router.push('/my/mentorship/programs/create')
  const handleView = (key: string) => router.push(`/my/mentorship/programs/${key}`)
  const handleEdit = (key: string) => router.push(`/my/mentorship/programs/${key}/edit`)

  if (!username) {
    return <LoadingSpinner />
  }

  if (!isProjectLeader) {
    return (
      <div className="flex min-h-[80vh] flex-col items-center justify-center px-4 text-center">
        <FontAwesomeIcon icon={faGraduationCap} className="mb-4 text-6xl text-red-400" />
        <h2 className="mb-2 text-2xl font-bold text-gray-600 dark:text-white">Access Denied</h2>
        <p className="text-gray-600 dark:text-gray-400">
          Only project leaders can access this page.
        </p>
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
        <ActionButton onClick={handleCreate}>
          <FontAwesomeIcon icon={faPlus} className="mr-2" />
          {'Create Program'}
        </ActionButton>
      </div>

      <SearchPageLayout
        isLoaded={!loadingPrograms}
        totalPages={totalPages}
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
        <div className="mt-16 grid grid-cols-1 gap-x-4 gap-y-6 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
          {programs.length === 0 ? (
            <div className="col-span-full flex min-h-[40vh] flex-col items-center justify-center py-12 text-gray-500 dark:text-gray-400">
              <p className="text-lg font-semibold">Program not found</p>
            </div>
          ) : (
            programs.map((p) => (
              <ProgramCard
                accessLevel="admin"
                key={p.id}
                program={p}
                onEdit={handleEdit}
                onView={handleView}
              />
            ))
          )}
        </div>
      </SearchPageLayout>
    </div>
  )
}

export default MyMentorshipPage
