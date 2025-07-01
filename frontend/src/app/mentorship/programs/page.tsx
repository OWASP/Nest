'use client'

import { useQuery } from '@apollo/client'
import { addToast } from '@heroui/toast'
import { useRouter, useSearchParams } from 'next/navigation'
import React, { useEffect, useState } from 'react'

import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import { GET_PROGRAM_DATA } from 'server/queries/getProgramsQueries'
import { Program } from 'types/program'
import Card from 'components/Card'
import SearchPageLayout from 'components/SearchPageLayout'

const ProgramsSearchPage: React.FC = () => {
  const searchParams = useSearchParams()
  const router = useRouter()

  const initialPage = parseInt(searchParams.get('page') || '1', 10)
  const initialQuery = searchParams.get('q') || ''

  const [page, setPage] = useState(initialPage)
  const [searchQuery, setSearchQuery] = useState(initialQuery)
  const [programs, setPrograms] = useState<Program[]>([])

  // Update URL on state changes
  useEffect(() => {
    const params = new URLSearchParams()
    if (searchQuery) params.set('q', searchQuery)
    if (page > 1) params.set('page', page.toString())

    router.push(`?${params.toString()}`)
  }, [page, searchQuery, router])

  // Query with current page and search query
  const { data, loading, error } = useQuery(GET_PROGRAM_DATA, {
    variables: { page, search: searchQuery },
    fetchPolicy: 'cache-and-network',
  })

  const totalPages = data?.allPrograms?.totalPages || 1
  const currentPage = data?.allPrograms?.currentPage || 1

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

  const renderProgramCard = (program: Program) => {
    const handleButtonClick = () => {
      router.push(`/mentorship/programs/${program.id}`)
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
        setPage(1) // reset to page 1 on search
      }}
      searchQuery={searchQuery}
      searchPlaceholder="Search Programs"
      indexName="programs"
      empty="No programs found"
    >
      {programs.map(renderProgramCard)}
    </SearchPageLayout>
  )
}

export default ProgramsSearchPage
