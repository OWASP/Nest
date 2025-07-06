'use client'

import { useQuery } from '@apollo/client'
import { Button } from '@heroui/button'
import { addToast } from '@heroui/toast'
import { useRouter, useSearchParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import React, { useEffect, useState } from 'react'

import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import { GET_PROGRAM_DATA } from 'server/queries/programsQueries'
import { Program, SessionWithRole } from 'types/program'
import Card from 'components/Card'
import SearchPageLayout from 'components/SearchPageLayout'

const ProgramsSearchPage: React.FC = () => {
  const searchParams = useSearchParams()
  const router = useRouter()
  const { data: session } = useSession()

  const initialPage = parseInt(searchParams.get('page') || '1', 10)
  const initialQuery = searchParams.get('q') || ''

  const [page, setPage] = useState(initialPage)
  const [searchQuery, setSearchQuery] = useState(initialQuery)
  const [programs, setPrograms] = useState<Program[]>([])
  const [mentor, setMentor] = useState<string>('')

  useEffect(() => {
    const params = new URLSearchParams()
    if (searchQuery) params.set('q', searchQuery)
    if (page > 1) params.set('page', page.toString())

    const queryString = params.toString()
    const newUrl = queryString ? `?${queryString}` : window.location.pathname

    if (window.location.search !== (queryString ? `?${queryString}` : '')) {
      router.push(newUrl, { scroll: false })
    }
  }, [page, searchQuery, router])

  const { data, loading, error } = useQuery(GET_PROGRAM_DATA, {
    variables: { page, search: searchQuery, mentorUsername: mentor },
    fetchPolicy: 'cache-and-network',
    errorPolicy: 'all',
  })

  const totalPages = data?.allPrograms?.totalPages || 1
  const currentPage = data?.allPrograms?.currentPage || page

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
    const username = (session as SessionWithRole)?.user?.username
    if (username) {
      setMentor(username)
      setPage(1)
    }
  }

  const handleShowAllPrograms = () => {
    setMentor('')
    setPage(1)
  }

  const renderProgramCard = (program: Program) => {
    const handleButtonClick = () => {
      router.push(`/mentorship/programs/${program.key}`)
    }

    const submitButton = {
      label: 'View Details',
      icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
      onclick: handleButtonClick,
    }

    return (
      <Card
        key={program.id}
        title={program.name}
        summary={program.description}
        button={submitButton}
        timeline={{
          start: program.startedAt,
          end: program.endedAt,
        }}
        url={`/mentorship/programs/${program.id}`}
      />
    )
  }

  function handleCreateButton(): void {
    router.push('/mentorship/programs/create')
  }
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
      empty="No programs found"
    >
      <div>
        <div className="mt-8 flex justify-end gap-4">
          {(session as SessionWithRole)?.user?.role === 'mentor' && (
            <>
              <div>
                <Button className="rounded-lg" onPress={handleCreateButton}>
                  Create
                </Button>
              </div>

              {!mentor ? (
                <Button className="rounded-lg" onPress={handleMyProgramsClick}>
                  My Programs
                </Button>
              ) : (
                <Button className="rounded-lg" onPress={handleShowAllPrograms}>
                  All Programs
                </Button>
              )}
            </>
          )}
        </div>
        {programs.map(renderProgramCard)}
      </div>
    </SearchPageLayout>
  )
}

export default ProgramsSearchPage
