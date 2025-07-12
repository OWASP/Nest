'use client'

import { useQuery } from '@apollo/client'
import { Button } from '@heroui/button'
import { addToast } from '@heroui/toast'
import { useUserRoles } from 'hooks/useUserRoles'
import { debounce } from 'lodash'
import { useRouter, useSearchParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import React, { useEffect, useState, useMemo } from 'react'

import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import { GET_PROGRAM_DATA } from 'server/queries/programsQueries'
import { Program, ExtendedSession } from 'types/program'
import Card from 'components/Card'
import SearchPageLayout from 'components/SearchPageLayout'

const ProgramsSearchPage: React.FC = () => {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { data: session } = useSession()
  const { roles, isLoadingRoles } = useUserRoles()

  const initialPage = parseInt(searchParams.get('page') || '1', 10)
  const initialQuery = searchParams.get('q') || ''
  const initialMentor = searchParams.get('mentor') || ''

  const [page, setPage] = useState(initialPage)
  const [searchQuery, setSearchQuery] = useState(initialQuery)
  const [debouncedQuery, setDebouncedQuery] = useState(initialQuery)
  const [programs, setPrograms] = useState<Program[]>([])
  const [mentor, setMentor] = useState<string>(initialMentor)

  const debounceSearch = useMemo(() => {
    return debounce((query: string) => {
      setDebouncedQuery(query)
    }, 500)
  }, []) // if setDebouncedQuery is from props or context, include it in deps

  useEffect(() => {
    debounceSearch(searchQuery)

    return () => {
      debounceSearch.cancel()
    }
  }, [searchQuery, debounceSearch])

  // Sync URL with query and page
  useEffect(() => {
    const params = new URLSearchParams()
    if (searchQuery) params.set('q', searchQuery)
    if (page > 1) params.set('page', page.toString())
    if (mentor) params.set('mentor', mentor)

    const queryString = params.toString()
    const newUrl = queryString ? `?${queryString}` : window.location.pathname

    if (window.location.search !== `?${queryString}`) {
      router.push(newUrl, { scroll: false })
    }
  }, [page, searchQuery, mentor, router])

  const { data, loading, error } = useQuery(GET_PROGRAM_DATA, {
    variables: {
      page,
      search: debouncedQuery,
      mentorUsername: mentor || undefined,
    },
    fetchPolicy: 'cache-and-network',
    errorPolicy: 'all',
  })

  const totalPages = data?.allPrograms?.totalPages
  const currentPage = data?.allPrograms?.currentPage

  useEffect(() => {
    if (data?.allPrograms?.programs) {
      setPrograms(data.allPrograms.programs)
    }
  }, [data])

  useEffect(() => {
    if (error) {
      addToast({
        description: 'Unable to fetch programs',
        title: 'GraphQL Error',
        timeout: 3000,
        color: 'danger',
        variant: 'solid',
      })
    }
  }, [error])

  const handleMyProgramsClick = () => {
    const githubLogin = (session as ExtendedSession)?.user?.login
    if (githubLogin) {
      setMentor(githubLogin)
      setPage(1)
    }
  }

  const handleShowAllPrograms = () => {
    setMentor('')
    setPage(1)
  }

  const handleCreateButton = () => {
    router.push('/mentorship/programs/create')
  }

  const renderProgramCard = (program: Program) => (
    <Card
      key={program.id}
      title={program.name}
      summary={program.description}
      button={{
        label: 'View Details',
        icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
        onclick: () => router.push(`/mentorship/programs/${program.key}`),
      }}
      timeline={{
        start: program.startedAt,
        end: program.endedAt,
      }}
      url={`/mentorship/programs/${program.key}`}
    />
  )

  return (
    <SearchPageLayout
      isLoaded={!loading}
      totalPages={totalPages}
      currentPage={currentPage}
      onPageChange={(p) => {
        setPage(p)
        window.scrollTo({ top: 0, behavior: 'auto' })
      }}
      onSearch={(q) => {
        setSearchQuery(q)
        setPage(1)
      }}
      searchQuery={searchQuery}
      searchPlaceholder="Search Programs"
      indexName="programs"
    >
      <div>
        <div className="mt-8 flex justify-end gap-4">
          {!isLoadingRoles && roles.includes('mentor') && (
            <>
              <Button className="rounded-lg" onPress={handleCreateButton}>
                Create
              </Button>
              {mentor ? (
                <Button className="rounded-lg" onPress={handleShowAllPrograms}>
                  All Programs
                </Button>
              ) : (
                <Button className="rounded-lg" onPress={handleMyProgramsClick}>
                  My Programs
                </Button>
              )}
            </>
          )}
        </div>

        {totalPages === 0 && (
          <div className="text m-4 flex h-[60vh] w-full items-center justify-center text-xl dark:text-white">
            No programs found.
          </div>
        )}

        {programs.map(renderProgramCard)}
      </div>
    </SearchPageLayout>
  )
}

export default ProgramsSearchPage
