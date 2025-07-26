'use client'

import { useQuery } from '@apollo/client'
import { addToast } from '@heroui/toast'
import { debounce } from 'lodash'
import { useRouter, useSearchParams } from 'next/navigation'
import React, { useEffect, useState, useMemo } from 'react'

import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import { GET_PROGRAM_DATA } from 'server/queries/programsQueries'
import type { Program } from 'types/mentorship'
import Card from 'components/Card'
import SearchPageLayout from 'components/SearchPageLayout'

const ProgramsSearchPage: React.FC = () => {
  const router = useRouter()
  const searchParams = useSearchParams()

  const initialPage = parseInt(searchParams.get('page') || '1', 10)
  const initialQuery = searchParams.get('q') || ''
  const [page, setPage] = useState(initialPage)
  const [searchQuery, setSearchQuery] = useState(initialQuery)
  const [debouncedQuery, setDebouncedQuery] = useState(initialQuery)
  const [programs, setPrograms] = useState<Program[]>([])

  const debounceSearch = useMemo(() => {
    return debounce((query: string) => {
      setDebouncedQuery(query)
    }, 500)
  }, [])

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

    const queryString = params.toString()
    const newUrl = queryString ? `?${queryString}` : window.location.pathname

    if (window.location.search !== `?${queryString}`) {
      router.push(newUrl, { scroll: false })
    }
  }, [page, searchQuery, router])

  const { data, loading, error } = useQuery(GET_PROGRAM_DATA, {
    variables: {
      page,
      search: debouncedQuery,
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
        {totalPages === 0 && (
          <div className="py-16 text-center">
            <FontAwesomeIconWrapper
              icon="fa-solid fa-search"
              className="mb-4 text-6xl text-gray-300 dark:text-gray-600"
            />
            <h3 className="mb-2 text-xl font-medium text-gray-900 dark:text-white">
              No programs found
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              {searchQuery
                ? 'Try adjusting your search criteria.'
                : 'There are no programs available at the moment.'}
            </p>
          </div>
        )}

        {programs.map(renderProgramCard)}
      </div>
    </SearchPageLayout>
  )
}

export default ProgramsSearchPage
